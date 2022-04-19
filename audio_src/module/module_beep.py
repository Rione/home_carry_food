#!/usr/bin/env python

import os
import subprocess
# Define path
file_path = os.path.abspath(__file__)

def beep():
    ###############
    #
    # use this module to make beep sound
    #
    # return >> None
    #
    ###############

    beep_wave = file_path.replace(
        'module/module_beep.py', 'beep/start.wav')
    
    subprocess.call('aplay -q --quiet {}'.format(beep_wave), shell=True)

if __name__ == '__main__':
    beep()

