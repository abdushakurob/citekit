"""CiteKit — Let AI agents open specific parts of files."""

from citekit.models import ResourceMap, Node, Location, ResolvedEvidence
from citekit.client import CiteKitClient
from citekit.address import parse_address, build_address
from citekit.mapper.base import MapperProvider
from citekit.mapper.gemini import GeminiMapper
from citekit.aggregator import create_agent_context
from citekit.adapters import MapAdapter, GenericAdapter, GraphRAGAdapter, LlamaIndexAdapter
from citekit.resolvers import Resolver, DocumentResolver, VideoResolver, AudioResolver, ImageResolver, TextResolver

__version__ = "0.1.7"

__all__ = [
    "ResourceMap",
    "Node",
    "Location",
    "ResolvedEvidence",
    "CiteKitClient",
    "parse_address",
    "build_address",
    "MapperProvider",
    "GeminiMapper",
    "create_agent_context",
    "MapAdapter",
    "GenericAdapter",
    "GraphRAGAdapter",
    "LlamaIndexAdapter",
    "Resolver",
    "DocumentResolver",
    "VideoResolver",
    "AudioResolver",
    "ImageResolver",
    "TextResolver",
]
