"""
Describes a class to represent a block of memory.
"""
import numpy as np


class Block:
    """
    Represents a block of memory.

    Attributes:
        - data ([float]): values stored in given Block instance
        - tag (str): tag associated with given Block instance

    Methods:
        - set_val: adds a value to given Block instance
    """

    def __init__(self, size: int) -> None:
        """
        Initializes a new instance of the `Block` class.

        Parameters:
            - size (int): the size of the block
            - data (list of floats): the data to store in the block
                must be the length of the size of the block

        Returns: nothing
        """
        temp = [np.nan] * size
        self.data = np.array(temp)
        self.tag = None

    def set_val(self, val: float, loc: int, tag: str) -> None:
        """
        Sets a given value in the memory block.

        Parameters:
            - data (list of floats): the data to store in the block
                must be the length of the size of the block

        Returns: nothing
        """
        self.tag = tag
        self.data[loc] = val
