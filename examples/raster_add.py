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

b = Raster(
    data=np.ones((3, 3), dtype="float32") * 2,
    profile=profile,
)

c = a + b

print(c.data)
d = a * 5

print(d.data)