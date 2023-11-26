from aiwolf import AbstractPlayer, Agent, Content, GameInfo, GameSetting, Role
from bodyguard import HyunjiBodyguard
from medium import HyunjiMedium
from possessed import HyunjiPossessed
from seer import HyunjiSeer
from villager import HyunjiVillager
from werewolf import HyunjiWerewolf
from argparse import ArgumentParser
from aiwolf import TcpipClient
from random import randint

myname = 'KimAgent{:02d}'.format(randint(0,1000))

class HyunjiPlayer(AbstractPlayer):
    villager: AbstractPlayer
    bodyguard: AbstractPlayer
    medium: AbstractPlayer
    seer: AbstractPlayer
    possessed: AbstractPlayer
    werewolf: AbstractPlayer
    player: AbstractPlayer

    def __init__(self, agent_name) -> None:
        self.myname = agent_name
        self.villager = HyunjiVillager(agent_name)
        self.bodyguard = HyunjiBodyguard(agent_name)
        self.medium = HyunjiMedium(agent_name)
        self.seer = HyunjiSeer(agent_name)
        self.possessed = HyunjiPossessed(agent_name)
        self.werewolf = HyunjiWerewolf(agent_name)
        self.player = self.villager
        self.game_setting: GameSetting = None
        self.game_info: GameInfo = None
    
    def getName(self):
        return self.myname
    
    def attack(self) -> Agent:
        return self.player.attack()

    def day_start(self) -> None:
        self.player.day_start()

    def divine(self) -> Agent:
        return self.player.divine()

    def finish(self) -> None:
        self.player.finish()

    def guard(self) -> Agent:
        return self.player.guard()

    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        self.game_setting = game_setting
        self.game_info = game_info
        role: Role = game_info.my_role
        if role == Role.VILLAGER:
            self.player = self.villager
        elif role == Role.BODYGUARD:
            self.player = self.bodyguard
        elif role == Role.MEDIUM:
            self.player = self.medium
        elif role == Role.SEER:
            self.player = self.seer
        elif role == Role.POSSESSED:
            self.player = self.possessed
        elif role == Role.WEREWOLF:
            self.player = self.werewolf
        self.player.initialize(game_info, game_setting)

    def talk(self) -> Content:
        return self.player.talk()

    def update(self, game_info: GameInfo) -> None:
        self.player.update(game_info)

    def vote(self) -> Agent:
        return self.player.vote()

    def whisper(self) -> Content:
        return self.player.whisper()

if __name__ == "__main__":
    agent: AbstractPlayer = HyunjiPlayer(myname)
    parser: ArgumentParser = ArgumentParser(add_help=False)
    parser.add_argument("-p", type=int, action="store", dest="port", required=True)
    parser.add_argument("-h", type=str, action="store", dest="hostname", required=True)
    parser.add_argument("-r", type=str, action="store", dest="role", default="none")
    parser.add_argument("-n", type=str, action="store", dest="name", default=myname)
    input_args = parser.parse_args()
    
    TcpipClient(agent, input_args.name, input_args.hostname, input_args.port, input_args.role).connect()
