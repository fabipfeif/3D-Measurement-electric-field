import numpy as np
import RsInstrument
import time

class OscilloscopeController:
    def __init__(self, resource_string, volts_per_division, num_samples, acq_time, visa_timeout=2000, simulation=False):
        self.volts_per_division = volts_per_division
        self.num_samples = num_samples
        self.acq_time = acq_time
        self.sampling_rate = num_samples / acq_time
        self.simulation = simulation

        if not self.simulation:
            rtb = RsInstrument.RsInstrument(resource_string, True, False)
            rtb.visa_timeout = visa_timeout

            idn = rtb.query_str('*IDN?')
            print(f"\nInstrument Name: '{idn}'")
            print(f'RsInstrument driver version: {rtb.driver_version}')
            print(f'Visa manufacturer: {rtb.visa_manufacturer}')
            print(f'Instrument full name: {rtb.full_instrument_model_name}')
            print(f'Instrument installed options: {",".join(rtb.instrument_options)}')

            rtb.write_str("ACQ:POIN %i"%num_samples) 
            rtb.write_str("TIM:ACQT %0.8f"%acq_time)
            rtb.write_str("CHAN1:RANG 10.0")
            rtb.write_str("CHAN1:OFFS 0.0")
            rtb.write_str("CHAN1:COUP DCL")
            rtb.write_str("CHAN1:STAT ON")

            rtb.write_str("CHAN2:RANG %0.8f"%(volts_per_division*10)) 
            rtb.write_str("CHAN2:OFFS 0.0") 
            rtb.write_str("CHAN2:COUP ACL")  
            rtb.write_str("CHAN2:STAT ON")

            rtb.write_str("CHAN3:RANG %0.8f"%(volts_per_division*10))
            rtb.write_str("CHAN3:OFFS 0.0") 
            rtb.write_str("CHAN3:COUP ACL")
            rtb.write_str("CHAN3:STAT ON") 

            rtb.write_str("TRIG:A:MODE NORM")
            rtb.write_str("TRIG:A:TYPE EDGE;:TRIG:A:EDGE:SLOP POS")
            # rtb.write_str("TRIG:A:SOUR CH1")
            # rtb.write_str("TRIG:A:LEV1 1.0") 

            # rtb.write_str("TRIG:STATE ON")
            rtb.query_opc()

            self.rtb = rtb
            

        self.t = np.arange(0, self.acq_time, 1.0/self.sampling_rate)

        time.sleep(1)

    def sample(self):
        if not self.simulation:
            # This tells the driver in which format to expect the binary float data
            # self.rtb.query_str('*TRG')
           
            # self.write("TRIG:IMM")
            self.rtb.bin_float_numbers_format = RsInstrument.BinFloatFormat.Single_4bytes_swapped

            self.rtb.write_str('*TRG')

            time.sleep(self.acq_time)
           
            trace2 = np.array(self.rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN2:DATA?'))
            trace3 = np.array(self.rtb.query_bin_or_ascii_float_list('FORM REAL,32;:CHAN3:DATA?'))
            return self.t, np.array([trace2, trace3])
        else:
            return self.simulated_sample(carrier_frequency=34.6e3, modfreq=100, noise=0.2)
    
    def simulated_sample(self, carrier_frequency, modfreq, noise):
        raw = np.zeros((2, len(self.t)))
        raw[0] = np.sin(2*np.pi*carrier_frequency*self.t)* (1+np.cos(2*np.pi*modfreq*self.t)) / 2
        raw[1] = raw[0] * 0.5
        raw += np.random.normal(scale=noise, size=raw.shape)
        time.sleep(0.1)
        return self.t, raw
