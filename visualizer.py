"""Assignment 1 - Visualizer

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Visualizer class, which is responsible for interacting
with Pygame, the graphics library we're using for this assignment.
There's quite a bit in this file, but you aren't responsible for most of it.
(You'll be doing more with Pygame on Assignment 2, though!)

It also contains the Map class, which is responsible for converting between
lat/long coordinates and pixel coordinates on the pygame window.

DO NOT CHANGE ANY CODE IN THIS FILE. You don't need to for this assignment,
and in fact you aren't even submitting this file!
"""
from datetime import datetime
import os
from typing import List, Tuple
import pygame
from bikeshare import Drawable


WHITE = (255, 255, 255)
MAP_FILE = 'montreal.png'
# Map upper-left and bottom-right coordinates (long, lat).
MAP_MIN = (-73.840119, 45.638191)
MAP_MAX = (-73.471199, 45.425780)

# Window size
SCREEN_SIZE = (960, 787)


class Visualizer:
    """Visualizer for the current state of a simulation.
    """
    # === Private attributes ===
    # _screen: the pygame window that is shown to the user.
    # _mouse_down: whether the user is holding down a mouse button
    #   on the pygame window.
    # _map: the Map object responsible for converting between long/lat
    #   coordinates and the pixels of the visualization window.
    _screen: pygame.Surface
    _mouse_down: bool
    _map: 'Map'

    def __init__(self) -> None:
        """Initialize this visualization.
        """
        pygame.init()
        self._screen = pygame.display.set_mode(
            SCREEN_SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._screen.fill(WHITE)
        self._mouse_down = False
        self._map = Map(SCREEN_SIZE)

        # Initial render. Pass in datetime.now() as an dummy value.
        self.render_drawables([], datetime.now())

    def render_drawables(self, drawables: List[Drawable],
                         time: datetime) -> None:
        """Render the simulation objects to the screen for the given time."""
        # Draw the background map onto the screen
        self._screen.fill(WHITE)
        self._screen.blit(self._map.get_current_view(), (0, 0))

        # Add all of the objects onto the screen
        self._map.render_objects(drawables, self._screen, time)

        # Show the new image
        pygame.display.flip()

    def handle_window_events(self) -> bool:
        """Handle any user events triggered through the pygame window.

        Return True if the user closed the window (by pressing the 'X'),
        and False otherwise.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._mouse_down = True
                elif event.button == 4:
                    self._map.zoom(-0.1)
                elif event.button == 5:
                    self._map.zoom(0.1)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if self._mouse_down:
                    self._map.pan(pygame.mouse.get_rel())
                else:
                    pygame.mouse.get_rel()
        return False


class Map:
    """Window panning and zooming interface.

    === Attributes ===
    image:
        the full image for the area to cover with the map
    min_coords:
        the minimum long/lat coordinates
    max_coords:
        the maximum long/lat coordinates
    """
    image: pygame.image
    min_coords: Tuple[float, float]
    max_coords: Tuple[float, float]

    def __init__(self, screendims: Tuple[int, int]) -> None:
        """Initialize this map for the given screen dimensions.
        """
        self.image = pygame.image.load(
            os.path.join(os.path.dirname(__file__), MAP_FILE))
        self.min_coords = MAP_MIN
        self.max_coords = MAP_MAX

        self._xoffset = 0
        self._yoffset = 0
        self._zoom = 1
        self.screensize = screendims

    def render_objects(self, drawables: List[Drawable],
                       screen: pygame.Surface, time: datetime) -> None:
        """Render the given objects onto the given screen.

        Calculate their positions based on the given time.
        """
        for drawable in drawables:
            latlong_position = drawable.get_position(time)
            sprite_position = self._latlong_to_screen(latlong_position)
            sprite_file = os.path.join(os.path.dirname(__file__),
                                       drawable.sprite)
            screen.blit(pygame.image.load(sprite_file),
                        sprite_position)

    def _latlong_to_screen(self,
                           location: Tuple[float, float]) -> Tuple[int, int]:
        """Convert the given (long, lat) coordinates into pixel coordinates.

        You can safely ignore the calculations done in this method!
        """
        x = round((location[0] - self.min_coords[0]) /
                  (self.max_coords[0] - self.min_coords[0]) *
                  self.image.get_width())
        y = round((location[1] - self.min_coords[1]) /
                  (self.max_coords[1] - self.min_coords[1]) *
                  self.image.get_height())

        x = round((x - self._xoffset) * self._zoom * self.screensize[0] /
                  self.image.get_width())
        y = round((y - self._yoffset) * self._zoom * self.screensize[1] /
                  self.image.get_height())
        return x, y

    def pan(self, dp: Tuple[int, int]) -> None:
        """Pan the view in the image by (dx, dy) screenspace pixels.
        """
        self._xoffset -= dp[0]
        self._yoffset -= dp[1]
        self._clamp_transformation()

    def zoom(self, dx: float) -> None:
        """Zooms the view by the given amount.

        The centre of the zoom is the top-left corner of the visible region.
        """
        if (self._zoom >= 4 and dx > 0) or (self._zoom <= 1 and dx < 0):
            return

        self._zoom += dx
        self._clamp_transformation()

    def _clamp_transformation(self) -> None:
        """Ensure that the transformation parameters are within a fixed range.
        """
        raw_width = self.image.get_width()
        raw_height = self.image.get_height()
        zoom_width = round(raw_width / self._zoom)
        zoom_height = round(raw_height / self._zoom)

        self._xoffset = min(raw_width - zoom_width, max(0, self._xoffset))
        self._yoffset = min(raw_height - zoom_height, max(0, self._yoffset))

    def get_current_view(self) -> pygame.Surface:
        """Get the subimage to display to screen from the map.
        """
        raw_width = self.image.get_width()
        raw_height = self.image.get_height()
        zoom_width = round(raw_width / self._zoom)
        zoom_height = round(raw_height / self._zoom)

        mapsegment = self.image.subsurface(((self._xoffset, self._yoffset),
                                            (zoom_width, zoom_height)))
        return pygame.transform.smoothscale(mapsegment, self.screensize)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'typing',
            'datetime', 'os', 'pygame',
            'bikeshare'
        ],
        'generated-members': 'pygame.*'
    })
