from .tokens import Token
from .nodes import NODE_TYPES, ASTNode, ChapterNode, TocNode


def parse(tokens: list[Token]) -> list[ASTNode]:
    nodes: list[ASTNode] = []

    for token in tokens:
        for node_type in NODE_TYPES:
            node = node_type.from_token(token)
            if node is not None:
                nodes.append(node)
                break

    # Post-parse: ensure all chapters have anchors, then resolve TOC
    chapters = [n for n in nodes if isinstance(n, ChapterNode)]
    for ch in chapters:
        ch.ensure_anchor()

    for node in nodes:
        if isinstance(node, TocNode):
            node.resolve(chapters)

    return nodes
