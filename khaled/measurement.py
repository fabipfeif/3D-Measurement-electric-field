import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from scipy import signal
import time
from datetime import datetime

from stepper_controller import StepperController
from oscilloscope_controller import OscilloscopeController
from analyse_offline import load

# if true, the extend of modulation will be measured (max-min of signal envelope),
# otherwise, only the signal amplitude is measured
radius = 40 #mm

signal_modulated = True
simulation = False

carrier_frequency = 34.6e3  # Hz
envelope_filter_cutoff = 200  # Hz

# band frequencies = carrier_filter_bands * carrier_frequency
carrier_filter_bands = [0.9, 1.1]
carrier_filter_order = 3
envelope_filter_order = 3
edge_length = 0.05  # edge_length*acquisition_num_samples samples are removed from both edges of the signal after hilbert transform

acquisition_time = 0.02  # seconds
acquisition_num_samples = 100000

stepper_controller_port = 'COM11'
osc_resource_string = 'USB0::0x0AAD::0x01D6::201033::INSTR'

steppers = StepperController(
    stepper_controller_port, verbose=True, simulation=simulation)
oscilloscope = OscilloscopeController(
    osc_resource_string, 0.1, acquisition_num_samples, acquisition_time, simulation=simulation)
sampling_rate = oscilloscope.sampling_rate

# initialize filters
carrier_filter = signal.butter(3, np.array(
    carrier_filter_bands) * carrier_frequency / (sampling_rate/2), 'band')
envelope_filter = signal.butter(
    3, [envelope_filter_cutoff / (sampling_rate/2)], 'low')

#####

if __name__ == '__main__':

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    sc = ax.scatter([], [], [])  # , c=field_amp_global, cmap='coolwarm')

    color_converter = cm.ScalarMappable(
        norm=mpl.colors.Normalize(vmin=0, vmax=0.1 * (radius/80)), cmap=cm.coolwarm)

    ax.set_xlim([-radius-10, radius+10])
    ax.set_ylim([-radius-10, radius+10])
    ax.set_zlim([0, radius+10])

    delay = 0.1

    x_global = []

    y_global = []

    z_global = []

    amp_global = []

    for i in range(steppers.plate_num_steps):

        for j in range(steppers.probe_num_steps):
            if not( i == 0 and j == 0):

                if j == 0 and i != 0:
                    steppers.rotate_plate_clkwise()
                

                elif i % 2 == 0 :
                    steppers.rotate_probe_clkwise()
                else:
                    steppers.rotate_probe_anti_clkwise()

                while (True):
                    b = steppers.read()
                    if b == b'\x03':
                        break

            t, raw = oscilloscope.sample()

            carrier = signal.filtfilt(*carrier_filter, raw, axis=-1)
            envelope = np.abs(signal.hilbert(carrier, axis=-1))
            envelope_filtered = signal.filtfilt(
                *envelope_filter, envelope, axis=-1)
            # number of samples removed from each edge
            NR = int(edge_length*acquisition_num_samples)
            envelope_filtered = envelope_filtered[:, NR:-NR]

            pos = np.max(envelope_filtered, axis=-1) - \
                (np.min(envelope_filtered, axis=-1) if signal_modulated else 0)
            amp_global.append(np.sqrt(np.square(pos[0])+np.square(pos[1])))

            x_global.append(
                radius*np.sin(np.deg2rad(steppers.theta))*np.cos(np.deg2rad(steppers.phi)))
            y_global.append(
                radius*np.sin(np.deg2rad(steppers.theta))*np.sin(np.deg2rad(steppers.phi)))
            z_global.append(radius*np.cos(np.deg2rad(steppers.theta)))

            sc._offsets3d = (x_global, y_global, z_global)
            sc._facecolors = color_converter.to_rgba(amp_global)

            print("theta: ",steppers.theta, "phi: ",steppers.phi, "amplitude: ",amp_global[-1],end='\r')

            fig.canvas.draw_idle()
            plt.pause(0.05)

            time.sleep(delay)
        

    now = datetime.now()

    filename = str(now.strftime("%H:%M:%S")+'_radius_' +
               str(radius)+'.npy').replace(':', '_')
    
    np.save(filename, np.asarray([x_global,y_global,z_global, amp_global]))
    print("data_saved.")