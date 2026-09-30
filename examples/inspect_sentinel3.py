from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import planetary_computer
import pystac_client
import xarray as xr


COLLECTION = "sentinel-3-slstr-lst-l2-netcdf"

# ---------------------------------------------------------
# Connect to Planetary Computer
# ---------------------------------------------------------

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)


# ---------------------------------------------------------
# Search Sentinel-3 SLSTR LST
# ---------------------------------------------------------

search = catalog.search(
    collections=[COLLECTION],
    bbox=[
        -8.55,
        31.55,
        -8.35,
        31.75,
    ],
    datetime="2025-01-01/2025-01-31",
)

items = list(search.items())

print("Number of scenes:", len(items))

if not items:
    raise RuntimeError(
        "No Sentinel-3 LST scenes found."
    )


# ---------------------------------------------------------
# Inspect first scene
# ---------------------------------------------------------

item = planetary_computer.sign(items[0])

print("\nScene:")
print(item.id)

print("\nDatetime:")
print(item.datetime)

print("\nStart:")
print(item.properties.get("start_datetime"))

print("\nEnd:")
print(item.properties.get("end_datetime"))


# ---------------------------------------------------------
# Assets required by STAR
# ---------------------------------------------------------

assets_to_inspect = [
    "lst-in",
    "slstr-geodetic-in",
    "slstr-flags-in",
]


# ---------------------------------------------------------
# Temporary download directory
# ---------------------------------------------------------

download_directory = Path(
    "data/sentinel3_test"
)

download_directory.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------
# Download and inspect assets
# ---------------------------------------------------------

for asset_name in assets_to_inspect:

    print("\n" + "=" * 70)
    print(asset_name)
    print("=" * 70)

    asset = item.assets[asset_name]

    output_file = (
        download_directory
        / f"{asset_name}.nc"
    )

    if not output_file.exists():

        print("Downloading...")

        urlretrieve(
            asset.href,
            output_file,
        )

    else:

        print("Already downloaded.")

    with xr.open_dataset(output_file) as ds:

        print("\nDimensions:")
        print(ds.sizes)

        print("\nVariables:")

        for variable_name in ds.variables:

            variable = ds[variable_name]

            print(
                f"\n{variable_name}"
                f"\n  shape: {variable.shape}"
                f"\n  dtype: {variable.dtype}"
            )

            print("  attributes:")

            for key, value in variable.attrs.items():

                print(
                    f"    {key}: {value}"
                )

            # ---------------------------------------------
            # Inspect numerical range of 2-D variables
            # ---------------------------------------------

            if variable.ndim == 2:

                values = variable.values

                if np.issubdtype(
                    values.dtype,
                    np.number,
                ):

                    print(
                        "  min:",
                        np.nanmin(values),
                    )

                    print(
                        "  max:",
                        np.nanmax(values),
                    )


# ---------------------------------------------------------
# Explicitly inspect the variables needed by STAR
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("STAR-LST VARIABLES")
print("=" * 70)


# LST
lst_file = (
    download_directory
    / "lst-in.nc"
)

with xr.open_dataset(lst_file) as ds:

    lst = ds["LST"].values

    print("\nLST")
    print("shape:", lst.shape)
    print("dtype:", lst.dtype)
    print("min:", np.nanmin(lst))
    print("max:", np.nanmax(lst))


# Geolocation
geo_file = (
    download_directory
    / "slstr-geodetic-in.nc"
)

with xr.open_dataset(geo_file) as ds:

    latitude = ds["latitude_in"].values
    longitude = ds["longitude_in"].values

    print("\nLatitude")
    print("shape:", latitude.shape)
    print("min:", np.nanmin(latitude))
    print("max:", np.nanmax(latitude))

    print("\nLongitude")
    print("shape:", longitude.shape)
    print("min:", np.nanmin(longitude))
    print("max:", np.nanmax(longitude))


# Flags
flags_file = (
    download_directory
    / "slstr-flags-in.nc"
)

with xr.open_dataset(flags_file) as ds:

    cloud = ds["cloud_in"].values
    confidence = ds["confidence_in"].values

    print("\nCloud flags")
    print("shape:", cloud.shape)
    print("min:", np.nanmin(cloud))
    print("max:", np.nanmax(cloud))

    print("\nConfidence flags")
    print("shape:", confidence.shape)
    print("min:", np.nanmin(confidence))
    print("max:", np.nanmax(confidence))