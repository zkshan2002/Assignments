import numpy as np
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt
import open3d as o3d

bias = -0.2


def wing_func(x: np.array):
    result = np.zeros_like(x)
    mask = np.logical_and((x > 0 + bias), (x < 1 + bias))
    for k, exp in zip([0.2969, -0.126, -0.3516, 0.2843, -0.1015], [0.5, 1.0, 2, 3, 4]):
        result[mask] += k * np.power(x[mask] - bias, exp)
    return result * 0.6


def cartesian2polar(x: np.array, y: np.array):
    rou = np.sqrt(np.square(x) + np.square(y))
    theta = np.arctan2(y, x)
    theta[theta < 0] += np.pi * 2
    return rou, theta


def polar2cartesian(rou: np.array, theta: np.array):
    x = rou * np.cos(theta)
    y = rou * np.sin(theta)
    return x, y


def sqrt_transform(x: np.array, y: np.array):
    rou, theta = cartesian2polar(x, y)
    rou = np.sqrt(rou)
    theta = theta / 2
    x, y = polar2cartesian(rou, theta)
    return x, y


def inverse_sqrt_transform(x: np.array, y: np.array):
    rou, theta = cartesian2polar(x, y)
    rou = np.square(rou)
    theta = theta * 2
    x, y = polar2cartesian(rou, theta)
    return x, y


def main():
    # sample points from original frame
    x = np.linspace(bias, 1.2 + bias, 100000)
    y = wing_func(x)

    # transform the sampled points to sqrt frame
    x_prime, y_prime = sqrt_transform(x, y)

    # obtain points on transformed curve by interpolation
    lerp_result = splrep(x_prime, y_prime)
    x_grid = np.linspace(0, 1, 1000)
    y_grid = splev(x_grid, lerp_result)

    x_grid = np.concatenate([-x_grid[-1:0:-1], x_grid])
    y_grid = np.concatenate([y_grid[-1:0:-1], y_grid])
    num_points = x_grid.shape[0]
    y_1 = np.ones(num_points) * 0.5

    x_curve, y_curve = inverse_sqrt_transform(x_grid, y_grid)
    x_1, y_1 = inverse_sqrt_transform(x_grid, y_1)

    # plt.plot(x_curve, y_curve)
    # plt.plot(x_1, y_1)
    # plt.show()

    x = np.concatenate([x_curve, x_1]).reshape(-1, 1)
    y = np.concatenate([y_curve, y_1]).reshape(-1, 1)
    z = np.zeros_like(x)
    vertices = np.concatenate([x, y, z], axis=-1)
    # quad
    # 5 6 7 8 9
    # 0 1 2 3 4
    # 0 1 6 5
    # 1 2 7 6
    # 2 3 8 7
    # 3 4 9 8
    # faces = np.empty((num_points - 1, 4))
    # faces[:] = np.arange(num_points - 1).reshape(-1, 1)
    # faces[:, 1] += 1
    # faces[:, 2] += num_points + 1
    # faces[:, 3] += num_points

    # tri
    # 5 6 7 8 9
    # 0 1 2 3 4

    # 0 1 5 5 1 6
    # 1 2 6 6 2 7
    # 2 3 7 7 3 8
    # 3 4 8 8 4 9
    faces = np.empty(((num_points - 1) * 2, 3))
    faces[:num_points - 1] = np.arange(num_points - 1).reshape(-1, 1)
    faces[:num_points - 1, 1] += 1
    faces[:num_points - 1, 2] += num_points
    faces[num_points - 1:] = np.arange(num_points - 1).reshape(-1, 1)
    faces[num_points - 1:, 0] += num_points
    faces[num_points - 1:, 1] += 1
    faces[num_points - 1:, 2] += num_points + 1

    mesh = o3d.geometry.TriangleMesh(vertices=o3d.utility.Vector3dVector(vertices), triangles=o3d.utility.Vector3iVector(faces))
    mesh.compute_triangle_normals()
    o3d.visualization.draw_geometries([mesh])


if __name__ == '__main__':
    main()