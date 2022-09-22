"""
FIR module

FIR coefficients generator
"""

#Standard python
import numpy
import struct
import scipy.signal as signal

class Fir:
    """
    Fir class
    """
    
    def classic_sinc_design(self, order, f_cut, f_s, type_window):
        """
        Build FIR coefficients using sinc funtion
        """
        
        #Force to use odd number
        M = 2 * numpy.floor(order/2) + 1;
        n_samp = int(M)
        
        #Symmetric 
        n = numpy.linspace(-numpy.floor(M/2), numpy.floor(M/2), n_samp)
        idx = int(numpy.argwhere(n==0))
        
        #Normalization cut frequency to Fs, w.r.t \pi
        w_cut = 2 * numpy.pi * f_cut/ f_s;
        
        #Generate Ideal filter based on Sinc function
        x = w_cut * n / numpy.pi;
        h = w_cut / numpy.pi * numpy.sinc(x)
        
        #Force 1 for index 0
        h[idx] = w_cut / numpy.pi ;
        
        #Windows
        w_hanning = numpy.hanning(n_samp)
        w_hamming = numpy.hamming(n_samp)
        w_blackman = numpy.blackman(n_samp)
        
        if type_window == "hann":
            h = numpy.multiply(h, w_hanning)
        elif type_window == "hamming":
            h = numpy.multiply(h, w_hamming)
        elif type_window == "blackman":
            h = numpy.multiply(h, w_blackman)
        else:
            raise Exception("Window type not supported, must be hann, hamming or blackman")
            
        return (h, n_samp)

    def python_scipy_design(self, order, f_cut, f_s, type_window):
        """
        Build FIR coefficients using python scipy module
        """
        
        #Force to use odd number
        M = 2 * numpy.floor(order/2) + 1;
        n_samp = int(M)
        
        h = signal.firwin(n_samp, f_cut, window=type_window, fs=f_s)
        
        return (h, n_samp)
        
    def save_bin_coeff(self, file_prefix, coeff_array, n_samp, quant, n_bytes, whole=True):
        """
        Save FIR coefficients into binary file
        """
        
        b_odd = True
        if (n_samp % 2) == 0:
            b_odd = False
            
        if (whole):
            N = n_samp
        else:
            if (b_odd):
                N = int((n_samp - 1) / 2 + 1) #n_samp is odd, take also the middle coeff
            else:
                N = int(n_samp/2)
            
        x = bytearray(N*n_bytes) #integers of xx Bytes
        
        #LE format
        for k in range(N):
            val = int(coeff_array[k]*numpy.power(2, quant))
            if n_bytes == 1:
                val_array = struct.pack('<b', val)
                x[k] = val_array[0]
            elif n_bytes == 2:
                val_array = struct.pack('<h', val)
                x[2*k+0] = val_array[0]
                x[2*k+1] = val_array[1]
            elif n_bytes == 3:
                x[3*k+0] = (val & 0x000000FF) >> 0;
                x[3*k+1] = (val & 0x0000FF00) >> 8;
                x[3*k+2] = (val & 0x00FF0000) >> 16;
            elif n_bytes == 4:
                val_array = struct.pack('<i', val)
                x[4*k+0] = val_array[0]
                x[4*k+1] = val_array[1]
                x[4*k+2] = val_array[2]
                x[4*k+3] = val_array[3]
            else:
                raise Exception(f'Coefficient size in bytes {n_bytes} is not supported, must be 1, 2, 3 or 4 (i.e. 8, 16, 24 or 32 bits)')
            
        info = "_le_"
        if (b_odd):
            info = info + "odd"
        else:
            info = info + "even"
            
        if (whole):
            info = info + "_" + "whole"
        else:
            info = info + "_" + "half"

        with open(file_prefix + "_samp-" + str(N) + "_B-" + str(n_bytes) + "_q-" + str(quant) + info + ".bin", "wb") as binfile:
            binfile.write(x)
            
            
