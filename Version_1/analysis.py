import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import hilbert
from mpl_toolkits.mplot3d import Axes3D
from progress.bar import Bar
sampleRate = 5000000 #1MS/s
carrier_freq = 34.5e3
band_low = 30e3
band_high = 40e3



def map_data(data):
    if type(data) == str:
        print("open file...")
        data = np.load(data)
    print("file opened")
    steps_plate = 37
    steps_probe = 50
    r = 40 #in mm


    aps_probe = 180/steps_probe
    aps_plate = 180/steps_plate
    #print(aps_plate, aps_probe)
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

    theta_global = np.asarray(theta_global).flatten()
    phi_global = np.asarray(phi_global).flatten()


    for a in range(0, len(theta_global)):
        x_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.cos(np.deg2rad(phi_global[a])))
        y_global.append(r*np.sin(np.deg2rad(theta_global[a]))*np.sin(np.deg2rad(phi_global[a])))
        z_global.append(r*np.cos(np.deg2rad(theta_global[a])))

    

    field_amp_global = []

    bar = Bar('Plotting electric field', max=len(data)-1,fill='#',suffix='%(percent)d%% - %(eta)ds' ' to go' )

    for positions in range(0,len(data)):
    
        pos = np.zeros([2])

        for channels in range(0, len(data[0])): #1
            fltr = filter_data(data[positions][channels])
            amp = np.mean(fltr) #avergae of hilber-tranformation
            fltr_without_edges = fltr[20000:-20000]
            #amp = np.mean(fltr_without_edges) #use this for singl coil analysis
            # plt.plot(data[positions][channels][20000:-20000])
            # plt.plot(fltr_without_edges)
            # plt.show()
            amp = np.max(fltr_without_edges)-np.min(fltr_without_edges) ##use this for the temp interference analysis
            pos[channels] = amp

        field_amp = np.sqrt(np.square(pos[0])+np.square(pos[1]))
        field_amp_global.append(field_amp)
        bar.next()
    bar.finish()

    #print(field_amp_global)
    fig=plt.figure()
    ax = plt.axes(projection='3d')
    p = ax.scatter3D(x_global[:len(data)], y_global[:len(data)], z_global[:len(data)], c=field_amp_global, cmap='coolwarm');
    fig.colorbar(p)

    return fig

  

def filter_data(sample):
    #sample = data[0][0]
    #times = np.arange(len(sample))/sampleRate
    b, a = signal.butter(3, [band_low/(sampleRate/2), band_high/(sampleRate/2)], 'band') #carrier frequency at 0.069
    filteredBandPass = signal.filtfilt(b, a, sample)
    #return filteredBandPass
    hilbert_transformed = np.abs(hilbert(filteredBandPass))

    c,d = signal.butter(3,[200/(sampleRate/2)],'low')
    hilbert_transformed_2 = signal.filtfilt(c,d,hilbert_transformed)

    return  np.asarray(hilbert_transformed_2)

# fig = map_data("13_21_05.npy")
# plt.show()
