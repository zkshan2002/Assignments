import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import logging


def get_logger(logfile):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(logfile)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger


workdir = os.path.realpath('hw5')


def solve(n, dt, nu, max_iter, n_log, n_save, checkpoint=0):
    os.makedirs(workdir, exist_ok=True)
    if checkpoint != 0:
        with open(os.path.join(workdir, f'u_{checkpoint}.npy'), 'rb') as f:
            u = np.load(f)
    else:
        u = np.ones((n * 3 + 1, n * 4 + 1), dtype=np.float64) * 20
        u[-1, :] = 100
    c = nu * dt / (1 / n ** 2)
    logger = get_logger(os.path.join(workdir, 'info.log'))
    logger.info(f'Parameters: n {n}, dt {dt}, nu {nu}, iteration {max_iter}.')
    logger.info(f'By such parameters, c = {c}.')
    logger.info(f'Simulation starts.')
    for i in range(checkpoint + 1, max_iter + 1):
        delta = c * (
                u[1:-1, :-2] + u[1:-1, 2:]
                + u[:-2, 1:-1] + u[2:, 1:-1]
                - u[1:-1, 1:-1] * 4
        )
        u[1:-1, 1:-1] += delta
        if i % n_log == 0:
            msg = f'Iteration {i}. u mean {np.mean(u)}.'
            logger.info(msg)
            if i % n_save == 0:
                with open(os.path.join(workdir, f'u_{i}.npy'), 'wb') as f:
                    np.save(f, u)
    return


def plot(step):
    with open(os.path.join(workdir, f'u_{step}.npy'), 'rb') as f:
        u = np.load(f)
    plt.matshow(u)
    plt.colorbar()
    plt.show()
    return


if __name__ == '__main__':
    max_iter = 5 * 10 ** 5
    solve(n=100, dt=0.001, nu=0.01, max_iter=max_iter, n_log=10 ** 3, n_save=10 ** 4, checkpoint=max_iter)
    plot(max_iter)
