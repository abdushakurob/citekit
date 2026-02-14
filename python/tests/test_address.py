"""Tests for CiteKit address parser and builder."""

import pytest

from citekit.address import build_address, parse_address
from citekit.models import Location


class TestParseAddress:
    def test_document_page_range(self):
        resource_id, loc = parse_address("doc://calculus_book#pages=12-13")
        assert resource_id == "calculus_book"
        assert loc.modality == "document"
        assert loc.pages == [12, 13]

    def test_document_single_page(self):
        resource_id, loc = parse_address("doc://book#pages=5-5")
        assert loc.pages == [5]

    def test_document_page_list(self):
        resource_id, loc = parse_address("doc://book#pages=1,3,7")
        assert loc.pages == [1, 3, 7]

    def test_video_seconds(self):
        resource_id, loc = parse_address("video://lecture1#t=192-230")
        assert resource_id == "lecture1"
        assert loc.modality == "video"
        assert loc.start == 192.0
        assert loc.end == 230.0

    def test_video_hms_format(self):
        resource_id, loc = parse_address("video://lecture#t=00:03:12-00:03:40")
        assert loc.start == 192.0
        assert loc.end == 220.0

    def test_audio_seconds(self):
        resource_id, loc = parse_address("audio://podcast#t=60-120")
        assert loc.modality == "audio"
        assert loc.start == 60.0
        assert loc.end == 120.0

    def test_image_bbox(self):
        resource_id, loc = parse_address("image://diagram#bbox=0.2,0.3,0.8,0.7")
        assert resource_id == "diagram"
        assert loc.modality == "image"
        assert loc.bbox == (0.2, 0.3, 0.8, 0.7)

    def test_no_fragment(self):
        resource_id, loc = parse_address("doc://book")
        assert resource_id == "book"
        assert loc.modality == "document"
        assert loc.pages is None

    def test_invalid_address(self):
        with pytest.raises(ValueError, match="Invalid CiteKit address"):
            parse_address("not_a_valid_address")

    def test_unknown_scheme(self):
        with pytest.raises(ValueError, match="Unknown scheme"):
            parse_address("unknown://resource#foo=bar")

    def test_invalid_bbox_count(self):
        with pytest.raises(ValueError, match="bbox must have 4 values"):
            parse_address("image://img#bbox=0.1,0.2,0.3")


class TestBuildAddress:
    def test_document_consecutive_pages(self):
        loc = Location(modality="document", pages=[3, 4, 5])
        addr = build_address("book", loc)
        assert addr == "doc://book#pages=3-5"

    def test_document_non_consecutive_pages(self):
        loc = Location(modality="document", pages=[1, 3, 7])
        addr = build_address("book", loc)
        assert addr == "doc://book#pages=1,3,7"

    def test_video_time(self):
        loc = Location(modality="video", start=192.0, end=230.0)
        addr = build_address("lecture", loc)
        assert addr == "video://lecture#t=03:12-03:50"

    def test_audio_time(self):
        loc = Location(modality="audio", start=60.0, end=120.0)
        addr = build_address("podcast", loc)
        assert addr == "audio://podcast#t=01:00-02:00"

    def test_image_bbox(self):
        loc = Location(modality="image", bbox=(0.2, 0.3, 0.8, 0.7))
        addr = build_address("diagram", loc)
        assert addr == "image://diagram#bbox=0.2,0.3,0.8,0.7"

    def test_no_location_data(self):
        loc = Location(modality="document")
        addr = build_address("book", loc)
        assert addr == "doc://book"

    def test_empty_pages_raises(self):
        loc = Location(modality="document", pages=[])
        with pytest.raises(ValueError, match="Pages list cannot be empty"):
            build_address("book", loc)


class TestRoundTrip:
    """Test that parse → build → parse produces the same result."""

    def test_document_roundtrip(self):
        original = "doc://book#pages=3-5"
        resource_id, loc = parse_address(original)
        rebuilt = build_address(resource_id, loc)
        _, loc2 = parse_address(rebuilt)
        assert loc.pages == loc2.pages

    def test_image_roundtrip(self):
        original = "image://diagram#bbox=0.2,0.3,0.8,0.7"
        resource_id, loc = parse_address(original)
        rebuilt = build_address(resource_id, loc)
        _, loc2 = parse_address(rebuilt)
        assert loc.bbox == loc2.bbox
