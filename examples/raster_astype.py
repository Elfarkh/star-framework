import numpy as np

from star.raster import Raster

profile = {
    "crs": None,
    "transform": None,
    "nodata": np.nan,
    "dtype": "float32",
}

a = Raster(
    data=np.ones((3, 3), dtype="float32"),
    profile=profile,
)

b = a.astype("uint16")

print(a.dtype)
print(b.dtype)