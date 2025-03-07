"""PDF processor implementation."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import fitz  # PyMuPDF

from xllm.processors.base import BaseProcessor

logger = logging.getLogger(__name__)


class PDFProcessor(BaseProcessor):
    """Processor for PDF documents.
    
    This processor extracts structured information from PDF documents,
    including text, tables, and metadata.
    """
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        min_title_font_size: float = 12.0,
        table_detection_threshold: float = 0.5,
    ):
        """Initialize the PDF processor.
        
        Args:
            output_dir: Directory to save processed data
            min_title_font_size: Minimum font size for text to be considered a title
            table_detection_threshold: Threshold for table detection
        """
        self.output_dir = output_dir or Path("data/processed")
        self.min_title_font_size = min_title_font_size
        self.table_detection_threshold = table_detection_threshold
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def process(self, content: bytes) -> Dict[str, Any]:
        """Process PDF content.
        
        Args:
            content: The PDF content as bytes
            
        Returns:
            A dictionary containing the processed data
        """
        try:
            # Open the PDF from memory
            pdf_document = fitz.open(stream=content, filetype="pdf")
            return self._process_pdf(pdf_document)
        except Exception as e:
            logger.error(f"Error processing PDF content: {e}")
            return {"error": str(e)}
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            A dictionary containing the processed data
        """
        try:
            # Open the PDF file
            pdf_document = fitz.open(file_path)
            result = self._process_pdf(pdf_document)
            
            # Add file metadata
            result["file_path"] = file_path
            result["file_name"] = Path(file_path).name
            
            return result
        except Exception as e:
            logger.error(f"Error processing PDF file {file_path}: {e}")
            return {"error": str(e), "file_path": file_path}
    
    def _process_pdf(self, pdf_document: fitz.Document) -> Dict[str, Any]:
        """Process a PDF document.
        
        Args:
            pdf_document: The PDF document to process
            
        Returns:
            A dictionary containing the processed data
        """
        result = {
            "metadata": self._extract_metadata(pdf_document),
            "pages": [],
            "tables": [],
            "entities": [],
        }
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            page_data = self._process_page(page, page_num, pdf_document)
            result["pages"].append(page_data)
            
            # Extract tables from the page
            tables = self._extract_tables(page)
            if tables:
                for table_idx, table in enumerate(tables):
                    table_data = {
                        "page_num": page_num,
                        "table_idx": table_idx,
                        "content": table,
                    }
                    result["tables"].append(table_data)
        
        # Extract structured entities
        result["entities"] = self._extract_entities(result["pages"])
        
        return result
    
    def _extract_metadata(self, pdf_document: fitz.Document) -> Dict[str, Any]:
        """Extract metadata from a PDF document.
        
        Args:
            pdf_document: The PDF document
            
        Returns:
            A dictionary containing the metadata
        """
        metadata = pdf_document.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": len(pdf_document),
        }
    
    def _process_page(self, page: fitz.Page, page_num: int, pdf_document: fitz.Document) -> Dict[str, Any]:
        """Process a single page.
        
        Args:
            page: The page to process
            page_num: The page number
            pdf_document: The PDF document
            
        Returns:
            A dictionary containing the processed page data
        """
        # Extract text with formatting information
        text_data = page.get_text("dict")
        
        # Process blocks to identify structure
        blocks = []
        for block in text_data["blocks"]:
            if block["type"] == 0:  # Text block
                block_data = self._process_text_block(block, page_num)
                blocks.append(block_data)
            elif block["type"] == 1:  # Image block
                block_data = {
                    "type": "image",
                    "bbox": block["bbox"],
                    "page_num": page_num,
                }
                blocks.append(block_data)
        
        return {
            "page_num": page_num,
            "text": page.get_text(),
            "blocks": blocks,
        }
    
    def _process_text_block(self, block: Dict[str, Any], page_num: int) -> Dict[str, Any]:
        """Process a text block.
        
        Args:
            block: The text block to process
            page_num: The page number
            
        Returns:
            A dictionary containing the processed block data
        """
        lines = []
        block_type = "paragraph"
        max_font_size = 0
        
        for line in block["lines"]:
            line_text = ""
            line_spans = []
            
            for span in line["spans"]:
                span_data = {
                    "text": span["text"],
                    "font": span["font"],
                    "size": span["size"],
                    "color": span["color"],
                    "flags": span["flags"],
                }
                line_spans.append(span_data)
                line_text += span["text"]
                
                # Update max font size
                max_font_size = max(max_font_size, span["size"])
            
            lines.append({
                "text": line_text,
                "spans": line_spans,
            })
        
        # Determine block type based on font size and content
        if max_font_size >= self.min_title_font_size:
            block_type = "title"
        elif self._is_list_item(lines):
            block_type = "list"
        elif self._is_table_row(lines):
            block_type = "table_row"
        
        return {
            "type": block_type,
            "bbox": block["bbox"],
            "page_num": page_num,
            "lines": lines,
            "max_font_size": max_font_size,
        }
    
    def _is_list_item(self, lines: List[Dict[str, Any]]) -> bool:
        """Check if lines represent a list item.
        
        Args:
            lines: The lines to check
            
        Returns:
            True if the lines represent a list item, False otherwise
        """
        if not lines:
            return False
        
        first_line = lines[0]["text"].strip()
        # Check for bullet points or numbered lists
        return (
            first_line.startswith("•") or
            first_line.startswith("-") or
            first_line.startswith("*") or
            (len(first_line) >= 2 and first_line[0].isdigit() and first_line[1] in [".", ")", ":"])
        )
    
    def _is_table_row(self, lines: List[Dict[str, Any]]) -> bool:
        """Check if lines represent a table row.
        
        Args:
            lines: The lines to check
            
        Returns:
            True if the lines represent a table row, False otherwise
        """
        if not lines:
            return False
        
        # Check for multiple tab characters or pipe symbols
        line_text = lines[0]["text"]
        return line_text.count("\t") > 1 or line_text.count("|") > 1
    
    def _extract_tables(self, page: fitz.Page) -> List[List[List[str]]]:
        """Extract tables from a page.
        
        Args:
            page: The page to extract tables from
            
        Returns:
            A list of tables, where each table is a list of rows, and each row is a list of cells
        """
        tables = []
        
        # Use PyMuPDF's table detection
        tab_finder = page.find_tables(
            vertical_strategy="lines",
            horizontal_strategy="lines",
            snap_tolerance=self.table_detection_threshold,
        )
        
        for tab in tab_finder:
            try:
                # Extract the table
                table_data = tab.extract()
                if table_data:
                    tables.append(table_data)
            except Exception as e:
                logger.warning(f"Error extracting table: {e}")
        
        return tables
    
    def _extract_entities(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract structured entities from pages.
        
        Args:
            pages: The processed pages
            
        Returns:
            A list of structured entities
        """
        entities = []
        
        # Track the current section and subsection
        current_section = None
        current_subsection = None
        
        for page in pages:
            for block in page["blocks"]:
                if block["type"] == "title":
                    # Get the title text
                    title_text = " ".join([line["text"] for line in block["lines"]])
                    
                    # Determine if it's a section or subsection based on font size
                    if block["max_font_size"] >= self.min_title_font_size + 2:
                        # It's a main section
                        current_section = title_text
                        current_subsection = None
                        
                        entities.append({
                            "type": "section",
                            "text": title_text,
                            "page_num": page["page_num"],
                            "parent": None,
                        })
                    else:
                        # It's a subsection
                        current_subsection = title_text
                        
                        entities.append({
                            "type": "subsection",
                            "text": title_text,
                            "page_num": page["page_num"],
                            "parent": current_section,
                        })
                
                elif block["type"] == "list":
                    # Extract list items
                    for line in block["lines"]:
                        entities.append({
                            "type": "list_item",
                            "text": line["text"],
                            "page_num": page["page_num"],
                            "section": current_section,
                            "subsection": current_subsection,
                        })
                
                elif block["type"] == "table_row":
                    # We handle tables separately, but we can mark table rows here
                    entities.append({
                        "type": "table_row",
                        "text": " ".join([line["text"] for line in block["lines"]]),
                        "page_num": page["page_num"],
                        "section": current_section,
                        "subsection": current_subsection,
                    })
        
        return entities 