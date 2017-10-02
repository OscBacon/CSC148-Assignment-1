"""Assignment 1 - Container and priority queue

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This module contains the Container and PriorityQueue classes.

Your only task here is to implement the add method for PriorityQueue,
according to its docstring.
"""
from typing import Generic, List, TypeVar

# Ignore this line; it is only used to facilitate PyCharm's typechecking.
T = TypeVar('T')


class Container(Generic[T]):
    """A container that holds objects.

    This is an abstract class. Only child classes should be instantiated.
    """
    def add(self, item: T) -> None:
        """Add <item> to this Container.
        """
        raise NotImplementedError

    def remove(self) -> T:
        """Remove and return a single item from this container.
        """
        raise NotImplementedError

    def is_empty(self) -> bool:
        """Return True iff this Container is empty.
        """
        raise NotImplementedError


class PriorityQueue(Container[T]):
    """A queue of items that operates in FIFO-priority order.

    Items are removed from the queue according to priority; the item with the
    smallest priority is removed first. In this basic implementation, each
    item's value is its priority, and we compare values simply with '<'.

    Ties are resolved in first-in-first-out (FIFO) order, meaning the item
    that was inserted *earlier* is the first one to be removed.

    All objects in the container must be of the same type.

    === Private Attributes ===
    _queue: List
      The end of the list represents the *front* of the queue, that is,
      the next item to be removed.

    === Representation Invariants ===
    - all elements of _queue are of the same type
    - the elements of _queue are in non-increasing order
    """
    _queue: List[T]

    def __init__(self) -> None:
        """Initialize this to an empty PriorityQueue.
        """
        self._queue = []

    def add(self, item: T) -> None:
        """Add <item> to this PriorityQueue.

        NOTE: See the docstring for the 'remove' method for a sample doctest.
        """
        # TODO: Implement this method!
        pass

    def remove(self) -> T:
        """Remove and return the next item from this PriorityQueue.

        Precondition: this priority queue is non-empty.

        >>> pq = PriorityQueue()
        >>> pq.add('fred')
        >>> pq.add('arju')
        >>> pq.add('monalisa')
        >>> pq.add('hat')
        >>> pq.remove()
        'arju'
        >>> pq.remove()
        'fred'
        >>> pq.remove()
        'hat'
        >>> pq.remove()
        'monalisa'
        """
        return self._queue.pop()

    def is_empty(self):
        """Return True iff this PriorityQueue is empty.

        >>> pq = PriorityQueue()
        >>> pq.is_empty()
        True
        >>> pq.add('fred')
        >>> pq.is_empty()
        False
        """
        return not self._queue


if __name__ == '__main__':
    # import doctest
    # doctest.testmod()
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'typing'
        ],
    })
