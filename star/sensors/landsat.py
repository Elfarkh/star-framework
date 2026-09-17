
"""
Landsat sensor module.

This module provides access to Landsat products within
the STAR Framework.
"""

from geopandas import GeoDataFrame

from .landsat_tile import LandsatTile


class Landsat:
    """
    Interface to the Landsat archive.
    """

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
