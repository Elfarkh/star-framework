"""
STAR-LST model.
"""

from .datasets import (
    TriangleGeometry,
    LocalRegression,
)
from ...core.star_dataset import STARDataset
from .datasets import PredictionDataset
from .preparation import prepare
from .triangles import (
    build_triangle_geometry,
    assign_samples,
)
from .regression import fit_regressions
from .prediction import predict as predict_lst

class STARLST:
    """
    STAR-LST model.
    """

    def __init__(self):
        """
        Initialize an uncalibrated STAR-LST model.
        """

        self.geometry: TriangleGeometry | None = None

        self.regressions: list[LocalRegression] | None = None

        self.is_calibrated = False

    def calibrate(
        self,
        dataset: STARDataset,
    ):
        """
        Calibrate the STAR-LST model.
        """

        prepared = prepare(dataset)

        geometry = build_triangle_geometry(prepared)

        triangles = assign_samples(
            prepared,
            geometry,
        )

        regression = fit_regressions(triangles)

        self.geometry = regression.geometry
        self.regressions = regression.regressions

        self.is_calibrated = True

        return self


    def predict(
        self,
        dataset: STARDataset,
    ) -> PredictionDataset:
        """
        Predict fine-resolution LST.
        """

        if not self.is_calibrated:
            raise RuntimeError(
                "STAR-LST must be calibrated before prediction."
            )

        raise NotImplementedError