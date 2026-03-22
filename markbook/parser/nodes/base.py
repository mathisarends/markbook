import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import nbformat
    from markbook.parser.views import Token


class Node(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def from_token(cls, token: Token) -> Node | None:
        """Try to construct this node from a token. Return None if it doesn't match."""

    @abc.abstractmethod
    def render(self, nb: nbformat.NotebookNode) -> None:
        """Append this node's cell(s) to the notebook."""
