import numpy as np
import matplotlib.pyplot as plt


def u_gt(x):
    return np.sin(x) / np.sin(1) - x


def evaluate(u_hat, n=10000, verbose=True):
    x = np.linspace(0, 1, n + 1)
    dif = u_hat(x) - u_gt(x)
    l1_error = np.mean(np.abs(dif))
    if verbose:
        print(f'{l1_error: .8e}')
    return l1_error


def main_compare():
    def u_hat_curry(a_1, a_2):
        def u_hat(x):
            return x * (1 - x) * (a_1 + a_2 * x)

        return u_hat

    # 1 配置法
    u_hat = u_hat_curry(81 / 416, 9 / 52)
    evaluate(u_hat)
    # 2 子区域法
    u_hat = u_hat_curry(97 / 517, 24 / 141)
    evaluate(u_hat)
    # 3 最小二乘法
    u_hat = u_hat_curry(46161 / 246137, 413 / 2437)
    evaluate(u_hat)
    # 4 矩法
    u_hat = u_hat_curry(122 / 649, 10 / 59)
    evaluate(u_hat)
    # 5 Galerkin法
    u_hat = u_hat_curry(71 / 369, 7 / 41)
    evaluate(u_hat)
    return


f = np.array([0, -1])


def poly_prod(p1, p2):
    l = p1.shape[0], p2.shape[0]
    p = np.zeros(l[0] + l[1] - 1)
    for i, a in enumerate(p1):
        for j, b in enumerate(p2):
            p[i + j] += a * b
    return p


def poly_int(p):
    res = 0
    for i, a in enumerate(p):
        res += p[i] / (i + 1)
    return res


def poly_add(p1, p2):
    l1, l2 = p1.shape[0], p2.shape[0]
    p = np.zeros(max(l1, l2))
    p[:l1] += p1
    p[:l2] += p2
    return p


def poly_d2(p):
    res = np.zeros(p.shape[0] - 2)
    for i, a in enumerate(p[2:]):
        res[i] = a * (i + 2) * (i + 1)
    return res


def phi(i):
    p = [0] * i
    p.extend([1, -1])
    return np.array(p)


def l_phi(i):
    phi_i = phi(i)
    return poly_add(poly_d2(phi_i), phi_i)


def u_hat_n(a):
    res = np.array([])
    for i in range(a.shape[0]):
        res = poly_add(res, a[i] * phi(i + 1))
    return res


def galerkin(n):
    A = np.zeros((n, n))
    b = np.zeros(n)
    for i in range(n):
        phi_i = phi(i + 1)
        for j in range(n):
            A[i, j] = poly_int(poly_prod(phi_i, l_phi(j + 1)))
        b[i] = poly_int(poly_prod(f, phi_i))
    a = np.linalg.inv(A).dot(b)
    u_hat = u_hat_n(a)

    def u_hat_func(x):
        res = 0
        x_pow = 1
        for a in u_hat:
            res += a * x_pow
            x_pow *= x
        return res

    return u_hat_func


def main_galerkin():
    x_list = []
    y_list = []
    for n in range(1, 11):
        u_hat = galerkin(n)
        error = evaluate(u_hat, verbose=False)
        x_list.append(n)
        y_list.append(error)
    x = np.array(x_list)
    y = np.array(y_list)
    plt.plot(x, np.log10(y))
    plt.xlabel("n")
    plt.ylabel("log_10(l1_error)")
    plt.show()
    return


def check_min_squares():
    A = np.zeros((2, 2))
    A[0, 0] = poly_int(poly_prod(l_phi(1), l_phi(1)))
    A[0, 1] = poly_int(poly_prod(l_phi(1), l_phi(2)))
    A[1, 0] = poly_int(poly_prod(l_phi(1), l_phi(2)))
    A[1, 1] = poly_int(poly_prod(l_phi(2), l_phi(2)))
    b = np.zeros(2)
    b[0] = poly_int(poly_prod(f, l_phi(1)))
    b[1] = poly_int(poly_prod(f, l_phi(2)))
    print(np.linalg.inv(A).dot(b))
    print(46161 / 246137, 413 / 2437)
    return


if __name__ == '__main__':
    main_galerkin()
