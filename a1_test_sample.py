"""CSC148 Assignment 1: Sample tests

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto

=== Module description ===
This module contains sample tests for Assignment 1.

Warning: This is an extremely incomplete set of tests!
Add your own to practice writing tests and to be confident your code is correct.

For more information on hypothesis (one of the testing libraries we're using),
please see
<http://www.teach.cs.toronto.edu/~csc148h/fall/software/hypothesis.html>.

Note: this file is for support purposes only, and is not part of your
submission.
"""
from datetime import datetime, timedelta
import os
import pygame
from pytest import approx
from bikeshare import Ride, Station
from simulation import Simulation, create_stations, create_rides


###############################################################################
# Sample tests for Task 1
###############################################################################
def test_create_stations_simple():
    """Test reading in a station from provided sample stations.json.
    """
    stations = create_stations('stations.json')
    test_id = '6023'
    assert test_id in stations

    station = stations[test_id]
    assert isinstance(station, Station)
    assert station.name == 'de la Commune / Berri'
    assert station.location == (-73.54983, 45.51086)  # NOTE: (long, lat) coordinates!
    assert station.num_bikes == 18
    assert station.capacity == 39


def test_create_rides_simple():
    """Test reading in a rides file from provided sample sample_rides.csv.

    NOTE: This test relies on test_create_stations working correctly.
    """
    stations = create_stations('stations.json')
    rides = create_rides('sample_rides.csv', stations)

    # Check the first ride
    ride = rides[0]
    assert isinstance(ride, Ride)
    assert ride.start is stations['6134']
    assert ride.end is stations['6721']
    assert ride.start_time == datetime(2017, 6, 1, 7, 31, 0)
    assert ride.end_time == datetime(2017, 6, 1, 7, 54, 0)


###############################################################################
# Sample tests for Task 2
###############################################################################
def test_get_position_station():
    """Test get_position for a simple station.
    """
    stations = create_stations('stations.json')
    test_id = '6023'
    assert test_id in stations

    station = stations[test_id]
    time = datetime(2017, 9, 1, 0, 0, 0)  # Note: the time shouldn't matter.
    assert station.get_position(time) == (-73.54983, 45.51086)


def test_get_position_ride():
    """Test get_position for a simple ride.
    """
    stations = create_stations('stations.json')
    rides = create_rides('sample_rides.csv', stations)

    ride = rides[0]

    # Check ride endpoints. We use pytest's approx function to
    # avoid floating point issues.
    assert ride.get_position(ride.start_time) == approx(ride.start.location)
    assert ride.get_position(ride.end_time) == approx(ride.end.location)

    # Manually check a time during the ride.
    # Note that this ride lasts *23 minutes*, and
    # goes from (-73.562643, 45.537964) to
    # (-73.54628920555115, 45.57713595014113).
    # We're checking the position after 10 minutes have passed.
    assert (
        ride.get_position(datetime(2017, 6, 1, 7, 41, 0)) ==
        approx((-73.5555326546, 45.5549952827),
               abs=1e-5)
    )


###############################################################################
# Sample tests for Task 4
###############################################################################
def test_statistics_simple():
    """A very small test simulation.

    This runs a simulation on the sample data files
    in the time range 9:30 to 9:45, in which there's only
    one ride (the very last ride in the file).
    """
    os.environ['SDL_VIDEODRIVER'] = 'dummy'                 # Ignore this line
    sim = Simulation('stations.json', 'sample_rides.csv')
    pygame.event.post(pygame.event.Event(pygame.QUIT, {}))  # Ignore this line

    sim.run(datetime(2017, 6, 1, 9, 30, 0),
            datetime(2017, 6, 1, 9, 45, 0))
    stats = sim.calculate_statistics()

    # Only one ride started!
    assert stats['max_start'] == (
        sim.all_stations['6091'].name,
        1
    )

    # Only one ride ended!
    assert stats['max_end'] == (
        sim.all_stations['6052'].name,
        1
    )

    # Many stations spent all 15 minutes (900 seconds) with
    # "low availability" or "low unoccupied".
    # We pick the ones whose names are *smallest* when compared
    # using <. Note that numbers come before letters in this ordering.

    # This station starts with only 3 bikes at the station.
    assert stats['max_time_low_availability'] == (
        '15e avenue / Masson',
        900  # 900 seconds
    )

    # This stations starts with only 1 unoccupied spot.
    assert stats['max_time_low_unoccupied'] == (
        '10e Avenue / Rosemont',
        900  # 900 seconds
    )


def test_ride_ends_outside_run():
    """Test a special case: when a ride ends outside the run period.
    """
    os.environ['SDL_VIDEODRIVER'] = 'dummy'                 # Ignore this line
    sim = Simulation('stations.json', 'sample_rides.csv')
    pygame.event.post(pygame.event.Event(pygame.QUIT, {}))  # Ignore this line

    # This last ride in the sample_rides.csv file now begins
    # during the simulation run, but ends after the run.
    sim.run(datetime(2017, 6, 1, 9, 30, 0),
            datetime(2017, 6, 1, 9, 40, 0))
    stats = sim.calculate_statistics()

    # One ride still started.
    assert stats['max_start'] == (
        sim.all_stations['6091'].name,
        1
    )

    # *No* rides were ended during the simulation time period.
    # As in the previous test, we pick the station whose name
    # is smallest when compared with <.
    assert stats['max_end'] == (
        '10e Avenue / Rosemont',
        0
    )


if __name__ == '__main__':
    import pytest
    pytest.main(['a1_test_sample.py'])
