"""
Landsat scene data model.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class LandsatScene:
    """
    Represents a single Landsat acquisition.
    """

    scene_id: str
    platforme: str
    acquisition_date: datetime

    path: int
    row: int

    cloud_cover: float

    local_path: Path
