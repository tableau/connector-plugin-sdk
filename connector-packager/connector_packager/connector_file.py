import os.path


class ConnectorFile:

    def __init__(self, file_name: str, file_type: str):
        self.file_name: str = file_name
        self.file_type: str = file_type

    def extension(self) -> str:
        ext = os.path.splitext(self.file_name)[-1]
        # Remove the leading period.
        return ext if not ext else ext[1:]

    def __lt__(self, other: 'ConnectorFile') -> bool:
        return self.file_name < other.file_name

    def __eq__(self, other: 'ConnectorFile') -> bool:
        return self.file_name == other.file_name and self.file_type == other.file_type
