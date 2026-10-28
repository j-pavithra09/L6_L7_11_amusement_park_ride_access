import pytest

from amusement_park_ride_access import (
    process_ride_admissions,
    inspect_safety_restraints,
)


# --------------------------------------------------
# 1. Input validation
# --------------------------------------------------

def test_invalid_groups_input():
    with pytest.raises(ValueError):
        process_ride_admissions("invalid", 5.0)


def test_negative_express_pass_fee():
    with pytest.raises(ValueError):
        process_ride_admissions([], -1.0)


# --------------------------------------------------
# 2. Ride availability and ride types
# --------------------------------------------------

def test_closed_ride_is_skipped():
    groups = [
        {
            "is_open": False,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_ADMISSIONS",
    }


def test_roller_coaster_adult_ticket():
    groups = [
        {
            "is_open": True,
            "ride_type": "roller_coaster",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 25.0
    assert result["status"] == "COMPLETED"


def test_water_ride_adult_ticket():
    groups = [
        {
            "is_open": True,
            "ride_type": "water_ride",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 18.0


def test_family_ride_child_discount():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 130, "is_child": True}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 6.0


def test_unknown_ride_type():
    groups = [
        {
            "is_open": True,
            "ride_type": "unknown_ride",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "ZERO_ADMISSIONS"
    assert result["total_revenue"] == 0.0


def test_default_ride_type_is_family():
    groups = [
        {
            "is_open": True,
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


# --------------------------------------------------
# 3. Patron eligibility
# --------------------------------------------------

def test_patron_with_zero_height_is_rejected():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 0}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_patron_below_minimum_height_is_rejected():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 100}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_health_warning_on_water_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "water_ride",
            "patrons": [
                {
                    "height_cm": 150,
                    "health_warning": True,
                }
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_health_warning_on_roller_coaster():
    groups = [
        {
            "is_open": True,
            "ride_type": "roller_coaster",
            "patrons": [
                {"height_cm": 150},
                {"height_cm": 160, "health_warning": True},
                {"height_cm": 170},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_child_and_adult_tickets():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 130, "is_child": True},
                {"height_cm": 150, "is_child": False},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 16.0


def test_missing_patron_fields_use_defaults():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


# --------------------------------------------------
# 4. Express lane and final admission status
# --------------------------------------------------

def test_express_lane_fee_is_added():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "has_fast_lane": True,
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 15.0
    assert result["status"] == "COMPLETED"


def test_safety_audit_after_multiple_rejections():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 0},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "SAFETY_AUDIT"
    assert result["total_revenue"] == 0.0


def test_rounding_of_total_revenue():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 150},
                {"height_cm": 150},
            ],
            "has_fast_lane": True,
        }
    ]

    result = process_ride_admissions(groups, 2.345)

    assert result["total_revenue"] == 22.34

# --------------------------------------------------
# 5. Safety restraint monitoring
# --------------------------------------------------

def test_empty_restraint_streams():
    assert inspect_safety_restraints([]) == "NO_DATA"
    assert inspect_safety_restraints(None) == "NO_DATA"


def test_single_zero_reading_is_safe():
    assert inspect_safety_restraints([[0, 1, 1]]) == "SAFE"


def test_two_consecutive_zero_readings_trigger_emergency():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"


def test_nonconsecutive_zero_readings_are_safe():
    assert inspect_safety_restraints([[0, 1, 0, 1]]) == "SAFE"


def test_emergency_in_a_later_sensor_stream():
    assert inspect_safety_restraints([[1, 1], [0, 0]]) == "EMERGENCY_LOCK"


def test_empty_sensor_stream():
    assert inspect_safety_restraints([[]]) == "SAFE"