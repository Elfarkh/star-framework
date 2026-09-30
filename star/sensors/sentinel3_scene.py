"""
Sentinel-3 scene.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sentinel3Scene:
    """
    Sentinel-3 SLSTR LST scene.
    """

    scene_id: str

    datetime: datetime

    assets: dict

    local_path: object | None = None