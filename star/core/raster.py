"""
Raster data model.
"""

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import rasterio

@dataclass
class Raster:
    """
    Represents a raster dataset.
    """

    data: np.ndarray
    profile: dict

    @property
    def crs(self):
        return self.profile["crs"]

    @property
    def transform(self):
        return self.profile["transform"]

    @property
    def nodata(self):
        return self.profile["nodata"]

    @property
    def dtype(self):
        return self.profile["dtype"]

    @property
    def shape(self):
        return self.data.shape

    @property
    def min(self):
        return np.nanmin(self.data)

    @property
    def max(self):
        return np.nanmax(self.data)

    @property
    def mean(self):
        return np.nanmean(self.data)

    def write(self, filename: str | Path) -> None:
        """
        Write the raster to a GeoTIFF file.
        """

        profile = self.profile.copy()

        profile["count"] = 1
        profile["dtype"] = self.data.dtype

        with rasterio.open(filename, "w", **profile) as dst:
            dst.write(self.data, 1)

    def copy(self):
        """
        Return a copy of the raster.
        """

        return Raster(
            data=self.data.copy(),
            profile=self.profile.copy(),
        )
    
    def astype(self, dtype):
        """
        Return the raster converted to another data type.
        """

        raster = self.copy()

        raster.data = raster.data.astype(dtype)

        raster.profile["dtype"] = raster.data.dtype.name

        return raster
    
    def __add__(self, other):
        """
        Add two rasters.
        """

        if not isinstance(other, Raster):
            return NotImplemented

        return Raster(
            data=self.data + other.data,
            profile=self.profile.copy(),
        )

    def __sub__(self, other):
        """
        Subtract two rasters.
        """

        if not isinstance(other, Raster):
            return NotImplemented

        return Raster(
            data=self.data - other.data,
            profile=self.profile.copy(),
        )

    def __mul__(self, other):
        """
        Multiply a raster by a scalar.
        """

        if isinstance(other, (int, float)):
            return Raster(
                data=self.data * other,
                profile=self.profile.copy(),
            )

        return NotImplemented

    def __truediv__(self, other):
        """
        Divide one raster by another raster or by a scalar.
        """

        if isinstance(other, Raster):
            return Raster(
                data=self.data / other.data,
                profile=self.profile.copy(),
            )

        if isinstance(other, (int, float)):
            return Raster(
                data=self.data / other,
                profile=self.profile.copy(),
            )

        return NotImplemented