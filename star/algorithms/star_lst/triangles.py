"""
STAR-LST triangle construction.
"""
import numpy as np
from .datasets import (
    PreparedDataset,
    TriangleDataset,
)


def build_triangles(
    prepared: PreparedDataset,
) -> TriangleDataset:
    """
    Build the STAR-LST triangular partition.
    """

    raise NotImplementedError


def _compute_ndvi_domain(
    prepared: PreparedDataset,
):
    """
    Compute the NDVI domain.
    """

    ndvi = prepared.samples.ndvi

    ndvi_min = np.min(ndvi)

    ndvi_max = 1.0

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
        5,
    )

    baseline = np.mean(
        lst[lst <= threshold]
    )

    return baseline


def _compute_dry_edge(
    prepared: PreparedDataset,
):
    """
    Compute the dry edge (P1).
    """

    raise NotImplementedError


def _build_ndvi_bins(
    prepared: PreparedDataset,
):
    """
    Partition the NDVI domain.
    """

    raise NotImplementedError


def _build_triangles(
    prepared: PreparedDataset,
):
    """
    Construct the STAR-LST triangles.
    """

    raise NotImplementedError