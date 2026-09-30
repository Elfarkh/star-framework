"""
STAR-LST calibration scene selection.
"""

from dataclasses import dataclass
from datetime import datetime

from ...sensors.landsat_scene import LandsatScene
from ...sensors.sentinel3_scene import Sentinel3Scene
import numpy as np

TARGET_CALIBRATION_SCENES = 16
TARGET_SCENES_PER_QUARTER = 4

MAX_TIME_DIFFERENCE_MINUTES = 15
MIN_VALID_FRACTION = 0.60


def _quarter(date: datetime) -> int:
    """
    Return the calendar quarter of an acquisition.
    """

    return (date.month - 1) // 3 + 1


@dataclass
class CalibrationPair:
    """
    Candidate Landsat / Sentinel-3 calibration pair.
    """

    landsat: LandsatScene
    sentinel3: Sentinel3Scene
    time_difference_minutes: float

    @property
    def quarter(self) -> int:
        return _quarter(
            self.landsat.acquisition_date
        )


def match_calibration_pairs(
    landsat_scenes: list[LandsatScene],
    sentinel3_scenes: list[Sentinel3Scene],
) -> list[CalibrationPair]:
    """
    Match Landsat scenes with temporally compatible
    Sentinel-3 scenes.
    """

    pairs = []

    for landsat_scene in landsat_scenes:

        same_day = [
            scene
            for scene in sentinel3_scenes
            if scene.datetime.date()
            == landsat_scene.acquisition_date.date()
        ]

        if not same_day:
            continue

        sentinel3_scene = min(
            same_day,
            key=lambda scene: abs(
                scene.datetime
                - landsat_scene.acquisition_date
            ),
        )

        time_difference_minutes = abs(
            sentinel3_scene.datetime
            - landsat_scene.acquisition_date
        ).total_seconds() / 60

        if (
            time_difference_minutes
            > MAX_TIME_DIFFERENCE_MINUTES
        ):
            continue

        pairs.append(
            CalibrationPair(
                landsat=landsat_scene,
                sentinel3=sentinel3_scene,
                time_difference_minutes=time_difference_minutes,
            )
        )

    return sorted(
        pairs,
        key=lambda pair: pair.landsat.acquisition_date,
        reverse=True,
    )

def select_calibration_pairs(
    pairs: list[CalibrationPair],
    valid_fraction_function,
) -> list[CalibrationPair]:
    """
    Select seasonally balanced calibration pairs.

    Candidate pairs are evaluated from newest to oldest.
    Selection stops when four valid pairs have been
    accepted for each calendar quarter.
    """

    selected = []

    quarter_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
    }

    for pair in pairs:

        quarter = pair.quarter

        # Quarter already complete
        if (
            quarter_counts[quarter]
            >= TARGET_SCENES_PER_QUARTER
        ):
            continue

        valid_fraction = valid_fraction_function(
            pair
        )

        if valid_fraction < MIN_VALID_FRACTION:
            continue

        selected.append(pair)

        quarter_counts[quarter] += 1

        # Stop as soon as the calibration target is reached
        if all(
            count >= TARGET_SCENES_PER_QUARTER
            for count in quarter_counts.values()
        ):
            break

    return selected

def sentinel3_valid_fraction(
    pair: CalibrationPair,
    sentinel3,
    landsat,
    geometry,
) -> float:
    """
    Calculate valid Sentinel-3 LST coverage over
    the Landsat calibration processing domain.
    """

    # Download only the required Sentinel-3 assets
    sentinel3.download(
        pair.sentinel3
    )

    # Create the Landsat processing grid without
    # downloading Landsat imagery
    target = landsat.grid(
        geometry
    )

    # Grid Sentinel-3 LST over the Landsat domain
    sentinel3_lst = sentinel3.lst(
        scene=pair.sentinel3,
        target=target,
        geometry=geometry,
    )

    valid = np.isfinite(
        sentinel3_lst.data
    )

    if valid.size == 0:
        return 0.0

    return float(
        np.mean(valid)
    )

def find_calibration_pairs(
    aoi,
    landsat,
    sentinel3,
    start_year: int,
    earliest_year: int = 2016,
) -> list[CalibrationPair]:
    """
    Find a seasonally balanced set of STAR-LST
    calibration pairs.
    """

    tile = landsat.find_tile(aoi)
    tile_geometry = landsat._tile_geometry(tile)

    selected = []

    quarter_counts = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
    }

    for year in range(
        start_year,
        earliest_year - 1,
        -1,
    ):

        start_date = datetime(
            year,
            1,
            1,
        )

        end_date = datetime(
            year,
            12,
            31,
            23,
            59,
            59,
        )

        landsat_scenes = landsat.search(
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
        )

        sentinel3_scenes = sentinel3.search(
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
        )

        pairs = match_calibration_pairs(
            landsat_scenes=landsat_scenes,
            sentinel3_scenes=sentinel3_scenes,
        )

        for pair in pairs:

            quarter = pair.quarter

            if (
                quarter_counts[quarter]
                >= TARGET_SCENES_PER_QUARTER
            ):
                continue

            valid_fraction = sentinel3_valid_fraction(
                pair=pair,
                sentinel3=sentinel3,
                landsat=landsat,
                geometry=tile_geometry,
            )

            if valid_fraction < MIN_VALID_FRACTION:
                continue

            selected.append(pair)

            quarter_counts[quarter] += 1

        if all(
            count >= TARGET_SCENES_PER_QUARTER
            for count in quarter_counts.values()
        ):
            break

    return selected