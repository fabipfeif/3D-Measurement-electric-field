import numpy as np
import serial, time

class StepperController:
    # serial control commands
    baudrate = 9600
    CMD_STEP_PROBE_CLKWISE          = b's'
    CMD_STEP_PLATE_CLKWISE          = b'd'
    CMD_STEP_PROBE_ANTI_CLKWISE     = b'w'
    CMD_STEP_PLATE_ANTI_CLKWISE     = b'a'
    CMD_RECEIVED                    = b'r'

    # step magnitudes
    probe_num_steps_per_cmd = 2
    plate_num_steps_per_cmd = 9

    # step angles
    probe_angles_per_cmd = probe_num_steps_per_cmd * 1.8                # degrees
    plate_angles_per_cmd = plate_num_steps_per_cmd * 1.8 * (12.0/40.0)  # degrees

    # number of steps to cover full movement range
    probe_num_steps = int(np.round(180/probe_angles_per_cmd))+1
    plate_num_steps = int(np.round(180/plate_angles_per_cmd))

    # current angles
    theta = 90 # degrees, probe angle
    phi   =  90 # degrees, plate angle
    
    def __init__(self, port, verbose=False, simulation=False):
        self.verbose = verbose # if true print current position after every move command
        self.simulation = simulation

        if not self.simulation: self.serial = serial.Serial(port, self.baudrate)
        time.sleep(1.0) # wait for serial port to initialize

    def read(self):
        return self.serial.read(1)
    
    def rotate_probe_clkwise(self):
        if not self.simulation: self.serial.write(self.CMD_STEP_PROBE_CLKWISE)
        self.theta -= self.probe_angles_per_cmd
        if self.verbose: self.print_position()
        
    
    def rotate_probe_anti_clkwise(self):
        if not self.simulation: self.serial.write(self.CMD_STEP_PROBE_ANTI_CLKWISE)
        self.theta += self.probe_angles_per_cmd
        if self.verbose: self.print_position()

    def rotate_plate_clkwise(self):
        if not self.simulation: self.serial.write(self.CMD_STEP_PLATE_CLKWISE)
        self.phi -= self.plate_angles_per_cmd
        if self.verbose: self.print_position()

    def rotate_plate_anti_clkwise(self):
        if not self.simulation: self.serial.write(self.CMD_STEP_PLATE_ANTI_CLKWISE)
        self.phi += self.plate_angles_per_cmd
        if self.verbose: self.print_position()

    def print_position(self):
        pass
        #print('CURRENT POSITION: PROBE THETA = %0.3f, PLATE PHI = %0.3f'%(self.theta, self.phi))
    

if __name__ == '__main__':
    controller = StepperController('COM11', verbose=True)
    
    delay = 0.1

    for i in range(controller.plate_num_steps):
        for j in range(controller.probe_num_steps):
            if i%2==0: controller.rotate_probe_anti_clkwise()
            else: controller.rotate_probe_clkwise()

            time.sleep(delay)

        controller.rotate_plate_clkwise()

        

    