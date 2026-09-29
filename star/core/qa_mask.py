"""
Quality mask data model.
"""

from dataclasses import dataclass

from .raster import Raster


@dataclass
class QAMask:
    """
    Landsat QA masks.
    """

    cloud: Raster
    shadow: Raster
    snow: Raster
    water: Raster