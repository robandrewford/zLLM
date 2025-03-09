"""Tests for the EnterprisePDFProcessor class."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
import fitz  # type: ignore  # PyMuPDF

from xllm.enterprise.pdf_processor import EnterprisePDFProcessor


@pytest.fixture
def sample_pdf_path():
    """Return a path to a sample PDF file."""
    # This is a fixture that would normally return a path to a real PDF file
    # For testing purposes, we'll just return a dummy path
    return "tests/test_data/sample_nvidia.pdf"


@pytest.fixture
def mock_pdf_document():
    """Create a mock PDF document."""
    mock_doc = MagicMock(spec=fitz.Document)

    # Mock document properties
    mock_doc.__len__.return_value = 3  # 3 pages

    # Create mock pages
    mock_pages = []
    for i in range(3):
        mock_page = MagicMock(spec=fitz.Page)

        # Mock page methods
        mock_page.get_text.return_value = {
            "blocks": [
                {
                    "type": 0,  # Text block
                    "number": i,
                    "bbox": [0, 100 * i, 500, 100 * (i + 1)],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": f"Title {i}",
                                    "font": "NVIDIASans-Bold",
                                    "size": 16.0,
                                    "color": 16777215,
                                },
                                {
                                    "text": f"Regular text {i}",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                },
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": f"Data row {i}|Value {i}|Status {i}",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        },
                        {
                            "spans": [
                                {
                                    "text": chr(8226)
                                    + f" Bullet point {i}",  # Bullet point character
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        },
                    ],
                },
                {
                    "type": 0,  # Text block with financial data
                    "number": i + 10,
                    "bbox": [0, 200 * i, 500, 200 * (i + 1)],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": f"Revenue: ${i}00M",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,  # Text block with technical data
                    "number": i + 20,
                    "bbox": [0, 300 * i, 500, 300 * (i + 1)],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": f"Memory: {i}GB GDDR6",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,  # Text block with product data
                    "number": i + 30,
                    "bbox": [0, 400 * i, 500, 400 * (i + 1)],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": f"RTX {i}080 GPU",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
            ]
        }

        # Mock find_tables method
        mock_table = MagicMock()
        mock_table.extract.return_value = [
            ["Header 1", "Header 2", "Header 3"],
            ["Data 1", "Data 2", "Data 3"],
            ["Data 4", "Data 5", "Data 6"],
        ]
        mock_page.find_tables.return_value = [mock_table]

        # Mock get_images method
        mock_page.get_images.return_value = [
            (i, 0, 0, 0, 0, 0, 0)  # Mock image reference
        ]

        mock_pages.append(mock_page)

    # Mock load_page method
    mock_doc.load_page = lambda i: mock_pages[i]

    # Mock extract_image method
    mock_doc.extract_image.return_value = {"image": b"mock_image_data", "ext": "png"}

    return mock_doc


@pytest.fixture
def processor():
    """Create an EnterprisePDFProcessor instance."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield EnterprisePDFProcessor(
            output_dir=temp_dir,
            min_title_font_size=14.0,
            table_detection_threshold=0.3,
            extract_images=True,
            save_debug_info=False,
        )


