"""
STAR-LST triangle construction.
"""
import numpy as np
from .metadata import NDVI_MAX
from .metadata import DEFAULT_NUMBER_OF_NDVI_BINS
from .metadata import (
    NDVI_MAX,
    DRY_EDGE_WIDTH,
    THERMAL_BASELINE_PERCENTILE,
    DEFAULT_NUMBER_OF_NDVI_BINS,
)

from .datasets import (
    PreparedDataset,
    TriangleDataset,
    TriangleGeometry,
    Triangle,
    DryEdgeAnchor,
)
import shapely
from shapely.geometry import Polygon

def _compute_ndvi_domain(
    prepared: PreparedDataset,
):
    """
    Compute the NDVI domain.
    """

    ndvi = prepared.samples.ndvi

    ndvi_min = np.min(ndvi)

    ndvi_max = NDVI_MAX

    return ndvi_min, ndvi_max


def _compute_lst_baseline(
    prepared: PreparedDataset,
) -> float:
    """
    Estimate the thermal baseline of the scene.
    """

    lst = prepared.samples.lst

    threshold = np.percentile(
        lst,
        THERMAL_BASELINE_PERCENTILE,
    )

    baseline = np.mean(
        lst[lst <= threshold]
    )

    return baseline


def _compute_dry_edge_anchor(
    prepared: PreparedDataset,
    ndvi_min: float,
) -> DryEdgeAnchor:
    """
    Compute the dry-edge anchor point (P1).
    """

    samples = prepared.samples

    low_ndvi_mask = (
        (samples.ndvi >= ndvi_min)
        &
        (samples.ndvi <= ndvi_min + DRY_EDGE_WIDTH)
    )

    ndvi = samples.ndvi[low_ndvi_mask]
    lst = samples.lst[low_ndvi_mask]

    index = np.argmax(lst)

    return DryEdgeAnchor(
        ndvi=float(ndvi[index]),
        lst=float(lst[index]),
    )


def _build_ndvi_bins(
    ndvi_min: float,
    num_bins: int = DEFAULT_NUMBER_OF_NDVI_BINS,
) -> np.ndarray:
    """
    Partition the NDVI domain.
    """

    return np.linspace(
        ndvi_min,
        NDVI_MAX,
        num_bins + 1,
    )


def build_triangle_geometry(
    prepared: PreparedDataset,
) -> TriangleGeometry:

    ndvi_min, ndvi_max = _compute_ndvi_domain(prepared)

    lst_baseline = _compute_lst_baseline(prepared)

    dry_edge_anchor = _compute_dry_edge_anchor(
        prepared,
        ndvi_min,
    )

    ndvi_edges = _build_ndvi_bins(ndvi_min)

    triangles = _build_triangles(
        dry_edge_anchor,
        lst_baseline,
        ndvi_edges,
    )

    return TriangleGeometry(
        ndvi_min=ndvi_min,
        ndvi_max=ndvi_max,
        lst_baseline=lst_baseline,
        dry_edge_anchor=dry_edge_anchor,
        ndvi_edges=ndvi_edges,
        triangles=triangles,
    )

def _build_triangles(
    dry_edge_anchor: DryEdgeAnchor,
    lst_baseline: float,
    ndvi_edges: np.ndarray,
) -> list[Triangle]:

    triangles = []

    for i in range(len(ndvi_edges) - 1):

        triangles.append(
            Triangle(
                apex=dry_edge_anchor,
                left=(ndvi_edges[i], lst_baseline),
                right=(ndvi_edges[i + 1], lst_baseline),
            )
        )

    return triangles

def assign_samples(
    prepared: PreparedDataset,
    geometry: TriangleGeometry,
) -> TriangleDataset:
    """
    Assign calibration samples to STAR-LST triangles.
    """

    triangle_ids = _assign_triangle_ids(
        prepared,
        geometry,
    )

    return TriangleDataset(
        **prepared.__dict__,
        geometry=geometry,
        triangle_ids=triangle_ids,
    )

def _assign_triangle_ids(
    prepared: PreparedDataset,
    geometry: TriangleGeometry,
) -> np.ndarray:
    """
    Assign every calibration sample to one triangle.
    """

    ndvi = prepared.samples.ndvi
    lst = prepared.samples.lst

    # Create all sample points at once
    points = shapely.points(ndvi, lst)

    triangle_ids = np.full(
        ndvi.shape,
        -1,
        dtype=int,
    )

    for i, triangle in enumerate(geometry.triangles):

        polygon = Polygon(
            [
                (
                    triangle.apex.ndvi,
                    triangle.apex.lst,
                ),
                triangle.left,
                triangle.right,
            ]
        )

        inside = shapely.contains(
            polygon,
            points,
        )

        triangle_ids[inside] = i

    return triangle_ids
