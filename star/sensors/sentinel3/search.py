"""
Sentinel-3 search operations.
"""

from datetime import datetime

from geopandas import GeoDataFrame

from ..sentinel3_scene import Sentinel3Scene
from .metadata import SENTINEL3_LST_COLLECTION


class Sentinel3Search:
    """
    Sentinel-3 search operations.
    """

    def search(
        self,
        aoi: GeoDataFrame,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Sentinel3Scene]:
        """
        Search Sentinel-3 SLSTR LST scenes.
        """

        geometry = aoi.union_all()

        items = self._catalog.search(
            collection=SENTINEL3_LST_COLLECTION,
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
        )

        return [
            self._item_to_scene(item)
            for item in items
        ]

    def _item_to_scene(
        self,
        item,
    ) -> Sentinel3Scene:
        """
        Convert a STAC item to a Sentinel-3 scene.
        """

        return Sentinel3Scene(
            scene_id=item.id,
            datetime=item.datetime,
            assets=item.assets,
        )