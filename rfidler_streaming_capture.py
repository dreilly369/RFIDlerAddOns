#!/usr/bin/env python2
#encoding: UTF-8

import RFIDler
from optparse import OptionParser
from random import randint
        
def banner():
    print """
    This is a Proximity Card cloning interface designed to operate with the RFIDler package.
    It's basic usage is to continuosly capture UIDs to a file for later usage.
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
	   print "Example: python %s start a streaming capture dumping to a file" % __file__
           print "Example: python %s -p /dev/otherACM1 -o /data/cap.txt [Change standard port and out file name]" % __file__
           print "Example: python %s -c EM4x02 [try an alternate card (default is askraw]" % __file__
	   

parser = OptionParser()
parser.add_option("-c", "--card-type", dest="cardType", default ="askraw",
                  help="The type of card to emulate")
parser.add_option("-r", "--replay-file", dest="replayFile", default=None,
                      help="try making clones from a previous capture file")
parser.add_option("-o", "--out-file", dest="outFile", default="quick_stream_%d.txt" % randint(0,999999999999999),
                      help="The first id in the series to try")
parser.add_option("-p", "--port", dest="commPort", default="/dev/ttyACM0",
                      help="The number of samples per chunk")
parser.add_option("-m", "--multi-clone", dest="multiClone", default=False ,
                      help="The first id in the series to try")

                      
(options, args) = parser.parse_args()

port = options.commPort
rfidler = RFIDler.RFIDler()
result, reason = rfidler.connect(port)
if not result:
    print 'Warning - could not open serial port:', reason
    exit()
result, TAGLIST=rfidler.command('TAGS')

def go_dark():
    for i in range(1,7):
        rfidler.ledOff(i)

if __name__ == "__main__":
    go_dark()
    usage()
    
    of = open(options.outFile,'w')
    
    while True:
        
        rfidler.toggleLED(3)
        result, data=rfidler.command('set tag %s ' % options.cardType)
        result, uid=rfidler.command('uid')
        print uid[0]
        of.write(uid[0]+"\n")
        rfidler.toggleLED(3)