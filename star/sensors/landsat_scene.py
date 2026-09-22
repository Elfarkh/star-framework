"""
Landsat scene data model.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

@dataclass
class LandsatScene:
    """
    Represents a single Landsat acquisition.
    """

    scene_id: str
    platform: str
    acquisition_date: datetime

    path: int
    row: int

    cloud_cover: float | None = None

    assets: dict | None = field(default=None, repr=False)
    local_path: Optional[Path] = None
