"""utterance module."""
from __future__ import annotations

from enum import Enum
from typing import Final, TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import AGENT_NONE


class UtteranceType(Enum):
    """Enumeration type for the kind of utterance."""

    TALK = "TALK"
    """Talk."""

    WHISPER = "WHISPER"
    """Whisper."""


class _Utterance(TypedDict):
    day: int
    agent: int
    idx: int
    text: str
    turn: int


class Utterance:
    """Class for utterance."""

    day: int
    """The date of this utterance."""
    agent: Agent
    """The agent who uttered."""
    idx: int
    """The index number of this utterance."""
    text: str
    """The contents of this utterance."""
    turn: int
    """The turn of this utterance."""

    OVER: Final[str] = "Over"
    """The string that nothing to say."""

    SKIP: Final[str] = "Skip"
    """The string that means skip this turn."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Utterance.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        self.day = day
        self.agent = agent
        self.idx = idx
        self.text = text
        self.turn = turn

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Utterance):
            return NotImplemented
        return self is __o or (type(self) == type(__o) and self.day == __o.day and self.agent == __o.agent
                               and self.idx == __o.idx and self.text == __o.text and self.turn == __o.turn)


class Talk(Utterance):
    """Talk class."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Talk.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance: _Utterance) -> Talk:
        """Convert a _Utterance into the corresponding Talk.

        Args:
            utterance: The _Utterance to be converted.

        Returns:
            The Talk converted from the given _Utterance.
        """
        t = Talk()
        t.day = utterance["day"]
        t.agent = Agent(utterance["agent"])
        t.idx = utterance["idx"]
        t.text = utterance["text"]
        t.turn = utterance["turn"]
        return t

class Whisper(Utterance):
    """Whisper class."""

    def __init__(self, day: int = -1, agent: Agent = AGENT_NONE, idx: int = -1, text: str = "", turn: int = -1) -> None:
        """Initialize a new instance of Whisper.

        Args:
            day(opional): The date of the utterance. Defaults to -1.
            agent(optional): The agent that utters. Defaults to C.AGENT_NONE.
            idx(optional): The index number of the utterance. Defaults to -1.
            text(optional): The uttered text. Defaults to "".
            turn(optional): The turn of the utterance. Defaults to -1.
        """
        super().__init__(day, agent, idx, text, turn)

    @staticmethod
    def compile(utterance: _Utterance) -> Whisper:
        """Convert a _Utterance into the corresponding Whisper.

        Args:
            utterance: The _Utterance to be converted.

        Returns:
            The Whisper converted from the given _Utterance.
        """
        w = Whisper()
        w.day = utterance["day"]
        w.agent = Agent(utterance["agent"])
        w.idx = utterance["idx"]
        w.text = utterance["text"]
        w.turn = utterance["turn"]
        return w
