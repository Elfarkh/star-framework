"""
Landsat sensor module.

This module provides access to Landsat products within
the STAR Framework.
"""

from pathlib import Path

import geopandas as gpd
from geopandas import GeoDataFrame

from .landsat_tile import LandsatTile
from .landsat_scene import LandsatScene
from datetime import datetime
from ..catalogs.stac import STAC
from urllib.request import urlretrieve
from urllib.parse import urlparse
import rasterio
from ..raster import Raster
import numpy as np

STAR_ASSETS = [
    "red",
    "nir08",
    "lwir11",
    "qa_pixel",
]

class Landsat:
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
            Path(__file__).parent.parent
            / "data"
            / "wrs2"
            / "usgs"
            / "WRS2_descending.shp"
        )

        return gpd.read_file(wrs2_file)

    def _item_to_scene(self, item) -> LandsatScene:
        """
        Convert a STAC Item into a LandsatScene.
        """

        return LandsatScene(
            scene_id=item.id,
            platform=item.properties["platform"],
            acquisition_date=datetime.fromisoformat(
                item.properties["datetime"].replace("Z", "+00:00")
            ),
            path=int(item.properties["landsat:wrs_path"]),
            row=int(item.properties["landsat:wrs_row"]),
            cloud_cover=item.properties["eo:cloud_cover"],
            assets=item.assets,
        )

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

    def _tile_geometry(self, tile: LandsatTile):
        """
        Return the geometry of a Landsat tile.
        """

        tile_geometry = self._wrs2[
            (self._wrs2["PATH"] == tile.path)
            & (self._wrs2["ROW"] == tile.row)
        ]

        return tile_geometry.geometry.iloc[0]


    def search(
            self,
            aoi: GeoDataFrame,
            start_date: datetime,
            end_date: datetime,
    ) -> list[LandsatScene]:
        """
        Search Landsat scenes.

        Parameters
        ----------
        tile : LandsatTile
        Landsat tile.

        start_date : datetime
        Start date.

        end_date : datetime
        End date.

        Returns
        -------
        list[LandsatScene]
        Matching Landsat scenes.
        """

        geometry = aoi.union_all()


        items = self._catalog.search(
            collection="landsat-c2-l2",
            geometry=geometry,
            start_date=start_date,
            end_date=end_date,
        )

        return [
            self._item_to_scene(item)
            for item in items
        ]


    def download(self, scene: LandsatScene):
        """
        Download the assets required by STAR for one Landsat scene.
        """

        scene_directory = (
            self.download_directory
            / "landsat"
            / scene.scene_id
        )

        scene_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        url = scene.assets["red"].href

        for asset_name in STAR_ASSETS:

            asset = scene.assets[asset_name]

            filename = Path(
                urlparse(asset.href).path
            ).name

            output_file = scene_directory / filename

            if output_file.exists():
                print(f"Skipping {filename}")
                continue

            print(f"Downloading {filename}")

            urlretrieve(asset.href, output_file)

        scene.local_path = scene_directory

        return scene

    def read(self, scene: LandsatScene, band: str):
        """
        Read one downloaded Landsat band.
        """

        filename = {
            "red": "SR_B4",
            "nir08": "SR_B5",
            "lwir11": "ST_B10",
            "qa_pixel": "QA_PIXEL",
        }[band]

        files = list(
            scene.local_path.glob(f"*{filename}.TIF")
        )

        if len(files) != 1:
            raise FileNotFoundError(
                f"Could not find band '{band}' for scene {scene.scene_id}."
            )
        
        with rasterio.open(files[0]) as src:

            image = src.read(1).astype("float32")

            profile = src.profile

            nodata = src.nodata

            if nodata is not None:
                image[image == nodata] = np.nan

        return Raster(
            data=image,
            profile=profile,
        )

    def _reflectance(
        self,
        scene: LandsatScene,
        band: str,
    ) -> Raster:
        """
        Read a surface reflectance band.
        """

        raster = self.read(scene, band)

        reflectance = raster.data.astype("float32") * 0.0000275 - 0.2

        reflectance[reflectance <= 0] = np.nan

        return Raster(
            data=reflectance,
            profile=raster.profile,
        )
    
    def ndvi(self, scene: LandsatScene) -> Raster:
        """
        Compute NDVI from a Landsat scene.
        """

        red = self._reflectance(scene, "red")

        nir = self._reflectance(scene, "nir08")

        ndvi = (nir.data - red.data) / (nir.data + red.data)

        return Raster(
            data=ndvi,
            profile=red.profile,
        )

    def __repr__(self):
        return "Landsat()"
