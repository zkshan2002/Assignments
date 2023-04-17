import sys
import os.path as osp
import numpy as np
from typing import List


def parse_input(lines: List[str]):
    try:
        n = int(lines[0])
        c = np.empty((n,), dtype=np.float64)

        def parse_line(line: str):
            return [float(num_str) for num_str in line.strip().split(' ') if num_str != '']

        c[:] = parse_line(lines[1])
        assert len(lines) == 2
        return c
    except:
        raise IOError("error while parsing file")


def primary_eigen(c, eps):
    n = c.shape[0]
    A = np.zeros((n, n), dtype=np.float64)
    A[0] = -c
    A[1:, :-1] = np.eye(n - 1)

    x = np.random.randn(n)
    lam = 0
    for i in range(10000):
        y = x / np.max(x)
        x = A.dot(y)
        new_lam = np.max(np.abs(x))
        if np.abs(new_lam - lam) < eps:
            return new_lam
        lam = new_lam
    return lam


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise AssertionError('Usage: one argument specifies path to input file')
    file = sys.argv[1]
    if not osp.exists(file):
        raise FileNotFoundError(osp.abspath(file))
    with open(file, 'r') as f:
        lines = f.readlines()

    c = parse_input(lines)
    lam = primary_eigen(c, eps=1e-20)
    print(f'{lam:.8e}')
