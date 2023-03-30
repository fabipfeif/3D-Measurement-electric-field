import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import hilbert
from mpl_toolkits.mplot3d import Axes3D
from progress.bar import Bar
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
    print(aps_plate, aps_probe)
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

    ### calculating the rotated vectors ###
    field_vecs_global = np.zeros([2]) #create empty array with dimension 2
    initial_vector = np.array([1,1,0])

    for i in range(0, len(phi_global)): # first turn every vector around x axis, then around z
        phi = np.deg2rad(phi_global[i])
        theta = np.deg2rad(theta_global[i])
        
        turn_x = np.array([[1, 0, 0],
                          [0, np.cos(phi), -np.sin(phi)],
                          [0, np.sin(phi), np.cos(phi)]]) 

        turn_z = np.array([[np.cos(theta), -np.sin(theta), 0],
                          [np.sin(theta), np.cos(theta), 0],
                          [0, 0, 1]]) 
        
        turned_vector =  np.matmul(initial_vector, turn_x)
        turned_vector =  np.matmul(turned_vector, turn_z)

        np.concatenate(field_vecs_global,initial_vector)
    #######################################

    #here is where the reading from the numpy file starts  

    field_amp_global = []

    bar = Bar('Plotting electric field', max=len(data)-1,fill='#',suffix='%(percent)d%% - %(eta)ds' ' to go' )

    for positions in range(0,len(data)):
    
        pos = np.zeros([2])

        for channels in range(0, len(data[1])):
            fltr = filter_data(data[positions][channels])
            amp = np.average(fltr) #avergae of hilber-tranformation
            pos[channels] = amp

        field_amp = np.sqrt(np.square(pos[0])+np.square(pos[1]))
        field_amp_global.append(field_amp)
        bar.next()
    bar.finish()

    fig=plt.figure()
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global, y_global, z_global, c=field_amp_global, cmap='coolwarm');
    fig.colorbar(p)

    plt.show()


def filter_data(sample):
    #sample = data[0][0]
    #times = np.arange(len(sample))/sampleRate
    b, a = signal.butter(3, [.065, .073], 'band') #carrier frequency at 0.069
    filteredBandPass = signal.filtfilt(b, a, sample)
    hilbert_transformed = hilbert(filteredBandPass)


    return  np.asarray(np.abs(hilbert_transformed))

map_data("16_06_17.npy")