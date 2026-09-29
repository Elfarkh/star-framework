import numpy as np
from rasterio.transform import from_origin

from star.core.raster import Raster

from star.algorithms.star_lst.datasets import (
    CalibrationSamples,
    PreparedDataset,
)
from star.algorithms.star_lst.triangles import (
    build_triangle_geometry,
    assign_samples,
)
from star.algorithms.star_lst.regression import fit_regressions
from star.algorithms.star_lst.prediction import predict


def test_prediction():

    # Calibration samples
    ndvi = np.linspace(0.1, 0.9, 500)
    lst = 310.0 - 20.0 * ndvi

    # Fine-resolution NDVI image
    fine_ndvi_data = np.linspace(
        0.1,
        0.9,
        100,
        dtype="float32",
    ).reshape(10, 10)

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

    fine_ndvi = Raster(
        data=fine_ndvi_data,
        profile=profile,
    )

    prepared = PreparedDataset(
        coarse_lst=None,
        fine_ndvi=fine_ndvi,
        aggregated_ndvi=None,
        samples=CalibrationSamples(
            ndvi=ndvi,
            lst=lst,
        ),
    )

    geometry = build_triangle_geometry(prepared)

    triangles = assign_samples(
        prepared,
        geometry,
    )

    regression = fit_regressions(triangles)

    prediction = predict(regression)

    assert prediction.predicted_lst is not None

    assert prediction.predicted_lst.shape == fine_ndvi.shape

    expected_lst = (
        310.0
        - 20.0 * fine_ndvi_data
    )

    valid = ~np.isnan(
        prediction.predicted_lst.data
    )

    assert np.any(valid)

    assert np.allclose(
        prediction.predicted_lst.data[valid],
        expected_lst[valid],
        atol=1e-5,
    )