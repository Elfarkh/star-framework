from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

import numpy as np
import planetary_computer
import rasterio

from ...core.raster import Raster
from ..landsat_scene import LandsatScene
from .metadata import STAR_ASSETS

class LandsatIO:
    """
    Landsat input/output operations.
    """
    
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