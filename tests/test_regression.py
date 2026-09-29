import numpy as np

from star.algorithms.star_lst.datasets import (
    CalibrationSamples,
    PreparedDataset,
)
from star.algorithms.star_lst.triangles import (
    build_triangle_geometry,
    assign_samples,
)
from star.algorithms.star_lst.regression import fit_regressions


def test_regression():

    # Synthetic calibration samples
    ndvi = np.linspace(0.1, 0.9, 500)

    # Synthetic decreasing LST-NDVI relationship
    lst = 310.0 - 20.0 * ndvi

    prepared = PreparedDataset(
        coarse_lst=None,
        fine_ndvi=None,
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

    assert regression.regressions is not None

    assert len(regression.regressions) > 0

    for local_regression in regression.regressions:

        assert local_regression.model is not None
        assert local_regression.triangle_id >= 0

        slope = local_regression.model.coef_[0]
        intercept = local_regression.model.intercept_

        assert np.isclose(
            slope,
            -20.0,
            atol=1e-6,
        )

        assert np.isclose(
            intercept,
            310.0,
            atol=1e-6,
        )