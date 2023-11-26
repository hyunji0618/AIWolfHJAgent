from collections import Counter, defaultdict
from typing import DefaultDict, Dict, List

from aiwolf import Agent, GameInfo, Role
from aiwolf.constant import AGENT_NONE


class Analyzer:
    exit_on_error = False
    local = False
    need_traceback = True

    rtoi = {Role.VILLAGER: 0, Role.SEER: 1, Role.POSSESSED: 2, Role.WEREWOLF: 3, Role.MEDIUM: 4, Role.BODYGUARD: 5}
    debug_mode = True

    game_count: int = 0
    win_count: DefaultDict[Agent, int] = {}
    win_rate: DefaultDict[Agent, float] = {}
    # 役職ごとの回数
    agent_role_count: DefaultDict[Agent, DefaultDict[Role, int]] = defaultdict(lambda: defaultdict(int))
    # 役職ごとの勝利回数
    win_role_count: DefaultDict[Agent, DefaultDict[Role, int]] = defaultdict(lambda: defaultdict(int))
    # 役職ごとの勝率
    win_rate_by_role: DefaultDict[Agent, DefaultDict[Role, float]] = defaultdict(lambda: defaultdict(float))
    sum_score: float = 0.0


    @staticmethod
    def init():
        Analyzer.game_count = 0
        Analyzer.win_count = defaultdict(int)
        Analyzer.win_rate = defaultdict(float)
        Analyzer.sum_score = 0

    @staticmethod
    def debug_print(*args, **kwargs):
        # if type(args[0]) == str and ("exec_time" in args[0] or "len(self.assignments)" in args[0]):
        #     return
        if Analyzer.debug_mode:
            print(*args, **kwargs)

    @staticmethod
    def update_win_rate(game_info: GameInfo, villager_win: bool):
        for agent, role in game_info.role_map.items():
            is_villager_side = role in [Role.VILLAGER, Role.SEER, Role.MEDIUM, Role.BODYGUARD]
            win = villager_win if is_villager_side else not villager_win
            if agent not in Analyzer.win_count:
                Analyzer.win_count[agent] = 0
            Analyzer.agent_role_count[agent][role] += 1
            if win:
                Analyzer.win_count[agent] += 1
                Analyzer.win_role_count[agent][role] += 1
            Analyzer.win_rate[agent] = Analyzer.win_count[agent] / Analyzer.game_count
            Analyzer.win_rate_by_role[agent][role] = Analyzer.win_role_count[agent][role] / Analyzer.agent_role_count[agent][role]
        Analyzer.debug_print("")
        Analyzer.debug_print("-----------------------------------")
        for agent in game_info.agent_list:
            Analyzer.debug_print("Win rate so far: ", agent, round(Analyzer.win_rate[agent], 3))
            role = game_info.role_map[agent]
            Analyzer.debug_print("Win rate by role: ", role, round(Analyzer.win_rate_by_role[agent][role], 3))
        Analyzer.debug_print("-----------------------------------")


    @staticmethod
    def get_strong_agent(agent_list: List[Agent], threshold: float = 0.0) -> Agent:
        rate = threshold
        strong_agent = AGENT_NONE
        for agent in agent_list:
            if Analyzer.win_rate[agent] >= rate:
                rate = Analyzer.win_rate[agent]
                strong_agent = agent
        return strong_agent


    @staticmethod
    def get_weak_agent(agent_list: List[Agent], threshold: float = 1.0) -> Agent:
        rate = threshold
        weak_agent = AGENT_NONE
        for agent in agent_list:
            if Analyzer.win_rate[agent] <= rate:
                rate = Analyzer.win_rate[agent]
                weak_agent = agent
        return weak_agent



