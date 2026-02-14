"""Tests for CiteKit models."""

import json
from datetime import datetime, timezone

from citekit.models import Location, Node, ResolvedEvidence, ResourceMap


class TestLocation:
    def test_document_location(self):
        loc = Location(modality="document", pages=[1, 2, 3])
        assert loc.modality == "document"
        assert loc.pages == [1, 2, 3]
        assert loc.start is None

    def test_video_location(self):
        loc = Location(modality="video", start=10.0, end=20.0)
        assert loc.modality == "video"
        assert loc.start == 10.0
        assert loc.end == 20.0

    def test_image_location(self):
        loc = Location(modality="image", bbox=(0.1, 0.2, 0.8, 0.9))
        assert loc.bbox == (0.1, 0.2, 0.8, 0.9)

    def test_serialization_roundtrip(self):
        loc = Location(modality="document", pages=[5, 6])
        data = loc.model_dump(mode="json")
        loc2 = Location.model_validate(data)
        assert loc == loc2


class TestNode:
    def test_create_node(self):
        node = Node(
            id="chapter1.intro",
            title="Introduction",
            type="section",
            location=Location(modality="document", pages=[1]),
            summary="Introduces the topic.",
        )
        assert node.id == "chapter1.intro"
        assert node.type == "section"

    def test_node_without_optional_fields(self):
        node = Node(
            id="test",
            type="example",
            location=Location(modality="video", start=0, end=10),
        )
        assert node.title is None
        assert node.summary is None

    def test_serialization_roundtrip(self):
        node = Node(
            id="test.node",
            title="Test",
            type="definition",
            location=Location(modality="document", pages=[1, 2]),
            summary="A test node.",
        )
        data = json.loads(node.model_dump_json())
        node2 = Node.model_validate(data)
        assert node == node2


class TestResourceMap:
    def _sample_map(self) -> ResourceMap:
        return ResourceMap(
            resource_id="test_book",
            type="document",
            title="Test Book",
            source_path="/path/to/book.pdf",
            nodes=[
                Node(
                    id="ch1.intro",
                    title="Chapter 1 Intro",
                    type="section",
                    location=Location(modality="document", pages=[1, 2]),
                ),
                Node(
                    id="ch1.example",
                    title="Example 1",
                    type="example",
                    location=Location(modality="document", pages=[3]),
                ),
            ],
        )

    def test_get_node_found(self):
        rmap = self._sample_map()
        node = rmap.get_node("ch1.intro")
        assert node is not None
        assert node.title == "Chapter 1 Intro"

    def test_get_node_not_found(self):
        rmap = self._sample_map()
        assert rmap.get_node("nonexistent") is None

    def test_list_node_ids(self):
        rmap = self._sample_map()
        assert rmap.list_node_ids() == ["ch1.intro", "ch1.example"]

    def test_serialization_roundtrip(self):
        rmap = self._sample_map()
        data = json.loads(rmap.model_dump_json())
        rmap2 = ResourceMap.model_validate(data)
        assert rmap.resource_id == rmap2.resource_id
        assert len(rmap2.nodes) == 2


class TestResolvedEvidence:
    def test_create(self):
        node = Node(
            id="test",
            type="section",
            location=Location(modality="document", pages=[1]),
        )
        evidence = ResolvedEvidence(
            output_path="/out/test.pdf",
            modality="document",
            address="doc://book#pages=1-1",
            node=node,
            resource_id="book",
        )
        assert evidence.output_path == "/out/test.pdf"
        assert evidence.address == "doc://book#pages=1-1"
