"""
tools module

Useful routines on:
- files I/O
- basic formatting
- pickle/unpickle
...
"""

#Standard python
import os
import time
import pickle
import numpy
import struct

class Tools:
    """
    Tools class
    """
    
    def dump_obj_pickle(self, filepath, obj):
        """
        save object with pickle
        """
        with open(filepath, "wb") as myfile:
            mypickler = pickle.Pickler(myfile)
            mypickler.dump(obj)
    
    def load_obj_unpickle(self, filepath):
        """
        read object with pickle
        """        
        with open(filepath, "rb") as myfile:
            myunpickler = pickle.Unpickler(myfile)
            obj = myunpickler.load()
            
        return obj
    
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
        
    def read_file_two_col_decimal(self, filepath):
        """
        Read text file decimal values in 2 columns separated by spaces
        """
        real = []
        imag = []
        with open(filepath, 'r') as myfile:
            for line in myfile:
                s = line.split()
                real.append(int(s[0], base = 10))
                imag.append(int(s[1], base = 10))
                
        return (real, imag)
        
    def read_file_one_col_decimal(self, filepath):
        """
        Read text file decimal values in column
        """
        val = []
        with open(filepath, 'r') as myfile:
            for line in myfile:
                s = line.split()
                val.append(int(s[0], base = 10))
                
        return val
        
    def write_file_one_col_decimal(self, filepath, array_val):
        """
        Write text file decimal values in column
        """
        val = []
        with open(filepath, 'w') as myfile:
            for item in array_val:
                myfile.write("%d\n" % item)
                
    def sinwave_gen(self, payload_size, sample_size, f0, Fs, N, sample_format, multiple, endian, filesuffix=None):
    
        if sample_size == 8:
            B = 1
        elif sample_size == 16:
            B = 2
        elif sample_size == 20: #20bit sample will be extended to 32bits
            B = 4
        elif sample_size == 24: #24bit sample will be extended to 32bits
            B = 4
        elif sample_size == 32:
            B = 4
        else:
            raise Exception(f'Sample size {sample_size} is not supported, must be 8, 16, 20, 24 or 32 bits')
            
        if (endian == 0):
            endian_type = '<' #LE
        else:
            endian_type = '>' #BE
            
        for idx in range(multiple):
            x = bytearray(N*B) #integers of xx Bytes
            f_ch = (idx+1)*f0 #each channel carrier is a multiple of f0
            for k in range(N):
                val = round(((pow(2, payload_size)/2)-1) * numpy.sin(2*numpy.pi*k*(f_ch/Fs)))
                
                if sample_size == 8:
                    val_array = struct.pack('{0}b'.format(endian_type), val)
                    x[k] = val_array[0]
                elif sample_size == 16:
                    val_array = struct.pack('{0}h'.format(endian_type), val)
                    x[2*k+0] = val_array[0]
                    x[2*k+1] = val_array[1]
                else: #4 Bytes sample
                    val_array = struct.pack('{0}i'.format(endian_type), val)
                    x[4*k+0] = val_array[0]
                    x[4*k+1] = val_array[1]
                    x[4*k+2] = val_array[2]
                    x[4*k+3] = val_array[3]
            
            #Save samples into binary file
            if (filesuffix):
                filename = "ref_sine" + "_f0-" + str(f_ch) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(N/Fs) + "sec" + "_N-" + str(N) + "_B-" + str(B) + filesuffix
            else:
                filename = "ref_sine" + "_f0-" + str(f_ch) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(N/Fs) + "sec" + "_N-" + str(N) + "_B-" + str(B)
            with open(filename + ".bin", "wb") as binfile:
                binfile.write(x)
