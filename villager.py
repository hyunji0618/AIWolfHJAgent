import random
from typing import Dict, List
from collections import defaultdict


from aiwolf import (AbstractPlayer, Agent, Content, GameInfo, GameSetting,
                    Judge, Role, Species, Status, Talk, Topic, Vote, Operator, 
                    VoteContentBuilder, ComingoutContentBuilder, 
                    )
from aiwolf.constant import AGENT_NONE, AGENT_ANY
from analyzer import Analyzer
from const import CONTENT_SKIP

class HyunjiVillager(AbstractPlayer):
    me: Agent # Myself.
    game_info: GameInfo # Information about current game.
    game_setting: GameSetting # Settings of current game.
    vote_candidate: Agent # Candidate for voting.
    lie_execution: Agent
    talker: Agent
    comingout_map: Dict[Agent, Role] # Mapping between an agent and the role it claims that it is.
    divination_reports: List[Judge] # Time series of divination reports.
    identification_reports: List[Judge] # Time series of identification reports.
    vote_talk: List[Vote] # Talk containing VOTE.
    voted_reports: List[Vote] # Time series of voting reports.
    request_vote_talk: List[Vote] # Talk containing REQUEST VOTE.
    talk_list_head: int # Index of the talk to be analyzed next.
    content_list: List[Content]
    will_vote_reports: Dict[Agent, Agent] 
    talk_list_all: List[Talk] # List of all talks
    talk_turn: int # Turn of the talks
    has_first_co: bool
        
    def __init__(self, agent_name) -> None:
        self.me = AGENT_NONE
        self.myname = agent_name
        self.vote_candidate = AGENT_NONE
        self.lie_execution = AGENT_NONE
        self.talker = AGENT_NONE
        self.game_info = None  
        self.comingout_map = {}
        self.divination_reports = []
        self.identification_reports = []
        self.vote_talk = []
        self.voted_reports = []
        self.request_vote_talk = []
        self.talk_list_head = 0
        self.talk_list_all = []
        self.talk_turn = 0
        self.has_first_co = False
        
    def getName(self):
        return self.myname
    
    def is_alive(self, agent: Agent) -> bool:
        """Bool value of whether the agent is alive."""
        return self.game_info.status_map[agent] == Status.ALIVE
    
    @property
    def alive_comingout_map(self) -> Dict[Agent, Role]:
        return {a: r for a, r in self.comingout_map.items() if self.is_alive(a) and r != Role.UNC}

    @property
    def alive_comingout_map_str(self) -> Dict[str, str]:
        return {a.agent_idx: r.value for a, r in self.alive_comingout_map.items() if self.is_alive(a) and r != Role.UNC}

    @property
    def will_vote_reports_str(self) -> Dict[str, str]:
        return {a.agent_idx: t.agent_idx for a, t in self.will_vote_reports.items()}

    def get_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of agents excluding myself from the given list of agents."""
        return [a for a in agent_list if a != self.me]

    def get_alive(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents contained in the given list of agents."""
        return [a for a in agent_list if self.is_alive(a)]

    def get_alive_others(self, agent_list: List[Agent]) -> List[Agent]:
        """Return a list of alive agents that is contained in the given list of agents
        and is not equal to myself."""
        return self.get_alive(self.get_others(agent_list))
    
    def vote_to_dict(self, vote_list: List[Vote]) -> Dict[int, int]:
        return {v.agent.agent_idx: v.target.agent_idx for v in vote_list}
    
    def vote_print(self, agent_int: Dict[Agent, int]) -> None:
        return {a.agent_idx: i for a, i in agent_int.items()}
    
    def get_co_players(self, agent_list: List[Agent], role: Role = Role.ANY) -> List[Agent]:
        """Return a list of agents who have claimed the given role.
        Args:
            agent_list: The list of agents.
            role: The role. If Role.ANY, return all agents who have claimed any role.
        Returns:
            A list of agents who have claimed the given role.
        """
        return [a for a in agent_list if (role == Role.ANY and self.comingout_map[a] != Role.UNC) or self.comingout_map[a] == role]
    
    def get_divination_about(self, divination_list: List[Judge], agent: Agent) -> List[Judge]:
        """Return a list of divination reports that targeted the given agent.
        Args:
            divination_list: The list of divination.
            agent: The agent.
        Returns:
            A list of divination about the given agent.
        """
        return [a for a in divination_list if a.target == agent]
    
    def wrong_divination_about_me(self, divination_list: List[Judge]) -> List[Agent]:
        """Return a list of agents that gave a wrong divination about me.
        Args:
            divination_list: The list of divination.
        Returns:
            A list of agents.
        """
        divination_about_me: List[Judge] = self.get_divination_about(divination_list, self.me)
        wrong_divination: List[Judge] = [a for a in divination_about_me if a.result != Species.HUMAN]
        return [a.agent for a in wrong_divination]

    def random_select(self, agent_list: List[Agent]) -> Agent:
        """Return one agent randomly chosen from the given list of agents."""
        return random.choice(agent_list) if agent_list else AGENT_NONE
    
    def agent_to_index(self, agent_list: List[Agent]) -> List[int]:
        return [a.agent_idx for a in agent_list]

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_info = game_info 
        self.game_setting = game_setting
        self.me = game_info.me
        self.comingout_map.clear()
        self.divination_reports.clear()
        self.identification_reports.clear()
        self.vote_talk.clear()
        self.voted_reports.clear()
        self.request_vote_talk.clear()
        self.talk_list_head = 0
        self.talk_list_all = []
        self.talk_turn = 0
        self.has_first_co = False
        
        Analyzer.game_count += 1
        Analyzer.debug_print("***************** Start of Game",  Analyzer.game_count - 1, "*****************")
        Analyzer.debug_print("My role: ", game_info.my_role)
        Analyzer.debug_print("My index: ", self.me)

    # Start the day (called everyday)
    def day_start(self) -> None:
        self.talk_list_head = 0 # Initialize talk list
        self.vote_candidate = AGENT_NONE # Initialize vote candidate
        day: int = self.game_info.day
        # From the end of day1: Print the vote reports
        if day >= 2:
            vote_list: List[Vote] = self.game_info.vote_list
            # ex) Vote list: {1: 4, 2: 4, 3: 4, 4: 3, 5: 2}
            Analyzer.debug_print('Vote list:', self.vote_to_dict(vote_list))
        
        # Start of the day. Print current state
        Analyzer.debug_print("")
        Analyzer.debug_print("------- Day Start: Day", self.game_info.day, "-------")
        Analyzer.debug_print("No. of alive agents: ", len(self.game_info.alive_agent_list))
        
        # Execution report of last night
        Analyzer.debug_print("Executed last night: ", self.game_info.executed_agent)
        Analyzer.debug_print("Latest Executed: ", self.game_info.latest_executed_agent)
        if self.game_info.executed_agent == self.me:
            Analyzer.debug_print("---------- I am killed by execution ----------")
        
        # Attack report of last night
        attacked: List[Agent] = self.game_info.last_dead_agent_list
        if len(attacked) > 0:
            Analyzer.debug_print("Attacked by werewolf: ", self.game_info.last_dead_agent_list[0])
            if self.game_info.last_dead_agent_list[0] == self.me:
                Analyzer.debug_print("---------- I was attacked ----------")
            if len(attacked) > 1:
                Analyzer.error_print("Attacked: ", *self.game_info.last_dead_agent_list)
        else:
            Analyzer.debug_print("Attacked: None")

    def update(self, game_info: GameInfo) -> None:
        self.game_info = game_info  # Update game information.
        for i in range(self.talk_list_head, len(game_info.talk_list)): # Analyze talks that have not been analyzed yet.
            tk: Talk = game_info.talk_list[i]  # The talk to be analyzed.
            talker: Agent = tk.agent
            #if talker == self.me:  # Skip my talk.
                #continue
            content: Content = Content.compile(tk.text)
            if content.topic == Topic.COMINGOUT:
                self.comingout_map[talker] = content.role
                Analyzer.debug_print("CO: ", talker, content.role)
            elif content.topic == Topic.DIVINED:
                self.divination_reports.append(Judge(talker, game_info.day, content.target, content.result))
                Analyzer.debug_print("DIVINED: ", talker, content.target, content.result)
            elif content.topic == Topic.IDENTIFIED:
                self.identification_reports.append(Judge(talker, game_info.day, content.target, content.result))
                Analyzer.debug_print("IDENTIFIED: ", talker, content.target, content.result)
            elif content.topic == Topic.ESTIMATE:
                Analyzer.debug_print("ESTIMATE: ", talker, "estimate", content.target, content.role)
            elif content.topic == Topic.VOTE:
                self.vote_talk.append(Vote(talker, game_info.day, content.target))
                Analyzer.debug_print("VOTE: ", talker, "to", content.target)
            elif content.topic == Topic.VOTED: 
                self.voted_reports.append(Vote(talker, game_info.day, content.target))
            elif content.topic == Topic.GUARDED: 
                Analyzer.debug_print("GUARDED: ", talker, content.target)
            elif content.topic == Topic.OPERATOR and content.operator == Operator.REQUEST:
                for contents in content.content_list:
                    if contents.topic == Topic.VOTE:
                        self.request_vote_talk.append(Vote(talker, game_info.day, contents.target))
                        Analyzer.debug_print("REQUEST: ", talker, "request", content.subject, "to vote", contents.target)
        self.talk_list_head = len(game_info.talk_list)  # All done.

    def talk(self) -> Content:
        if not self.has_first_co and self.game_info.day == 1:
            self.has_first_co = True
            return Content(ComingoutContentBuilder(self.me, Role.VILLAGER))
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
        reported_wolves: List[Agent] = [j.target for j in self.divination_reports
                                        if j.agent not in fake_seers and j.result == Species.WEREWOLF]
        # Vote for one of the alive agents that were judged as werewolves by non-fake seers.
        candidates: List[Agent] = self.get_alive_others(reported_wolves)

        for i in range(0, len(self.game_info.talk_list)): # Analyze talks that have not been analyzed yet.
            tk: Talk = self.game_info.talk_list[i]  # The talk to be analyzed.
            content: Content = Content.compile(tk.text)
            if content.topic == Topic.ESTIMATE and content.role == Role.WEREWOLF:
                if content.target not in candidates:
                    if self.is_alive(content.target):
                        candidates.append(content.target)
            if content.topic == Topic.OPERATOR and content.operator == Operator.REQUEST:
                for contents in content.content_list:
                    if contents.topic == Topic.VOTE:
                        if content.target not in candidates and self.is_alive(contents.target):
                            candidates.append(contents.target)
            if content.topic == Topic.DIVINED:
                if content.target not in candidates and self.is_alive(content.target):
                    candidates.append(content.target)

        # Vote for one of the alive agents that can vote for me this turn.
        if not candidates:
            candidates = self.get_alive_others(vote_talk_for_me)
        # Vote for one of the alive agents that requested to vote for me this turn.
        if not candidates:
            candidates = self.get_alive_others(request_vote_for_me)
        # Vote for one of the alive agents that voted for me in the last turn.
        if not candidates:
            candidates = self.get_alive(voted_for_me)
        # Vote for one of the alive fake seers if there are no candidates.
        if not candidates:
            candidates = self.get_alive(fake_seers)
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

    def attack(self) -> Agent:
        raise NotImplementedError()

    def divine(self) -> Agent:
        raise NotImplementedError()

    def guard(self) -> Agent:
        raise NotImplementedError()

    def whisper(self) -> Content:
        raise NotImplementedError()

    def finish(self) -> None:
        vote_list: List[Vote] = self.game_info.vote_list
        Analyzer.debug_print('List of the final vote:', self.vote_to_dict(vote_list))

        alive_wolves = [a for a in self.game_info.alive_agent_list if self.game_info.role_map[a] == Role.WEREWOLF]
        villagers_win = (len(alive_wolves) == 0)
        is_villagers_side = self.game_info.my_role in [Role.VILLAGER, Role.SEER, Role.MEDIUM, Role.BODYGUARD]
        Analyzer.update_win_rate(self.game_info, villagers_win)

        Analyzer.debug_print("")
        Analyzer.debug_print("Villagers won?: ", is_villagers_side == villagers_win)
        Analyzer.debug_print("My win rate so far: ", Analyzer.win_count[self.me], "/", Analyzer.game_count, " = ", Analyzer.win_rate[self.me])
        Analyzer.debug_print("")
        
        pass