import numpy as np
import matplotlib.pyplot as plt


def init():
    grid = np.linspace(0, 3, int(3 / dx) + 1, dtype=np.float64)
    grid = grid[:-1]
    return np.sin(grid * 2 * np.pi), grid


def get_right_periodic(u):
    return np.concatenate([u[1:], u[:1]])


def get_left_periodic(u):
    return np.concatenate([u[-1:], u[:-1]])


def forward_gt(grid, num_forward):
    return np.sin((grid - dt * num_forward) * 2 * np.pi)


def forward(u, type, num_forward):
    for i in range(num_forward):
        u_prime = scheme_forward(u, type)
        u = u_prime
    return u


def scheme_forward(u, type):
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


def draw_batch(u_list, u_gt_list, grid, num_x, num_y):
    assert len(u_list) == num_x * num_y

    def draw(u, u_gt, grid):
        plt.plot(grid, u, label='u')
        plt.plot(grid, u_gt, label='gt', linestyle='--')
        plt.legend(loc='upper left')
        return

    for i in range(num_x * num_y):
        plt.subplot(num_x, num_y, i + 1, ylim=(-2, 2))
        draw(u_list[i], u_gt_list[i], grid)
    plt.show()
    return


def l1_error(u, u_gt):
    return np.mean(np.abs(u - u_gt))


dx = 1 / 100
dt = 1 / 100
c = dt / dx


def precision_test(type):
    u, grid = init()
    num_forward = 1
    u_h = forward(u, type, num_forward)
    u_gt = forward_gt(grid, num_forward)
    print(f'{l1_error(u_h, u_gt):.4e}')
    # draw_batch([u_h], [u_gt], grid, 1, 1)
    return


def long_term_test(type, num_rollout, num_total):
    u, grid = init()
    num_forward = 0
    for i in range(num_total):
        u_list, u_gt_list = [], []
        for j in range(12):
            num_forward += num_rollout
            u_prime = forward(u, type, num_rollout)
            u_gt = forward_gt(grid, num_forward)
            u_list.append(u_prime)
            u_gt_list.append(u_gt)
            u = u_prime
        draw_batch(u_list, u_gt_list, grid, 3, 4)
    return


if __name__ == '__main__':
    # Lax Wendroff first second order upwind
    # long_term_test('first order upwind', num_rollout=10000, num_total=1)
    precision_test('Lax')
