"""
spectrum module

FFT function
"""

#Standard python
import numpy

class Spectrum:
    """
    Spectrum class
    """
    
    def build_axis_tf(self, Fs, N, t_format, f_format):
        """
        Build time an frequency axis
        """
        Ts = 1 / Fs #s
        resol = Fs/N #Hz
        
        t_axis = numpy.linspace(0, N-1, N)
        t_axis = (Ts*t_axis)/t_format.get("format")
        t_unit  = "Time ({})".format(t_format.get("unit"))
        
        #f_axis = [] #numpy.fft.fftfreq(N, 1.0)
        f_axis = numpy.linspace(-N/2, N/2-1, N)
        f_axis = (resol*f_axis)/f_format.get("format")
        f_unit  = "Frequency ({})".format(f_format.get("unit"))
        
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
        data_out = numpy.absolute(data_in)**2
        data_out = 10*numpy.log10(data_out)
        
        return (data_out, "dB")
