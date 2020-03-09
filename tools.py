"""
tools module

Useful routines on:
- files I/O
- basic formatting
...
"""

#Standard python
import os
import time

class Tools:
    """
    Tools class
    """
    
    def print_dict_w_comments(self, mydict):
        """
        Print key, value of a dict with an extra
        """
        for key, val in mydict.items():
            print("{} = {} {}".format(key, val[0], val[1]))
            
    def kill_process(self, pstring):
        """
        Send SIGKILL signal to the specified process
        """
        for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid), signal.SIGKILL)
            
    def check_process(self, process):
        """
        Check for a given process
        """
        for line in os.popen("ps ax | grep " + process + " | grep -v grep"):
            fields = line.split()
            pstring = fields[4]
            if (pstring.find(process) >= 0):
                return True
                
    def get_time(self):
        """
        Timestamp based on the current time
        """
        pstring = time.strftime("%Y%m%d_%H%M%S") #'%Y-%m-%d_%Hh%M'
        return pstring
        
    def sort_text_files(self, list_of_files):
        """
        Filter on .txt files only and sort files by most recent
        """
        filt = filter(lambda x: x[-4:] == '.txt', list_of_files)
        file_filt_rev = sorted(list(filt), reverse = True)
        return file_filt_rev
        
    def list_all_files(self, path):
        """
        List all files 
        """
        all_files = os.listdir(path)
    
    def check_folder_path(self, folder_path):
        if (os.path.isdir(folder_path)):
            return True
        else:
            return False
            
    def check_file_path(self, file_path):
        if (os.path.isfile(file_path)):
            return True
        else:
            return False
            
    def create_folder(self, folder_path):
        """
        Create new folder if not exists
        """
        if self.check_folder_path(folder_path):
            return False
        else:
            os.system("mkdir " + folder_path)
            return True
            
    def dec2hex_list(self, dec_array, remove_0x, zero_pad):
        """
        hex format conversion
        """
        if (zero_pad > 0): #0-pad in order to have n digits (e.g. 0x03 instead of 0x3 if zero_pad = 2)
            if (remove_0x):
                tab = [hex(x)[2:].zfill(zero_pad) for x in dec_array] #remove the 0x at the beginning of each byte
            else:
                tab = [hex(x).zfill(zero_pad) for x in dec_array]
        else:
            if (remove_0x):
                tab = [hex(x)[2:] for x in dec_array] #remove the 0x at the beginning of each byte
            else:
                tab = [hex(x) for x in dec_array]
        return tab
