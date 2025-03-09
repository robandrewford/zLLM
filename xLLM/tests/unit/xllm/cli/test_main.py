"""Tests for the main CLI module."""

from unittest.mock import MagicMock, patch


from xllm.cli.main import main


class TestMain:
    """Tests for the main CLI module."""

    @patch("xllm.cli.main.argparse.ArgumentParser")
    def test_main_no_args(self, mock_parser_class):
        """Test main function with no arguments."""
        # Set up mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(command=None)

        # Call main with no arguments
        result = main([])

        # Check that help was printed and return code is 1
        mock_parser.print_help.assert_called_once()
        assert result == 1

    @patch("xllm.cli.main.argparse.ArgumentParser")
    def test_main_with_command(self, mock_parser_class):
        """Test main function with a command."""
        # Set up mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Create a mock command
        mock_command = MagicMock()
        mock_command.return_value = 0

        # Create mock args with a command
        mock_args = MagicMock(command="test-command", func=mock_command)
        mock_parser.parse_args.return_value = mock_args

        # Call main with a command
        result = main(["test-command"])

        # Check that the command was called and return code is 0
        mock_command.assert_called_once_with(mock_args)
        assert result == 0

    @patch("xllm.cli.main.argparse.ArgumentParser")
    def test_main_command_error(self, mock_parser_class):
        """Test main function when a command returns an error."""
        # Set up mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Create a mock command that returns an error
        mock_command = MagicMock()
        mock_command.return_value = 1

        # Create mock args with a command
        mock_args = MagicMock(command="test-command", func=mock_command)
        mock_parser.parse_args.return_value = mock_args

        # Call main with a command
        result = main(["test-command"])

        # Check that the command was called and return code is 1
        mock_command.assert_called_once_with(mock_args)
        assert result == 1

    @patch("xllm.cli.main.sys.argv", ["xllm"])
    @patch("xllm.cli.main.argparse.ArgumentParser")
    def test_main_default_args(self, mock_parser_class):
        """Test main function with default arguments from sys.argv."""
        # Set up mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.return_value = MagicMock(command=None)

        # Call main with default arguments
        result = main()

        # Check that parse_args was called with an empty list
        mock_parser.parse_args.assert_called_once_with([])
        assert result == 1
