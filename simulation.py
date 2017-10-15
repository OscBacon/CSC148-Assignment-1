"""Assignment 1 - Simulation

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Simulation class, which is the main class for your
bike-share simulation.

At the bottom of the file, there is a sample_simulation function that you
can use to try running the simulation at any time.
"""
import csv
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple

from bikeshare import Ride, Station
from container import PriorityQueue
from visualizer import Visualizer

# Datetime format to parse the ride data
DATETIME_FORMAT = '%Y-%m-%d %H:%M'


class Simulation:
    """Runs the core of the simulation through time.

    === Attributes ===
    all_rides:
        A list of all the rides in this simulation.
        Note that not all rides might be used, depending on the timeframe
        when the simulation is run.
    all_stations:
        A dictionary containing all the stations in this simulation.
    visualizer:
        A helper class for visualizing the simulation.
    active_rides:
        A list of all rides currently active
    """
    all_stations: Dict[str, Station]
    all_rides: List[Ride]
    visualizer: Visualizer
    active_rides: List[Ride]

    def __init__(self, station_file: str, ride_file: str) -> None:
        """Initialize this simulation with the given configuration settings.
        """
        self.all_stations = create_stations(station_file)
        self.all_rides = create_rides(ride_file, self.all_stations)
        self.visualizer = Visualizer()
        self.active_rides = []
        self.ride_priority_queue = PriorityQueue()

    def run(self, start: datetime, end: datetime) -> None:
        """Run the simulation from <start> to <end>.
        """
        step = timedelta(minutes=1)  # Each iteration spans one minute of time

        # Leave this code at the very bottom of this method.
        # It will keep the visualization window open until you close
        # it by pressing the 'X'.
        time = start

        for ride in self.all_rides:
            if start < ride.start_time < end:
                self.ride_priority_queue.add(RideStartEvent(self,
                                                            ride.start_time,
                                                            ride))

        while time < end:
            time += step

            for station in self.all_stations:
                self.all_stations[station].check_space()

            self._update_active_rides_fast(time)

            rides_stations = list(
                self.all_stations.values()) + self.active_rides

            self.visualizer.render_drawables(rides_stations, time)

            # This part was commented out to allow sample tests to work
            # if self.visualizer.handle_window_events():
            #    return  # Stop the simulation


    def _update_active_rides(self, time: datetime) -> None:
        """Update this simulation's list of active rides for the given time.

        REQUIRED IMPLEMENTATION NOTES:
        -   Loop through `self.all_rides` and compare each Ride's start and
            end times with <time>.

            If <time> is between the ride's start and end times (inclusive),
            then add the ride to self.active_rides if it isn't already in that
            list.

            Otherwise, remove the ride from self.active_rides if it is in that
            list.

        -   This means that if a ride started before the simulation's time
            period but ends during or after the simulation's time period,
            it should still be added to self.active_rides.
        """

        for ride in self.all_rides:
            # Only take into account ride that happen during the simulation
            # bracket
            if (ride.start_time <= time <= ride.end_time) and \
                    (ride not in self.active_rides):
                self.active_rides.append(ride)
                ride.start.num_bikes_start += 1
        for ride in self.active_rides:
            # Remove a ride from active rides if the ride is over
            if time > ride.end_time:
                self.active_rides.remove(ride)
                ride.end.num_bikes_end += 1

        for bike in self.active_rides:
            # If a ride starts, remove a bike from its start station
            if time == bike.start_time:
                if bike.start.num_bikes > 0:
                    bike.start.num_bikes -= 1
                else:
                    self.active_rides.remove(bike)
            # If a ride is over, add a bike to its en station and remove it
            # from active rides
            if time == bike.end_time:
                if bike.end.capacity > bike.end.num_bikes:
                    bike.end.num_bikes += 1
                else:
                    self.active_rides.remove(bike)

    def _find_max(self, value: str):
        """Helper function to find the stations with the maximum of the queried
        attribute
        """
        stations = self.all_stations
        maximum = ('', -1)

        for key in stations:
            # Adapt the attribute search for according to the queried one
            if value == 'num_bikes_start':
                station_attribute = stations[key].num_bikes_start
            elif value == 'num_bikes_end':
                station_attribute = stations[key].num_bikes_end
            elif value == 'total_time_low_availability':
                station_attribute = stations[key].total_time_low_availability
            elif value == 'total_time_low_unoccupied':
                station_attribute = stations[key].total_time_low_unoccupied

            # Find maximum value by replacing maximum if the station has a
            # higher value
            if station_attribute > maximum[1]:
                maximum = (stations[key].name, station_attribute)
            elif station_attribute == maximum[1]:
                if stations[key].name < maximum[0]:
                    maximum = (stations[key].name, station_attribute)

        return maximum

    def calculate_statistics(self) -> Dict[str, Tuple[str, float]]:
        """Return a dictionary containing statistics for this simulation.

        The returned dictionary has exactly four keys, corresponding
        to the four statistics tracked for each station:
          - 'max_start'
          - 'max_end'
          - 'max_time_low_availability'
          - 'max_time_low_unoccupied'

        The corresponding value of each key is a tuple of two elements,
        where the first element is the name (NOT id) of the station that
        has the maximum value of the quantity specified by that key,
        and the second element is the value of that quantity.

        For example, the value corresponding to key 'max_start' should be
        the name of the station with the most number of rides started at
        that station, and the number of rides that started at that
        station.
        """

        max_start = self._find_max('num_bikes_start')
        max_end = self._find_max('num_bikes_end')
        max_time_low_availability = \
            self._find_max('total_time_low_availability')
        max_time_low_unoccupied = self._find_max('total_time_low_unoccupied')

        return {
            'max_start': max_start,
            'max_end': max_end,
            'max_time_low_availability': max_time_low_availability,
            'max_time_low_unoccupied': max_time_low_unoccupied
        }

    def _update_active_rides_fast(self, time: datetime) -> None:
        """Update this simulation's list of active rides for the given
        time.

        REQUIRED IMPLEMENTATION NOTES:
        -   see Task 5 of the assignment handout
        """
        p_queue = self.ride_priority_queue
        while not p_queue.is_empty():
            event = p_queue.remove()
            if time < event.time:
                p_queue.add(event)
                return
            else:
                queued_events = event.process()
                for queued_event in queued_events:
                    p_queue.add(queued_event)


