import sys
import os.path as osp
import numpy as np
from typing import List


def parse_input(lines: List[str]):
    try:
        num_list = lines[0].split(',')
        n = int(num_list[0])
        lam = float(num_list[1])

        S = np.empty((n, n), dtype=np.float64)
        T = np.empty((n, n), dtype=np.float64)
        b = np.empty((n,), dtype=np.float64)

        def parse_line(line: str):
            return [float(num_str) for num_str in line.strip().split(' ') if num_str != '']

        for i in range(n):
            S[i] = parse_line(lines[i + 1])
            T[i] = parse_line(lines[i + 1 + n])
        b[:] = parse_line(lines[n * 2 + 1])
        assert len(lines) == n * 2 + 2
        return n, lam, S, T, b
    except:
        raise IOError("error while parsing file")


def solve(n, lam, S, T, b):
    x = np.empty((n,), dtype=np.float64)
    t_tilde = np.zeros((n,), dtype=np.float64)
    for i in reversed(range(n)):
        x[i] = (b[i] - np.sum(S[i, i:] * t_tilde[i:])) / (S[i, i] * T[i, i] - lam)
        t_tilde += T[:, i] * x[i]
    return x


def vec2str(x):
    str_list = []
    for val in x:
        str_list.append(f'{val:.9E}')
    return ' '.join(str_list)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise AssertionError('Usage: one argument specifies path to input file')
    file = sys.argv[1]
    if not osp.exists(file):
        raise FileNotFoundError(osp.abspath(file))
    with open(file, 'r') as f:
        lines = f.readlines()

    args = parse_input(lines)
    res = solve(*args)
    print(vec2str(res))
