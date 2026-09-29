"""
Landsat metadata and constants.
"""

LANDSAT_COLLECTION = "landsat-c2-l2"

STAR_ASSETS = [
    "red",
    "nir08",
    "lwir11",
    "qa_pixel",
]

REFLECTANCE_SCALE = 0.0000275
REFLECTANCE_OFFSET = -0.2

TEMPERATURE_SCALE = 0.00341802
TEMPERATURE_OFFSET = 149.0