class TestEnterprisePDFProcessor:
    """Tests for the EnterprisePDFProcessor class."""

    def test_init(self):
        """Test initialization of EnterprisePDFProcessor."""
        with tempfile.TemporaryDirectory() as temp_dir:
            processor = EnterprisePDFProcessor(
                output_dir=temp_dir,
                min_title_font_size=15.0,
                table_detection_threshold=0.4,
                extract_images=True,
                save_debug_info=True,
            )

            assert processor.output_dir == Path(temp_dir)
            assert processor.min_title_font_size == 15.0
            assert processor.table_detection_threshold == 0.4
            assert processor.extract_images is True
            assert processor.save_debug_info is True
            assert processor.debug_file is None

    @patch("fitz.open")
    @patch("builtins.open", new_callable=mock_open)
    def test_process_file(self, mock_file, mock_fitz_open, processor, mock_pdf_document):
        """Test processing a PDF file."""
        # Setup mocks
        mock_fitz_open.return_value = mock_pdf_document

        # Call the method
        result = processor.process_file("dummy.pdf")

        # Verify the result
        assert "title" in result
        assert "pages" in result
        assert "tables" in result
        assert "entities" in result
        assert "financial_data" in result
        assert "technical_specs" in result
        assert "product_info" in result
        assert "images" in result

        # Verify that fitz.open was called
        mock_fitz_open.assert_called_once_with("dummy.pdf")

    def test_extract_images_from_pdf(self, processor, mock_pdf_document):
        """Test extracting images from a PDF document."""
        # Call the method
        images = processor._extract_images_from_pdf(mock_pdf_document)

        # Verify the result
        assert len(images) == 3  # One image per page
        for i, image in enumerate(images):
            assert image["page_num"] == i
            assert image["image_index"] == 1
            assert image["format"] == "png"
            assert image["data"] == b"mock_image_data"

    def test_process_nvidia_pdf(self, processor, mock_pdf_document):
        """Test processing a PDF document with NVIDIA-specific handling."""
        # Call the method
        nvidia_data = processor._process_nvidia_pdf(mock_pdf_document)

        # Verify the result
        assert "tables" in nvidia_data
        assert "entities" in nvidia_data
        assert "financial_data" in nvidia_data
        assert "technical_specs" in nvidia_data
        assert "product_info" in nvidia_data

        # Verify that we have the expected number of entities
        assert len(nvidia_data["entities"]) > 0

        # Verify that we have financial data
        assert len(nvidia_data["financial_data"]) > 0
        for entity in nvidia_data["financial_data"]:
            assert "Revenue" in entity["text"]

        # Verify that we have technical specs
        assert len(nvidia_data["technical_specs"]) > 0
        for entity in nvidia_data["technical_specs"]:
            assert "Memory" in entity["text"]

        # Verify that we have product info
        assert len(nvidia_data["product_info"]) > 0
        for entity in nvidia_data["product_info"]:
            assert "RTX" in entity["text"]

    def test_process_nvidia_page(self, processor, mock_pdf_document):
        """Test processing a page with NVIDIA-specific handling."""
        # Get a mock page
        page = mock_pdf_document.load_page(0)

        # Call the method
        page_data = processor._process_nvidia_page(page, 0, mock_pdf_document)

        # Verify the result
        assert "page_num" in page_data
        assert "tables" in page_data
        assert "entities" in page_data
        assert "images" in page_data

        # Verify page number
        assert page_data["page_num"] == 0

        # Verify tables
        assert len(page_data["tables"]) > 0

        # Verify entities
        assert len(page_data["entities"]) > 0

        # Verify images
        assert len(page_data["images"]) > 0

    def test_extract_nvidia_tables(self, processor, mock_pdf_document):
        """Test extracting tables from a page with enhanced NVIDIA-specific detection."""
        # Get a mock page
        page = mock_pdf_document.load_page(0)

        # Call the method
        tables = processor._extract_nvidia_tables(page)

        # Verify the result
        assert len(tables) > 0
        assert len(tables[0]) == 3  # 3 rows
        assert len(tables[0][0]) == 3  # 3 columns

    def test_detect_nvidia_tables(self, processor):
        """Test detecting NVIDIA-style tables."""
        # Create mock text data
        text_data = {
            "blocks": [
                {
                    "type": 0,
                    "bbox": [0, 100, 500, 150],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Header 1|Header 2|Header 3",
                                    "font": "NVIDIASans-Bold",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,
                    "bbox": [0, 150, 500, 200],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Data 1|Data 2|Data 3",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,
                    "bbox": [0, 200, 500, 250],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Data 4|Data 5|Data 6",
                                    "font": "NVIDIASans-Regular",
                                    "size": 10.0,
                                    "color": 16777215,
                                }
                            ]
                        }
                    ],
                },
            ]
        }

        # Call the method
        tables = processor._detect_nvidia_tables(text_data)

        # Verify the result
        assert len(tables) == 1  # 1 table
        assert len(tables[0]) == 3  # 3 rows
        assert len(tables[0][0]) == 3  # 3 columns

    def test_extract_nvidia_entities(self, processor, mock_pdf_document):
        """Test extracting NVIDIA-specific entities from text data."""
        # Get text data from a mock page
        page = mock_pdf_document.load_page(0)
        text_data = page.get_text()

        # Call the method
        entities = processor._extract_nvidia_entities(text_data, 0)

        # Verify the result
        assert len(entities) > 0

        # Verify that we have different entity types
        entity_types = set(entity["type"] for entity in entities)
        assert "Title" in entity_types
        assert "List" in entity_types or "SubList" in entity_types
        assert "Note" in entity_types or "Data" in entity_types

    def test_detect_and_mark_tables(self, processor):
        """Test detecting and marking tables in the entities list."""
        # Create mock entities
        entities = [
            {
                "type": "Note",
                "text": "Header 1|Header 2|Header 3",
                "page_num": 0,
                "block_id": 0,
                "item_id": -1,
                "sub_id": -1,
                "font_name": "NVIDIASans-Bold",
                "font_size": 10.0,
                "font_color": 16777215,
                "block_number": 0,
            },
            {
                "type": "Data",
                "text": "Data 1|Data 2|Data 3",
                "page_num": 0,
                "block_id": 0,
                "item_id": -1,
                "sub_id": -1,
                "font_name": "NVIDIASans-Regular",
                "font_size": 10.0,
                "font_color": 16777215,
                "block_number": 0,
            },
            {
                "type": "Data",
                "text": "Data 4|Data 5|Data 6",
                "page_num": 0,
                "block_id": 0,
                "item_id": -1,
                "sub_id": -1,
                "font_name": "NVIDIASans-Regular",
                "font_size": 10.0,
                "font_color": 16777215,
                "block_number": 0,
            },
        ]

        # Call the method
        marked_entities = processor._detect_and_mark_tables(entities)

        # Verify the result
        assert len(marked_entities) == 3

        # Verify that entities are marked as table
        assert "table_id" in marked_entities[0]
        assert "table_role" in marked_entities[0]
        assert marked_entities[0]["table_role"] == "TL"  # Table Label

        assert "table_id" in marked_entities[1]
        assert "table_role" in marked_entities[1]
        assert marked_entities[1]["table_role"] == "TD"  # Table Data

        assert "table_id" in marked_entities[2]
        assert "table_role" in marked_entities[2]
        assert marked_entities[2]["table_role"] == "TD"  # Table Data

    def test_extract_page_images(self, processor, mock_pdf_document):
        """Test extracting images from a page."""
        # Get a mock page
        page = mock_pdf_document.load_page(0)

        # Call the method
        images = processor._extract_page_images(page, 0, mock_pdf_document)

        # Verify the result
        assert len(images) == 1
        assert images[0]["page_num"] == 0
        assert images[0]["image_index"] == 1
        assert images[0]["format"] == "png"
        assert images[0]["data"] == b"mock_image_data"

    def test_is_financial_entity(self, processor):
        """Test checking if an entity contains financial information."""
        # Create financial entities
        financial_entities = [
            {"text": "Revenue: $100M"},
            {"text": "Profit margin: 15%"},
            {"text": "Q2 FY24 earnings"},
            {"text": "Financial results"},
        ]

        # Create non-financial entities
        non_financial_entities = [
            {"text": "Product specifications"},
            {"text": "Technical details"},
            {"text": "User manual"},
        ]

        # Verify financial entities
        for entity in financial_entities:
            assert processor._is_financial_entity(entity) is True

        # Verify non-financial entities
        for entity in non_financial_entities:
            assert processor._is_financial_entity(entity) is False

    def test_is_technical_entity(self, processor):
        """Test checking if an entity contains technical specifications."""
        # Create technical entities
        technical_entities = [
            {"text": "Memory: 24GB GDDR6X"},
            {"text": "Clock speed: 1.8GHz"},
            {"text": "Power consumption: 350W"},
            {"text": "Technical specifications"},
        ]

        # Create non-technical entities
        non_technical_entities = [
            {"text": "Financial results"},
            {"text": "Product launch"},
            {"text": "Company overview"},
        ]

        # Verify technical entities
        for entity in technical_entities:
            assert processor._is_technical_entity(entity) is True

        # Verify non-technical entities
        for entity in non_technical_entities:
            assert processor._is_technical_entity(entity) is False

    def test_is_product_entity(self, processor):
        """Test checking if an entity contains product information."""
        # Create product entities
        product_entities = [
            {"text": "RTX 4090 GPU"},
            {"text": "NVIDIA GeForce GTX 1080"},
            {"text": "Quadro P5000"},
            {"text": "Product features"},
        ]

        # Create non-product entities
        non_product_entities = [
            {"text": "Financial results"},
            {"text": "Technical specifications"},
            {"text": "Company overview"},
        ]

        # Verify product entities
        for entity in product_entities:
            assert processor._is_product_entity(entity) is True

        # Verify non-product entities
        for entity in non_product_entities:
            assert processor._is_product_entity(entity) is False

    @patch("builtins.open", new_callable=mock_open)
    def test_debug_print_entities(self, mock_file, processor):
        """Test printing entities to the debug file."""
        # Create mock entities
        entities = [
            {
                "type": "Title",
                "text": "NVIDIA Investor Presentation",
                "page_num": 0,
                "block_id": 0,
                "item_id": -1,
                "sub_id": -1,
                "font_name": "NVIDIASans-Bold",
                "font_size": 16.0,
                "font_color": 16777215,
                "block_number": 0,
                "table_id": 0,
                "table_role": "TL",
            }
        ]

        # Set debug file
        processor.debug_file = mock_file()

        # Call the method
        processor._debug_print_entities(entities)

        # Verify that the debug file was written to
        mock_file().write.assert_called()

    def test_integration(self, processor, mock_pdf_document):
        """Test the entire processing pipeline."""
        # Mock fitz.open to return our mock document
        with patch("fitz.open", return_value=mock_pdf_document):
            # Call the process_file method
            result = processor.process_file("dummy.pdf")

            # Verify the result
            assert "title" in result
            assert "pages" in result
            assert "tables" in result
            assert "entities" in result
            assert "financial_data" in result
            assert "technical_specs" in result
            assert "product_info" in result
            assert "images" in result

            # Verify that we have the expected number of pages
            assert len(result["pages"]) == 3

            # Verify that we have tables
            assert len(result["tables"]) > 0

            # Verify that we have entities
            assert len(result["entities"]) > 0

            # Verify that we have financial data
            assert len(result["financial_data"]) > 0

            # Verify that we have technical specs
            assert len(result["technical_specs"]) > 0

            # Verify that we have product info
            assert len(result["product_info"]) > 0

            # Verify that we have images
            assert len(result["images"]) > 0
