"""
Landsat tile data model.
"""

from dataclasses import dataclass


@dataclass
class LandsatTile:
    """
    Represents a single Landsat WRS-2 tile.
    """

    path: int
    row: int
