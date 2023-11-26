from collections import deque
import random
from typing import Deque, List, Optional

from aiwolf import (Agent, ComingoutContentBuilder, Content, ContentBuilder,
                    DivinedResultContentBuilder, GameInfo, GameSetting, Judge,
                    Role, Species, Vote, VoteContentBuilder, RequestContentBuilder, 
                    EstimateContentBuilder, EmptyContentBuilder)
from aiwolf.constant import AGENT_NONE, AGENT_ANY
from aiwolf.utterance import UtteranceType, Talk

from const import CONTENT_SKIP
from villager import HyunjiVillager
from analyzer import Analyzer


class HyunjiSeer(HyunjiVillager):
    me: Agent # Myself.
    co_date: int # Scheduled comingout date.
    has_co: bool # Whether or not comingout has done.
    has_first_co: bool
    my_judge_queue: Deque[Judge] # Queue of divination results.
    not_divined_agents: List[Agent] # Agents that have not been divined.
    werewolves: List[Agent] # Found werewolves.
    vote_talk: List[Vote] # Talk containing VOTE.
    voted_reports: List[Vote] # Time series of voting reports.
    request_vote_talk: List[Vote] # Talk containing REQUEST VOTE.
    random_co_role: Role
    co_villagers: List[Agent]

    def __init__(self, agent_name) -> None:
        super().__init__(agent_name)
        self.myname = agent_name
        self.co_date = 0
        self.has_co = False
        self.has_first_co = False
        self.my_judge_queue = deque()
        self.not_divined_agents = []
        self.werewolves = []
        self.vote_talk = []
        self.voted_reports = []
        self.request_vote_talk = []
        self.co_villagers = []

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.co_date = 3
        self.has_co = False
        self.has_first_co = False
        self.my_judge_queue.clear()
        self.not_divined_agents = self.get_others(self.game_info.agent_list)
        self.werewolves.clear()
        self.vote_talk.clear()
        self.voted_reports.clear()
        self.request_vote_talk.clear()
        self.co_villagers = self.get_alive_others([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.VILLAGER])

    def day_start(self) -> None:
        super().day_start()
        judge: Optional[Judge] = self.game_info.divine_result
        if judge is not None:
            self.my_judge_queue.append(judge)
            if judge.target in self.not_divined_agents:
                self.not_divined_agents.remove(judge.target)
            if judge.target in self.co_villagers:
                self.co_villagers.remove(judge.target)
            if judge.result == Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        # Comingout SEER or VILLAGER on the first day
        if not self.has_first_co and self.game_info.day == 1:
            self.has_first_co = True
            self.random_co_role: Role = random.choice([Role.SEER, Role.VILLAGER])
            return Content(ComingoutContentBuilder(self.me, self.random_co_role))
        # Situation 1: No real seer among CO SEER
        if self.random_co_role == Role.VILLAGER:
            fake_seers: List[Agent] = self.get_alive([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.SEER])
            if len(fake_seers) >= 1:
                fake_seer = self.random_select(fake_seers)
                sit1_talk: ContentBuilder = random.choice([RequestContentBuilder(fake_seer, Content(VoteContentBuilder(fake_seer))),
                                                      EstimateContentBuilder(fake_seer, Role.WEREWOLF),
                                                      EmptyContentBuilder()])
                fake_seers.remove(fake_seer)
                return Content(sit1_talk)
        # Situation 2: I am the real seer among CO SEER
        elif self.random_co_role == Role.SEER:
            fake_seers: List[Agent] = self.get_alive_others([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.SEER])
                
            if len(fake_seers) >= 1:
                fake_seer = self.random_select(fake_seers)
                sit2_talk: ContentBuilder = random.choice([EstimateContentBuilder(fake_seer, Role.SEER),
                                                           EstimateContentBuilder(fake_seer, Role.WEREWOLF),
                                                           RequestContentBuilder(fake_seer, Content(VoteContentBuilder(fake_seer))),
                                                           EmptyContentBuilder()])
                fake_seers.remove(fake_seer)
                return Content(sit2_talk)
            
        # The list of agents that voted for me in the last turn.
        voted_for_me: List[Agent] = [j.agent for j in self.voted_reports if j.target == self.me]
        # The list of agents that said they would vote for me.
        vote_talk_for_me: List[Agent] = [j.agent for j in self.vote_talk if j.target == self.me]
        # The list of agents that requested to vote for me.
        request_vote_for_me: List[Agent] = [j.agent for j in self.request_vote_talk if j.target == self.me]
            
        # Do comingout if it's on scheduled day or a werewolf is found.
        if not self.has_co and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, Role.SEER))
        # Report the divination result after doing comingout.
        if self.has_co and self.my_judge_queue:
            judge: Judge = self.my_judge_queue.popleft()
            return Content(DivinedResultContentBuilder(judge.target, judge.result))
        # Vote for one of the alive werewolves.
        candidates: List[Agent] = self.get_alive(self.werewolves)
        # Vote for one of the alive fake seers if there are no candidates.
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.SEER])
        # Vote for one of the alive agents that can vote for me this turn.
        if not candidates:
            candidates = self.get_alive_others(vote_talk_for_me)
        # Vote for one of the alive agents that requested to vote for me this turn.
        if not candidates:
            candidates = self.get_alive_others(request_vote_for_me)
        # Vote for one of the alive agents that voted for me in the last turn.
        if not candidates:
            candidates = self.get_alive(voted_for_me)
        # Vote for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate == AGENT_NONE or self.vote_candidate not in candidates:
            Analyzer.debug_print("Vote candidates: ", self.agent_to_index(candidates))
            self.vote_candidate = self.random_select(candidates)
            if self.vote_candidate != AGENT_NONE:
                return Content(VoteContentBuilder(self.vote_candidate))
        else:
            Analyzer.debug_print("Vote candidates: ", self.agent_to_index(candidates))
        return CONTENT_SKIP

    def divine(self) -> Agent:
        # Divine a agent randomly chosen from undivined agents.
        if len(self.co_villagers) > 8:
            target: Agent = self.random_select(self.co_villagers)
        else:
            target: Agent = self.random_select(self.not_divined_agents)
        return target if target != AGENT_NONE else self.me
