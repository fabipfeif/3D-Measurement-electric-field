from RsInstrument import *
from time import time
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import serial
from progress.bar import Bar
from datetime import datetime
from analysis import map_data, filter_data
import plotly.express as px

scanner = serial.Serial('COM11', 9600)

resource_string = 'USB0::0x0AAD::0x01D6::201033::INSTR'

rtb = RsInstrument(resource_string, True, False)

rtb.visa_timeout = 20000

idn = rtb.query_str('*IDN?')
print(f"\nHello, I am: '{idn}'")
print(f'RsInstrument driver version: {rtb.driver_version}')
print(f'Visa manufacturer: {rtb.visa_manufacturer}')
print(f'Instrument full name: {rtb.full_instrument_model_name}')
print(f'Instrument installed options: {",".join(rtb.instrument_options)}')

rtb.write_str("ACQ:POIN 100000")  # 100k samples
rtb.write_str("TIM:ACQT 0.02")  # 20ms Acquisition time
rtb.write_str("CHAN1:RANG 5.0")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN1:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN1:COUP DCL")  # Coupling AC 1MOhm
rtb.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON

rtb.write_str("CHAN2:RANG 0.5")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN2:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN2:COUP ACL")  # Coupling AC 1MOhm
rtb.write_str("CHAN2:STAT ON")  # Switch Channel 2 ON

rtb.write_str("CHAN3:RANG 0.5")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN3:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN3:COUP ACL")  # Coupling AC 1MOhm
rtb.write_str("CHAN3:STAT ON")  # Switch Channel 2 ON

# Trigger Auto mode in case of no signal is applied
rtb.write_str("TRIG:A:MODE NORM")
rtb.write_str("TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")
rtb.write_str("TRIG:A:SOUR CH1")  # Trigger source CH1
rtb.write_str("TRIG:A:LEV1 1.0")  # Trigger level 0.00V
rtb.query_opc()  # Using *OPC? query waits until all the instrument settings are finished

r = 40  # radius of probe


def aquire_data():
    t = time()
    # This tells the driver in which format to expect the binary float data
    rtb.bin_float_numbers_format = BinFloatFormat.Single_4bytes_swapped
    trace2 = np.array(rtb.query_bin_or_ascii_float_list(
        'FORM REAL,32;:CHAN2:DATA?'))
    trace3 = np.array(rtb.query_bin_or_ascii_float_list(
        'FORM REAL,32;:CHAN3:DATA?'))
    return np.array([trace2, trace3])


def send_move():
    scanner.write(b'\x03')
    while (True):
        b = scanner.read(1)
        if b == b'\x03':
            return True


def calc_coordinates(r):
    steps_plate = 37
    steps_probe = 50

    aps_probe = 180/steps_probe
    aps_plate = 180/steps_plate

    phi = []
    theta = []

    phi_global = []
    theta_global = []

    x_global = []
    y_global = []
    z_global = []

    theta = np.linspace(90, -90, steps_probe)

    for j in range(0, steps_plate):
        for o in range(steps_probe):
            phi.append(90-j*aps_plate)

    phi_global = phi

    for x in range(0, steps_plate):
        if x % 2 == 0:
            theta_global.append(theta)
        else:
            theta_global.append(theta[::-1])

    theta_global = np.asarray(theta_global).flatten()
    phi_global = np.asarray(phi_global).flatten()

    for a in range(0, len(theta_global)):
        x_global.append(
            r*np.sin(np.deg2rad(theta_global[a]))*np.cos(np.deg2rad(phi_global[a])))
        y_global.append(
            r*np.sin(np.deg2rad(theta_global[a]))*np.sin(np.deg2rad(phi_global[a])))
        z_global.append(r*np.cos(np.deg2rad(theta_global[a])))

    return x_global, y_global, z_global


def run_measurement(r):
    x_global, y_global, z_global = calc_coordinates(r)

    data = []

    field_amp_global = []

    num_steps = 1850
    bar = Bar('Aquiring Data', max=num_steps, fill='#',
              suffix='%(percent)d%% - %(eta)ds' ' to go')

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    sc = ax.scatter([], [], [])  # , c=field_amp_global, cmap='coolwarm')
    color_converter = cm.ScalarMappable(
        norm=mpl.colors.Normalize(vmin=0, vmax=0.1), cmap=cm.coolwarm)

    ax.set_xlim([-r-10, r+10])
    ax.set_ylim([-r-10, r+10])
    ax.set_zlim([0, r+10])

    while (len(data) < num_steps):

        while (not send_move()):
            pass

        bar.next()
        point = aquire_data()
        data.append(point)

        pos = np.zeros([2])

        for channels in range(0, len(point)):  # 1
            fltr = filter_data(point[channels])
            # amp = np.mean(fltr) #avergae of hilber-tranformation
            fltr_without_edges = fltr[20000:-20000]
            # amp = np.mean(fltr_without_edges) #avergae of hilber-tranformation
            amp = np.max(fltr_without_edges)-np.min(fltr_without_edges) # use this for the temp interference analysis
            pos[channels] = amp

        field_amp = np.sqrt(np.square(pos[0])+np.square(pos[1]))
        field_amp_global.append(field_amp)

        sc._offsets3d = (x_global[:len(field_amp_global)], y_global[:len(
            field_amp_global)], z_global[:len(field_amp_global)])
        sc._facecolors = color_converter.to_rgba(field_amp_global)

        fig.canvas.draw_idle()
        plt.pause(0.05)

    bar.finish()
    data = np.asarray(data)
    return data


try:
    data = run_measurement(r)
except:
    rtb.close()

now = datetime.now()
filename = str(now.strftime("%H:%M:%S")+'_radius_' +
               str(r)+'.npy').replace(':', '_')
print("save data to "+filename+"...")
np.save(filename, data)
print("data saved")
rtb.close()


fig = map_data(filename)
plt.show()
