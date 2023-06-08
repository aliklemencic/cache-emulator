"""
Describes a class to represent RAM.
"""
from emulator.block import Block
import numpy as np


class RAM:
    """
    Represents RAM.

    Attributes:
        - data ([Blocks]): the memory blocks associated with given RAM instance

    Methods:
        - get_block: reads a block from RAM
        - set_block: writes a block to RAM
    """

    def __init__(self, num_blocks: int, block_size: int) -> None:
        """
        Initializes a new instance of the `RAM` class.

        Parameters:
            - num_blocks (int): the number of blocks in RAM
            - data (Block): the data to store
                must be the length of the number of blocks

        Returns: nothing
        """
        temp = [[False, Block(block_size)]] * num_blocks
        self.blocks = np.array(temp)

    def get_block(self, tag: str, index: str) -> Block:
        """
        Accesses a block of data in RAM.

        Parameters:
            - address (int): the address

        Returns: (Block) the data in the block
        """
        index = int(tag + index, 2)
        valid, block = self.blocks[index]
        if valid:
            return block
        return None

    def set_block(self, tag: str, index: str, data: Block) -> None:
        """
        Sets a block of data in RAM.

        Parameters:
            - address (int): the address

        Returns: nothing
        """
        index = int(tag + index, 2)
        self.blocks[index] = [True, data]
