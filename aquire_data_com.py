# Simple example on how to use the RsInstrument module for remote-controlling yor VISA instrument
# Preconditions:
# - Installed RsInstrument Python module (see the attached RsInstrument_PythonModule folder Readme.txt)
# - Installed VISA e.g. R&S Visa 5.12.x or newer

from RsInstrument import *
from time import time
import numpy as np
import matplotlib.pyplot as plt
import serial
from progress.bar import Bar
from datetime import datetime
from analysis import map_data, filter_data

scanner = serial.Serial('COM9',9600)

resource_string = 'USB0::0x0AAD::0x01D6::201033::INSTR'  # USB-TMC (Test and Measurement Class)

rtb = RsInstrument(resource_string,True, False)

rtb.visa_timeout = 20000
  
idn = rtb.query_str('*IDN?')
print(f"\nHello, I am: '{idn}'")
print(f'RsInstrument driver version: {rtb.driver_version}')
print(f'Visa manufacturer: {rtb.visa_manufacturer}')
print(f'Instrument full name: {rtb.full_instrument_model_name}')
print(f'Instrument installed options: {",".join(rtb.instrument_options)}')

# rtb.clear_status()
# rtb.reset()

rtb.write_str("ACQ:POIN 100000") # 100k samples
rtb.write_str("TIM:ACQT 0.1")  # 100ms Acquisition time
rtb.write_str("CHAN1:RANG 5.0")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN1:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN1:COUP DCL")  # Coupling AC 1MOhm
rtb.write_str("CHAN1:STAT ON")  # Switch Channel 1 ON

rtb.write_str("CHAN2:RANG 5.0")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN2:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN2:COUP ACL")  # Coupling AC 1MOhm
rtb.write_str("CHAN2:STAT ON")  # Switch Channel 2 ON

rtb.write_str("CHAN3:RANG 5.0")  # Horizontal range 5V (0.5V/div)
rtb.write_str("CHAN3:OFFS 0.0")  # Offset 0
rtb.write_str("CHAN3:COUP ACL")  # Coupling AC 1MOhm
rtb.write_str("CHAN3:STAT ON")  # Switch Channel 2 ON

rtb.write_str("TRIG:A:MODE NORM")  # Trigger Auto mode in case of no signal is applied
rtb.write_str("TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")  # Trigger type Edge Positive
rtb.write_str("TRIG:A:SOUR CH1")  # Trigger source CH1
rtb.write_str("TRIG:A:LEV1 1.6")  # Trigger level 0.00V
rtb.query_opc()  # Using *OPC? query waits until all the instrument settings are finished

# rtb.write_str("SING")
# rtb.query_opc()

# rtb.write_str("SING")
# rtb.query_opc()

def aquire_data():
    t = time()
    rtb.bin_float_numbers_format = BinFloatFormat.Single_4bytes_swapped  # This tells the driver in which format to expect the binary float data
    #trace1 = np.array(rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN1:DATA?'))  # Query binary array of floats - the query function is the same as for the ASCII format
    trace2 = np.array(rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN2:DATA?')) 
    trace3 = np.array(rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN3:DATA?')) 
    # trace = rtb.query_bin_or_ascii_float_list('FORM ASC;:CHAN1:DATA?')  # Query ascii array of floats
    #print(f'Instrument returned {len(trace1)} points in the binary trace, query duration {time() - t:.3f} secs')
    return np.array([trace2,trace3])

def send_move():
    scanner.write(b'\x03')
    while(True):
        b = scanner.read(1)
        if b == b'\x03':
            return True

def run_measurement():
    data=[]
    num_steps = 1850
    bar = Bar('Aquiring Data', max=num_steps,fill='#',suffix='%(percent)d%% - %(eta)ds' ' to go' )
    while(len(data)< num_steps ):
        if send_move():
            #print("position: "+ str(len(data)), end='\r')
            bar.next()
            point = aquire_data()
            data.append(point)
    bar.finish()
    data = np.asarray(data)
    return data

try:
    data = run_measurement()
    #print("Shape of array: "+data.shape)
except:
    rtb.close()

now = datetime.now()
filename = str(now.strftime("%H:%M:%S")+'.npy').replace(':','_')
print("save data to "+filename+"...")
np.save(filename, data)
print("data saved")
rtb.close()
map_data(filename)

