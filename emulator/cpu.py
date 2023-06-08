"""
Describes a class to represent a CPU.
"""
from emulator.address import Address
from emulator.cache import Cache
from emulator.ram import RAM
import numpy as np


class CPU:
    """
    Represents a CPU.

    Attributes:
        - cache (Cache): the Cache associated with given CPU instance
        - ram (RAM): the RAM associated with given CPU instance
        - instructions (int): total number of instructions run

    Methods:
        - load: reads a value at a given address
        - store: writes a value at a given address
        - add: adds two arrays
        - multiply: multiplies two arrays using standard element-wise multiplication
        - matmul: multiplies two matrices using matrix multiplication
    """

    def __init__(
        self,
        block_size: int,
        num_sets: int,
        num_blocks_cache: int,
        num_blocks_ram: int,
        replacement: str,
    ) -> None:
        """
        Initializes a new instance of the `CPU` class.

        Parameters:
            - num_sets
            - num_blocks

        Returns: nothing
        """
        self.cache = Cache(block_size, num_sets, num_blocks_cache, replacement)
        self.ram = RAM(num_blocks_ram, block_size)
        self.instructions = 0

    def load(self, address: int) -> float:
        """
        Loads the data at a given address.

        Parameters:
            - address (int): the address

        Returns: (float) the data at the given address
        """
        address = Address(
            address, self.cache.block_size, len(self.cache.blocks), len(self.cache.sets)
        )
        self.instructions += 1
        return self.cache.get_val(address, self.ram)

    def store(self, address: int, value: float) -> None:
        """
        Stores data at a given address.

        Parameters:
            - address (int): the address
            - value (float): the value to store at the given address

        Returns: nothing
        """
        address = Address(
            address, self.cache.block_size, len(self.cache.blocks), len(self.cache.sets)
        )
        self.instructions += 1
        self.cache.set_val(address, value, self.ram)

    def add(self, arr1: np.ndarray, arr2: np.ndarray) -> np.ndarray:
        """
        Adds the two given arrays.

        Parameters:
            - arr1 (ndarray): the first array to multiply
            - arr2 (ndarray): the second array to multiply

        Returns: (ndarray) the result of multiplying the two arrays
        """
        self.instructions += len(arr1)
        return arr1 + arr2

    def multiply(self, arr1: np.ndarray, arr2: np.ndarray) -> np.ndarray:
        """
        Multiplies the two given arrays.

        Parameters:
            - arr1 (ndarray): the first array to multiply
            - arr2 (ndarray): the second array to multiply

        Returns: (ndarray) the result of multiplying the two arrays
        """
        self.instructions += len(arr1)
        return arr1 * arr2

    def matmul(self, mat1: np.ndarray, mat2: np.ndarray) -> np.ndarray:
        """
        Multiplies the two given matrices.

        Parameters:
            - mat1 (ndarray): the first matrix to multiply
            - mat2 (ndarray): the second matrixto multiply

        Returns: (ndarray) the result of multiplying the two matrices
        """
        n = len(mat1)
        self.instructions += 2 * (n**3) - n**2
        return np.matmul(mat1, mat2)
