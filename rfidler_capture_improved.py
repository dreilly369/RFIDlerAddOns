#!/usr/bin/env python2
#encoding: UTF-8
import sys
import time
import RFIDler
from optparse import OptionParser
from random import randint
# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

def dict_output(input, delimiter=":"):
    out = {}
    for c in input:
        if c != '':
            parts = c.split(delimiter)
            k = parts[0].strip()
            v = parts[1].strip()
            out[k] = v
    return out

def banner():
    print """
    This is a Proximity Card cloning interface designed to operate with the RFIDler package.
    It's basic usage is to capture any non-blank autotag guesses to a file for later usage.
    It can be used to try and create clones from these stored files as well.
    Finally there is an experimental interactive cloning option that lets you immediately
    try to create cards with the captured values.
    Created By: Oni (Daniel)
    
        /\\       
        ||_____-----_____-----_____      
        ||     O             O     \\         
        ||    O\\\\    ___    //O    /       
        ||      \\\ /     \\ //      \\      
        ||         |_O O_|         /         
        ||          ^ | ^          \\        
        ||        // UUU \\\\        /         
        ||      O//       \\\\O      \\          
        ||        O       O        /           
        ||_____-----_____-----_____\\            
        ||
        ||.
    """
def usage():
	   banner()
	   print "Example: python %s [Do a multicard capture stored to a quick dump file]" % __file__
           print "Example: python %s  -p /dev/otherACM1 -o /data/cap.txt [Change standard port and out file name]" % __file__
           print "Example: python %s -m [try an experimental multi-clone]" % __file__
	   

parser = OptionParser()
parser.add_option("-c", "--card-type", dest="cardType", default ="askraw",
                  help="The type of card to emulate")
parser.add_option("-r", "--replay-file", dest="replayFile", default=None,
                      help="try making clones from a previous capture file")
parser.add_option("-o", "--out-file", dest="outFile", default="quick_capture_%d.txt" % randint(0,999999999999999),
                      help="The first id in the series to try")
parser.add_option("-p", "--port", dest="commPort", default="/dev/ttyACM0",
                      help="The number of samples per chunk")
parser.add_option("-m", "--multi-clone", dest="multiClone", default=False % randint(0,999999999999999),
                      help="The first id in the series to try")

                      
(options, args) = parser.parse_args()

usage()

'''
on_pi = True
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    on_pi = False
    
if on_pi:
    mode = GPIO.getmode()
    capture_btn = 24 # Bring to ground to start a capture stream
    working_led = 23
    print "Pin number mode: %s" % mode
    GPIO.setup(working_led, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(capture_btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
'''

port = options.commPort
rfidler = RFIDler.RFIDler()
result, reason = rfidler.connect(port)
if not result:
    print 'Warning - could not open serial port:', reason
    exit()
result, data=rfidler.command('autotag ')
detected = {}
with open(options.outFile,'w') as f:
    for c in data:
        if c.strip() != '':
            dat_pieces = c.split(":")
            if dat_pieces[1].strip() != "":
                print c
                f.write(c)
                f.write("\n")
                detected[dat_pieces[0].strip()] = dat_pieces[1].strip() 
    f.close()
time.sleep(1)
if options.multiClone:
    for k in detected.keys():
        v = detected[k]
        print "Would you like to try cloning a %s card with value %s" % (k,v)
        ans = raw_input("[y/n]? ")
        if ans.upper()[0] == "Y":
            time.sleep(2)
            rfidler.command('set tag %s' % k)
            time.sleep(2)
            rfidler.command('encode %s %s' % (k,v))
            time.sleep(2)
            result, data=rfidler.command('vtag')
            loaded = dict_output(data)
            print "VTAG Data Stored"
            for field in loaded.keys():
                print "\t%s: %s" % (field,loaded[field])
            print "\n"
            raw_input("Place new card on Antenna and press [Enter] ")
            result, data=rfidler.command('clone')
            print result," : ",data
        else:
            print "Skipping %s, you can still try to clone this later from the file." % k
        