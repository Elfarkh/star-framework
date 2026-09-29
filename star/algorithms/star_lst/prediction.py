"""
STAR-LST prediction.
"""

from .datasets import (
    RegressionDataset,
    PredictionDataset,
)
import numpy as np

from ...core.raster import Raster

def predict(
    regression: RegressionDataset,
) -> PredictionDataset:
    """
    Predict fine-resolution LST.
    """

    bin_indices = _compute_bin_indices(regression)

    predicted_lst = np.full(
        regression.fine_ndvi.data.size,
        np.nan,
        dtype="float32",
    )

    for triangle_id in range(
        len(regression.geometry.triangles)
    ):
        mask = bin_indices == triangle_id

        _predict_bin(
            regression,
            triangle_id,
            mask,
            predicted_lst,
        )

    predicted_lst = predicted_lst.reshape(
        regression.fine_ndvi.shape
    )

    return PredictionDataset(
        **regression.__dict__,
        predicted_lst=Raster(
            data=predicted_lst,
            profile=regression.fine_ndvi.profile.copy(),
        ),
    )


def _compute_bin_indices(
    regression: RegressionDataset,
) -> np.ndarray:
    """
    Assign each fine NDVI pixel to its NDVI bin.
    """

    ndvi = regression.fine_ndvi.data.flatten()

    ndvi_edges = regression.geometry.ndvi_edges

    return np.digitize(
        ndvi,
        ndvi_edges,
    ) - 1


def _predict_bin(
    regression: RegressionDataset,
    triangle_id: int,
    mask: np.ndarray,
    predicted_lst: np.ndarray,
):
    """
    Predict LST for one NDVI bin.
    """

    local_regression = next(
        (
            r
            for r in regression.regressions
            if r.triangle_id == triangle_id
        ),
        None,
    )

    if local_regression is None:
        return

    ndvi = regression.fine_ndvi.data.flatten()

    predicted_lst[mask] = (
        local_regression.model.predict(
            ndvi[mask].reshape(-1, 1)
        )
    )