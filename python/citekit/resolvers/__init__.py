"""Resource resolvers for CiteKit."""

from citekit.resolvers.base import Resolver
from citekit.resolvers.document import DocumentResolver
from citekit.resolvers.video import VideoResolver
from citekit.resolvers.audio import AudioResolver
from citekit.resolvers.image import ImageResolver

__all__ = [
    "Resolver",
    "DocumentResolver",
    "VideoResolver",
    "AudioResolver",
    "ImageResolver",
]
