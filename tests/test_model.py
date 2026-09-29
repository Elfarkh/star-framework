import numpy as np
from rasterio.transform import from_origin

from star.core.raster import Raster
from star.core.star_dataset import STARDataset
from star.algorithms.star_lst.model import STARLST


def test_model():

    # Synthetic coarse calibration data
    ndvi_data = np.linspace(
        0.1,
        0.9,
        100,
        dtype="float32",
    ).reshape(10, 10)

    lst_data = (
        310.0 - 20.0 * ndvi_data
    ).astype("float32")

    profile = {
        "driver": "GTiff",
        "height": 10,
        "width": 10,
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:32629",
        "transform": from_origin(
            0,
            300,
            30,
            30,
        ),
        "nodata": np.nan,
    }

    coarse_lst = Raster(
        data=lst_data,
        profile=profile,
    )

    fine_ndvi = Raster(
        data=ndvi_data,
        profile=profile,
    )

    calibration_dataset = STARDataset(
        coarse_lst=coarse_lst,
        fine_ndvi=fine_ndvi,
    )

    model = STARLST()

    model.calibrate(calibration_dataset)

    assert model.is_calibrated
    assert model.geometry is not None
    assert model.regressions is not None

    prediction = model.predict(
        calibration_dataset
    )

    assert prediction.predicted_lst is not None
    assert prediction.predicted_lst.shape == fine_ndvi.shape

    valid = ~np.isnan(
        prediction.predicted_lst.data
    )

    assert np.any(valid)

    expected_lst = (
        310.0 - 20.0 * ndvi_data
    )

    assert np.allclose(
        prediction.predicted_lst.data[valid],
        expected_lst[valid],
        atol=1e-5,
    )