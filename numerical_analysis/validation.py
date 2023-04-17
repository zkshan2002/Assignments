import numpy as np


def hw4_1():
    A = np.array([
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5]
    ], dtype=np.float64)

    x = np.array([1, 1, 1]).reshape(-1, 1)
    for i in range(6):
        y = x / np.max(x)
        x = A.dot(y)
        print(f'iteration {i}, y {y.reshape(-1)}, x {x.reshape(-1)}')
    print(x / np.linalg.norm(x, ord=2))
    return


def hw4_2():
    def clear(A, i, j):
        aii, aij, ajj = A[i, i], A[i, j], A[j, j]
        theta = np.arctan(aij * 2 / (aii - ajj)) / 2
        cos = np.cos(theta)
        sin = np.sin(theta)
        Q = np.eye(A.shape[0])
        Q[i, i] = cos
        Q[j, j] = cos
        Q[i, j] = -sin
        Q[j, i] = sin
        return theta, Q

    def jacob(A, max_iter, eps):
        n = A.shape[0]
        Q = np.eye(n, dtype=np.float64)
        eig = np.zeros(n, dtype=np.float64)
        for iter in range(max_iter):
            temp = A.copy()
            temp[np.arange(n), np.arange(n)] = 0
            index = np.argmax(np.abs(temp))
            i, j = index // n, index % n
            if i > j:
                i, j = j, i
            theta, q = clear(A, i, j)
            Q = Q.dot(q)
            print(f'iteration {iter}\n{A}\npick {i},{j}, theta {theta}')
            A = q.transpose().dot(A).dot(q)
            new_eig = A[np.arange(n), np.arange(n)]
            if np.max(np.abs(new_eig - eig)) < eps:
                return new_eig, Q, iter
            eig = new_eig
        return eig, Q, max_iter

    A = np.array([
        [4, 2, 2],
        [2, 5, 1],
        [2, 1, 6]
    ])
    print(np.linalg.eig(A))
    eig, Q, iter = jacob(A.copy(), 5, 1e-9)
    print(eig, Q)
    print(Q.transpose().dot(A).dot(Q))
    return


def hw4_3():
    def householder_transform(u):
        u = u / np.linalg.norm(u, ord=2)
        return np.eye(u.shape[0]) - 2 * u.reshape(-1, 1).dot(u.reshape(1, -1))

    def householder_qr(A):
        n = A.shape[0]
        print(np.linalg.eig(A))
        H = np.eye(n, dtype=np.float64)
        for i in range(n):
            sigma = np.sign(A[i, i]) * np.linalg.norm(A[i:, i], ord=2)
            u = A[i:, i].copy()
            u[0] += sigma
            print(f'iteration {i}')
            print(sigma)
            print(u)
            h = np.eye(n, dtype=np.float64)
            h[i:, i:] = householder_transform(u)
            H = H.dot(h)
            A = h.dot(A)
            print(h)
            print(A)
        return H, A

    A = np.array([
        [-4, -3, -7],
        [2, 3, 2],
        [4, 2, 7]
    ])

    Q, R = householder_qr(A.copy())
    print(Q)
    print(R)
    print(Q.dot(R))
    return


if __name__ == '__main__':
    hw4_3()
