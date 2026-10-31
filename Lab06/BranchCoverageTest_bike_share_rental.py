import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# ---------- ride_cost ----------

def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40


def test_unknown_bike_type():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("scooter", 30, False, False)


def test_zero_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", 0, False, False)


def test_negative_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", -10, False, False)


def test_subscriber_free_first_block():
    # 1 block - 1 free = 0, returns 0 early
    assert ride_cost("standard", 20, True, False) == 0


def test_subscriber_pays_remaining_blocks():
    assert ride_cost("standard", 45, True, False) == 20


def test_non_subscriber_pays_all_blocks():
    assert ride_cost("standard", 30, False, False) == 20


def test_peak_surcharge_standard():
    assert ride_cost("standard", 30, False, True) == 35


def test_peak_surcharge_electric():
    assert ride_cost("electric", 30, False, True) == 50


def test_peak_cargo_no_surcharge():
    # peak ride but cargo bike, so no surcharge
    assert ride_cost("cargo", 30, False, True) == 50


def test_off_peak_no_surcharge():
    assert ride_cost("electric", 30, False, False) == 35


def test_subscriber_peak():
    assert ride_cost("standard", 45, True, True) == 35


def test_long_ride_penalty():
    assert ride_cost("standard", 200, False, False) == 240


def test_exactly_180_minutes_no_penalty():
    # boundary: 180 is not > 180
    assert ride_cost("standard", 180, False, False) == 120


def test_181_minutes_penalty():
    assert ride_cost("standard", 181, False, False) == 240


def test_cargo_long_ride():
    assert ride_cost("cargo", 200, False, False) == 450


# ---------- dock_status ----------

def test_zero_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, 0)


def test_negative_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(1, -5)


def test_negative_bikes_docked():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(-1, 10)


def test_bikes_exceed_capacity():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(11, 10)


def test_dock_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_full():
    assert dock_status(10, 10) == "full"


def test_dock_few_bikes_lower():
    assert dock_status(1, 10) == "few bikes"


def test_dock_few_bikes_boundary():
    # boundary: bikes_docked == 2
    assert dock_status(2, 10) == "few bikes"


def test_dock_few_slots_boundary():
    # boundary: free_slots == 2
    assert dock_status(8, 10) == "few slots"


def test_dock_few_slots_one_free():
    assert dock_status(9, 10) == "few slots"


def test_dock_available():
    assert dock_status(5, 10) == "available"


def test_dock_available_just_above_few_bikes():
    assert dock_status(3, 10) == "available"


# ---------- can_unlock ----------

def test_unlock_blocked_active_ride():
    assert can_unlock(500, True, 25) is False


def test_unlock_too_young():
    assert can_unlock(500, False, 15) is False


def test_unlock_minor_enough_balance():
    assert can_unlock(100, False, 17) is True


def test_unlock_minor_insufficient_balance():
    assert can_unlock(99, False, 17) is False


def test_unlock_age_16_boundary():
    assert can_unlock(100, False, 16) is True


def test_unlock_age_18_boundary():
    # 18 counts as an adult, so only 50 is needed
    assert can_unlock(50, False, 18) is True


def test_unlock_adult_enough_balance():
    assert can_unlock(50, False, 30) is True


def test_unlock_adult_insufficient_balance():
    assert can_unlock(49, False, 30) is False