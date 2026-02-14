"""CiteKit — Let AI agents open specific parts of files."""

from citekit.models import ResourceMap, Node, Location, ResolvedEvidence
from citekit.client import CiteKitClient
from citekit.address import parse_address, build_address
from citekit.mapper.base import MapperProvider
from citekit.mapper.gemini import GeminiMapper

__version__ = "0.1.0"

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
]
