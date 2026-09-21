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

    def __init__(self):
        """
        Initialize the Landsat interface.
        """

        self._wrs2 = self._load_wrs2_grid()

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
        grid = self._wrs2
        if aoi.crs != grid.crs:
            aoi = aoi.to_crs(grid.crs)

        matches = grid[grid.intersects(aoi.union_all())]

        if len(matches) == 0:
            raise ValueError(
                "The AOI does not intersect any Landsat tile."
            )

        if len(matches) == 1:
            tile = matches.iloc[0]

            return LandsatTile(
                path=int(tile["PATH"]),
                row=int(tile["ROW"]),
            )

        matches = matches.to_crs("EPSG:6933")
        aoi = aoi.to_crs("EPSG:6933")

        matches = matches.copy()

        matches["overlap_area"] = (
            matches.geometry.intersection(aoi.union_all()).area
        )

        tile = matches.loc[
            matches["overlap_area"].idxmax()
        ]

        return LandsatTile(
            path=int(tile["PATH"]),
            row=int(tile["ROW"]),
        )

    def __repr__(self):
        return "Landsat()"
