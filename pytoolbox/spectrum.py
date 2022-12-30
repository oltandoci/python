"""
spectrum module

FFT function and spectral analyzis
"""

#Standard python
import numpy

class Spectrum:
    """
    Spectrum class
    """
    
    def build_axis_time(self, Fs, N, t_format):
        """
        Build time axis
        """
        Ts = 1 / Fs #s
        
        t_axis = numpy.linspace(0, N-1, N)
        t_axis = (Ts*t_axis)/t_format.get("format")
        t_unit  = "Time ({})".format(t_format.get("unit"))
        
        return (t_axis, t_unit)
        
    def build_axis_samples(self, N):
        """
        Build sample axis
        """
        
        samp_axis = numpy.linspace(0, N-1, N)
        samp_unit  = "Samples"
        
        return (samp_axis, samp_unit)
    
    def build_axis_freq(self, Fs, N, f_format, freq_shift=True):
        """
        Build frequency axis
        """
        resol = Fs/N #Hz
        
        #f_axis = [] #numpy.fft.fftfreq(N, 1.0)
        if (freq_shift):
            f_axis = numpy.linspace(-N/2, N/2-1, N)
        else:
            f_axis = numpy.linspace(0, N-1, N)
            
        f_axis = (resol*f_axis)/f_format.get("format")
        f_unit  = "Frequency ({})".format(f_format.get("unit"))
        
        return (f_axis, f_unit)
        
    def build_axis_tf(self, Fs, N, t_format, f_format):
        """
        Build time and frequency axis
        """
        (t_axis, t_unit) = self.build_axis_time(Fs, N, t_format)
        (f_axis, f_unit) = self.build_axis_freq(Fs, N, f_format)
        
        return (t_axis, t_unit, f_axis, f_unit)
        
    def fft(self, data_in, norm, shift=True, window=False):
        """
        Run FFT
        """
        if (window):
            data_in = numpy.multiply(data_in, numpy.hamming(len(data_in)))
        data_out = numpy.fft.fft(data_in) / norm
        if (shift):
            data_out = numpy.fft.fftshift(data_out) 
        
        return data_out
        
    def psd_db(self, data_in):
        """
        Power Spectral Density computing
        """
        data_out = numpy.absolute(data_in)
        data_out = numpy.square(data_out, dtype=numpy.double)
        data_out = 10*numpy.log10(data_out)
        
        return (data_out, "dB (FS)")
        
    def _check_start_stop_interval(self, idx, min_idx, max_idx, interval_idx):
        start = int(-interval_idx/2)
        stop = int(interval_idx/2)
        
        if (idx + start < min_idx):
            start = -idx
        if (idx + stop > max_idx):
            stop = max_idx - idx
            
        return (start, stop)
        
    def frequency_analysis(self, data_in, amp_comp_interval=0, sig_rem_interval=8, spur_rem_interval=8, dc_rem_interval=8, har_rem_interval=8):
        """
        Spectral analyser
        cd: https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf
        Add sanity checks on vetor indexes...
        """
        
        #Start power computing (signal squared)
        vect_analyzis = numpy.absolute(data_in)
        vect_analyzis = numpy.square(vect_analyzis, dtype=numpy.double)
        vect_analyzis_thd = numpy.absolute(data_in)
        vect_analyzis_thd = numpy.square(vect_analyzis_thd, dtype=numpy.double)
        
        min_idx = 0
        max_idx = len(vect_analyzis) - 1
        
        #compute signal
        sig_idx = numpy.argmax(vect_analyzis)
        (start, stop) = self._check_start_stop_interval(sig_idx, min_idx, max_idx, amp_comp_interval)
        sig = []
        for k in range(start, stop + 1): #(3 samples are enough for amplitude)
            sig.append(vect_analyzis[sig_idx+k])
        rms_sig = numpy.sqrt(numpy.mean(sig))
        
        #remove signal
        (start, stop) = self._check_start_stop_interval(sig_idx, min_idx, max_idx, sig_rem_interval)
        for k in range(start, stop + 1):
            vect_analyzis[sig_idx+k] = 0
            vect_analyzis_thd[sig_idx+k] = 0
        
        #compute spurious
        spur_idx = numpy.argmax(vect_analyzis)
        (start, stop) = self._check_start_stop_interval(spur_idx, min_idx, max_idx, amp_comp_interval)
        spur = []
        for k in range(start, stop + 1): #(3 samples are enough for amplitude)
            spur.append(vect_analyzis[spur_idx+k])
        rms_spur = numpy.sqrt(numpy.mean(spur))
        
        #remove DC
        dc_idx = 0 #we assume that input samples are taken from the 2nd half spectrum after fftshift
        (start, stop) = self._check_start_stop_interval(dc_idx, min_idx, max_idx, dc_rem_interval)
        for k in range(start, stop + 1):
            vect_analyzis[dc_idx+k] = 0
        sfdr = 20*numpy.log10(rms_sig/rms_spur)
        
        #compute noise and THD+N (DC should be removed first)
        thd_n_val = numpy.sqrt(numpy.sum(vect_analyzis, dtype=numpy.double))
        thd_n = 20*numpy.log10(rms_sig/thd_n_val)
        
        #compute SNR
        rms_noise = numpy.sqrt(numpy.mean(vect_analyzis_thd))
        snr = 20*numpy.log10(rms_sig/rms_noise)
        n_floor = 20*numpy.log10(rms_noise)
        
        #remove spurious
        (start, stop) = self._check_start_stop_interval(spur_idx, min_idx, max_idx, spur_rem_interval)
        for k in range(start, stop + 1):
            vect_analyzis[spur_idx+k] = 0
        
        #compute the 1st 5 harmonics
        har_tab = []
        har_idx_res = []
        for k_thd in range(5):
            har_idx = numpy.argmax(vect_analyzis_thd)
            har_idx_res.append(har_idx)
            har = []
            (start, stop) = self._check_start_stop_interval(har_idx, min_idx, max_idx, amp_comp_interval)
            for k in range(start, stop + 1): #(3 samples are enough for amplitude)
                har.append(vect_analyzis_thd[har_idx+k])
            har_tab.append(numpy.mean(har))
            #remove harmonic
            (start, stop) = self._check_start_stop_interval(har_idx, min_idx, max_idx, har_rem_interval)
            for k in range(start, stop + 1):
                vect_analyzis_thd[har_idx+k] = 0
        
        thd_val = numpy.sqrt(numpy.sum(har_tab, dtype=numpy.double))
        thd = 20*numpy.log10(rms_sig/thd_val)
        thd_100 = ((thd_val/rms_sig)*100)
        
        return (sfdr, thd, thd_100, thd_n, snr, n_floor, sig_idx, spur_idx, har_idx_res)
