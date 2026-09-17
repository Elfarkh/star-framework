"""
Landsat sensor module.

This module provides access to Landsat products within
the STAR Framework.
"""

from pathlib import Path

import geopandas as gpd
from geopandas import GeoDataFrame

from .landsat_tile import LandsatTile


class Landsat:
    """
    Interface to the Landsat archive.
    """

    def _load_wrs2_grid(self) -> gpd.GeoDataFrame:
        """
        Load the official USGS WRS-2 descending grid.

        Returns
        -------
        GeoDataFrame
        Landsat WRS-2 descending grid.
        """

        wrs2_file = (
            Path(__file__).parent.parent
            / "data"
            / "wrs2"
            / "usgs"
            / "WRS2_descending.shp"
        )

        return gpd.read_file(wrs2_file)

    def find_tile(self, aoi: GeoDataFrame) -> LandsatTile:
        """
        Find the Landsat tile covering the Area of Interest.

        Parameters
        ----------
        aoi : GeoDataFrame
            Area of interest.

        Returns
        -------
        LandsatTile
            Landsat tile covering the AOI.
        """

        raise NotImplementedError(
            "find_tile() has not been implemented yet."
        )

    def __repr__(self):
        return "Landsat()"
