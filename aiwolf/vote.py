"""vote module."""
from __future__ import annotations

from typing import TypedDict

from aiwolf.agent import Agent
from aiwolf.constant import AGENT_NONE


class _Vote(TypedDict):
    agent: int
    day: int
    target: int


class Vote:
    """Information of the vote for execution/attack."""

    agent: Agent
    """The agent that votes."""
    day: int
    """The date of the vote."""
    target: Agent
    """The agent to be voted on."""

    def __init__(self, agent: Agent = AGENT_NONE, day: int = -1, target: Agent = AGENT_NONE) -> None:
        """Initialize a new instance of Vote.

        Args:
            agent(optional): The agent that votes. Defaults to C.AGENT_NONE.
            day(optional): The date of the vote. Defaults to -1.
            target(optional): The agent to be voted on. Defaults to C.AGENT_NONE.
        """
        self.agent = agent
        self.day = day
        self.target = target

    @staticmethod
    def compile(vote: _Vote) -> Vote:
        """Convert a _Vote into the corresponding Vote.

        Args:
            vote: The _Vote to be converted.

        Returns:
            The Vote converted from the given _Vote.
        """
        v = Vote()
        v.agent = Agent(vote["agent"])
        v.day = vote["day"]
        v.target = Agent(vote["target"])
        return v

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Vote):
            return NotImplemented
        return self is __o or (type(self) == type(__o) and self.agent == __o.agent
                               and self.day == __o.day and self.target == __o.target)
