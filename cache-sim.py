"""
Main module to emulate a cache and run various algorithms.
"""
from emulator.cpu import CPU
import argparse
import numpy as np


# initialize arguments to parse
parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--cachesize",
    default=65536,
    dest="cachesize",
    help="size of cache (bytes)",
    type=int,
)
parser.add_argument(
    "-b",
    "--blocksize",
    default=64,
    dest="blocksize",
    help="size of data block (bytes)",
    type=int,
)
parser.add_argument(
    "-n",
    "--nway",
    default=2,
    dest="nway",
    help="n-way associativity of cache",
    type=int,
)
parser.add_argument(
    "-r",
    "--replacement",
    default="LRU",
    dest="replacement",
    help="replacement policy: random, FIFO, or LRU",
    choices=["random", "FIFO", "LRU"],
)
parser.add_argument(
    "-a",
    "--algorithm",
    default="mxm_block",
    dest="algorithm",
    help="algorithm to run: daxpy, mxm, or mxm_block",
    choices=["daxpy", "mxm", "mxm_block"],
)
parser.add_argument(
    "-d",
    "--dimension",
    default=480,
    dest="dimension",
    help="dimension of algorithmic matrix/vector",
    type=int,
)
parser.add_argument(
    "-p",
    "--print",
    dest="print",
    help="prints the solution matrix/vector",
    action="store_true",
)
parser.add_argument(
    "-f",
    "--factor",
    default=32,
    dest="factor",
    help="blocking factor for mxm_blocked",
    type=int,
)


SIZE = 8  # bytes per word


def daxpy(cpu, p, n):
    """
    Function to run a daxpy algorithm: c = da + b.

    Paramters:
        - cpu (CPU): the CPU for this emulator run
        - p (bool): whether to print each step
        - n (int): length of array

    Returns: nothing
    """
    # create arrays
    a, b, c = create_addresses(n, False)

    # store data
    for i in range(n):
        cpu.store(a[i], i)
        cpu.store(b[i], i * 2)
        cpu.store(c[i], 0)

    # run daxpy
    r0 = np.array([3])
    r1 = np.zeros_like(a)
    r2 = np.zeros_like(b)
    for i in range(n):
        r1[i] = cpu.load(a[i])
        r2[i] = cpu.load(b[i])
    r3 = cpu.multiply(r0, r1)
    r4 = cpu.add(r3, r2)

    # store result
    for i in range(n):
        cpu.store(c[i], r4[i])

    # print array
    if p:
        c_print = np.zeros_like(c)
        for i in range(n):
            c_print[i] = cpu.load(c[i])
        print(c_print)


def mxm(cpu, p, n):
    """
    Function to run a matrix-matrix multiplication algorithm.

    Paramters:
        - cpu (CPU): the CPU for this emulator run
        - p (bool): whether to print each step
        - n (int): length of matirx

    Returns: nothing
    """
    # create matrices
    a, b, c = create_addresses(n, True)

    # store data
    val = 0
    for i in range(n):
        for j in range(n):
            cpu.store(a[i][j], val)
            cpu.store(b[i][j], 2 * val)
            cpu.store(c[i][j], 0)
            val += 1

    # run matrix multiplication
    r1 = np.zeros_like(a)
    r2 = np.zeros_like(b)
    for i in range(n):
        for j in range(n):
            r1[i][j] = cpu.load(a[i][j])
            r2[i][j] = cpu.load(b[i][j])
    r3 = cpu.matmul(r1, r2)

    for i in range(n):
        for j in range(n):
            cpu.store(c[i][j], r3[i][j])

    # print matrix
    if p:
        c_print = np.zeros_like(c)
        for i in range(n):
            for j in range(n):
                c_print[i][j] = cpu.load(c[i][j])
        print(c_print)


def mxm_block(cpu, p, n, factor):
    """
    Function to run a matrix-matrix multiplication
    algorithm with blocking and a variable blocking factor.

    Paramters:
        - cpu (CPU): the CPU for this emulator run
        - p (bool): whether to print each step
        - n (int): length of matrix
        - factor (int): blocking factor

    Returns: nothing
    """
    # create matrices
    a, b, c = create_addresses(n, True)

    # store data
    val = 0
    for i in range(n):
        for j in range(n):
            cpu.store(a[i][j], val)
            cpu.store(b[i][j], 2 * val)
            cpu.store(c[i][j], 0)
            val += 1

    # run blocked matrix multiplication
    temp = np.zeros_like(c, dtype="float64")
    for i in range(0, n, factor):
        for j in range(0, n, factor):
            for k in range(0, n, factor):
                r1 = np.zeros((factor, factor))
                r2 = np.zeros((factor, factor))
                for ii in range(factor):
                    for jj in range(factor):
                        r1[ii][jj] = cpu.load(a[i + ii][k + jj])
                        r2[ii][jj] = cpu.load(b[k + ii][j + jj])
                r3 = cpu.matmul(r1, r2)
                temp[i : i + factor, j : j + factor] = cpu.add(
                    temp[i : i + factor, j : j + factor], r3
                )

    for i in range(n):
        for j in range(n):
            cpu.store(c[i][j], temp[i][j])

    # print matrix
    if p:
        c_print = []
        for i in range(n):
            row = []
            for j in range(n):
                r4 = cpu.load(c[i][j])
                row.append(r4)
            c_print.append(row)
        print(c_print)


