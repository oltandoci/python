#!/usr/bin/env python3

"""
noise mudule

noise techniques and signal patterns
"""

#Standard python
import numpy

class Const:
    EXP_AMPLITUDE = 1
        
class Noise:
    """
    Noise class
    """
    
    def build_exp_cplx(self, n_samp, sampling_freq, f0):
        """
        complex exponential
        """
        Ts = 1 / sampling_freq #s
        idx = numpy.linspace(0, n_samp-1, n_samp)
        t = Ts * idx
        phi = 2*numpy.pi*f0*t
        s_cplx = Const.EXP_AMPLITUDE * numpy.exp(1j*phi);
        
        return s_cplx
        
    def build_noise_cplx(self, noise_power, n_samp):
        """
        complex white Gaussian noise
        """
        #std dev
        sigma = numpy.sqrt(noise_power /2)
        #normal (Gaussian) distributioan
        n_real = sigma*numpy.random.randn(n_samp)
        n_imag = sigma*numpy.random.randn(n_samp)
        #complex noise
        n_cplx = n_real + 1j*n_imag
        
        return n_cplx
        
    def add_noise_cplx(self, sig_cplx, n_samp, sampling_freq, snr_db, enbw, quant = 0):
        """
        signal + noise
        """
        if (enbw > sampling_freq):
            enbw = sampling_freq
        snr_lin = 10**(snr_db/10)
            
        #Ps
        s_abs = numpy.absolute(sig_cplx)
        s_abs_2 = numpy.square(s_abs)
        Ps = (1 / n_samp) * numpy.sum(s_abs_2)
        #Pn
        Pn = (Ps / snr_lin) * (sampling_freq / enbw)
        #add noise to the signal
        s_n = sig_cplx + self.build_noise_cplx(Pn, n_samp)
        #quantization
        if (quant > 0):
            s_n = numpy.round( (2**(quant-1)) * s_n ); #Signed
        
        re = numpy.real(s_n)
        im = numpy.imag(s_n)
        
        return (s_n, re, im)
