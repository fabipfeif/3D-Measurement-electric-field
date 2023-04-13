import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import hilbert
from mpl_toolkits.mplot3d import Axes3D
from progress.bar import Bar
import itertools
sampleRate = 1000000 #1MS/s



def map_data(data):
    print("open file...")
    data = np.load(data)
    print("file opened")
    steps_plate = 37
    steps_probe = 50
    r = 40 #in mm

    aps_probe = 180/steps_probe
    aps_plate = 180/steps_plate
    phi = []
    theta = []

    phi_global = []
    theta_global = []

    theta = np.linspace(90,-90,steps_probe)
    for j in range(0, steps_plate):
        for o in range(steps_probe):
            phi.append(90-j*aps_plate)

    phi_global = phi

    for x in range(0, steps_plate):
        if x%2 ==0:
            theta_global.append(theta)
        else:
            theta_global.append(theta[::-1])

    theta_global = np.asarray(theta_global).flatten()  # arrays with the angles of each point
    phi_global = np.asarray(phi_global).flatten()

########################################### get cartersian coordinates####################
    x_global = []
    y_global = []
    z_global = []

    for a in range(0, len(theta_global)):
        x_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.cos(np.deg2rad(phi_global[a])))
        y_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.sin(np.deg2rad(phi_global[a])))
        z_global.append(r*np.cos(np.deg2rad(theta_global[a])))

#########################################################################################

    #here is where the reading from the numpy file starts  
    #amplitudes_cartesian = np.zeros(len(data),1,3)

    #amplitudes = np.zeros([len(data)],dtype=object)

    field_amp_global_x = []
    field_amp_global_y = []
    field_amp_global_z = []
    field_amp_global = []

    bar = Bar('Plotting electric field', max=len(data)-1,fill='#',suffix='%(percent)d%% - %(eta)ds' ' to go' )

    for positions in range(0,len(data)):
    
        phi_pos = phi_global[positions]
        theta_pos = theta_global[positions]

        rotation_matrix =np.array([[np.sin(theta_pos)*np.cos(phi_pos), np.cos(theta_pos)*np.cos(phi_pos), -np.sin(phi_pos)],
                                  [np.sin(theta_pos)*np.sin(phi_pos), np.cos(theta_pos)*np.sin(phi_pos), np.cos(phi_pos)],
                                  [np.cos(theta_pos), -np.sin(theta_pos), 0]])
        
        efield_spherical = np.array([np.zeros_like(data[positions][1]),data[positions][1],data[positions][0]])
        rotation_matrix = np.eye(3)
        efield_cartesian = np.matmul(rotation_matrix,efield_spherical)

        efield_cartesian_max_x = np.mean(filter_data(efield_cartesian[0]))
        efield_cartesian_max_y = np.mean(filter_data(efield_cartesian[1]))
        efield_cartesian_max_z = np.mean(filter_data(efield_cartesian[2]))

        field_amp_global_x.append(efield_cartesian_max_x)
        field_amp_global_y.append(efield_cartesian_max_y)
        field_amp_global_z.append(efield_cartesian_max_z)

        field_amp_global.append(np.sqrt(np.square(efield_cartesian_max_x)+np.square(efield_cartesian_max_y)+np.square(efield_cartesian_max_z)))


        bar.next()
    bar.finish()


    fig_1=plt.figure("x-direction")
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global, y_global, z_global, c=field_amp_global_x, cmap='coolwarm');
    fig_1.colorbar(p)

    fig_2=plt.figure("y-direction")
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global, y_global, z_global, c=field_amp_global_y, cmap='coolwarm');
    fig_2.colorbar(p)

    fig_3=plt.figure("z-direction")
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global, y_global, z_global, c=field_amp_global_z, cmap='coolwarm');
    fig_3.colorbar(p)

    fig_4=plt.figure("scalar of all vectors")
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global, y_global, z_global, c=field_amp_global, cmap='coolwarm');
    fig_4.colorbar(p)

    plt.show()

                
    

        


def filter_data(sample):
    #sample = data[0][0]
    #times = np.arange(len(sample))/sampleRate
    b, a = signal.butter(3, [.065, .073], 'band') #carrier frequency at 0.069
    filteredBandPass = signal.filtfilt(b, a, sample)
    hilbert_transformed = hilbert(filteredBandPass)

    return  np.asarray(np.abs(hilbert_transformed))

map_data("12_33_44.npy")