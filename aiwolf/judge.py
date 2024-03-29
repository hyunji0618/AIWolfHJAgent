
"""judge module."""
from __future__ import annotations

from typing import TypedDict

from aiwolf.agent import Agent, Species
from aiwolf.constant import AGENT_NONE


class _Judge(TypedDict):
    agent: int
    day: int
    target: int
    result: str


class Judge:
    """The judgement whether the player is a human or a werewolf."""

    agent: Agent
    """The agent that judged."""
    day: int
    """The date of the judgement."""
    target: Agent
    """The judged agent."""
    result: Species
    """The result of the judgement."""

    def __init__(self, agent: Agent = AGENT_NONE, day: int = -1, target: Agent = AGENT_NONE, result: Species = Species.UNC) -> None:
        """Initialize a new instance of Judge.

        Args:
            agent(optional): The agent that judged. Defaults to C.AGENT_NONE.
            day(optional): The date of the judgement. Defaults to -1.
            target(optional): The judged agent. Defaults to C.AGENT_NONE.
            result(optional): The result of the judgement. Defaults to Species.UNC.
        """
        self.agent = agent
        self.day = day
        self.target = target
        self.result = result

    @staticmethod
    def compile(judge: _Judge) -> Judge:
        """Convert a _Judge into the corresponding Judge.

        Args:
            judge: The _Judge to be converted.

        Returns:
            The Judge converted from the given _Judge.
        """
        j: Judge = Judge()
        j.agent = Agent(judge['agent'])
        j.day = judge['day']
        j.target = Agent(judge['target'])
        j.result = Species[judge['result']]
        return j

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Judge):
            return NotImplemented
        return self is __o or (type(self) == type(__o) and self.agent == __o.agent and self.day == __o.day
                               and self.target == __o.target and self.result == __o.result)
