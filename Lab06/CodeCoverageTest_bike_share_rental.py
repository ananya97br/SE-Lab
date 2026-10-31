import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock

# ---------- ride_cost ----------
def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40

def test_unknown_bike():
    with pytest.raises(ValueError):
        ride_cost("scooter", 30, False, False)

def test_invalid_duration():
    with pytest.raises(ValueError):
        ride_cost("standard", 0, False, False)

def test_subscriber_free_first_block():
    assert ride_cost("standard", 20, True, False) == 0

def test_subscriber_pays_extra_blocks():
    assert ride_cost("standard", 45, True, False) == 20

def test_peak_surcharge():
    assert ride_cost("standard", 30, False, True) == 35

def test_long_ride_penalty():
    assert ride_cost("standard", 200, False, False) == 240

# ---------- dock_status ----------
def test_dock_available():
    assert dock_status(5, 10) == "available"

def test_invalid_capacity():
    with pytest.raises(ValueError):
        dock_status(1, 0)

def test_invalid_bike_count():
    with pytest.raises(ValueError):
        dock_status(11, 10)

def test_dock_empty():
    assert dock_status(0, 10) == "empty"

def test_dock_full():
    assert dock_status(10, 10) == "full"

def test_dock_few_bikes():
    assert dock_status(2, 10) == "few bikes"

def test_dock_few_slots():
    assert dock_status(9, 10) == "few slots"

# ---------- can_unlock ----------
def test_unlock_active_ride():
    assert can_unlock(500, True, 25) is False

def test_unlock_too_young():
    assert can_unlock(500, False, 15) is False

def test_unlock_minor_enough_balance():
    assert can_unlock(100, False, 17) is True

def test_unlock_adult_enough_balance():
    assert can_unlock(50, False, 30) is True