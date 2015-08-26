#! /usr/bin/python

# This tool automates the capture of ASKRAW tag data into xml files
# It can optionally zip the files to save on space.
# This is not bug free yet but works great 90% of the time

import subprocess
import os
from optparse import OptionParser
import time
import shutil
import os
import zipfile
import glob 

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            if ".xml" in f:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
            
    return total_size

def zip_dir(zip_file):
    zf = zipfile.ZipFile(zip_file, "w")
    for dirname, subdirs, files in os.walk(os.getcwd()):
        for filename in files:
            if ".xml" in filename:
                fullpath = os.path.join(dirname, filename)
                print "Archiving %s to %s" % (fullpath, zip_file)
                zf.write(fullpath)
                os.remove(fullpath)
    zf.close()

# yyyy-mm-dd format
thedate =  (time.strftime("%Y-%m-%d"))
max_mb = 1024 # max size in Mb to trigger a zip of the xml
curr_dir = os.getcwd()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-r", "--rfidler-loc", dest="rfidlerLoc",
                      help="The path to the rfidler base directory")
    parser.add_option("-c", "--chunk-size", dest="chunkSize", default=5000000,
                      help="The number of samples per chunk")
    parser.add_option("-f", "--file-prefix", dest="chunkDest", default="%s_" % thedate,
                      help="The prefix to use when saving the chunk files.")
    parser.add_option("-z", "--zip-data", dest="zipDir", default=False,
                      help="Zip the data dir periodically to conserve space.")
    parser.add_option("-d", "--device", dest="rfidDev",
                      help="The device to communicate over")
    parser.add_option("-n", "--name", dest="capName", default="scripted_cap",
                      help="The name to prepend to cap files")
                      
    (options, args) = parser.parse_args()
    scriptLoc = options.rfidlerLoc+"/python/rfidler.py"
    options.chunkSize = int(options.chunkSize)
     
    move_zips_to = curr_dir+"/zips/"
    move_caps_to = curr_dir+"/data_caps/"
    zip_file = ""
    # options.chunkDest = options.rfidlerLoc + "/" + options.chunkDest
    zcnt = 0
    try:
        while True:
            nat_cmd = "%s %s \"set tag ASKRAW\" STORE %s %s" % (scriptLoc, options.rfidDev, options.chunkSize, options.capName)
            #print nat_cmd
            subprocess.check_call(nat_cmd, shell=True)
            for f in glob.glob1(curr_dir,"*.xml"):
                shutil.move(f, move_caps_to)
            if options.zipDir:
                base_size = get_size(move_caps_to)
                dirSize = base_size/1024
                if dirSize >= max_mb: # Zip dir, then wipe all the files
                    num_offset = len(glob.glob1(move_zips_to,"*.zip"))+1
                    zip_file = "rfidler_block_%d" % num_offset
                    full_dest = move_zips_to+zip_file+".zip"
                    shutil.make_archive(zip_file, 'zip', move_caps_to)
                    #print "mv %s %s" % (curr_dir+"/"+zip_file+".zip", full_dest)
                    #print "rm -r %s*" % move_caps_to
                    files=glob.glob(move_zips_to+'*.bak')
                    for filename in files:
                        os.unlink(filename)
                    shutil.move(zip_file+".zip", full_dest)

    except KeyboardInterrupt as e:
        #Cleanup the directory some
        for f in glob.glob1(curr_dir,"*.xml"):
            shutil.move(f, move_caps_to)
        zip_dir(zip_file) #Zips any file that might not get moved to te cap dir
        print "Finished"
        exit(0)
