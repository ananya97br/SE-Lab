import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock

#Example test cases:
def test_standard_ride():
    assert ride_cost("standard", 45, False, False) == 40

def test_dock_available():
    assert dock_status(5, 10) == "available"

#Write the rest of the test cases so that the code is 90- 100% covered.
