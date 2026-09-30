"""
Sentinel-3 input/output operations.
"""

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

from ..sentinel3_scene import Sentinel3Scene
from .metadata import SENTINEL3_LST_ASSETS

import xarray as xr

class Sentinel3IO:
    """
    Sentinel-3 input/output operations.
    """

    def download(
        self,
        scene: Sentinel3Scene,
    ) -> Sentinel3Scene:
        """
        Download the assets required for one Sentinel-3 LST scene.
        """

        scene_directory = (
            self.download_directory
            / "sentinel3"
            / scene.scene_id
        )

        scene_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        for asset_name in SENTINEL3_LST_ASSETS:

            asset = scene.assets[asset_name]

            filename = Path(
                urlparse(asset.href).path
            ).name

            output_file = (
                scene_directory
                / filename
            )

            if output_file.exists():
                print(f"Skipping {filename}")
                continue

            print(f"Downloading {filename}")

            urlretrieve(
                asset.href,
                output_file,
            )

        scene.local_path = scene_directory

        return scene

    def read(
        self,
        scene: Sentinel3Scene,
    ):
        """
        Read the Sentinel-3 SLSTR LST data and geolocation.
        """

        if scene.local_path is None:
            raise ValueError(
                "Scene must be downloaded before reading."
            )

        with xr.open_dataset(
            scene.local_path / "LST_in.nc"
        ) as ds:
            lst = ds["LST"].values.astype("float32")

        with xr.open_dataset(
            scene.local_path / "geodetic_in.nc"
        ) as ds:
            latitude = ds["latitude_in"].values
            longitude = ds["longitude_in"].values

        with xr.open_dataset(
            scene.local_path / "flags_in.nc"
        ) as ds:
            cloud = ds["cloud_in"].values
            confidence = ds["confidence_in"].values

        with xr.open_dataset(
            scene.local_path / "LST_in.nc"
        ) as ds:
            lst = ds["LST"].values.astype("float32")
            exception = ds["exception"].values

        return {
            "lst": lst,
            "exception": exception,
            "latitude": latitude,
            "longitude": longitude,
            "cloud": cloud,
            "confidence": confidence,
        }