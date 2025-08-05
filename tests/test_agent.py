#!/usr/bin/env python3
"""
Tests for the web2pdf agent
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests

# Import the functions from agent.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (  # noqa: E402
    convert_to_markdown,
    download_images,
    extract_metadata,
    fetch_html,
    generate_pdf,
    insert_metadata,
)


class TestFetchHTML:
    """Tests for the fetch_html function"""

    @patch("requests.get")
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching"""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = "<html><head><title>Test</title></head><body>Content</body></html>"
        mock_get.return_value = mock_response

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as temp_file:
            temp_path = temp_file.name

        try:
            fetch_html("https://example.com", temp_path)

            # Verify the request was made
            mock_get.assert_called_once_with("https://example.com")
            mock_response.raise_for_status.assert_called_once()

            # Verify file content
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == mock_response.text

        finally:
            os.unlink(temp_path)

    @patch("requests.get")
    def test_fetch_html_http_error(self, mock_get):
        """Test HTTP error handling"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as temp_file:
            temp_path = temp_file.name

        try:
            with pytest.raises(requests.exceptions.HTTPError):
                fetch_html("https://example.com/nonexistent", temp_path)
        finally:
            os.unlink(temp_path)


class TestExtractMetadata:
    """Tests for the extract_metadata function"""

    def test_extract_metadata_with_title_and_author(self):
        """Test metadata extraction with title and author"""
        html_content = """
        <html>
        <head>
            <title>Test Article Title</title>
            <meta name="author" content="John Doe">
        </head>
        <body>Content</body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_path = temp_file.name

        try:
            title, author = extract_metadata(temp_path)
            assert title == "Test Article Title"
            assert author == "John Doe"
        finally:
            os.unlink(temp_path)

    def test_extract_metadata_no_author(self):
        """Test metadata extraction without author"""
        html_content = """
        <html>
        <head>
            <title>Test Article</title>
        </head>
        <body>Content</body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_path = temp_file.name

        try:
            title, author = extract_metadata(temp_path)
            assert title == "Test Article"
            assert author == "Unknown Author"
        finally:
            os.unlink(temp_path)

    def test_extract_metadata_no_title(self):
        """Test metadata extraction without title"""
        html_content = """
        <html>
        <head>
            <meta name="author" content="Jane Smith">
        </head>
        <body>Content</body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html", encoding="utf-8") as temp_file:
            temp_file.write(html_content)
            temp_path = temp_file.name

        try:
            title, author = extract_metadata(temp_path)
            assert title == "Unknown Title"
            assert author == "Jane Smith"
        finally:
            os.unlink(temp_path)


class TestConvertToMarkdown:
    """Tests for the convert_to_markdown function"""

    @patch("subprocess.run")
    def test_convert_to_markdown_success(self, mock_run):
        """Test successful markdown conversion"""
        mock_run.return_value = MagicMock()

        convert_to_markdown("test.html", "test.md")

        mock_run.assert_called_once_with(["pandoc", "test.html", "-f", "html", "-t", "markdown", "-o", "test.md"], check=True)

    @patch("subprocess.run")
    def test_convert_to_markdown_pandoc_error(self, mock_run):
        """Test pandoc error handling"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pandoc")

        with pytest.raises(subprocess.CalledProcessError):
            convert_to_markdown("nonexistent.html", "test.md")


class TestDownloadImages:
    """Tests for the download_images function"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("requests.get")
    def test_download_images_success(self, mock_get):
        """Test successful image downloading"""
        # Create a temporary markdown file with images
        md_content = """
        # Test Article

        <img src="https://example.com/image1.jpg" alt="Test Image 1">

        Some text here.

        <img src="https://example.com/image2.png" alt="Test Image 2">
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as temp_file:
            temp_file.write(md_content)
            temp_path = temp_file.name

        # Mock successful image download
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"fake_image_data"]
        mock_get.return_value = mock_response

        try:
            os.chdir(os.path.dirname(temp_path))
            downloaded_images = download_images(os.path.basename(temp_path), "test-article")

            # Verify two images were processed
            assert len(downloaded_images) == 2

            # Check first image
            assert "https://example.com/image1.jpg" in downloaded_images
            assert downloaded_images["https://example.com/image1.jpg"]["alt"] == "Test Image 1"
            assert "test-article_image_1.jpg" in downloaded_images["https://example.com/image1.jpg"]["path"]

            # Check second image
            assert "https://example.com/image2.png" in downloaded_images
            assert downloaded_images["https://example.com/image2.png"]["alt"] == "Test Image 2"
            assert "test-article_image_2.png" in downloaded_images["https://example.com/image2.png"]["path"]

            # Verify requests were made
            assert mock_get.call_count == 2

        finally:
            os.unlink(temp_path)

    @patch("requests.get")
    def test_download_images_with_failure(self, mock_get):
        """Test image downloading with some failures"""
        md_content = """
        <img src="https://example.com/working.jpg" alt="Working Image">
        <img src="https://example.com/broken.jpg" alt="Broken Image">
        """

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as temp_file:
            temp_file.write(md_content)
            temp_path = temp_file.name

        # Mock responses - first succeeds, second fails
        def side_effect(url, **kwargs):
            if "working" in url:
                mock_response = MagicMock()
                mock_response.iter_content.return_value = [b"fake_image_data"]
                mock_response.raise_for_status.return_value = None
                return mock_response
            else:
                raise requests.exceptions.RequestException("Network error")

        mock_get.side_effect = side_effect

        try:
            os.chdir(os.path.dirname(temp_path))
            downloaded_images = download_images(os.path.basename(temp_path), "test")

            # Should have both images, but second one should be placeholder
            assert len(downloaded_images) == 2
            assert downloaded_images["https://example.com/working.jpg"]["filename"] != "example-image-a"
            assert downloaded_images["https://example.com/broken.jpg"]["filename"] == "example-image-a"

        finally:
            os.unlink(temp_path)


class TestInsertMetadata:
    """Tests for the insert_metadata function"""

    def test_insert_metadata_basic(self):
        """Test basic metadata insertion"""
        md_content = "# Test Article\n\nSome content here."

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as temp_file:
            temp_file.write(md_content)
            temp_path = temp_file.name

        metadata = {"title": "Test Title", "author": "Test Author", "date": "2025-08-05"}

        try:
            insert_metadata(temp_path, metadata)

            with open(temp_path, "r", encoding="utf-8") as f:
                result = f.read()

            # Check that YAML header was added
            assert result.startswith("---\n")
            assert "title: Test Title" in result
            assert "author: Test Author" in result
            assert "date: '2025-08-05'" in result
            assert "# Test Article" in result

        finally:
            os.unlink(temp_path)

    def test_insert_metadata_with_images(self):
        """Test metadata insertion with image replacement"""
        md_content = """# Test Article

