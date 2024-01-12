
"""constant module."""
import warnings
from typing import Final

from aiwolf.agent import Agent

AGENT_NONE: Final[Agent] = Agent(0)
AGENT_UNSPEC: Final[Agent] = AGENT_NONE
AGENT_ANY: Final[Agent] = Agent(0xff)


class Constant:
    """Constant class that defines some constants."""

    warnings.warn("Constant class will be deprecated in the next version.", PendingDeprecationWarning)

    AGENT_NONE: Final[Agent] = Agent(0)
    """Agent that does not exist in this game."""

    AGENT_UNSPEC: Final[Agent] = AGENT_NONE
    """Agent that means no agent specified. (Alias of AGENT_NONE)"""

    AGENT_ANY: Final[Agent] = Agent(0xff)
    """Agent that means any of the agents in this game."""