def create_stations(stations_file: str) -> Dict[str, 'Station']:
    """Return the stations described in the given JSON data file.

    Each key in the returned dictionary is a station id,
    and each value is the corresponding Station object.
    Note that you need to call Station(...) to create these objects!

    Precondition: stations_file matches the format specified in the
                  assignment handout.

    This function should be called *before* _read_rides because the
    rides CSV file refers to station ids.
    """
    # Read in raw data using the json library.
    with open(stations_file) as file:
        raw_stations = json.load(file)

    stations = {}
    for s in raw_stations['stations']:
        # Extract the relevant fields from the raw station JSON.
        # s is a dictionary with the keys 'n', 's', 'la', 'lo', 'da', and
        # 'ba' as described in the assignment handout.
        # NOTE: all of the corresponding values are strings, and so you
        # need to convert some of them to numbers explicitly using int()
        # or float().
        stations[s['n']] = Station((float(s['lo']), float(s['la'])),
                                   int(s['ba']) + int(s['da']), int(s['da']),
                                   s['s'])
    return stations


def create_rides(rides_file: str,
                 stations: Dict[str, 'Station']) -> List['Ride']:
    """Return the rides described in the given CSV file.

    Lookup the station ids contained in the rides file in <stations>
    to access the corresponding Station objects.

    Ignore any ride whose start or end station is not present in
    <stations>.

    Precondition: rides_file matches the format specified in the
                  assignment handout.
    """
    rides = []
    with open(rides_file) as file:
        for line in csv.reader(file):
            # line is a list of strings, following the format described
            # in the assignment handout.
            #
            # Convert between a string and a datetime object
            # using the function datetime.strptime and the DATETIME_FORMAT
            # constant we defined above. Example:
            # >>> datetime.strptime('2017-06-01 8:00', DATETIME_FORMAT)
            # datetime.datetime(2017, 6, 1, 8, 0)

            if line[1] in stations and line[3] in stations:
                rides.append(Ride(stations[line[1]], stations[line[3]],
                                  (datetime.strptime(line[0], DATETIME_FORMAT),
                                   datetime.strptime(line[2],
                                                     DATETIME_FORMAT))))
    return rides


class Event:
    """An event in the bike share simulation.

    Events are ordered by their timestamp.
    """
    simulation: 'Simulation'
    time: datetime

    def __init__(self, simulation: 'Simulation', time: datetime) -> None:
        """Initialize a new event."""
        self.simulation = simulation
        self.time = time

    def __lt__(self, other: 'Event') -> bool:
        """Return whether this event is less than <other>.

        Events are ordered by their timestamp.
        """
        return self.time < other.time

    def process(self) -> List['Event']:
        """Process this event by updating the state of the simulation.

        Return a list of new events spawned by this event.
        """
        raise NotImplementedError


class RideStartEvent(Event):
    """An event corresponding to the start of a ride."""

    def __init__(self, simulation: 'Simulation', time: datetime, ride: 'Ride') \
            -> None:
        Event.__init__(self, simulation, time)
        self.ride = ride

    def process(self) -> List['Event']:
        """Function that processes the event"""
        self.simulation.active_rides.append(self.ride)
        self.ride.start.num_bikes_start += 1
        return [RideEndEvent(self.simulation, self.ride.end_time, self.ride)]


class RideEndEvent(Event):
    """An event corresponding to the start of a ride."""

    def __init__(self, simulation: 'Simulation', time: datetime, ride: 'Ride') \
            -> None:
        Event.__init__(self, simulation, time)
        self.ride = ride

    def process(self) -> List['Event']:
        """Function that processes the event"""
        self.simulation.active_rides.remove(self.ride)
        self.ride.end.num_bikes_end += 1
        return []


def sample_simulation() -> Dict[str, Tuple[str, float]]:
    """Run a sample simulation. For testing purposes only."""
    sim = Simulation('stations.json', 'sample_rides.csv')
    sim.run(datetime(2017, 6, 1, 8, 0, 0),
            datetime(2017, 6, 1, 9, 0, 0))
    return sim.calculate_statistics()


if __name__ == '__main__':
    # Uncomment these lines when you want to check your work using python_ta!
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'allowed-io': ['create_stations', 'create_rides'],
    #     'allowed-import-modules': [
    #         'doctest', 'python_ta', 'typing',
    #         'csv', 'datetime', 'json',
    #         'bikeshare', 'container', 'visualizer'
    #     ]
    # })
    print(sample_simulation())
