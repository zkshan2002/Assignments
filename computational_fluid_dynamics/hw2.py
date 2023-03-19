import numpy as np
import matplotlib.pyplot as plt


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


def func2(n, k1, k2, dtype):
    assert dtype in [np.float32, np.float64]
    x = np.linspace(0, 1, n + 1, dtype=dtype)
    f = np.sin(k1 * x) + np.cos(k2 * x)
    d1 = k1 * np.cos(k1 * x) - k2 * np.sin(k2 * x)
    d2 = -k1 ** 2 * np.sin(k1 * x) - k2 ** 2 * np.cos(k2 * x)
    return f, d1, d2


def func(n, k1, k2, dtype):
    assert dtype in [np.float32, np.float64]
    x = np.linspace(0, 1, n + 1, dtype=dtype)
    f = np.square(x) + x + 1
    d1 = x * 2 + 1
    d2 = np.ones_like(x) * 2
    return f, d1, d2

dtype_list = [np.float32, np.float64]
dtype2str = ['float32', 'float64']
n_list = [(int)(8 * (2 ** (i / 10.0))) for i in range(15 * 10)]
format2str = ['forward', 'backward', 'mid']


def evaluate(n, k1, k2, dtype):
    f, d1_gt, d2_gt = func(n, k1, k2, dtype)
    results = np.empty((2, len(format2str)), dtype=np.float64)
    for i, format in enumerate(format2str):
        d1_val = d1(f, 1 / n, format)
        results[0, i] = error_func(d1_val, d1_gt)

        d2_val = d2(f, 1 / n, format)
        results[1, i] = error_func(d2_val, d2_gt)
    return results


if __name__ == '__main__':
    k1, k2 = 1, 2
    results = np.empty((len(dtype_list), len(n_list), 2, len(format2str)), dtype=np.float64)
    for i, dtype in enumerate(dtype_list):
        for j, n in enumerate(n_list):
            results[i, j] = evaluate(n, k1, k2, dtype)

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
    # print('\n'.join(msg_list))

    n_curve = np.log2(np.array(n_list))
    for i in range(2):
        for j in range(len(dtype_list)):
            for k in range(len(format2str)):
                y_curve = np.log2(results[j, :, i, k])
                label = f'{format2str[k]} {dtype2str[j]}'
                plt.plot(n_curve, y_curve, label=label)
        plt.xlabel('log2(n)')
        plt.ylabel('log2(E)')
        plt.title(f'd{i + 1} E-n Curve')
        plt.legend()
        plt.show()

    file = 'hw2_results.npy'
    with open(file, 'wb') as f:
        np.save(f, results)
