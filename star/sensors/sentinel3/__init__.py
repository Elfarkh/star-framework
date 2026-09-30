"""
Sentinel-3 sensor module.

This module provides access to Sentinel-3 products
within the STAR Framework.
"""

from pathlib import Path

from .io import Sentinel3IO
from .search import Sentinel3Search
from .processing import Sentinel3Processing
from ...catalogs.stac import STAC

class Sentinel3(
    Sentinel3IO,
    Sentinel3Search,
    Sentinel3Processing,
):
    """
    Interface to Sentinel-3 products.
    """

    def __init__(
        self,
        download_directory: str | Path = "data",
    ):
        self.download_directory = Path(download_directory)
        self._catalog = STAC()

    def __repr__(self):
        return "Sentinel3()"