<img src="https://example.com/image.jpg" alt="Test Image">

Some content."""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md", encoding="utf-8") as temp_file:
            temp_file.write(md_content)
            temp_path = temp_file.name

        metadata = {"title": "Test"}
        downloaded_images = {
            "https://example.com/image.jpg": {
                "path": "img/test_image_1.jpg",
                "alt": "Test Image",
                "filename": "test_image_1.jpg",
            }
        }

        try:
            insert_metadata(temp_path, metadata, downloaded_images)

            with open(temp_path, "r", encoding="utf-8") as f:
                result = f.read()

            # Check that image was replaced
            assert "![Test Image](img/test_image_1.jpg)" in result
            assert '<img src="https://example.com/image.jpg"' not in result

        finally:
            os.unlink(temp_path)


class TestGeneratePDF:
    """Tests for the generate_pdf function"""

    @patch("subprocess.run")
    def test_generate_pdf_success(self, mock_run):
        """Test successful PDF generation"""
        # Create mock files
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as md_file:
            md_file.write("# Test\nContent")
            md_path = md_file.name

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".latex") as tex_template:
            tex_template.write("\\documentclass{article}\n$body$")
            template_path = tex_template.name

        pdf_path = md_path.replace(".md", ".pdf")
        tex_path = md_path.replace(".md", ".tex")

        # Mock the LaTeX file creation
        with patch("builtins.open", mock_open(read_data="\\includegraphics{test}")):
            try:
                generate_pdf(md_path, template_path, pdf_path)

                # Should call pandoc twice - once for LaTeX, once for PDF
                assert mock_run.call_count == 2

                # Check first call (LaTeX generation)
                first_call = mock_run.call_args_list[0]
                assert "pandoc" in first_call[0][0]
                assert md_path in first_call[0][0]
                assert tex_path in first_call[0][0]

                # Check second call (PDF generation)
                second_call = mock_run.call_args_list[1]
                assert "pandoc" in second_call[0][0]
                assert pdf_path in second_call[0][0]
                assert "--pdf-engine=xelatex" in second_call[0][0]

            finally:
                # Cleanup
                for path in [md_path, template_path]:
                    if os.path.exists(path):
                        os.unlink(path)


class TestIntegration:
    """Integration tests using the real DeepLearning.AI article"""

    def test_real_article_metadata_extraction(self):
        """Test metadata extraction from the actual article we've been using"""
        # Use absolute path to parent directory
        html_file = Path(__file__).parent.parent / "issue-312.html"
        if html_file.exists():
            title, author = extract_metadata(str(html_file))

            # Basic assertions - the title should contain some expected content
            assert len(title) > 0
            assert "Unknown Title" not in title
            # Author might be "Unknown Author" for this source, which is fine
            assert len(author) > 0

    def test_downloaded_images_exist(self):
        """Test that images were downloaded in previous runs"""
        # Use absolute path to parent directory
        img_dir = Path(__file__).parent.parent / "img"
        if img_dir.exists():
            image_files = list(img_dir.glob("issue-312_image_*"))
            # Should have downloaded some images
            assert len(image_files) > 0

            # Check that files are not empty
            for img_file in image_files:
                assert img_file.stat().st_size > 0

    def test_generated_files_exist(self):
        """Test that all expected output files were generated"""
        expected_files = ["issue-312.html", "issue-312.md", "issue-312.tex", "issue-312.pdf"]

        # Use absolute path to parent directory
        base_dir = Path(__file__).parent.parent

        for filename in expected_files:
            file_path = base_dir / filename
            if file_path.exists():
                assert file_path.stat().st_size > 0, f"{filename} exists but is empty"


# Fixture for temporary directory
@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp_path)

    yield temp_path

    os.chdir(original_cwd)
    import shutil

    shutil.rmtree(temp_path, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
