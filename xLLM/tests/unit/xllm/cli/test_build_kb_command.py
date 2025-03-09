"""Tests for the build_kb command."""

import argparse
from pathlib import Path
from unittest.mock import MagicMock, patch


from xllm.cli.commands.build_kb_command import register, run


class TestBuildKBCommand:
    """Tests for the build_kb command."""

    def test_register(self):
        """Test that the command registers correctly."""
        # Create a mock subparsers object
        mock_subparsers = MagicMock()
        mock_parser = MagicMock()
        mock_subparsers.add_parser.return_value = mock_parser

        # Register the command
        result = register(mock_subparsers)

        # Check that add_parser was called with the correct arguments
        mock_subparsers.add_parser.assert_called_once_with(
            "build-kb",
            help="Build a knowledge base from input data",
        )

        # Check that the parser has the expected arguments
        mock_parser.add_argument.assert_any_call(
            "--input-dir",
            type=Path,
            required=True,
            help="Directory containing input data",
        )

        mock_parser.add_argument.assert_any_call(
            "--output-dir",
            type=Path,
            required=True,
            help="Directory to save the knowledge base",
        )

        mock_parser.add_argument.assert_any_call(
            "--save",
            action="store_true",
            help="Save the knowledge base to disk",
        )

        # Check that set_defaults was called with the run function
        mock_parser.set_defaults.assert_called_once_with(func=run)

        # Check that the function returns the parser
        assert result == mock_parser

    @patch("xllm.cli.commands.build_kb_command.KnowledgeBaseBuilder")
    def test_run_success(self, mock_builder_class):
        """Test that the command runs successfully."""
        # Create mock objects
        mock_builder = MagicMock()
        mock_kb = MagicMock()
        mock_builder_class.return_value = mock_builder
        mock_builder.build.return_value = mock_kb

        # Create args
        args = argparse.Namespace(
            input_dir=Path("/path/to/input"),
            output_dir=Path("/path/to/output"),
            save=True,
        )

        # Run the command
        result = run(args)

        # Check that the builder was created with the correct arguments
        mock_builder_class.assert_called_once_with(
            input_dir=Path("/path/to/input"),
            output_dir=Path("/path/to/output"),
        )

        # Check that build was called
        mock_builder.build.assert_called_once()

        # Check that save was called
        mock_kb.save.assert_called_once()

        # Check that the function returns 0 (success)
        assert result == 0

    @patch("xllm.cli.commands.build_kb_command.KnowledgeBaseBuilder")
    def test_run_no_save(self, mock_builder_class):
        """Test that the command runs without saving."""
        # Create mock objects
        mock_builder = MagicMock()
        mock_kb = MagicMock()
        mock_builder_class.return_value = mock_builder
        mock_builder.build.return_value = mock_kb

        # Create args
        args = argparse.Namespace(
            input_dir=Path("/path/to/input"),
            output_dir=Path("/path/to/output"),
            save=False,
        )

        # Run the command
        result = run(args)

        # Check that save was not called
        mock_kb.save.assert_not_called()

        # Check that the function returns 0 (success)
        assert result == 0

    @patch("xllm.cli.commands.build_kb_command.KnowledgeBaseBuilder")
    def test_run_error(self, mock_builder_class):
        """Test that the command handles errors correctly."""
        # Make the builder raise an exception
        mock_builder_class.side_effect = Exception("Test error")

        # Create args
        args = argparse.Namespace(
            input_dir=Path("/path/to/input"),
            output_dir=Path("/path/to/output"),
            save=True,
        )

        # Run the command
        result = run(args)

        # Check that the function returns 1 (error)
        assert result == 1
