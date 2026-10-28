import pytest

from amusement_park_ride_access import (
    process_ride_admissions,
    inspect_safety_restraints,
)


# ============================================================
# 1. INPUT VALIDATION
# ============================================================

def test_invalid_groups_type():
    with pytest.raises(ValueError):
        process_ride_admissions("invalid", 5.0)


def test_negative_express_pass_fee():
    with pytest.raises(ValueError):
        process_ride_admissions([], -1.0)


def test_valid_groups_and_fee():
    result = process_ride_admissions([], 5.0)

    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_ADMISSIONS",
    }


# ============================================================
# 2. RIDE AVAILABILITY AND RIDE TYPE
# ============================================================

def test_closed_ride():
    groups = [
        {
            "is_open": False,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_open_roller_coaster():
    groups = [
        {
            "is_open": True,
            "ride_type": "roller_coaster",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 25.0


def test_open_water_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "water_ride",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 18.0


def test_open_family_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_unknown_ride_type():
    groups = [
        {
            "is_open": True,
            "ride_type": "haunted_ride",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_is_open_defaults_to_false():
    groups = [
        {
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_ride_type_defaults_to_family():
    groups = [
        {
            "is_open": True,
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_missing_patrons_defaults_to_empty_list():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "ZERO_ADMISSIONS"


# ============================================================
# 3. PATRON HEIGHT CONDITIONS
# ============================================================

def test_zero_height_rejected():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 0}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_negative_height_rejected():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": -10}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_positive_height_below_120_rejected():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 119}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_height_exactly_120_is_accepted():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 120}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_missing_height_defaults_to_zero():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


# ============================================================
# 4. HEALTH WARNINGS
# ============================================================

def test_health_warning_on_family_ride():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 150, "health_warning": True},
            ],
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
                {"height_cm": 150, "health_warning": True},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 0.0


def test_health_warning_resets_roller_coaster_group_revenue():
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


def test_health_warning_after_existing_revenue():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 150},
                {"height_cm": 150, "health_warning": True},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_missing_health_warning_defaults_to_false():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


# ============================================================
# 5. CHILD AND ADULT TICKETS
# ============================================================

def test_child_ticket_discount():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 130, "is_child": True},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 6.0


def test_adult_pays_full_ticket_price():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 150, "is_child": False},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_missing_is_child_defaults_to_false():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


# ============================================================
# 6. EXPRESS LANE
# ============================================================

def test_fast_lane_enabled():
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


def test_fast_lane_disabled():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "has_fast_lane": False,
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


def test_missing_fast_lane_defaults_to_false():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["total_revenue"] == 10.0


# ============================================================
# 7. FINAL ADMISSION STATUS
# ============================================================

def test_safety_audit_after_more_than_four_rejections():
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


def test_four_rejections_do_not_trigger_safety_audit():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 0},
                {"height_cm": 150},
            ],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "COMPLETED"
    assert result["total_revenue"] == 10.0


def test_zero_revenue_returns_zero_admissions():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result == {
        "total_revenue": 0.0,
        "status": "ZERO_ADMISSIONS",
    }


def test_positive_revenue_returns_completed():
    groups = [
        {
            "is_open": True,
            "ride_type": "family",
            "patrons": [{"height_cm": 150}],
        }
    ]

    result = process_ride_admissions(groups, 5.0)

    assert result["status"] == "COMPLETED"


def test_safety_audit_takes_precedence_over_zero_revenue():
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


# ============================================================
# 8. SAFETY RESTRAINT MONITORING
# ============================================================

def test_none_restraint_streams():
    assert inspect_safety_restraints(None) == "NO_DATA"


def test_empty_restraint_streams():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_single_zero_reading():
    assert inspect_safety_restraints([[0]]) == "SAFE"


def test_two_consecutive_zero_readings():
    assert inspect_safety_restraints([[0, 0]]) == "EMERGENCY_LOCK"


def test_zero_readings_separated_by_nonzero():
    assert inspect_safety_restraints([[0, 1, 0]]) == "SAFE"


def test_emergency_detected_after_nonzero_reading():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"


def test_emergency_detected_in_second_sensor_stream():
    assert inspect_safety_restraints([[1, 1], [0, 0]]) == "EMERGENCY_LOCK"


def test_empty_sensor_stream_is_safe():
    assert inspect_safety_restraints([[]]) == "SAFE"


def test_all_nonzero_sensor_readings_are_safe():
    assert inspect_safety_restraints([[1, 1, 1]]) == "SAFE"


def test_long_zero_streak_triggers_emergency():
    assert inspect_safety_restraints([[0, 0, 0]]) == "EMERGENCY_LOCK"