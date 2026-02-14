"""Tests for CiteKit resolvers."""

import os
import tempfile
from pathlib import Path

import pytest

from citekit.models import Location, Node


class TestDocumentResolver:
    """Test the document resolver with a real small PDF."""

    def test_extract_pages(self):
        """Create a small test PDF and extract specific pages."""
        import fitz

        from citekit.resolvers.document import DocumentResolver

        # Create a 5-page test PDF
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            doc = fitz.open()
            for i in range(5):
                page = doc.new_page()
                writer = fitz.TextWriter(page.rect)
                writer.append((50, 50), f"Page {i + 1}")
                writer.write_text(page)
            doc.save(pdf_path)
            doc.close()

            # Resolve pages 2 and 3
            resolver = DocumentResolver(output_dir=os.path.join(tmpdir, "output"))
            node = Node(
                id="test.section",
                type="section",
                location=Location(modality="document", pages=[2, 3]),
            )

            output_path = resolver.resolve(node, pdf_path)

            # Verify output
            assert os.path.exists(output_path)
            with fitz.open(output_path) as out_doc:
                assert len(out_doc) == 2

    def test_missing_pages_raises(self):
        from citekit.resolvers.document import DocumentResolver

        resolver = DocumentResolver()
        node = Node(
            id="test",
            type="section",
            location=Location(modality="document"),
        )
        with pytest.raises(ValueError, match="no page numbers"):
            resolver.resolve(node, "fake.pdf")

    def test_file_not_found(self):
        from citekit.resolvers.document import DocumentResolver

        resolver = DocumentResolver()
        node = Node(
            id="test",
            type="section",
            location=Location(modality="document", pages=[1]),
        )
        with pytest.raises(FileNotFoundError):
            resolver.resolve(node, "nonexistent.pdf")


class TestImageResolver:
    """Test the image resolver with a real image."""

    def test_crop_region(self):
        from PIL import Image

        from citekit.resolvers.image import ImageResolver

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a 100x100 test image
            img_path = os.path.join(tmpdir, "test.png")
            img = Image.new("RGB", (100, 100), color="red")
            img.save(img_path)

            # Crop the center region
            resolver = ImageResolver(output_dir=os.path.join(tmpdir, "output"))
            node = Node(
                id="test.region",
                type="diagram",
                location=Location(modality="image", bbox=(0.2, 0.2, 0.8, 0.8)),
            )

            output_path = resolver.resolve(node, img_path)

            # Verify output
            assert os.path.exists(output_path)
            with Image.open(output_path) as cropped:
                assert cropped.size == (60, 60)  # 0.6 * 100

    def test_missing_bbox_raises(self):
        from citekit.resolvers.image import ImageResolver

        resolver = ImageResolver()
        node = Node(
            id="test",
            type="diagram",
            location=Location(modality="image"),
        )
        with pytest.raises(ValueError, match="no bounding box"):
            resolver.resolve(node, "fake.png")

    def test_invalid_bbox_raises(self):
        from PIL import Image

        from citekit.resolvers.image import ImageResolver

        with tempfile.TemporaryDirectory() as tmpdir:
            img_path = os.path.join(tmpdir, "test.png")
            img = Image.new("RGB", (100, 100), color="red")
            img.save(img_path)

            resolver = ImageResolver(output_dir=os.path.join(tmpdir, "output"))
            # x1 > x2 is invalid
            node = Node(
                id="test",
                type="diagram",
                location=Location(modality="image", bbox=(0.8, 0.2, 0.2, 0.8)),
            )
            with pytest.raises(ValueError, match="Invalid bounding box"):
                resolver.resolve(node, img_path)


class TestVideoResolver:
    """Test the video resolver (mocked ffmpeg)."""

    def test_missing_timestamps_raises(self):
        from citekit.resolvers.video import VideoResolver

        resolver = VideoResolver()
        node = Node(
            id="test",
            type="explanation",
            location=Location(modality="video"),
        )
        with pytest.raises(ValueError, match="missing start/end"):
            resolver.resolve(node, "fake.mp4")

    def test_invalid_time_range(self):
        from citekit.resolvers.video import VideoResolver

        resolver = VideoResolver()
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            f.write(b"dummy")
            path = f.name
        
        try:
            node = Node(
                id="test",
                type="explanation",
                location=Location(modality="video", start=100, end=50),
            )
            with pytest.raises(ValueError, match="Invalid time range"):
                resolver.resolve(node, path)
        finally:
            if os.path.exists(path):
                os.remove(path)


class TestAudioResolver:
    """Test the audio resolver (mocked ffmpeg)."""

    def test_missing_timestamps_raises(self):
        from citekit.resolvers.audio import AudioResolver

        resolver = AudioResolver()
        node = Node(
            id="test",
            type="discussion",
            location=Location(modality="audio"),
        )
        with pytest.raises(ValueError, match="missing start/end"):
            # Should fail before checking file existence
            resolver.resolve(node, "fake.mp3")
