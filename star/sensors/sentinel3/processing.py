"""
Sentinel-3 processing operations.
"""

import numpy as np

from shapely.geometry.base import BaseGeometry
from pyproj import Transformer
from rasterio.transform import from_origin
from scipy.interpolate import griddata
from rasterio.transform import (
    array_bounds,
    from_origin,
)
from ...core.raster import Raster
from ..sentinel3_scene import Sentinel3Scene


class Sentinel3Processing:
    """
    Sentinel-3 processing operations.
    """

    def subset(
        self,
        scene: Sentinel3Scene,
        geometry: BaseGeometry,
    ):
        """
        Subset a Sentinel-3 swath to a processing domain.
        """

        data = self.read(scene)

        minx, miny, maxx, maxy = geometry.bounds

        spatial_mask = (
            (data["longitude"] >= minx)
            & (data["longitude"] <= maxx)
            & (data["latitude"] >= miny)
            & (data["latitude"] <= maxy)
        )

        rows, cols = np.where(spatial_mask)

        if rows.size == 0:
            raise ValueError(
                "Sentinel-3 scene does not intersect the processing domain."
            )

        row_min = rows.min()
        row_max = rows.max() + 1

        col_min = cols.min()
        col_max = cols.max() + 1

        return {
            name: array[
                row_min:row_max,
                col_min:col_max,
            ]
            for name, array in data.items()
        }

    def quality_mask(
        self,
        scene: Sentinel3Scene,
        geometry: BaseGeometry,
    ) -> np.ndarray:
        """
        Build the valid-pixel mask for Sentinel-3 SLSTR LST.
        """

        data = self.subset(
            scene,
            geometry,
        )

        lst = data["lst"]
        confidence = data["confidence"]
        exception = data["exception"]

        land = (confidence & (1 << 3)) != 0
        unfilled = (confidence & (1 << 5)) != 0
        snow = (confidence & (1 << 13)) != 0
        summary_cloud = (confidence & (1 << 14)) != 0

        valid = (
            np.isfinite(lst)
            & land
            & (~unfilled)
            & (~snow)
            & (~summary_cloud)
            & (exception == 0)
        )

        return valid

    def projected_points(
        self,
        scene: Sentinel3Scene,
        geometry: BaseGeometry,
        target_crs,
    ):
        """
        Project Sentinel-3 observations and their validity
        information to the target CRS.
        """

        data = self.subset(
            scene,
            geometry,
        )

        valid = self.quality_mask(
            scene,
            geometry,
        )

        longitude = data["longitude"].flatten()
        latitude = data["latitude"].flatten()
        lst = data["lst"].flatten()
        valid = valid.flatten()

        # Remove only pixels without valid coordinates.
        coordinate_mask = (
            np.isfinite(longitude)
            & np.isfinite(latitude)
        )

        longitude = longitude[coordinate_mask]
        latitude = latitude[coordinate_mask]
        lst = lst[coordinate_mask]
        valid = valid[coordinate_mask]

        transformer = Transformer.from_crs(
            "EPSG:4326",
            target_crs,
            always_xy=True,
        )

        x, y = transformer.transform(
            longitude,
            latitude,
        )

        return {
            "x": np.asarray(x),
            "y": np.asarray(y),
            "lst": lst,
            "valid": valid,
        }

    def lst(
        self,
        scene: Sentinel3Scene,
        target: Raster,
        geometry: BaseGeometry,
        resolution: float = 1000.0,
    ) -> Raster:
        """
        Create a regular Sentinel-3 LST raster aligned
        to the processing domain of the fine-resolution data.
        """

        points = self.projected_points(
            scene=scene,
            geometry=geometry,
            target_crs=target.crs,
        )

        # Get the full target raster extent
        left, bottom, right, top = array_bounds(
            target.shape[0],
            target.shape[1],
            target.transform,
        )

        # Define the Sentinel-3 grid dimensions
        width = int(
            np.ceil(
                (right - left) / resolution
            )
        )

        height = int(
            np.ceil(
                (top - bottom) / resolution
            )
        )

        # Define the Sentinel-3 raster transform
        transform = from_origin(
            left,
            top,
            resolution,
            resolution,
        )

        # Coordinates of the target pixel centres
        x = (
            left
            + resolution / 2
            + np.arange(width) * resolution
        )

        y = (
            top
            - resolution / 2
            - np.arange(height) * resolution
        )

        grid_x, grid_y = np.meshgrid(
            x,
            y,
        )

        # Sentinel-3 validity information
        valid = points["valid"]

        # --------------------------------------------------
        # Grid LST using only valid Sentinel-3 observations
        # --------------------------------------------------

        lst_grid = griddata(
            points=(
                points["x"][valid],
                points["y"][valid],
            ),
            values=points["lst"][valid],
            xi=(
                grid_x,
                grid_y,
            ),
            method="nearest",
        ).astype("float32")

        # --------------------------------------------------
        # Transfer the original Sentinel-3 validity mask
        # to the regular grid
        # --------------------------------------------------

        valid_grid = griddata(
            points=(
                points["x"],
                points["y"],
            ),
            values=points["valid"].astype("uint8"),
            xi=(
                grid_x,
                grid_y,
            ),
            method="nearest",
        ).astype(bool)

        # Restore cloudy / invalid pixels as NoData
        lst_grid[~valid_grid] = np.nan

        # --------------------------------------------------
        # Build raster profile
        # --------------------------------------------------

        profile = target.profile.copy()

        profile.update(
            height=height,
            width=width,
            transform=transform,
            dtype="float32",
            nodata=np.nan,
        )

        return Raster(
            data=lst_grid,
            profile=profile,
        )