import random
from collections import deque
from typing import Deque, List

from aiwolf import (Agent, ComingoutContentBuilder, Content, Talk, Topic, Operator,
                    DivinedResultContentBuilder, GameInfo, GameSetting,
                    IdentContentBuilder, Judge, Role, Species, Vote, Status, DivinationContentBuilder,
                    VoteContentBuilder, ContentBuilder, EstimateContentBuilder, RequestContentBuilder, EmptyContentBuilder)
from aiwolf.constant import AGENT_NONE, AGENT_ANY, AGENT_UNSPEC

from const import CONTENT_SKIP, JUDGE_EMPTY
from villager import HyunjiVillager
from analyzer import Analyzer

class HyunjiPossessed(HyunjiVillager):
    fake_role: Role # Fake role.
    co_date: int # Scheduled comingout date.
    has_co: bool # Whether or not comingout has done.
    has_first_co: bool
    random_co_role: Role
    my_judgee_queue: Deque[Judge] # Queue of fake judgements.
    not_judged_agents: List[Agent] #Agents that have not been judged.
    num_wolves: int # The number of werewolves.
    werewolves: List[Agent] # Fake werewolves.
    vote_talk: List[Vote] # Talk containing VOTE.
    voted_reports: List[Vote] # Time series of voting reports.
    request_vote_talk: List[Vote] # Talk containing REQUEST VOTE.
    co_seers_others: List[Agent]
    sit1_talk: ContentBuilder
    sit2_talk: ContentBuilder

    def __init__(self, agent_name) -> None:
        super().__init__(agent_name)
        self.myname = agent_name
        self.fake_role = Role.SEER
        self.co_date = 0
        self.has_co = False
        self.has_first_co = False
        self.my_judgee_queue = deque()
        self.not_judged_agents = []
        self.num_wolves = 0
        self.werewolves = []
        self.vote_talk = []
        self.voted_reports = []
        self.request_vote_talk = []
        self.co_seers_others = []

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        super().initialize(game_info, game_setting)
        self.fake_role = Role.SEER
        self.co_date = 1
        self.has_co = False
        self.has_first_co = False
        self.my_judgee_queue.clear()
        self.not_judged_agents = self.get_others(self.game_info.agent_list)
        self.num_wolves = game_setting.role_num_map.get(Role.WEREWOLF, 0)
        self.werewolves.clear()
        self.vote_talk.clear()
        self.voted_reports.clear()
        self.request_vote_talk.clear()
        self.co_seers_others.clear()

    def get_fake_judge(self) -> Judge:
        target: Agent = AGENT_NONE
        if self.fake_role == Role.SEER:  # Fake seer chooses a target randomly.
            if self.game_info.day != 0:
                target = self.random_select(self.get_alive(self.not_judged_agents))
        elif self.fake_role == Role.MEDIUM:
            target = self.game_info.executed_agent \
                if self.game_info.executed_agent is not None \
                else AGENT_NONE
        if target == AGENT_NONE:
            return JUDGE_EMPTY
        # Determine a fake result.
        # If the number of werewolves found is less than the total number of werewolves,
        # judge as a werewolf with a probability of 0.5.
        result: Species = Species.WEREWOLF \
            if len(self.werewolves) < self.num_wolves and random.random() < 0.5 \
            else Species.HUMAN
        return Judge(self.me, self.game_info.day, target, result)

    def day_start(self) -> None:
        super().day_start()
        # Process the fake judgement.
        judge: Judge = self.get_fake_judge()
        day: int = self.game_info.day
        if day >= 2:
            vote_list: List[Vote] = self.game_info.vote_list
            # Analyzer.debug_print('vote_list:', self.vote_to_dict(vote_list))
        if judge != JUDGE_EMPTY:
            self.my_judgee_queue.append(judge)
            if judge.target in self.not_judged_agents:
                self.not_judged_agents.remove(judge.target)
            if judge.result == Species.WEREWOLF:
                self.werewolves.append(judge.target)

    def talk(self) -> Content:
        if not self.has_first_co and self.game_info.day == 1:
            self.has_first_co = True
            self.random_co_role: Role = random.choice([Role.SEER, Role.VILLAGER])
            return Content(ComingoutContentBuilder(self.me, self.random_co_role))
        
        self.co_seers_others: List[Agent] = self.get_alive_others([a for a in self.comingout_map
                                         if self.comingout_map[a] == Role.SEER])
        # Situation 1: I CO Villager
        if self.random_co_role == Role.VILLAGER:
            if len(self.co_seers_others) >= 1:
                co_seers_other = self.random_select(self.co_seers_others)
                self.sit1_talk: ContentBuilder = random.choice([RequestContentBuilder(AGENT_ANY, Content(VoteContentBuilder(co_seers_other))),
                                                      EstimateContentBuilder(co_seers_other, Role.WEREWOLF),
                                                      EmptyContentBuilder()])
                return Content(self.sit1_talk)
        # Situation 2: I CO SEER
        elif self.random_co_role == Role.SEER:
            if len(self.co_seers_others) >= 1:
                co_seers_other = self.random_select(self.co_seers_others)
                self.sit2_talk: ContentBuilder = random.choice([EstimateContentBuilder(co_seers_other, Role.WEREWOLF),
                                                           RequestContentBuilder(AGENT_ANY, Content(VoteContentBuilder(co_seers_other))),
                                                           DivinedResultContentBuilder(co_seers_other, Species.WEREWOLF),
                                                           EmptyContentBuilder()])
                return Content(self.sit2_talk)
        
        # Do comingout if it's on scheduled day or a werewolf is found.
        if self.fake_role != Role.VILLAGER and not self.has_co \
                and (self.game_info.day == self.co_date or self.werewolves):
            self.has_co = True
            return Content(ComingoutContentBuilder(self.me, self.fake_role))
        
        # Report the judgement after doing comingout.
        if self.has_co and self.my_judgee_queue:
            judge: Judge = self.my_judgee_queue.popleft()
            if self.fake_role == Role.SEER:
                return Content(DivinedResultContentBuilder(judge.target, judge.result))
            elif self.fake_role == Role.MEDIUM:
                return Content(IdentContentBuilder(judge.target, judge.result))
        
        self.vote_candidate = self.vote()
        rnd = random.randint(0, 2)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate != AGENT_NONE and rnd == 0:
            return Content(VoteContentBuilder(self.vote_candidate))
        return CONTENT_SKIP
    
    def vote(self) -> Agent:
        # The list of agents that voted for me in the last turn.
        voted_for_me: List[Agent] = [j.agent for j in self.voted_reports if j.target == self.me]
        # The list of agents that said they would vote for me.
        vote_talk_for_me: List[Agent] = [j.agent for j in self.vote_talk if j.target == self.me]
        # The list of agents that requested to vote for me.
        request_vote_for_me: List[Agent] = [j.agent for j in self.request_vote_talk if j.target == self.me]
        # The list of fake seers that reported me as a werewolf.
        fake_seers: List[Agent] = [j.agent for j in self.divination_reports
                                if j.target == self.me and j.result == Species.WEREWOLF]  
        
        # Vote for one of the alive agents that can vote for me this turn.
        candidates: List[Agent] = self.get_alive_others(vote_talk_for_me) 
        for i in range(self.talk_list_head, len(self.game_info.talk_list)): # Analyze talks that have not been analyzed yet.
            tk: Talk = self.game_info.talk_list[i]  # The talk to be analyzed.
            content: Content = Content.compile(tk.text)
            talker: Agent = tk.agent
            if content.topic == Topic.ESTIMATE and content.role == Role.WEREWOLF and content.target == self.me:
                if talker not in candidates and self.is_alive(talker):
                        candidates.append(talker)
            if content.topic == Topic.ESTIMATE and content.role == Role.SEER and content.target == self.me:
                if talker not in candidates and self.is_alive(talker):
                        candidates.append(talker)
            if content.topic == Topic.OPERATOR and content.operator == Operator.REQUEST:
                for contents in content.content_list:
                    if contents.topic == Topic.VOTE and contents.target == self.me:
                        if talker not in candidates and self.is_alive(talker):
                            candidates.append(talker)
     
        # Vote for one of the alive agents that requested to vote for me this turn.
        if not candidates:
            candidates = self.get_alive_others(request_vote_for_me)
        # Vote for one of the alive agents that voted for me in the last turn.
        if not candidates:
            candidates = self.get_alive(voted_for_me)
        # Vote for one of the alive fake werewolves.
        if not candidates:
            candidates = self.get_alive(self.werewolves)
        # Vote for one of the alive agent that declared itself the same role of Possessed
        if not candidates:
            candidates = self.get_alive([a for a in self.comingout_map
                                         if self.comingout_map[a] == self.fake_role])
        # Vote for one of the alive agents if there are no candidates.
        if not candidates:
            candidates = self.get_alive_others(self.game_info.agent_list)
        # Declare which to vote for if not declare yet or the candidate is changed.
        if self.vote_candidate == AGENT_NONE or self.vote_candidate not in candidates:
            Analyzer.debug_print("Vote candidates: ", self.agent_to_index(candidates))
            self.vote_candidate = self.random_select(candidates)
        else:
            Analyzer.debug_print("Vote candidates: ", self.agent_to_index(candidates))
        return self.vote_candidate if self.vote_candidate != AGENT_NONE else self.me
    
