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
    
    def bessel(self, x):
        """
        Bessel used with Kaiser window
        """
        sum_val = 0.0;

        for i in range(1, 10):
            x_to_i_power = numpy.power(x/2, i)
            factorial = 1;
            for j in range(1, i + 1):
                factorial *= j

            if (factorial == 0):
                print("bad divisor- factorial = %d" % factorial)
            else:
                sum_val += numpy.power(x_to_i_power / factorial, 2);
                
        return (1 + sum_val)
    
    def classic_sinc_design(self, order, f_cut, f_s, type_window, beta, interpol_factor):
        """
        Build FIR coefficients using sinc funtion
        """
        
        if (interpol_factor):
            f_cut = f_cut / interpol_factor
            
        #Force to use odd number
        M = 2 * numpy.floor(order/2) + 1
        n_samp = int(M)
        
        #Symmetric 
        n = numpy.linspace(-numpy.floor(M/2), numpy.floor(M/2), n_samp)
        idx = int(numpy.argwhere(n==0))
        
        #Normalization cut frequency to Fs, w.r.t \pi
        w_cut = 2 * numpy.pi * (f_cut / f_s)
        
        #Generate Ideal filter based on Sinc function
        x = w_cut * n / numpy.pi
        h = w_cut / numpy.pi * numpy.sinc(x)
        
        #Force 1 for index 0
        h[idx] = w_cut / numpy.pi
        
        #Windows
        if type_window == "hann":
            h = numpy.multiply(h, numpy.hanning(n_samp))
        elif type_window == "hamming":
            h = numpy.multiply(h, numpy.hamming(n_samp))
        elif type_window == "blackman":
            h = numpy.multiply(h, numpy.blackman(n_samp))
        elif type_window == "kaiser":
            h = numpy.multiply(h, numpy.kaiser(n_samp, beta))
        elif type_window == "kaiser_bessel_derived":
            h = numpy.multiply(h, numpy.kaiser_bessel_derived(n_samp, beta))
        elif type_window == "kaiser_custom":
            for n in range(n_samp):
                tmp = beta * numpy.sqrt(1 - numpy.power((2*n+2 - n_samp) / n_samp, 2))
                val = self.bessel(tmp) / self.bessel(beta);
                h[n] = h[n] * val
        else:
            print("Window type not supported for classical FIR, must be hann, hamming, blackman, kaiser, kaiser_bessel_derived, or kaiser_custom, by default hamming window is used")
            type_window = "hamming"
            h = numpy.multiply(h, numpy.hamming(n_samp))
            
        return (h, n_samp, type_window)

    def python_scipy_design(self, order, f_cut, f_s, type_window, beta):
        """
        Build FIR coefficients using python scipy module
        """
        
        #Force to use odd number
        M = 2 * numpy.floor(order/2) + 1;
        n_samp = int(M)
        
        if (type_window == "kaiser_custom"):
            print("Window type not supported for scipy, by default kaiser window is used")
            type_window = "kaiser"
            h = signal.firwin(n_samp, f_cut, window=(type_window, beta), fs=f_s)
        elif (type_window == "kaiser_bessel_derived"):
            h = signal.firwin(n_samp, f_cut, window=(type_window, beta), fs=f_s)
        else:
            h = signal.firwin(n_samp, f_cut, window=type_window, fs=f_s)
            
        return (h, n_samp, type_window)
        
    def fract_delay_interp(self, interpRatio, nTaps, cutoff, sampFreq, type_window, centerTap=False):
        
        #Initialization
        intDelay = numpy.ceil((nTaps -1)/2)
        t = numpy.linspace(0, nTaps-1, nTaps) #normalized time axis for impulse response
        hMatrix = [] #fractional delay filter coefficients
        
        if type_window != "hann" and type_window != "hamming" and type_window != "blackman":
            print("Window type not supported for fractional delay FIR, must be hann, hamming, or blackman, by default hamming window is used")
            type_window = "hamming"
        
        #Polyphase filter computation
        for n in range(interpRatio):
            delay = intDelay - n/interpRatio #integer delay + fractional delay
            relativeTime = t - delay
            
            if type_window == "hann":
                window = 0.5 - 0.5*numpy.cos(numpy.pi + 2*numpy.pi*relativeTime/nTaps)
            elif type_window == "hamming":
                window = 0.54 - 0.46*numpy.cos(numpy.pi + 2*numpy.pi*relativeTime/nTaps)
            elif type_window == "blackman":
                window = 0.42 - 0.5*numpy.cos(numpy.pi + 2*numpy.pi*relativeTime/nTaps) + 0.08*numpy.cos(numpy.pi + 4*numpy.pi*relativeTime/nTaps)
            else: #use hamming window by default
                window = 0.54 - 0.46*numpy.cos(numpy.pi + 2*numpy.pi*relativeTime/nTaps)
                
            hMatrix.append(numpy.sinc(relativeTime*cutoff/sampFreq)*window)
            
        #transpose matrix for coefficients
        ht = []
        for n_row in range(interpRatio):
            for m_col in range(nTaps):
                ht.append(hMatrix[m_col][n_row])
                
        h = []
        b_odd = True
        if (centerTap):
            n_samp = interpRatio*nTaps + 1
            if (n_samp % 2) == 0:
                raise Exception("interpRatio*nTaps + 1 must be odd")
            
            idx = int((interpRatio*nTaps)/2)
            h.extend(ht[:idx])
            
            #Normalization cut frequency to Fs, w.r.t \pi
            w_cut = 2 * numpy.pi * (cutoff / sampFreq / interpRatio)
            w_hanning = numpy.hanning(n_samp)
            w_hamming = numpy.hamming(n_samp)
            w_blackman = numpy.blackman(n_samp)
            center_idx = int((n_samp - 1) / 2)
            if type_window == "hann":
                w_center = w_hanning[center_idx]
            elif type_window == "hamming":
                w_center = w_hamming[center_idx]
            else:
                w_center = w_blackman[center_idx]
            
            val = (w_cut / numpy.pi)*w_center*interpRatio #(ht[idx-1] + ht[idx])/2
            h.append(val)
            
            h.extend(ht[idx:])
        else:
            n_samp = interpRatio*nTaps
            h = ht
        
        return (h, n_samp, type_window)
        
    def save_bin_coeff(self, file_prefix, coeff_array, n_samp, quant, n_bytes, whole=True, filesuffix=None):
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
        
        scale_val = numpy.power(2, quant)
        scale_max = scale_val - 1;
        scale_min = -scale_val
        
        #LE format
        for k in range(N):
            val = int(coeff_array[k]*scale_val)
            if (val > scale_max):
                val = scale_max
            elif (val < scale_min):
                val = scale_min
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
        
        #Save samples into binary file
        if (filesuffix):
            filename = file_prefix + "_samp-" + str(N) + "_B-" + str(n_bytes) + "_q-" + str(quant) + info + filesuffix
        else:
            filename = file_prefix + "_samp-" + str(N) + "_B-" + str(n_bytes) + "_q-" + str(quant) + info
        with open(filename + ".bin", "wb") as binfile:
            binfile.write(x)
            