def create_addresses(n, matrix):
    """
    Creates the addresses for all variables.

    Parameters:
        - n (int): length of matrix/array
        - matrix (bool): True if a matrix, False if an array

    Returns: ((ndarray, ndarray, ndarry)) the address arrays or matrices
    """
    if matrix:
        a = []
        b = []
        c = []
        for i in range(n):
            a.append(list(range(i * n * SIZE, i * n * SIZE + n * SIZE, SIZE)))
        for i in range(n):
            b.append(
                list(
                    range(
                        a[-1][-1] + SIZE + i * n * SIZE,
                        a[-1][-1] + SIZE + i * n * SIZE + n * SIZE,
                        SIZE,
                    )
                )
            )
        for i in range(n):
            c.append(
                list(
                    range(
                        b[-1][-1] + SIZE + i * n * SIZE,
                        b[-1][-1] + SIZE + i * n * SIZE + n * SIZE,
                        SIZE,
                    )
                )
            )

    else:
        a = list(range(0, n * SIZE, SIZE))
        b = list(range(n * SIZE, 2 * n * SIZE, SIZE))
        c = list(range(2 * n * SIZE, 3 * n * SIZE, SIZE))

    return a, b, c


def get_inputs(args):
    """
    Determines the inputs for a given run of the emulator.

    Paramters:
        - args (ArgumentParser): the arguments passed to this module

    Returns: (dict) the inputs
    """
    inputs = {}

    inputs["Ram Size"] = SIZE * args.dimension * 3
    if "mxm" in args.algorithm:
        inputs["Ram Size"] *= args.dimension

    inputs["Cache Size"] = args.cachesize
    inputs["Block Size"] = args.blocksize
    inputs["Total Blocks in Cache"] = inputs["Cache Size"] / inputs["Block Size"]

    inputs["Associativity"] = args.nway
    inputs["Number of Sets"] = inputs["Total Blocks in Cache"] / inputs["Associativity"]

    inputs["Replacement Policy"] = args.replacement
    inputs["Algorithm"] = args.algorithm
    inputs["Matrix or Vector Dimension"] = args.dimension

    if inputs["Algorithm"] == "mxm_block":
        inputs["MXM Blocking Factor"] = args.factor

    return inputs


def print_results(inputs, cpu):
    """
    Prints the results of an emulator run.

    Parameters:
        - inputs (dict): the inputs for this emulator run
        - cpu (CPU): the CPU for this emulator run

    Returns: nothing, but prints the inputs and results
    """
    # print inputs
    print("------------------INPUTS------------------")
    for key, val in inputs.items():
        print(f"{key} = {val}")

    # print results
    print("-----------------RESULTS------------------")
    print(f"Instruction Count = {cpu.instructions}")

    print(f"Read Hits = {cpu.cache.read_hits}")
    print(f"Read Misses = {cpu.cache.read_misses}")
    total_reads = cpu.cache.read_hits + cpu.cache.read_misses
    print(f"Read Miss Rate = {round(cpu.cache.read_misses / total_reads * 100, 2)}%")

    print(f"Write Hits = {cpu.cache.write_hits}")
    print(f"Write Misses = {cpu.cache.write_misses}")
    total_writes = cpu.cache.write_hits + cpu.cache.write_misses
    print(f"Write Miss Rate = {round(cpu.cache.write_misses / total_writes * 100, 2)}%")


def main(args):
    """
    Main function to run a given function on the simulated CPU.

    Paramters:
        - args (ArgumentParser): the arguments passed to this module

    Returns: nothing, but prints the inputs and results
    """
    inputs = get_inputs(args)
    blocks_in_ram = -(inputs["Ram Size"] // -args.blocksize)
    cpu = CPU(
        args.blocksize, args.nway, args.cachesize, blocks_in_ram, args.replacement
    )

    # run algorithm
    if args.algorithm == "daxpy":
        daxpy(cpu, args.print, args.dimension)
    elif args.algorithm == "mxm":
        mxm(cpu, args.print, args.dimension)
    elif args.algorithm == "mxm_block":
        mxm_block(cpu, args.print, args.dimension, args.factor)

    print_results(inputs, cpu)


if __name__ == "__main__":
    """
    Runs the emulator.
    """
    # unpack arguments
    args = parser.parse_args()

    # enforce blocking factor if blocking
    if args.algorithm == "mxm_block" and not args.factor:
        parser.error("mxm_block algorithm requires -f (the blocking factor)")

    # run
    main(args)
