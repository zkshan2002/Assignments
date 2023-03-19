import numpy as np
import matplotlib.pyplot as plt
from typing import Callable


def d1(f, h, format):
    if format == 'forward':
        return np.concatenate([(f[1:] - f[:-1]) / h, [np.nan]])
    if format == 'backward':
        return np.concatenate([[np.nan], (f[1:] - f[:-1]) / h])
    if format == 'mid':
        return np.concatenate([[np.nan], (f[2:] - f[:-2]) / (h * 2), [np.nan]])
    assert False


def d2(f, h, format):
    if format == 'forward':
        return np.concatenate([(f[2:] - f[1:-1] * 2 + f[:-2]) / (h ** 2), [np.nan] * 2])
    if format == 'backward':
        return np.concatenate([[np.nan] * 2, (f[2:] - f[1:-1] * 2 + f[:-2]) / (h ** 2)])
    if format == 'mid':
        return np.concatenate([[np.nan], (f[2:] - f[1:-1] * 2 + f[:-2]) / (h ** 2), [np.nan]])
    assert False


def error_func(val, gt):
    mask = np.logical_not(np.isnan(val))
    return np.mean(np.abs((val[mask] - gt[mask])))


dtype_list = [np.float32, np.float64]  # np.float16,
dtype2str = ['float32', 'float64']  # 'float16',
n_list = [int(8 * (2 ** i)) for i in range(15)]
format2str = ['forward', 'backward', 'mid']

color_list = ['r', 'g', 'b']
style_list = ['--', '-']  # ':',


def evaluate(func: Callable, n, dtype, left, right):
    f, d1_gt, d2_gt = func(n, dtype, left, right)
    h = (right - left) / n
    results = np.empty((2, len(format2str)), dtype=np.float64)
    for i, format in enumerate(format2str):
        d1_val = d1(f, h, format)
        results[0, i] = error_func(d1_val, d1_gt)

        d2_val = d2(f, h, format)
        results[1, i] = error_func(d2_val, d2_gt)
    return results


def poly_func(a, b, c):
    def func(n, dtype, left, right):
        assert dtype in [np.float16, np.float32, np.float64]
        assert left < right
        x = np.linspace(left, right, n + 1, dtype=dtype)
        f = a * np.square(x) + b * x + c
        d1 = x * a * 2 + b
        d2 = np.ones_like(x) * a * 2
        return f, d1, d2

    return func


def tri_func(k1, k2):
    def func(n, dtype, left, right):
        assert dtype in [np.float16, np.float32, np.float64]
        assert left < right
        x = np.linspace(left, right, n + 1, dtype=dtype)
        f = np.sin(k1 * x) + np.cos(k2 * x)
        d1 = k1 * np.cos(k1 * x) - k2 * np.sin(k2 * x)
        d2 = -k1 ** 2 * np.sin(k1 * x) - k2 ** 2 * np.cos(k2 * x)
        return f, d1, d2

    return func


if __name__ == '__main__':

    left, right = 1, 4
    # func = poly_func(1, 2, 3)
    func = tri_func(1, 1.23)

    results = np.empty((len(dtype_list), len(n_list), 2, len(format2str)), dtype=np.float64)
    for i, dtype in enumerate(dtype_list):
        for j, n in enumerate(n_list):
            results[i, j] = evaluate(func, n, dtype, left, right)

    msg_list = []
    for i in range(len(dtype_list)):
        for j in range(len(n_list)):
            n = 8 * (2 ** j)
            msg = dtype2str[i]
            msg += f' {str(n).zfill(6)} |'
            for k in range(2):
                for l in range(len(format2str)):
                    msg += f' {results[i, j, k, l]: .4e}'
                msg += ' |'
            msg_list.append(msg)
    print('\n'.join(msg_list))

    n_curve = np.log2(np.array(n_list))
    results = np.clip(results, a_min=2 ** -20, a_max=None)
    for i in range(2):
        for j in range(len(dtype_list)):
            for k in range(len(format2str)):
                y_curve = np.log2(results[j, :, i, k])
                label = f'{format2str[k]} {dtype2str[j]}'
                plt.plot(n_curve, y_curve, label=label, color=color_list[k], linestyle=style_list[j])
        plt.xlabel('log2(n)')
        plt.ylabel('log2(E)')
        plt.title(f'd{i + 1} E-n Curve')
        plt.legend()
        plt.show()

    # file = 'hw2_results.npy'
    # with open(file, 'wb') as f:
    #     np.save(f, results)
