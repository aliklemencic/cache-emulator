# Cache Emulator

A CPU emulator capable of modelling a simplified memory hierarch.

## Overview

This application is a toy implementation of a CPU built in Python, specifically utilizing Numpy. The application assumes physical memory addressing, a single-level cache, and enough RAM to store all required data in memory. The cache simulates several block placement and replacement strategies depending on user inputs while emulator measures events such as cache hits and misses and prints the final totals for the user. 

The emulator was designed to provide performance predictions for running simple algorithms with different cache configurations.

This project was completed in May 2023 as a midterm project for the MPCS 52018 Advanced Computer Architecture class at the University of Chicago.

## Project Structure

```
.
├── emulator
    ├── address.py: class representing a 32-bit address 
    ├── block.py: class representing a block of memory
    ├── cache.py: class representing the cache
    ├── cpu.py: class representing the cpu
    └── ram.py: class representing the RAM
└── cache-sim.py: emulates the cache and runs various algorithms
```

## Running the Emulator

### Setup

This application assumes Python version 3.9.12 but should be able to run on slightly older versions. To prepare to run this emulator, run the setup.sh shell script. This will create a new virtual environment using Python's venv module and download the required packages listed in requirements.txt.

### Simulation

Once the setup is complete, the emulator can be run using various command line arguments to tailor the cache to specific needs. Possible arguments include:

- `-c`: size of the cache in bytes
    - default: 65,536
- `-b`: size of a data block in bytes
    - default: 64
- `-n`: n-way associativity of the cache
    - -n 1 is a direct-mapped cache
    - default: 2
- `-r`: replacement policy
    - valid options: random, FIFO, LRU
    - default: LRU
- `-a`: algorithm to simulate
    - valid options: daxpy (daxpy product), mxm (matrix-matrix multiplication), mxm_block (mxm with blocking)
    - default: mxm_block
- `-d`: dimension of the algorithmic matrix (or vector) operation
    - -d 100 would result in a 100 × 100 matrix-matrix multiplication or 100 x 1 daxpy product
    - default: 480
- `-p`: enables printing of the resulting solution matrix product or daxpy vector after the emulation is complete
    - if flag is not included, the solution is not printed
- `-f`: blocking factor for use with the blocked matrix multiplication algorithm
    - must me included if running the mxm_block algorithm
    - default: 32

### Example Run

```
python3 cache-sim.py -a mxm_blocked -d 400 -n 16 -f 8
```
