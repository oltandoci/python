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
        
    def fft(self, data_in, norm, shift = True):
        """
        Run FFT
        """
        data_out = numpy.fft.fft(data_in) / norm
        if (shift):
            data_out = numpy.fft.fftshift(data_out) 
        
        return data_out
        
    def psd_db(self, data_in):
        """
        Power Spectral Density computing
        """
        data_out = numpy.absolute(data_in)
        data_out = numpy.power(data_out, 2)
        data_out = 10*numpy.log10(data_out)
        
        return (data_out, "dB (FS)")
        
    def frequency_analysis(self, data_in):
        """
        Spectral analyser
        cd: https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf
        Add sanity checks on vetor indexes...
        """
        
        #compute signal
        vect_analyzis = numpy.absolute(data_in)
        sig_idx = numpy.argmax(vect_analyzis)
        sig = []
        for k_sig in range(-2, 2 + 1):
            sig.append(vect_analyzis[sig_idx+k_sig])
        sig2 = numpy.power(sig, 2)
        rms_sig = numpy.sqrt(numpy.mean(sig2))
        
        #remove signal
        vect_analyzis[sig_idx-2] = 0
        vect_analyzis[sig_idx-1] = 0
        vect_analyzis[sig_idx] = 0
        vect_analyzis[sig_idx+1] = 0
        vect_analyzis[sig_idx+2] = 0
        
        #compute spurious
        spur_idx = numpy.argmax(vect_analyzis)
        spur = []
        for k_spur in range(-2, 2 + 1):
            spur.append(vect_analyzis[spur_idx+k_spur])
        spur2 = numpy.power(spur, 2)
        rms_spur = numpy.sqrt(numpy.mean(spur2))
        
        #remove DC
        vect_analyzis[0] = 0
        vect_analyzis[1] = 0
        vect_analyzis[2] = 0
        sfdr = 20*numpy.log10(rms_sig/rms_spur)
        
        #compute noise and THD+N (DC should be removed first)
        noise_val = 0
        for elt in (vect_analyzis):
            elt2 = numpy.power(elt, 2)
            noise_val += elt2
        noise_val = numpy.sqrt(noise_val)
        noise_val /= len(vect_analyzis)
        thd_n = 20*numpy.log10(rms_sig/noise_val)
        
        #remove spurious
        vect_analyzis[spur_idx-2] = 0
        vect_analyzis[spur_idx-1] = 0
        vect_analyzis[spur_idx] = 0
        vect_analyzis[spur_idx+1] = 0
        vect_analyzis[spur_idx+2] = 0
        
        #compute the 1st 5 harmonics
        har_p = []
        for k_thd in range(5):
            har_idx = numpy.argmax(vect_analyzis)
            har = []
            for k_har in range(-2, 2 + 1):
                har.append(vect_analyzis[har_idx+k_har])
            har2 = numpy.power(har, 2)
            har_p.append(numpy.mean(har2))
            #remove harmonic
            vect_analyzis[har_idx-2] = 0
            vect_analyzis[har_idx-1] = 0
            vect_analyzis[har_idx] = 0
            vect_analyzis[har_idx+1] = 0
            vect_analyzis[har_idx+2] = 0
            
        thd_val = 0
        for elt in (har_p):
            thd_val += elt
        thd_val = numpy.sqrt(thd_val)
        thd_val /= len(har_p)
        thd = 20*numpy.log10(rms_sig/thd_val)
        
        return (sfdr, thd, thd_n)
