from datetime import datetime, timezone

from star.algorithms.star_lst.calibration import (
    _quarter,
    match_calibration_pairs,
)
from star.sensors.landsat_scene import LandsatScene
from star.sensors.sentinel3_scene import Sentinel3Scene


def test_quarter():

    assert _quarter(datetime(2025, 1, 1)) == 1
    assert _quarter(datetime(2025, 4, 1)) == 2
    assert _quarter(datetime(2025, 7, 1)) == 3
    assert _quarter(datetime(2025, 10, 1)) == 4


def test_match_calibration_pairs():

    landsat = LandsatScene(
        scene_id="landsat_test",
        platform="Landsat-8",
        acquisition_date=datetime(
            2025, 1, 30, 11, 4,
            tzinfo=timezone.utc,
        ),
        path=202,
        row=38,
    )

    sentinel3_close = Sentinel3Scene(
        scene_id="sentinel3_close",
        datetime=datetime(
            2025, 1, 30, 10, 58,
            tzinfo=timezone.utc,
        ),
        assets={},
    )

    sentinel3_far = Sentinel3Scene(
        scene_id="sentinel3_far",
        datetime=datetime(
            2025, 1, 30, 22, 50,
            tzinfo=timezone.utc,
        ),
        assets={},
    )

    pairs = match_calibration_pairs(
        landsat_scenes=[landsat],
        sentinel3_scenes=[
            sentinel3_far,
            sentinel3_close,
        ],
    )

    assert len(pairs) == 1

    pair = pairs[0]

    assert pair.landsat is landsat
    assert pair.sentinel3 is sentinel3_close

    assert pair.time_difference_minutes == 6.0

    assert pair.quarter == 1

def test_select_calibration_pairs():

    from star.algorithms.star_lst.calibration import (
        CalibrationPair,
        select_calibration_pairs,
    )

    pairs = []

    # Create 6 candidate scenes for each quarter
    for quarter, month in [
        (1, 1),
        (2, 4),
        (3, 7),
        (4, 10),
    ]:
        for day in range(1, 7):

            acquisition = datetime(
                2025,
                month,
                day,
                11,
                0,
                tzinfo=timezone.utc,
            )

            landsat = LandsatScene(
                scene_id=f"L_{quarter}_{day}",
                platform="Landsat-8",
                acquisition_date=acquisition,
                path=202,
                row=38,
            )

            sentinel3 = Sentinel3Scene(
                scene_id=f"S3_{quarter}_{day}",
                datetime=acquisition,
                assets={},
            )

            pairs.append(
                CalibrationPair(
                    landsat=landsat,
                    sentinel3=sentinel3,
                    time_difference_minutes=0.0,
                )
            )

    # Simulate coverage:
    # days 1-2 fail (<60%), days 3-6 pass.
    def valid_fraction(pair):

        day = pair.landsat.acquisition_date.day

        if day <= 2:
            return 0.40

        return 0.80

    selected = select_calibration_pairs(
        pairs=pairs,
        valid_fraction_function=valid_fraction,
    )

    assert len(selected) == 16

    for quarter in range(1, 5):

        quarter_pairs = [
            pair
            for pair in selected
            if pair.quarter == quarter
        ]

        assert len(quarter_pairs) == 4

    # Every selected scene must satisfy coverage criterion
    assert all(
        valid_fraction(pair) >= 0.60
        for pair in selected
    )