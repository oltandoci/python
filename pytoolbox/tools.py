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
import math

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
                
    def sinwave_gen_multiple_chan(self, payload_size, sample_size, f0, Fs, N, multiple, endian, interlaced=True, filesuffix=None):
    
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
                filename = "ref_sine" + "_f0-" + str(f_ch) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-1" + filesuffix
            else:
                filename = "ref_sine" + "_f0-" + str(f_ch) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-1" 
            with open(filename + ".bin", "wb") as binfile:
                binfile.write(x)

    def _check_format(self, endian, sample_size):
    
        if (endian == 0):
            endian_type = '<' #LE
        else:
            endian_type = '>' #BE
            
        if sample_size == 8:
            B = 1
            fmt = '{0}b'.format(endian_type)
        elif sample_size == 16:
            B = 2
            fmt = '{0}h'.format(endian_type)
        elif sample_size == 20: #20bit sample will be extended to 32bits
            B = 4
            fmt = '{0}i'.format(endian_type)
        elif sample_size == 24: #24bit sample will be extended to 32bits
            B = 4
            fmt = '{0}i'.format(endian_type)
        elif sample_size == 32:
            B = 4
            fmt = '{0}i'.format(endian_type)
        else:
            raise Exception(f'Sample size {sample_size} is not supported, must be 8, 16, 20, 24 or 32 bits')
            
        return (B, fmt)
        
    def _fill_1_ch_8b(self, k, N, fmt, val, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array = struct.pack(fmt, val)
        x[1*1*k] = val_array[0]
        
    def _fill_1_ch_16b(self, k, N, fmt, val, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array = struct.pack(fmt, val)
        x[1*2*k+0] = val_array[0]
        x[1*2*k+1] = val_array[1]
        
    def _fill_1_ch_32b(self, k, N, fmt, val, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array = struct.pack(fmt, val)
        x[1*4*k+0] = val_array[0]
        x[1*4*k+1] = val_array[1]
        x[1*4*k+2] = val_array[2]
        x[1*4*k+3] = val_array[3] 
        
    def _fill_2_ch_8b(self, k, N, fmt, val_0, val_1, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        x[2*1*k+0] = val_array_ch0[0]
        x[2*1*k+1] = val_array_ch1[0]
        
    def _fill_2_ch_16b(self, k, N, fmt, val_0, val_1, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        x[2*2*k+0] = val_array_ch0[0]
        x[2*2*k+1] = val_array_ch0[1]
        x[2*2*k+2] = val_array_ch1[0]
        x[2*2*k+3] = val_array_ch1[1]
        
    def _fill_2_ch_32b(self, k, N, fmt, val_0, val_1, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        x[2*4*k+0] = val_array_ch0[0]
        x[2*4*k+1] = val_array_ch0[1]
        x[2*4*k+2] = val_array_ch0[2]
        x[2*4*k+3] = val_array_ch0[3]
        x[2*4*k+4] = val_array_ch1[0]
        x[2*4*k+5] = val_array_ch1[1]
        x[2*4*k+6] = val_array_ch1[2]
        x[2*4*k+7] = val_array_ch1[3]
        
    def _fill_8_ch_8b(self, k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        val_array_ch2 = struct.pack(fmt, val_2)
        val_array_ch3 = struct.pack(fmt, val_3)
        val_array_ch4 = struct.pack(fmt, val_4)
        val_array_ch5 = struct.pack(fmt, val_5)
        val_array_ch6 = struct.pack(fmt, val_6)
        val_array_ch7 = struct.pack(fmt, val_7)
        x[8*1*k+0] = val_array_ch0[0]
        x[8*1*k+1] = val_array_ch1[0]
        x[8*1*k+2] = val_array_ch2[0]
        x[8*1*k+3] = val_array_ch3[0]
        x[8*1*k+4] = val_array_ch4[0]
        x[8*1*k+5] = val_array_ch5[0]
        x[8*1*k+6] = val_array_ch6[0]
        x[8*1*k+7] = val_array_ch7[0]

        
    def _fill_8_ch_16b(self, k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        val_array_ch2 = struct.pack(fmt, val_2)
        val_array_ch3 = struct.pack(fmt, val_3)
        val_array_ch4 = struct.pack(fmt, val_4)
        val_array_ch5 = struct.pack(fmt, val_5)
        val_array_ch6 = struct.pack(fmt, val_6)
        val_array_ch7 = struct.pack(fmt, val_7)
        x[8*2*k+0] = val_array_ch0[0]
        x[8*2*k+1] = val_array_ch0[1]
        x[8*2*k+2] = val_array_ch1[0]
        x[8*2*k+3] = val_array_ch1[1]
        x[8*2*k+4] = val_array_ch2[0]
        x[8*2*k+5] = val_array_ch2[1]
        x[8*2*k+6] = val_array_ch3[0]
        x[8*2*k+7] = val_array_ch3[1]
        x[8*2*k+8] = val_array_ch4[0]
        x[8*2*k+9] = val_array_ch4[1]
        x[8*2*k+10] = val_array_ch5[0]
        x[8*2*k+11] = val_array_ch5[1]
        x[8*2*k+12] = val_array_ch6[0]
        x[8*2*k+13] = val_array_ch6[1]
        x[8*2*k+14] = val_array_ch7[0]
        x[8*2*k+15] = val_array_ch7[1]

        
    def _fill_8_ch_32b(self, k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x):
        done = "Progress: %.2f%%" % ((k/N)*100)
        print(done, end="\r")
        val_array_ch0 = struct.pack(fmt, val_0)
        val_array_ch1 = struct.pack(fmt, val_1)
        val_array_ch2 = struct.pack(fmt, val_2)
        val_array_ch3 = struct.pack(fmt, val_3)
        val_array_ch4 = struct.pack(fmt, val_4)
        val_array_ch5 = struct.pack(fmt, val_5)
        val_array_ch6 = struct.pack(fmt, val_6)
        val_array_ch7 = struct.pack(fmt, val_7)
        x[8*4*k+0] = val_array_ch0[0]
        x[8*4*k+1] = val_array_ch0[1]
        x[8*4*k+2] = val_array_ch0[2]
        x[8*4*k+3] = val_array_ch0[3]
        x[8*4*k+4] = val_array_ch1[0]
        x[8*4*k+5] = val_array_ch1[1]
        x[8*4*k+6] = val_array_ch1[2]
        x[8*4*k+7] = val_array_ch1[3]
        x[8*4*k+8] = val_array_ch2[0]
        x[8*4*k+9] = val_array_ch2[1]
        x[8*4*k+10] = val_array_ch2[2]
        x[8*4*k+11] = val_array_ch2[3]
        x[8*4*k+12] = val_array_ch3[0]
        x[8*4*k+13] = val_array_ch3[1]
        x[8*4*k+14] = val_array_ch3[2]
        x[8*4*k+15] = val_array_ch3[3]
        x[8*4*k+16] = val_array_ch4[0]
        x[8*4*k+17] = val_array_ch4[1]
        x[8*4*k+18] = val_array_ch4[2]
        x[8*4*k+19] = val_array_ch4[3]
        x[8*4*k+20] = val_array_ch5[0]
        x[8*4*k+21] = val_array_ch5[1]
        x[8*4*k+22] = val_array_ch5[2]
        x[8*4*k+23] = val_array_ch5[3]
        x[8*4*k+24] = val_array_ch6[0]
        x[8*4*k+25] = val_array_ch6[1]
        x[8*4*k+26] = val_array_ch6[2]
        x[8*4*k+27] = val_array_ch6[3]
        x[8*4*k+28] = val_array_ch7[0]
        x[8*4*k+29] = val_array_ch7[1]
        x[8*4*k+30] = val_array_ch7[2]
        x[8*4*k+31] = val_array_ch7[3]

            
    def sinwave_gen_interleaced_chan(self, payload_size, sample_size, f0, Fs, N, num_of_chan, endian, filesuffix=None):
    
        (B, fmt) = self._check_format(endian, sample_size)
        A = (pow(2, payload_size)/2)-1
        x = bytearray(N*B*num_of_chan) #integers of xx Bytes
        f_ch_list = []
        for idx in range(num_of_chan):
            f_ch_list.append((idx+1)*f0) #each channel carrier is a multiple of f0
            
        if (num_of_chan == 1):
            for k in range(N):
                val = round(A * numpy.sin(2*numpy.pi*k*(f0/Fs)))
                if sample_size == 8:
                    self._fill_1_ch_8b(k, N, fmt, val, x)
                elif sample_size == 16:
                    self._fill_1_ch_16b(k, N, fmt, val, x)
                else: #4 Bytes sample
                    self._fill_1_ch_32b(k, N, fmt, val, x)
                        
        elif (num_of_chan == 2):
            for k in range(N):
                val_0 = round(A * numpy.sin(2*numpy.pi*k*(f0/Fs)))
                val_1 = round(A * numpy.sin(2*numpy.pi*k*(2*f0/Fs)))
                if sample_size == 8:
                    self._fill_2_ch_8b(k, N, fmt, val_0, val_1, x)
                elif sample_size == 16:
                    self._fill_2_ch_16b(k, N, fmt, val_0, val_1, x)
                else: #4 Bytes sample
                    self._fill_2_ch_32b(k, N, fmt, val_0, val_1, x)
                    
        elif (num_of_chan == 8):
            for k in range(N):
                val_0 = round(A * numpy.sin(2*numpy.pi*k*(f0/Fs)))
                val_1 = round(A * numpy.sin(2*numpy.pi*k*(2*f0/Fs)))
                val_2 = round(A * numpy.sin(2*numpy.pi*k*(3*f0/Fs)))
                val_3 = round(A * numpy.sin(2*numpy.pi*k*(4*f0/Fs)))
                val_4 = round(A * numpy.sin(2*numpy.pi*k*(5*f0/Fs)))
                val_5 = round(A * numpy.sin(2*numpy.pi*k*(6*f0/Fs)))
                val_6 = round(A * numpy.sin(2*numpy.pi*k*(7*f0/Fs)))
                val_7 = round(A * numpy.sin(2*numpy.pi*k*(8*f0/Fs)))
                if sample_size == 8:
                    self._fill_8_ch_8b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
                elif sample_size == 16:
                    self._fill_8_ch_16b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
                else: #4 Bytes sample
                    self._fill_8_ch_32b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
        else:
            raise Exception("only 2 or 8 channels can be interleaced!")
            
        #Save samples into binary file
        if (filesuffix):
            filename = "ref_sine" + "_f0-" + str(f0) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan) + filesuffix
        else:
            filename = "ref_sine" + "_f0-" + str(f0) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan)
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)
            
    def trianglewave_gen_interleaced_chan(self, payload_size, sample_size, f0, Fs, N, num_of_chan, endian, filesuffix=None):
        #https://en.wikipedia.org/wiki/Triangle_wave
        (B, fmt) = self._check_format(endian, sample_size)
        A = (pow(2, payload_size)/2)-1
        x = bytearray(N*B*num_of_chan) #integers of xx Bytes
        f_ch_list = []
        for idx in range(num_of_chan):
            f_ch_list.append((idx+1)*f0) #each channel carrier is a multiple of f0
        
        if (num_of_chan == 1):
            T0 = 1/f0
            for k in range(N):
                temp = numpy.abs(numpy.mod(k/Fs - T0/4, T0, dtype=numpy.double) - T0/2)
                val = round((4*A*temp)/T0 - A)
                if sample_size == 8:
                    self._fill_1_ch_8b(k, N, fmt, val, x)
                elif sample_size == 16:
                    self._fill_1_ch_16b(k, N, fmt, val, x)
                else: #4 Bytes sample
                    self._fill_1_ch_32b(k, N, fmt, val, x)
                        
        elif (num_of_chan == 2):
            T0_0 = 1/f0
            T0_1 = 1/(2*f0)
            for k in range(N):
                temp_0 = numpy.abs(numpy.mod(k/Fs - T0_0/4, T0_0, dtype=numpy.double) - T0_0/2)
                temp_1 = numpy.abs(numpy.mod(k/Fs - T0_1/4, T0_1, dtype=numpy.double) - T0_1/2)
                val_0 = round((4*A*temp_0)/T0_0 - A)
                val_1 = round((4*A*temp_1)/T0_1 - A)
                if sample_size == 8:
                    self._fill_2_ch_8b(k, N, fmt, val_0, val_1, x)
                elif sample_size == 16:
                    self._fill_2_ch_16b(k, N, fmt, val_0, val_1, x)
                else: #4 Bytes sample
                    self._fill_2_ch_32b(k, N, fmt, val_0, val_1, x)
                    
        elif (num_of_chan == 8):
            T0_0 = 1/f0
            T0_1 = 1/(2*f0)
            T0_2 = 1/(3*f0)
            T0_3 = 1/(4*f0)
            T0_4 = 1/(5*f0)
            T0_5 = 1/(6*f0)
            T0_6 = 1/(7*f0)
            T0_7 = 1/(8*f0)
            for k in range(N):
                temp_0 = numpy.abs(numpy.mod(k/Fs - T0_0/4, T0_0, dtype=numpy.double) - T0_0/2)
                temp_1 = numpy.abs(numpy.mod(k/Fs - T0_1/4, T0_1, dtype=numpy.double) - T0_1/2)
                temp_2 = numpy.abs(numpy.mod(k/Fs - T0_2/4, T0_2, dtype=numpy.double) - T0_2/2)
                temp_3 = numpy.abs(numpy.mod(k/Fs - T0_3/4, T0_3, dtype=numpy.double) - T0_3/2)
                temp_4 = numpy.abs(numpy.mod(k/Fs - T0_4/4, T0_4, dtype=numpy.double) - T0_4/2)
                temp_5 = numpy.abs(numpy.mod(k/Fs - T0_5/4, T0_5, dtype=numpy.double) - T0_5/2)
                temp_6 = numpy.abs(numpy.mod(k/Fs - T0_6/4, T0_6, dtype=numpy.double) - T0_6/2)
                temp_7 = numpy.abs(numpy.mod(k/Fs - T0_7/4, T0_7, dtype=numpy.double) - T0_7/2)
                val_0 = round((4*A*temp_0)/T0_0 - A)
                val_1 = round((4*A*temp_1)/T0_1 - A)
                val_2 = round((4*A*temp_2)/T0_2 - A)
                val_3 = round((4*A*temp_3)/T0_3 - A)
                val_4 = round((4*A*temp_4)/T0_4 - A)
                val_5 = round((4*A*temp_5)/T0_5 - A)
                val_6 = round((4*A*temp_6)/T0_6 - A)
                val_7 = round((4*A*temp_7)/T0_7 - A)
                if sample_size == 8:
                    self._fill_8_ch_8b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
                elif sample_size == 16:
                    self._fill_8_ch_16b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
                else: #4 Bytes sample
                    self._fill_8_ch_32b(k, N, fmt, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, x)
        else:
            raise Exception("only 2 or 8 channels can be interleaced!")
            
        #Save samples into binary file
        if (filesuffix):
            filename = "ref_triangle" + "_f0-" + str(f0) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan) + filesuffix
        else:
            filename = "ref_triangle" + "_f0-" + str(f0) + "Hz" + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan)
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)
            
    def rampupdownwave_gen_interleaced_chan(self, payload_size, sample_size, Fs, N, num_of_chan, endian, filesuffix=None):
    
        (B, fmt) = self._check_format(endian, sample_size)
        x = bytearray(N*B*num_of_chan) #integers of xx Bytes
        val = 0
        slope_pos = True
        for k in range(N):
            if (num_of_chan == 1):
                if sample_size == 8:
                    self._fill_1_ch_8b(k, N, fmt, val, x)
                elif sample_size == 16:
                    self._fill_1_ch_16b(k, N, fmt, val, x)
                else: #4 Bytes sample
                    self._fill_1_ch_32b(k, N, fmt, val, x)
            elif (num_of_chan == 2):
                if sample_size == 8:
                    self._fill_2_ch_8b(k, N, fmt, val, val, x)
                elif sample_size == 16:
                    self._fill_2_ch_16b(k, N, fmt, val, val, x)
                else: #4 Bytes sample
                    self._fill_2_ch_32b(k, N, fmt, val, val, x)
            elif (num_of_chan == 8):
                if sample_size == 8:
                    self._fill_8_ch_8b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                elif sample_size == 16:
                    self._fill_8_ch_16b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                else: #4 Bytes sample
                    self._fill_8_ch_32b(k, N, fmt, val, val, val, val, val, val, val, val, x)
            else:
                raise Exception("only 2 or 8 channels can be interleaced!")
                
            if (slope_pos):
                val = val + 1
            else:
                val = val - 1
            if (val == payload_size):
                slope_pos = False
            if (val == 0):
                slope_pos = True
                
        #Save samples into binary file
        if (filesuffix):
            filename = "ref_rampupdown" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan) + filesuffix
        else:
            filename = "ref_rampupdown" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan)
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)
            
    def rampupwave_gen_interleaced_chan(self, payload_size, sample_size, Fs, N, num_of_chan, endian, filesuffix=None):
    
        (B, fmt) = self._check_format(endian, sample_size)
        x = bytearray(N*B*num_of_chan) #integers of xx Bytes
        val = 0
        for k in range(N):
            if (num_of_chan == 1):
                if sample_size == 8:
                    self._fill_1_ch_8b(k, N, fmt, val, x)
                elif sample_size == 16:
                    self._fill_1_ch_16b(k, N, fmt, val, x)
                else: #4 Bytes sample
                    self._fill_1_ch_32b(k, N, fmt, val, x)
            elif (num_of_chan == 2):
                if sample_size == 8:
                    self._fill_2_ch_8b(k, N, fmt, val, val, x)
                elif sample_size == 16:
                    self._fill_2_ch_16b(k, N, fmt, val, val, x)
                else: #4 Bytes sample
                    self._fill_2_ch_32b(k, N, fmt, val, val, x)
            elif (num_of_chan == 8):
                if sample_size == 8:
                    self._fill_8_ch_8b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                elif sample_size == 16:
                    self._fill_8_ch_16b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                else: #4 Bytes sample
                    self._fill_8_ch_32b(k, N, fmt, val, val, val, val, val, val, val, val, x)
            else:
                raise Exception("only 2 or 8 channels can be interleaced!")
                
            val = val + 1
            if (val == payload_size):
                val = 0
                
        #Save samples into binary file
        if (filesuffix):
            filename = "ref_rampup" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan) + filesuffix
        else:
            filename = "ref_rampup" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan)
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)

    def rampdownwave_gen_interleaced_chan(self, payload_size, sample_size, Fs, N, num_of_chan, endian, filesuffix=None):
    
        (B, fmt) = self._check_format(endian, sample_size)
        x = bytearray(N*B*num_of_chan) #integers of xx Bytes
        val = payload_size
        for k in range(N):
            if (num_of_chan == 1):
                if sample_size == 8:
                    self._fill_1_ch_8b(k, N, fmt, val, x)
                elif sample_size == 16:
                    self._fill_1_ch_16b(k, N, fmt, val, x)
                else: #4 Bytes sample
                    self._fill_1_ch_32b(k, N, fmt, val, x)
            elif (num_of_chan == 2):
                if sample_size == 8:
                    self._fill_2_ch_8b(k, N, fmt, val, val, x)
                elif sample_size == 16:
                    self._fill_2_ch_16b(k, N, fmt, val, val, x)
                else: #4 Bytes sample
                    self._fill_2_ch_32b(k, N, fmt, val, val, x)
            elif (num_of_chan == 8):
                if sample_size == 8:
                    self._fill_8_ch_8b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                elif sample_size == 16:
                    self._fill_8_ch_16b(k, N, fmt, val, val, val, val, val, val, val, val, x)
                else: #4 Bytes sample
                    self._fill_8_ch_32b(k, N, fmt, val, val, val, val, val, val, val, val, x)
            else:
                raise Exception("only 2 or 8 channels can be interleaced!")
                
            val = val - 1
            if (val == 0):
                val = payload_size
                
        #Save samples into binary file
        if (filesuffix):
            filename = "ref_rampdown" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan) + filesuffix
        else:
            filename = "ref_rampdown" + "_max-" + str(payload_size)  + "_Fs-" + str(Fs) + "Hz" + "_t-" + str(int(N/Fs)) + "sec" + "_N-" + str(N) + "_B-" + str(B) + "_ch-" + str(num_of_chan)
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)
