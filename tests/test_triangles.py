import numpy as np

from star.algorithms.star_lst.datasets import (
    CalibrationSamples,
    PreparedDataset,
)
from star.algorithms.star_lst.triangles import (
    build_triangle_geometry,
    assign_samples,
)
from star.algorithms.star_lst.metadata import (
    DEFAULT_NUMBER_OF_NDVI_BINS,
)


def test_triangles():

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

    assert geometry.dry_edge_anchor is not None
    assert geometry.ndvi_edges is not None
    assert len(geometry.triangles) == DEFAULT_NUMBER_OF_NDVI_BINS

    triangles = assign_samples(
        prepared,
        geometry,
    )

    assert triangles.triangle_ids is not None

    assert (
        len(triangles.triangle_ids)
        == len(prepared.samples.ndvi)
    )