
"""player module."""
from abc import ABC, abstractmethod

from aiwolf.agent import Agent
from aiwolf.content import Content
from aiwolf.gameinfo import GameInfo
from aiwolf.gamesetting import GameSetting


class AbstractPlayer(ABC):
    """Abstract class that defines the functions every player agents must have."""

    @abstractmethod
    def attack(self) -> Agent:
        """Return the agent this werewolf wants to attack.

        The agent that does not exist means not wanting to attack any other.

        Returns:
            The agent this werewolf wants to attack.
        """
        pass

    @abstractmethod
    def day_start(self) -> None:
        """Called when the day starts."""
        pass

    @abstractmethod
    def divine(self) -> Agent:
        """Return the agent this seer wants to divine.

        The agent that does not exist means no divination.

        Returns:
            The agent this seer wants to divine.
        """
        pass

    @abstractmethod
    def finish(self) -> None:
        """Called when the game finishes."""
        pass

    def get_name(self) -> str:
        """Return this player's name.

        Returns:
            This player's name.
        """
        return type(self).__name__

    @abstractmethod
    def guard(self) -> Agent:
        """Return the agent this bodyguard wants to guard.

        The agent that does not exist means no guard.        

        Returns:
            The agent this bodyguard wants to guard.
        """
        pass

    @abstractmethod
    def initialize(self, game_info: GameInfo, game_setting: GameSetting) -> None:
        """Called when the game starts."""
        pass

    @abstractmethod
    def talk(self) -> Content:
        """Return this player's talk.

        Returns:
            This player's talk.
        """
        pass

    @abstractmethod
    def update(self, game_info: GameInfo) -> None:
        """Called when the game information is updated."""
        pass

    @abstractmethod
    def vote(self) -> Agent:
        """Return the agent this player wants to exclude from this game.

        Returning the agent that does not exist results in ramdom vote.

        Returns:
            The agent this player wants to exclude from this game.
        """
        pass

    @abstractmethod
    def whisper(self) -> Content:
        """Return this player's whisper.

        Returns:
            This player's whisper.
        """
        pass
