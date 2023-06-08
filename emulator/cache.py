"""
Describes a class to represent a cache.
"""
from emulator.address import Address
from emulator.block import Block
from emulator.ram import RAM
import random
import numpy as np
from datetime import datetime


class Cache:
    """
    Represents a cache in memory.

    Attributes:
        - block_size (int): size of a block
        - replacement (str): replacement strategy
        - sets (dict): starting block index for each set
        - blocks_per_set (int): number of blocks in a set
        - blocks (list[bool, str, Block, datetime, datetime]): 
            list of block information
            [valid bit, tag, Block, time in, access time]
        - read_hits (int): number of hits on read
        - read_misses (int): number of misses on read
        - write_hits (int): number of hits on write
        - write_misses (int): number of misses on write

    Methods:
        - (private) _get_sets: determines blocks for each set
        - get_val: reads a value from memory
        - set_val: writes a value to memory
        - get_block: reads a block from the cache
        - set_block: writes a block to the cache
    """

    def __init__(
        self, block_size: int, num_sets: int, num_blocks: int, replacement: str
    ) -> None:
        """
        Initializes a new instance of the `Cache` class.

        Parameters:
            - block_size (int): size of a block in bytes
            - num_sets (int): the number of sets (associativity)
                1 refers to a direct mapped cache while any number
                greater than 1 refers to an associative cache
            - num_blocks (int): the number of blocks in cache
            - replacement (str): the replacement strategy: random, FIFO, LRU

        Returns: nothing
        """
        self.block_size = block_size
        self.replacement = replacement
        self.sets = self._get_sets(num_sets, num_blocks)

        # store valid bit, data block, time in, and access time
        temp = [[False, None, Block(block_size), np.nan, np.nan]] * num_blocks
        self.blocks = np.array(temp)

        self.read_hits = 0
        self.read_misses = 0
        self.write_hits = 0
        self.write_misses = 0

    def _get_sets(self, num_sets: int, num_blocks: int) -> dict:
        """
        Determines which blocks are in each set.

        Parameters:
            - num_sets (int): the number of sets (associativity)
                1 refers to a direct mapped cache while any number
                greater than 1 refers to an associative cache
            - num_blocks (int): the number of blocks in cache

        Returns: (dict) blocks associated with each set
        """
        self.blocks_per_set = num_blocks // num_sets
        sets = {}
        ix = 0
        for i in range(num_sets):
            sets[i] = ix
            ix += self.blocks_per_set
        return sets

    def get_val(self, address: Address, ram: RAM) -> float:
        """
        Accesses the value at a given address.

        Parameters:
            - address (Address): the address of the value to get
            - ram (RAM): the ram associated with this CPU instance

        Returns: (float) the value located at the given address
            returns None if no value associated with the given address
        """
        offset = int(address.get_offset(), 2)
        ix, row = self.get_block(address)
        valid, tag, block, time_in, _ = row

        # hit
        if valid and address.get_tag() == tag:
            self.read_hits += 1
            # update access time
            self.blocks[ix] = [True, tag, block, time_in, datetime.now()]
            return block.data[offset]

        # miss
        else:
            self.read_misses += 1
            # load from ram
            new_block = ram.get_block(address.get_tag(), address.get_index())
            # set block in cache
            if block:
                self.set_block(address, new_block)
                return new_block.data[offset]
        return None

    def set_val(self, address: Address, val: int, ram: RAM) -> None:
        """
        Sets the value at a given address in cache and in RAM.

        Parameters:
            - address (Address): the address of the value to set
            - value (int): the value to store
            - ram (RAM): the ram associated with this CPU instance

        Returns: nothing
        """
        offset = int(address.get_offset(), 2)
        ix, row = self.get_block(address)
        valid, tag, block, time_in, _ = row

        # hit
        if valid and address.get_tag() == tag:
            self.write_hits += 1
            # update data
            block.set_val(val, offset, address.get_tag())
            # update access time
            self.blocks[ix] = [True, tag, block, time_in, datetime.now()]
            ram.set_block(address.get_tag(), address.get_index(), block)

        # miss
        else:
            self.write_misses += 1
            block = ram.get_block(address.get_tag(), address.get_index())
            # in ram
            if block and block.tag == address.get_tag():
                block.set_val(val, offset, address.get_tag())
            # not in ram
            else:
                block = Block(self.block_size)
                block.set_val(val, offset, address.get_tag())
                ram.set_block(address.get_tag(), address.get_index(), block)
            # set new block in cache
            self.set_block(address, block)

    def get_block(self, address: Address) -> Block:
        """
        Accesses the block at a given address.

        Parameters:
            - address (Address): the address of the value to get

        Returns: (Block) the block in which the given address is located
            returns None if no block associated with the given address
        """
        index = address.get_index()
        index = 0 if not index else int(index, 2)

        # direct mapped
        if len(self.sets) == 1:
            return index, self.blocks[index]

        # associative
        start = self.sets[index]
        end = start + self.blocks_per_set
        set = self.blocks[start:end]
        matching = np.where(
            np.logical_and(set[:, 0] == True, set[:, 1] == address.get_tag())
        )
        if len(matching[0]) > 0:
            ix = matching[0][0]
            match = set[ix]
            return ix + start, match
        return None, [False, None, None, None, None]

    def set_block(self, address: Address, data: Block) -> None:
        """
        Sets the block value at a given address in cache.

        Parameters:
            - address (Address): the address of the value to get
            - data (Block): the data to set in this block

        Returns: nothing
        """
        time = datetime.now()
        tag = address.get_tag()
        index = address.get_index()
        index = 0 if not index else int(index, 2)

        # direct mapped
        if len(self.sets) == 1:
            valid, _, _, in_time, _ = self.blocks[index]
            time_in = in_time if valid else time
            self.blocks[index] = [True, tag, data, time_in, time]

        # associative
        else:
            start = self.sets[index]
            end = start + self.blocks_per_set
            set = self.blocks[start:end]
            valids = np.where(set[:, 0] == False)
            if valids[0].size > 0:
                ix = start + valids[0][0]
                self.blocks[ix] = [True, tag, data, time, time]
            else:
                self.replace(tag, index, data)

    def replace(self, tag: str, index: int, data: Block) -> None:
        """
        Replaces a block in a full set using the given strategy.

        Parameters:
            - tag (str): the tag associated with the block
            - index (int): the index associated with the block
            - data (Block): the block of memory

        Returns: nothing
        """
        start = self.sets[index]
        end = start + self.blocks_per_set

        if self.replacement == "random":
            ix = random.choice(range(start, end))

        else:
            set = self.blocks[start:end]
            if self.replacement == "LRU":
                ix = np.argmin(set[:, 4])
            elif self.replacement == "FIFO":
                ix = np.argmin(set[:, 3])

        time = datetime.now()
        self.blocks[ix] = [True, tag, data, time, time]
