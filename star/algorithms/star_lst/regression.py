"""
STAR-LST local regression.
"""

from .datasets import (
    TriangleDataset,
    RegressionDataset,
)


def fit_regressions(
    triangles: TriangleDataset,
) -> RegressionDataset:
    """
    Fit one regression model for each triangle.
    """

    regressions = []

    for triangle_id in range(
        len(triangles.geometry.triangles)
    ):

        regression = _fit_triangle_regression(
            triangles,
            triangle_id,
        )

        if regression is not None:
            regressions.append(regression)

    return RegressionDataset(
        **triangles.__dict__,
        regressions=regressions,
    )

def _fit_triangle_regression(
    triangles: TriangleDataset,
    triangle_id: int,
) -> LocalRegression | None:
    """
    Fit the regression model of one triangle.
    """

    mask = triangles.triangle_ids == triangle_id

    if np.sum(mask) <= 5:
        return None

    model = LinearRegression().fit(
        triangles.samples.ndvi[mask].reshape(-1, 1),
        triangles.samples.lst[mask],
    )

    return LocalRegression(
        triangle_id=triangle_id,
        model=model,
    )