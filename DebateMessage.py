from langchain.schema import BaseMessage


class DebateMessage(BaseMessage):
    """Type of message that is spoken by a debater."""

    @property
    def type(self) -> str:
        """Type of the message, used for serialization."""
        return "chat"
