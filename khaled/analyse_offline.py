import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.interpolate import LinearNDInterpolator


def plot(path, resolution=10, x_dir=True):  # if x_dir is true, it slices the plot in the x direction

    x_global = []
    y_global = []
    z_global = []
    amp_global = []

    color_max = 0.1

    data_files = [f for f in os.listdir(path) if f.endswith('.npy')]

    for i in range(0, len(data_files)):

        data = np.load(os.path.join(path, data_files[i]))

        x_global.append(data[0])

        y_global.append(data[1])

        z_global.append(data[2])

        amp_global.append(data[3])

    x_global = np.array(x_global).flatten()
    y_global = np.array(y_global).flatten()
    z_global = np.array(z_global).flatten()
    amp_global = np.array(amp_global).flatten()

    points = np.column_stack((x_global, y_global, z_global))

    interfunc = LinearNDInterpolator(points, amp_global)

    fig = plt.figure(figsize=(17, 12))
    c = 1

    for depth in range(-79, 80, resolution):

        ax = fig.add_subplot(4, 4, c)

        if x_dir:  # cheks what direction to sclice in
            Y_l = np.arange(-80, 80, 1, dtype=int)
            Z_l = np.arange(0, 80, 1, dtype=int)

            Y1, Z1 = np.meshgrid(Y_l, Z_l, indexing='ij')

            X1 = np.full(len(Y1.flatten()), depth)

            # it interpolates in the area we are intersted in
            interpolated_values = interfunc(
                np.column_stack((X1, Y1.flatten(), Z1.flatten())))

            ax.scatter(Y1, Z1, c=interpolated_values, cmap='coolwarm',vmax = color_max)
        else:
            X_l = np.arange(-80, 80, 1, dtype=int)
            Z_l = np.arange(0, 80, 1, dtype=int)

            X1, Z1 = np.meshgrid(X_l, Z_l, indexing='ij')

            Y1 = np.full(len(X1.flatten()), depth)

            # it interpolates in the area we are intersted in
            interpolated_values = interfunc(
                np.column_stack((X1.flatten(), Y1, Z1.flatten())))

            ax.scatter(X1, Z1, c=interpolated_values, cmap='coolwarm',vmax = color_max)

        if x_dir:
            ax.set_title("X = " + str(depth) + " mm",fontsize= 10)
        else:
            ax.set_title("Y = " + str(depth) + " mm",fontsize= 10)

        # plot settings for the subplot
        print("interpolating at [mm]: ", depth, "          ", end="\r")
        ax.set_ylim(0, 80)
        ax.set_xlim(-80, 80)
        ax.set_yticks([20, 40, 60, 80])
        ax.set_xticks(np.arange(-80, 80, 20, dtype=int))
        # plt.axis('equal')
        c = c+1

    plt.tight_layout()
    plt.show()
    return


if __name__ == '__main__':

    plot('measurement_1',x_dir=True)
