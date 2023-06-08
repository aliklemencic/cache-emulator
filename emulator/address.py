"""
Describes a class to represent a 32-bit address.
"""
import math


class Address:
    """
    Represents a 32-bit address to store data in memory.

    Attributes:
        - address (str): binary 32-bit address
        - (private) _offset_len (int): length of the block offset
        - (private) _index_len (int): length of the index
        - (private) _tag_len (int): length of the tag

    Methods:
        - (private) _get_binary: get a 32 bit string of the binary
            representation of the numerical value
        - get_tag: returns the tag
        - get_index: returns the index
        - get_offset: returns the offset
    """

    def __init__(self, address: int, block_size: int, entries: int, sets: int) -> None:
        """
        Initializes a new instance of the `Address` class.

        Parameters:
            - address (int): the numerical address

        Returns: nothing
        """
        self.address = self._get_binary(address)
        self._offset_len = int(math.log(block_size, 2))
        self._index_len = self._get_index_len(sets, entries)
        self._tag_len = 32 - self._offset_len - self._index_len

    def _get_index_len(self, sets: int, entries: int) -> int:
        """
        Returns the length of the index in the address.

        Parameters:
            - sets (int): the number of sets in cache
            - entries (int): the number of rows in cache

        Returns: (int) the length of the index in bits
        """
        # direct mapped
        if sets == 1:
            return int(math.log(entries, 2))
        # fully associative
        elif sets == entries:
            return 0
        # set associative
        else:
            return int(math.log(sets, 2))

    def _get_binary(self, address: int) -> str:
        """
        Returns the numerical address as a binary string.

        Parameters:
            - address (int): the numerical address

        Returns: (str) the 32-bit address in binary
        """
        binary = bin(address)[2:]
        prefix = "0" * (32 - len(binary))
        return prefix + binary

    def get_tag(self) -> str:
        """
        Gets the tag from the address.

        Parameters: None

        Returns: (str) the tag for the address
        """
        return self.address[: self._tag_len]

    def get_index(self) -> str:
        """
        Gets the index from the address.

        Parameters: None

        Returns: (str) the index for the address
        """
        return self.address[self._tag_len : self._tag_len + self._index_len]

    def get_offset(self) -> str:
        """
        Gets the offset from the address.

        Parameters: None

        Returns: (str) the offset for the address
        """
        return self.address[-self._offset_len :]
