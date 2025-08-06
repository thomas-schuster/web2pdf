#!/usr/bin/env python3
"""
Tests for the LaTeX Compiler Module
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import after path manipulation (this fixes E402)
from latex_compiler import Colors, LaTeXCompiler  # noqa: E402


class TestLaTeXCompiler:
    """Test cases for the LaTeXCompiler class"""

    def test_init_default(self):
        """Test compiler initialization with default parameters"""
        compiler = LaTeXCompiler()
        assert compiler.verbose is True

    def test_init_verbose_false(self):
        """Test compiler initialization with verbose=False"""
        compiler = LaTeXCompiler(verbose=False)
        assert compiler.verbose is False

    def test_print_colored_verbose_true(self, capsys):
        """Test colored output when verbose=True"""
        compiler = LaTeXCompiler(verbose=True)
        compiler.print_colored("Test message", Colors.GREEN)
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert Colors.GREEN in captured.out

    def test_print_colored_verbose_false(self, capsys):
        """Test no output when verbose=False"""
        compiler = LaTeXCompiler(verbose=False)
        compiler.print_colored("Test message", Colors.GREEN)
        captured = capsys.readouterr()
        assert captured.out == ""

    @patch("latex_compiler.subprocess.run")
    def test_check_xelatex_available(self, mock_run):
        """Test XeLaTeX availability check when XeLaTeX is available"""
        mock_run.return_value = Mock()
        compiler = LaTeXCompiler()
        assert compiler.check_xelatex() is True
        mock_run.assert_called_once()

    @patch("latex_compiler.subprocess.run")
    def test_check_xelatex_not_available(self, mock_run):
        """Test XeLaTeX availability check when XeLaTeX is not available"""
        mock_run.side_effect = FileNotFoundError()
        compiler = LaTeXCompiler()
        assert compiler.check_xelatex() is False

    def test_get_file_size_nonexistent(self):
        """Test file size calculation for non-existent file"""
        compiler = LaTeXCompiler()
        result = compiler.get_file_size(Path("/nonexistent/file.pdf"))
        assert result == "0 B"

    def test_get_file_size_existing_file(self):
        """Test file size calculation for existing file"""
        compiler = LaTeXCompiler()
        with tempfile.NamedTemporaryFile() as tmp_file:
            tmp_file.write(b"x" * 1024)  # Write 1KB
            tmp_file.flush()
            size = compiler.get_file_size(Path(tmp_file.name))
            assert "1.0 KB" in size

    def test_compile_document_file_not_found(self):
        """Test compilation with non-existent file"""
        compiler = LaTeXCompiler(verbose=False)
        result = compiler.compile_document("/nonexistent/file.tex")
        assert result is False

    def test_compile_document_wrong_extension(self):
        """Test compilation with wrong file extension"""
        compiler = LaTeXCompiler(verbose=False)
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_file:
            result = compiler.compile_document(tmp_file.name)
            assert result is False

    @patch.object(LaTeXCompiler, "check_xelatex")
    def test_compile_document_no_xelatex(self, mock_check):
        """Test compilation when XeLaTeX is not available"""
        mock_check.return_value = False
        compiler = LaTeXCompiler(verbose=False)

        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as tmp_file:
            tmp_file.write(b"\\documentclass{article}\\begin{document}Test\\end{document}")
            tmp_file.flush()

            try:
                result = compiler.compile_document(tmp_file.name)
                assert result is False
            finally:
                os.unlink(tmp_file.name)

    def test_cleanup_aux_files(self):
        """Test auxiliary file cleanup"""
        compiler = LaTeXCompiler(verbose=False)

        with tempfile.TemporaryDirectory() as tmp_dir:
            base_name = "test"
            tex_file = Path(tmp_dir) / f"{base_name}.tex"
            aux_file = Path(tmp_dir) / f"{base_name}.aux"
            log_file = Path(tmp_dir) / f"{base_name}.log"
            pdf_file = Path(tmp_dir) / f"{base_name}.pdf"

            # Create test files
            tex_file.write_text("test")
            aux_file.write_text("aux")
            log_file.write_text("log")
            pdf_file.write_text("pdf")

            # Cleanup should remove aux/log but keep pdf
            compiler.cleanup_aux_files(tex_file, keep_pdf=True)

            assert tex_file.exists()
            assert not aux_file.exists()
            assert not log_file.exists()
            assert pdf_file.exists()


class TestColors:
    """Test the Colors class"""

    def test_color_constants(self):
        """Test that all color constants are defined"""
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "BLUE")
        assert hasattr(Colors, "BOLD")
        assert hasattr(Colors, "NC")

        # Check they're strings with escape sequences
        assert Colors.RED.startswith("\033[")
        assert Colors.NC == "\033[0m"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
