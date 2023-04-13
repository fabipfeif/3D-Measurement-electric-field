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

    x_global = []
    y_global = []
    z_global = []

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


    for a in range(0, len(theta_global)):
        x_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.cos(np.deg2rad(phi_global[a])))
        y_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.sin(np.deg2rad(phi_global[a])))
        z_global.append(r*np.cos(np.deg2rad(theta_global[a])))

    
        
    #######################################

    #here is where the reading from the numpy file starts  

    field_amp_global = []
    efield_spherical = []

    bar = Bar('Plotting electric field', max=len(data)-1,fill='#',suffix='%(percent)d%% - %(eta)ds' ' to go' )

    for positions in range(0,len(data)):
    
        pos = np.zeros([2])

        for channels in range(0, len(data[1])):
            fltr = filter_data(data[positions][channels])
            amp = np.average(fltr) #avergae of hilber-tranformation
            pos[channels] = amp

        efield_spherical.append(pos)

        #field_amp = np.sqrt(np.square(pos[0])+np.square(pos[1]))
        field_amp = pos[1]
        field_amp_global.append(field_amp)
        bar.next()
    bar.finish()

    ### calculating the rotated vectors ###
    
    u_global = []
    v_global = []
    w_global = []


    theta_hat = np.array([0,1,0])
    phi_hat = np.array([0,0,1])

    for i in range(0, len(phi_global)):
        phi = np.deg2rad(phi_global[i]) #plate rotation angle
        theta = np.deg2rad(theta_global[i]) #probe rotation angle
        
        rotation_matrix =np.array([[np.sin(theta)*np.cos(phi), np.cos(theta)*np.cos(phi), -np.sin(phi)],
                                  [np.sin(theta)*np.sin(phi), np.cos(theta)*np.sin(phi), np.cos(phi)],
                                  [np.cos(theta), -np.sin(theta), 0]])
        
        efield_spherical_vec = np.array([0, efield_spherical[i][1], efield_spherical[i][0]])

        proj_vec = np.matmul(rotation_matrix, efield_spherical_vec)

        u_global.append(proj_vec[0])
        v_global.append(proj_vec[1])
        w_global.append(proj_vec[2])


    #plot the stupid thing

    fig=plt.figure()
    plt.axes(projection='3d')

    NUM = len(x_global)//2
    SCALE=3

    # mapped_color = [255/max(field_amp_global)* field_amp_global[i] for i in range(0, len(field_amp_global))]

    plt.quiver(x_global[0:NUM], y_global[0:NUM], z_global[0:NUM], u_global[0:NUM], v_global[0:NUM], w_global[0:NUM], length=SCALE)
    plt.xlim([-40,40])
    plt.xlabel('x')
    plt.ylabel('y')

    plt.show()


def filter_data(sample):
    #sample = data[0][0]
    #times = np.arange(len(sample))/sampleRate
    b, a = signal.butter(3, [.065, .073], 'band') #carrier frequency at 0.069
    filteredBandPass = signal.filtfilt(b, a, sample)
    hilbert_transformed = hilbert(filteredBandPass)


    return  np.asarray(np.abs(hilbert_transformed))

map_data("16_06_17.npy")