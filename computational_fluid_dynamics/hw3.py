import numpy as np
import matplotlib.pyplot as plt


def init(dx):
    grid = np.linspace(0, 3, int(3 / dx) + 1, dtype=np.float64)
    grid = grid[:-1]
    return np.sin(grid * 2 * np.pi), grid


def get_right_periodic(u):
    return np.concatenate([u[1:], u[:1]])


def get_left_periodic(u):
    return np.concatenate([u[-1:], u[:-1]])


def forward_gt(grid, num_forward, dt):
    return np.sin((grid - dt * num_forward) * 2 * np.pi)


def forward(u, type, num_forward, c):
    for i in range(num_forward):
        u_prime = scheme_forward(u, type, c)
        u = u_prime
    return u


def scheme_forward(u, type, c):
    if type == 'Lax':
        u_prime = get_right_periodic(u) * (1 - c) / 2 + get_left_periodic(u) * (1 + c) / 2
    elif type == 'Lax Wendroff':
        left = get_left_periodic(u)
        right = get_right_periodic(u)
        u_prime = u - (right - left) * c / 2 + (right - u * 2 + left) * c * c / 2
    # elif type == 'two step Lax Wendroff':
    #     u_half = get_right_periodic(u) * (1 - c) / 2 + u * (1 + c) / 2
    #     u_prime = u - c * (u_half - get_left_periodic(u_half))
    # elif type == 'MacCormack':
    #     u_bar = get_right_periodic(u) * -c + u * (1 + c)
    #     u_prime = u / 2 + u_bar * (1 - c) / 2 + get_left_periodic(u_bar) * c / 2
    # elif type == 'first order upwind':
    #     u_prime = u - (u - get_left_periodic(u)) * c
    # elif type == 'second order upwind':
    #     left = get_left_periodic(u)
    #     u_prime = u - (u * 3 - left * 4 + get_left_periodic(left)) * c / 2
    else:
        assert False
    return u_prime


def draw_batch(u_list, u_gt_list, grid, num_row, num_col):
    assert len(u_list) == num_row * num_col

    def draw(u, u_gt, grid):
        plt.plot(grid, u, label='u')
        plt.plot(grid, u_gt, label='gt', linestyle='--')
        plt.legend(loc='upper left')
        return

    for i in range(num_row * num_col):
        plt.subplot(num_row, num_col, i + 1, ylim=(-2, 2))
        draw(u_list[i], u_gt_list[i], grid)
    plt.show()
    return


def l1_error(u, u_gt):
    return np.mean(np.abs(u - u_gt))


def long_term_test(type, num_rollout, num_total, dt, dx):
    u, grid = init(dx)
    c = dt / dx
    num_forward = 0
    for i in range(num_total):
        u_list, u_gt_list = [], []
        for j in range(12):
            num_forward += num_rollout
            u_prime = forward(u, type, num_rollout, c)
            u_gt = forward_gt(grid, num_forward, c)
            u_list.append(u_prime)
            u_gt_list.append(u_gt)
            u = u_prime
        draw_batch(u_list, u_gt_list, grid, 3, 4)
    return


def precision_test(type):
    dx = 1 / 1000
    num_forward = 1
    log_dx_list = np.linspace(-3.51, -0.501, 100)
    x_list, y_list = [], []
    for log_dx in log_dx_list:
        x_list.append(log_dx)
        dt = 10 ** log_dx
        c = dt / dx
        u, grid = init(dx)
        u_h = forward(u, type, num_forward, c)
        u_gt = forward_gt(grid, num_forward, dt)
        error = np.log10(l1_error(u_h, u_gt))
        y_list.append(error)
    plt.plot(x_list, y_list)
    plt.xlabel('log10(dx)')
    plt.ylabel('log10(error)')
    plt.show()


if __name__ == '__main__':
    # Lax Wendroff first second order upwind
    # long_term_test('Lax', num_rollout=100, num_total=1)
    precision_test('Lax')
