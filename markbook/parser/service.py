from markbook.parser.views import Token
from markbook.parser.nodes import NODE_TYPES, ASTNode, ChapterNode, TocNode, Node

class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._node_types: list[Node] = NODE_TYPES

    def parse(self) -> list[ASTNode]:
        nodes = self._build_nodes()
        self._assign_anchors(nodes)
        self._resolve_tocs(nodes)
        return nodes

    def _build_nodes(self) -> list[ASTNode]:
        return [node for token in self._tokens if (node := self._match_token(token)) is not None]

    def _assign_anchors(self, nodes: list[ASTNode]) -> None:
        for node in nodes:
            if isinstance(node, ChapterNode):
                node.ensure_anchor()

    def _resolve_tocs(self, nodes: list[ASTNode]) -> None:
        chapters = [n for n in nodes if isinstance(n, ChapterNode)]
        for node in nodes:
            if isinstance(node, TocNode):
                node.resolve(chapters)

    def _match_token(self, token: Token) -> ASTNode | None:
        return next(
            (node for nt in self._node_types if (node := nt.from_token(token)) is not None),
            None,
        )