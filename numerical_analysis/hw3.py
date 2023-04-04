import sys
import os.path as osp
import numpy as np
from typing import List, Callable, Tuple, Optional


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
        return A, b
    except:
        raise IOError("error while parsing file")


def update_i(A, b, lhs, L, U, i):
    lhs[i] = (b[i] - np.sum(A[i, :i] * L[:i]) - np.sum(A[i, i + 1:] * U[i + 1:])) / A[i, i]
    return


def jacobi_iteration(A, b, eps, max_iter):
    n = b.shape[0]
    x = np.zeros_like(b)
    for iter in range(max_iter):
        prev_x = x.copy()
        for i in range(n):
            update_i(A, b, x, prev_x, prev_x, i)
        if np.linalg.norm(x - prev_x, ord=2) < eps:
            return x, iter + 1
    return x, None


def gaussian_seidal_iteration(A, b, eps, max_iter):
    n = b.shape[0]
    x = np.zeros_like(b)
    for iter in range(max_iter):
        prev_x = x.copy()
        for i in range(n):
            update_i(A, b, x, x, prev_x, i)
        if np.linalg.norm(x - prev_x, ord=2) < eps:
            return x, iter + 1
    return x, None


def new_iteration(A, b, eps, max_iter):
    n = b.shape[0]
    x = np.zeros_like(b)
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


def fastest_descent(A, b, eps, max_iter):
    x = np.zeros_like(b)
    for iter in range(max_iter):
        r = b - A.dot(x)
        alpha = r.dot(r) / (A.dot(r)).dot(r)
        x += alpha * r
        if np.linalg.norm(alpha * r, ord=2) < eps:
            return x, iter
    return x, None


def conjugate_gradient(A, b, eps, max_iter):
    x = np.zeros_like(b)
    r = b - A.dot(x)
    d = r.copy()
    for iter in range(max_iter):
        A_dot_d = A.dot(d)
        alpha = r.dot(d) / A_dot_d.dot(d)
        x += alpha * d
        if np.linalg.norm(alpha * d, ord=2) < eps:
            return x, iter
        r -= alpha * A_dot_d
        beta = -(A.dot(r)).dot(d) / A_dot_d.dot(d)
        d = r - beta * d
    return x, None


def evaluate(
        func: Callable[[np.array, np.array, float, int], Tuple[np.array, Optional[int]]],
        A, b, eps=1e-9, max_iter=100
):
    def vec2str(x):
        str_list = []
        for val in x:
            str_list.append(f'{val:.8e}')
        return ' '.join(str_list)

    x, iter = func(A, b, eps, max_iter)
    print(iter)
    print(vec2str(x))
    return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise AssertionError('Usage: one argument specifies path to input file')
    file = sys.argv[1]
    if not osp.exists(file):
        raise FileNotFoundError(osp.abspath(file))
    with open(file, 'r') as f:
        lines = f.readlines()

    args = parse_input(lines)
    evaluate(jacobi_iteration, *args)
    evaluate(gaussian_seidal_iteration, *args)
    evaluate(new_iteration, *args)
    evaluate(fastest_descent, *args)
    evaluate(conjugate_gradient, *args)
