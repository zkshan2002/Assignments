import sys
import os.path as osp
import numpy as np
from typing import List


def parse_input(lines: List[str]):
    try:
        n = int(lines[0])
        A = np.empty((n, n), dtype=np.float64)
        b = np.empty((n,), dtype=np.float64)

        def parse_line(line: str):
            return [float(num_str) for num_str in line.strip().split(' ') if num_str != '']

        for i in range(n):
            A[i] = parse_line(lines[i + 1])
        b[:] = parse_line(lines[n + 1])
        assert len(lines) == n + 2
        return n, A, b
    except:
        raise IOError("error while parsing file")


def update_i(A, b, lhs, L, U, i):
    lhs[i] = (b[i] - np.sum(A[i, :i] * L[:i]) - np.sum(A[i, i + 1:] * U[i + 1:])) / A[i, i]
    return


def gaussian_seidal_iteration(n, A, b, eps, max_iter):
    x = np.zeros((n,), dtype=np.float64)
    for iter in range(max_iter):
        prev_x = x.copy()
        for i in range(n):
            update_i(A, b, x, x, prev_x, i)
        if np.linalg.norm(x - prev_x, ord=2) < eps:
            return x, iter + 1
    return x, None


def new_iteration(n, A, b, eps, max_iter):
    x = np.zeros((n,), dtype=np.float64)
    for iter in range(max_iter):
        prev_x = x.copy()
        x_tilde = np.empty_like(x)
        for i in range(n):
            update_i(A, b, x_tilde, x_tilde, prev_x, i)
        for i in reversed(range(n)):
            update_i(A, b, x, x_tilde, x, i)
        if np.linalg.norm(x - prev_x, ord=2) < eps:
            return x, iter + 1
    return x, None


def vec2str(x):
    str_list = []
    for val in x:
        str_list.append(f'{val:.8e}')
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
    x, iter = gaussian_seidal_iteration(eps=1e-9, max_iter=100, *args)
    print(iter)
    print(vec2str(x))
    x, iter = new_iteration(eps=1e-9, max_iter=100, *args)
    print(iter)
    print(vec2str(x))
