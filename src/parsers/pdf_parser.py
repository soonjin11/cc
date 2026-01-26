import pdfplumber
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """Parser for PDF documents"""

    def parse(self) -> str:
        """Extract text from PDF and convert to markdown"""
        markdown_lines = []
        markdown_lines.append(f"# {self.file_path.stem}\n")
        markdown_lines.append(f"*Source: {self.file_path.name}*\n")
        markdown_lines.append("---\n")

        try:
            with pdfplumber.open(self.file_path) as pdf:
                total_pages = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):
                    # Add page header
                    markdown_lines.append(f"\n## Page {page_num}/{total_pages}\n")

                    # Extract text
                    text = page.extract_text()
                    if text:
                        markdown_lines.append(text.strip() + "\n")

                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables, 1):
                            markdown_lines.append(f"\n### Table {table_idx}\n")
                            markdown_lines.append(self._table_to_markdown(table))
                            markdown_lines.append("\n")

        except Exception as e:
            markdown_lines.append(f"\n**Error parsing PDF:** {str(e)}\n")

        return "\n".join(markdown_lines)

    def _table_to_markdown(self, table) -> str:
        """Convert table data to markdown format"""
        if not table or len(table) == 0:
            return ""

        markdown_table = []

        # Header row
        header = table[0]
        header_clean = [str(cell).strip() if cell else "" for cell in header]
        markdown_table.append("| " + " | ".join(header_clean) + " |")
        markdown_table.append("| " + " | ".join(["---"] * len(header)) + " |")

        # Data rows
        for row in table[1:]:
            row_clean = [str(cell).strip() if cell else "" for cell in row]
            markdown_table.append("| " + " | ".join(row_clean) + " |")

        return "\n".join(markdown_table)
