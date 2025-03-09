"""Enterprise PDF processor implementation for NVIDIA documents.

This module provides the EnterprisePDFProcessor class, which extends the
PDFProcessor to handle NVIDIA-specific document processing.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, TextIO
import fitz  # type: ignore # PyMuPDF

from xllm.processors.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)


class EnterprisePDFProcessor(PDFProcessor):
    """Enterprise PDF processor for NVIDIA documents.

    This processor extends the base PDFProcessor with specialized functionality
    for processing NVIDIA documents, including:
    - Enhanced table detection
    - NVIDIA-specific document structure analysis
    - Entity extraction optimized for financial and technical content
    - Image extraction and processing
    """

    def __init__(
        self,
        output_dir: Optional[Union[str, Path]] = None,
        min_title_font_size: float = 14.0,  # NVIDIA docs use larger fonts for titles
        table_detection_threshold: float = 0.3,  # More aggressive table detection
        extract_images: bool = False,
        save_debug_info: bool = False,
    ):
        """Initialize the enterprise PDF processor.

        Args:
            output_dir: Directory to save processed data (str or Path)
            min_title_font_size: Minimum font size for text to be considered a title
            table_detection_threshold: Threshold for table detection
            extract_images: Whether to extract images from the PDF
            save_debug_info: Whether to save debug information
        """
        super().__init__(
            output_dir=output_dir,
            min_title_font_size=min_title_font_size,
            table_detection_threshold=table_detection_threshold,
        )
        self.extract_images = extract_images
        self.save_debug_info = save_debug_info

        # NVIDIA-specific parameters
        self.top_level_font_size = -1  # For bullet list detection
        self.min_title_font_size = min_title_font_size

        # Debug output file
        self.debug_file: Optional[TextIO] = None

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a PDF file with NVIDIA-specific handling.

        Args:
            file_path: Path to the PDF file

        Returns:
            A dictionary containing the processed data
        """
        logger.info(f"Processing NVIDIA PDF file: {file_path}")

        # Open debug file if needed
        if self.save_debug_info:
            debug_path = Path(file_path).with_suffix(".txt")
            self.debug_file = open(debug_path, "w", encoding="utf-8")
            logger.info(f"Debug information will be saved to {debug_path}")

        try:
            # Process the file using the parent method
            result = super().process_file(file_path)

            # Add NVIDIA-specific processing
            pdf_document = fitz.open(file_path)

            # Extract additional NVIDIA-specific information
            nvidia_data = self._process_nvidia_pdf(pdf_document)

            # Merge with standard processing results
            result.update(nvidia_data)

            # Extract images if requested
            if self.extract_images:
                result["images"] = self._extract_images_from_pdf(pdf_document)

            return result

        except Exception as e:
            logger.error(f"Error processing NVIDIA PDF file {file_path}: {e}")
            raise
        finally:
            # Close debug file if open
            if self.debug_file:
                self.debug_file.close()
                self.debug_file = None

    def _extract_images_from_pdf(self, pdf_document: fitz.Document) -> List[Dict[str, Any]]:
        """Extract all images from a PDF document.

        Args:
            pdf_document: The PDF document to extract images from

        Returns:
            A list of extracted images
        """
        images: List[Dict[str, Any]] = []

        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            page_images = self._extract_page_images(page, page_num, pdf_document)
            images.extend(page_images)

        return images

    def _process_nvidia_pdf(self, pdf_document: fitz.Document) -> Dict[str, Any]:
        """Process a PDF document with NVIDIA-specific handling.

        Args:
            pdf_document: The PDF document to process

        Returns:
            A dictionary containing NVIDIA-specific processed data
        """
        nvidia_data: Dict[str, Any] = {
            "tables": [],
            "entities": [],
            "financial_data": [],
            "technical_specs": [],
            "product_info": [],
        }

        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)

            # Debug output
            if self.debug_file:
                self.debug_file.write("\n----------------------------\n")
                self.debug_file.write(f"Processing page {page_num}\n\n")

            # Process page with NVIDIA-specific handling
            page_data = self._process_nvidia_page(page, page_num, pdf_document)

            # Add page data to results
            nvidia_data["tables"].extend(page_data.get("tables", []))
            nvidia_data["entities"].extend(page_data.get("entities", []))

            # Categorize entities
            for entity in page_data.get("entities", []):
                if self._is_financial_entity(entity):
                    nvidia_data["financial_data"].append(entity)
                elif self._is_technical_entity(entity):
                    nvidia_data["technical_specs"].append(entity)
                elif self._is_product_entity(entity):
                    nvidia_data["product_info"].append(entity)

        return nvidia_data

    def _process_nvidia_page(
        self, page: fitz.Page, page_num: int, pdf_document: fitz.Document
    ) -> Dict[str, Any]:
        """Process a page with NVIDIA-specific handling.

        Args:
            page: The page to process
            page_num: The page number
            pdf_document: The PDF document

        Returns:
            A dictionary containing the processed page data
        """
        page_data: Dict[str, Any] = {
            "page_num": page_num,
            "tables": [],
            "entities": [],
            "images": [],
        }

        # Extract text data
        text_data = page.get_text("dict")

        # Extract tables using enhanced detection
        tables = self._extract_nvidia_tables(page)
        page_data["tables"] = tables

        # Debug output for tables
        if self.debug_file and tables:
            for i, table in enumerate(tables):
                self.debug_file.write(f"Table ({page_num}, {i}):\n")
                for row in table:
                    self.debug_file.write(f"{row}\n")
                self.debug_file.write("\n")

        # Process text with NVIDIA-specific entity extraction
        entities = self._extract_nvidia_entities(text_data, page_num)
        page_data["entities"] = entities

        # Extract images if requested
        if self.extract_images:
            images = self._extract_page_images(page, page_num, pdf_document)
            page_data["images"] = images

            # Debug output for images
            if self.debug_file and images:
                for i, image in enumerate(images):
                    self.debug_file.write(
                        f"Image ({page_num}, {i}): {image['format']} size = {image['size']}\n"
                    )

        return page_data

    def _extract_nvidia_tables(self, page: fitz.Page) -> List[List[List[str]]]:
        """Extract tables from a page with enhanced NVIDIA-specific detection.

        Args:
            page: The page to extract tables from

        Returns:
            A list of tables, where each table is a list of rows, and each row is a list of cells
        """
        # First try PyMuPDF's built-in table detection
        tables: List[List[List[str]]] = []
        tabs = page.find_tables(
            vertical_strategy="text",
            horizontal_strategy="text",
            snap_tolerance=self.table_detection_threshold,
        )

        for tab in tabs:
            table_data = tab.extract()
            if len(table_data) > 0:
                tables.append(table_data)

        # If no tables found, try our custom detection for NVIDIA-style tables
        if not tables:
            text_data = page.get_text("dict")
            custom_tables = self._detect_nvidia_tables(text_data)
            tables.extend(custom_tables)

        return tables

    def _detect_nvidia_tables(self, text_data: Dict[str, Any]) -> List[List[List[str]]]:
        """Detect NVIDIA-style tables that may not be recognized by standard methods.

        Args:
            text_data: The text data from the page

        Returns:
            A list of detected tables
        """
        tables: List[List[List[str]]] = []
        current_table: List[List[str]] = []
        in_table = False

        # Group blocks by vertical position
        blocks_by_y: Dict[float, List[Dict[str, Any]]] = {}
        for block in text_data["blocks"]:
            if block["type"] == 0:  # Text block
                y = block["bbox"][1]  # Top y-coordinate
                if y not in blocks_by_y:
                    blocks_by_y[y] = []
                blocks_by_y[y].append(block)

        # Sort by y-coordinate
        sorted_y = sorted(blocks_by_y.keys())

        # Check for table patterns
        for i, y in enumerate(sorted_y):
            blocks = blocks_by_y[y]

            # Extract text from all blocks at this y-coordinate
            line_text = ""
            for block in blocks:
                for line in block["lines"]:
                    for span in line["spans"]:
                        line_text += span["text"] + " "

            line_text = line_text.strip()

            # Check if this line looks like a table row (contains multiple pipe characters)
            if "|" in line_text and line_text.count("|") >= 2:
                # Split by pipe character to get cells
                cells = [cell.strip() for cell in line_text.split("|") if cell.strip()]

                if not in_table:
                    in_table = True
                    current_table = []

                current_table.append(cells)
            elif in_table:
                # End of table
                if len(current_table) >= 2:  # Require at least 2 rows for a table
                    tables.append(current_table)
                current_table = []
                in_table = False

        # Add the last table if we were still in one
        if in_table and len(current_table) >= 2:
            tables.append(current_table)

        return tables

    def _extract_nvidia_entities(
        self, text_data: Dict[str, Any], page_num: int
    ) -> List[Dict[str, Any]]:
        """Extract NVIDIA-specific entities from text data.

        Args:
            text_data: The text data from the page
            page_num: The page number

        Returns:
            A list of extracted entities
        """
        entities: List[Dict[str, Any]] = []

        # Initialize tracking variables
        itemize = False
        item_id = -1
        sub_id = -1
        block_id = -1
        top_level_font_size = -1  # For bullet list detection
        old_font_size = -1
        old_text = ""
        old_type = ""

        # Process each block
        for block in text_data["blocks"]:
            if block["type"] == 0:  # Text block
                block_number = block["number"]

                # Process each line
                for line in block["lines"]:
                    # Process each span
                    for span in line["spans"]:
                        text = span["text"]
                        font_name = span["font"]
                        font_size = span["size"]
                        font_color = span["color"]

                        # Determine entity type
                        if font_size > self.min_title_font_size:
                            entity_type = "Title"
                        elif text and ord(text[0]) == 8226:  # Bullet point character
                            itemize = True
                            if top_level_font_size == -1:
                                top_level_font_size = font_size

                            if font_size > 0.98 * top_level_font_size:
                                item_id += 1
                                entity_type = "List"
                            else:
                                sub_id += 1
                                entity_type = "SubList"
                        elif itemize:
                            # Check if we're still in a list
                            if old_font_size > 0:  # Avoid division by zero
                                is_similar_font = 0.99 < font_size / old_font_size < 1.01
                            else:
                                is_similar_font = False

                            is_bullet_continuation = bool(old_text and ord(old_text[0]) == 8226)
                            itemize = bool(is_similar_font or is_bullet_continuation)

                            if not itemize:
                                item_id = -1
                                sub_id = -1
                                block_id += 1
                                entity_type = "Note"
                            else:
                                entity_type = old_type  # Continue with the same type
                        else:
                            # Not in a list
                            if text and not text[0].isdigit() and text[0] not in ("$", "+", "-"):
                                entity_type = "Note"
                            else:
                                entity_type = "Data"

                        # Update block ID
                        if block_id == -1:
                            block_id += 1
                        elif (entity_type not in (old_type, "List", "SubList")) or (
                            old_font_size > 0 and not (0.99 < font_size / old_font_size < 1.01)
                        ):
                            if (
                                old_text
                                and (not old_text[0].isdigit() or ord(old_text[0]) != 8226)
                                and entity_type not in ("List", "SubList")
                            ):
                                block_id += 1

                        # Create entity
                        entity = {
                            "type": entity_type,
                            "text": text,
                            "page_num": page_num,
                            "block_id": block_id,
                            "item_id": item_id,
                            "sub_id": sub_id,
                            "font_name": font_name,
                            "font_size": font_size,
                            "font_color": font_color,
                            "block_number": block_number,
                        }

                        # Add entity to list
                        entities.append(entity)

                        # Update tracking variables
                        old_font_size = font_size
                        old_text = text
                        old_type = entity_type

        # Detect and mark tables
        entities = self._detect_and_mark_tables(entities)

        # Debug output
        if self.debug_file:
            self._debug_print_entities(entities)

        return entities

    def _detect_and_mark_tables(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect and mark tables in the entities list.

        Args:
            entities: The list of entities

        Returns:
            The updated list of entities with table markings
        """
        table_id = -1
        table_flag = False

        for i in range(1, len(entities)):
            entity = entities[i]
            prev_entity = entities[i - 1]

            entity_type = entity["type"]
            prev_type = prev_entity["type"]
            entity_text = entity["text"]
            prev_text = prev_entity["text"]

            # Check for table pattern
            if (
                (
                    (entity_type == "Data" and prev_type == "Note")
                    or (entity_type == "Note" and prev_type == "Data")
                    or (entity_type == "Data" and prev_type == "Data")
                )
                and prev_text.count("|") == entity_text.count("|")
                and entity_text.count("|") > 2
            ):
                # Found a table
                if not table_flag:
                    table_id += 1
                    table_flag = True

                # Mark current entity
                if entity_type == "Data":
                    entities[i]["table_id"] = table_id
                    entities[i]["table_role"] = "TD"  # Table Data
                elif entity_type == "Note":
                    entities[i]["table_id"] = table_id
                    entities[i]["table_role"] = "TL"  # Table Label

                # Mark previous entity
                if prev_type == "Data":
                    entities[i - 1]["table_id"] = table_id
                    entities[i - 1]["table_role"] = "TD"  # Table Data
                elif prev_type == "Note":
                    entities[i - 1]["table_id"] = table_id
                    entities[i - 1]["table_role"] = "TL"  # Table Label
            else:
                table_flag = False

        return entities

    def _extract_page_images(
        self, page: fitz.Page, page_num: int, pdf_document: fitz.Document
    ) -> List[Dict[str, Any]]:
        """Extract images from a page.

        Args:
            page: The page to extract images from
            page_num: The page number
            pdf_document: The PDF document

        Returns:
            A list of extracted images
        """
        images: List[Dict[str, Any]] = []

        # Get list of images on the page
        image_list = page.get_images()

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            size = len(image_bytes)
            ext = base_image["ext"]

            # Create image entry
            image = {
                "page_num": page_num,
                "image_index": image_index,
                "format": ext,
                "size": size,
                "data": image_bytes,
            }

            # Save image if requested
            if self.save_debug_info:
                output_path = self.output_dir / f"image_{page_num}_{image_index}.{ext}"
                with open(output_path, "wb") as image_file:
                    image_file.write(image_bytes)

            images.append(image)

        return images

    def _is_financial_entity(self, entity: Dict[str, Any]) -> bool:
        """Check if an entity contains financial information.

        Args:
            entity: The entity to check

        Returns:
            True if the entity contains financial information, False otherwise
        """
        financial_keywords = [
            "revenue",
            "profit",
            "earnings",
            "financial",
            "quarter",
            "fiscal",
            "growth",
            "margin",
            "income",
            "statement",
            "balance",
            "sheet",
            "cash flow",
            "dividend",
            "stock",
            "share",
            "market",
            "cap",
            "investment",
            "investor",
            "q1",
            "q2",
            "q3",
            "q4",
            "fy",
            "year",
        ]

        text = entity.get("text", "").lower()

        # Check for financial keywords
        for keyword in financial_keywords:
            if keyword in text:
                return True

        # Check for currency symbols
        if "$" in text or "€" in text or "£" in text or "¥" in text:
            return True

        # Check for percentage
        if "%" in text and any(c.isdigit() for c in text):
            return True

        return False

    def _is_technical_entity(self, entity: Dict[str, Any]) -> bool:
        """Check if an entity contains technical specifications.

        Args:
            entity: The entity to check

        Returns:
            True if the entity contains technical specifications, False otherwise
        """
        technical_keywords = [
            "spec",
            "technical",
            "architecture",
            "memory",
            "bandwidth",
            "core",
            "clock",
            "speed",
            "frequency",
            "power",
            "consumption",
            "watt",
            "interface",
            "connector",
            "port",
            "dimension",
            "size",
            "weight",
            "cooling",
            "temperature",
            "thermal",
            "process",
            "nm",
            "technology",
        ]

        text = entity.get("text", "").lower()

        # Check for technical keywords
        for keyword in technical_keywords:
            if keyword in text:
                return True

        # Check for units
        units = ["gb", "tb", "mhz", "ghz", "w", "mm", "cm", "kg", "°c"]
        for unit in units:
            if unit in text and any(c.isdigit() for c in text):
                return True

        return False

    def _is_product_entity(self, entity: Dict[str, Any]) -> bool:
        """Check if an entity contains product information.

        Args:
            entity: The entity to check

        Returns:
            True if the entity contains product information, False otherwise
        """
        product_keywords = [
            "product",
            "gpu",
            "card",
            "processor",
            "chip",
            "hardware",
            "software",
            "driver",
            "release",
            "launch",
            "announce",
            "feature",
            "specification",
            "model",
            "series",
            "rtx",
            "gtx",
            "quadro",
            "tesla",
            "jetson",
            "drive",
            "shield",
            "geforce",
            "tegra",
            "cuda",
            "nvlink",
        ]

        text = entity.get("text", "").lower()

        # Check for product keywords
        for keyword in product_keywords:
            if keyword in text:
                return True

        # Check for NVIDIA product naming patterns
        if "rtx" in text or "gtx" in text or "quadro" in text or "tesla" in text:
            return True

        return False

    def _debug_print_entities(self, entities: List[Dict[str, Any]]) -> None:
        """Print entities to the debug file.

        Args:
            entities: The list of entities to print
        """
        if not self.debug_file:
            return

        for entity in entities:
            # Format entity for debug output
            entity_type = entity["type"]
            block_id = entity["block_id"]
            item_id = entity["item_id"]
            sub_id = entity["sub_id"]
            page_num = entity["page_num"]
            font_size = entity["font_size"]
            font_color = entity["font_color"]
            font_name = entity["font_name"]
            text = entity["text"]

            # Clean text for display
            text = text.strip()
            text = text.replace("  ", " ")
            text = text.replace(" |", "|")
            text = text.replace("| ", "|")
            text = text.replace("||", "|")

            # Add table information if available
            table_info = ""
            if "table_id" in entity:
                table_info = f" Table:{entity['table_id']} Role:{entity['table_role']}"

            # Write to debug file
            self.debug_file.write(
                f"{entity_type:<8}{block_id:>3}{item_id:>5}{sub_id:>3}{page_num:>3}"
                f"{font_size:>5}{font_color:>9} {font_name:<20}{text}{table_info}\n"
            )

        self.debug_file.write("\n")
