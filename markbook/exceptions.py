class MarkbookSyntaxError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line
