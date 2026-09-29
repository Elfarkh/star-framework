"""
Landsat sensor module.

"""
from pathlib import Path

import geopandas as gpd

from ...catalogs.stac import STAC

from .io import LandsatIO
from .search import LandsatSearch
from .processing import LandsatProcessing

class Landsat(
    LandsatIO,
    LandsatSearch,
    LandsatProcessing,
):
    """
    Interface to the Landsat archive.
    """

    def __init__(self, download_directory: str | Path = "data"):
        """
        Initialize the Landsat interface.

        Parameters
        ----------
        data_directory : str or Path
        Directory where Landsat data will be stored.
        """

        self.download_directory = Path(download_directory)

        self._wrs2 = self._load_wrs2_grid()
        self._catalog = STAC()

    def _load_wrs2_grid(self) -> gpd.GeoDataFrame:
        """
        Load the official USGS WRS-2 descending grid.

        Returns
        -------
        GeoDataFrame
            Landsat WRS-2 descending grid.
        """

        wrs2_file = (
            Path(__file__).parent.parent.parent
            / "data"
            / "wrs2"
            / "usgs"
            / "WRS2_descending.shp"
        )

        return gpd.read_file(wrs2_file)


    
    
    
    def __repr__(self):
        return "Landsat()"
