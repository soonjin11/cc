from abc import ABC, abstractmethod
from pathlib import Path


class BaseParser(ABC):
    """Base class for document parsers"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    @abstractmethod
    def parse(self) -> str:
        """Parse document and return markdown content"""
        pass

    def save_markdown(self, output_path: str) -> None:
        """Save parsed content to markdown file"""
        markdown_content = self.parse()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(markdown_content, encoding='utf-8')
