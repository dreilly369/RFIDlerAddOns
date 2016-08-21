#!/usr/bin/env python2
#encoding: UTF-8
import RFIDler
from optparse import OptionParser
import json
import RPi.GPIO as GPIO 
import time 
import datetime
from threading import Thread

blacklisted = [] # a list of UIDs to immediatly alert on
AUTHOPENTIME = 15 # time to run the afterAuth event for
AUTHCONTROLPIN = 7 # time to run the afterAuth event for
GPIO.setmode(GPIO.BOARD)
GPIO.setup(AUTHCONTROLPIN, GPIO.OUT) # Set GPIO Pin to OUT

def afterAuth():
    rfidler.toggleLED(5)
    GPIO.output(7,True)## Switch on pin 7
    time.sleep(AUTHOPENTIME)## Wait
    GPIO.output(7,False)
    rfidler.toggleLED(5)

def banner():
    print """
    This is a Proximity Card reader interface designed to operate with the RFIDler package.
    It's basic usage is to continuosly read UIDs and trigger some event when one or more from
    a whitelist are seen. 
    
    !!! This is still an example and needs improvement !!!
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
	   print "Example: python %s -w example_auths.json [Run the basic example card reader]" % __file__
           print "Example: python %s -w my_auths.json -a 60 -x 23 [Change the auth file, auth time, and control pin]" % __file__

    
dt_str = '{%Y-%m-%d}'.format(datetime.datetime.now())
parser = OptionParser()
parser.add_option("-c", "--card-type", dest="cardType", default =None,
                  help="The type of card being used. Overrides anything defined in the whitelist file")
parser.add_option("-w", "--whitelist-json", dest="goodFile", default=None,
                      help="The Json file with UID->Person mapping. Can define expected card type as well")
parser.add_option("-o", "--out-file", dest="outFile", default="reader_log_%d.txt" % dt_str,
                      help="The file to save logs to")
parser.add_option("-p", "--port", dest="commPort", default="/dev/ttyACM0",
                      help="The communication port. Default is /dev/ttyACM0")
parser.add_option("-a", "--auth-time", dest="authTime", default=AUTHOPENTIME,
                      help="The time to hold the afterAuth function")
parser.add_option("-x", "--control-pin", dest="controlPin", default=AUTHCONTROLPIN,
                      help="The pin to toggle in the afterAuth function")

(options, args) = parser.parse_args()
if options.goodFile is None:
    print "need to include an authorized UID list in json format. See example_auths.json"
    exit()
    
port = options.commPort
AUTHOPENTIME = int(options.authTime)
AUTHCONTROLPIN = int(options.controlPin)
rfidler = RFIDler.RFIDler()
result, reason = rfidler.connect(port)
if not result:
    print 'Warning - could not open RFIDler Port:', reason
    exit()
# Just for testing eventually back this with a db. I had some EM4X02 cards
# for testing so that is what this code was based on.
with open(options.goodFile,'r') as f:
    authed_people = json.loads(f.read())
    f.close()
    
if options.cardType != None:
    cardtype = options.cardType
elif "card_type" in authed_people.keys():
    cardType = auth_people["card_type"]
else:
    print "need to define an expected card. Either place a card_type field in the config or include it as -c"
    exit()
    
if __name__ == "__main__":
    go_dark()
    usage()
    
    of = open(options.outFile,'w')
    
    while True:
        rfidler.toggleLED(3)
        result, data=rfidler.command('set tag %s' % options.cardType)
        result, uid=rfidler.command('uid')
        ts_str = '[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())
        log_line = "%s %s\n" % (ts_str, uid[0])
        print log_line
        of.write(log_line)
        if uid[0] in authed_people.keys():
            thread = Thread(target = afterAuth)
            thread.start()
        elif uid[0] in blacklisted:
            print "This is not implemented yet..."
        
        rfidler.toggleLED(3)
