"""
Raster data model.
"""

from dataclasses import dataclass

import numpy as np


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