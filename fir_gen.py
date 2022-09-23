#!/usr/bin/env python3

#Standard python
import argparse
import sys
import struct
import numpy
import scipy.signal as signal

#Custom packages
sys.path.append('pytoolbox')
import pytoolbox.spectrum as mod_spectrum
import pytoolbox.figure as mod_figure
import pytoolbox.fir as mod_fir

class Const:
    SUBPLOT = False
    AXIS_DEF = {   
        "TIME_S"    : {
            "format"    : 1,
            "unit"     :"s"
        }, 
        "TIME_MS"   : {
            "format"    : 10**(-3),
            "unit"     :"ms"
        },
        "FREQ_HZ"    : {
            "format"    : 1,
            "unit"     :"Hz"
        },
        "FREQ_KHZ"    : {
            "format"    : 10**3,
            "unit"     :"kHz"
        }
    }
    
#main function
def main(order, cutoff, sampfreq, window, quant, n_bytes, interpol_factor=0, interpol_taps=0, beta=3.2):

    fir = mod_fir.Fir()
    
    #generate reference FIR taps using sinc classical computing
    (h_sinc, n_samp, window_sinc) = fir.classic_sinc_design(order, cutoff, sampfreq, window, beta, interpol_factor)
    
    if (interpol_factor > 0):
        h_sinc = h_sinc * interpol_factor
    
    #check if need to generate interolation FIR or not
    if (interpol_factor > 0):
        if (interpol_taps > 0):
            (h_compare, n_samp, window_comp) = fir.fract_delay_interp(interpol_factor, interpol_taps, cutoff, sampfreq, window, True)
        else:
            raise Exception("Then number of taps for polyphase FIR must be greater than 0")
        comp_str = "fractdelay"
    else:
        (h_compare, n_samp, window_comp) = fir.python_scipy_design(order, cutoff, sampfreq, window, beta)
        comp_str = "scipy"
        
    #Save file
    fir.save_bin_coeff("fir-sinc" + "_Fs-" + str(sampfreq) + "Hz" + "_fc-" + str(cutoff) + "Hz", h_sinc, n_samp, quant, n_bytes, False, "_win-" + window_sinc)
    fir.save_bin_coeff("fir-" + comp_str + "_Fs-" + str(sampfreq) + "Hz" + "_fc-" + str(cutoff) + "Hz", h_compare, n_samp, quant, n_bytes, False, "_win-" + window_comp)
    
    #Diffs, clip to 1 values <1 in order avoid negative log and have 0 instead
    delta = numpy.absolute(h_sinc - h_compare)
    delta = numpy.clip(delta, 1, None)
    delta = numpy.log2(delta)
    
    w_sinc, amp_sinc = signal.freqz(h_sinc, worN=n_samp, fs=sampfreq)
    spectrum_amp_sinc = 20*numpy.log10(abs(amp_sinc))
    
    w_comp, amp_comp = signal.freqz(h_compare, worN=n_samp, fs=sampfreq)
    spectrum_amp_comp = 20*numpy.log10(abs(amp_comp))
    
    #Plot
    spectrum = mod_spectrum.Spectrum()
    (t_axis, t_unit) = spectrum.build_axis_samples(n_samp)
    (f_axis, f_unit) = spectrum.build_axis_freq(sampfreq, n_samp, Const.AXIS_DEF["FREQ_HZ"], freq_shift=False)
    
    if (Const.SUBPLOT):
        curve = mod_figure.Plot(1, show_after = 4)
        curve.subplot(221, t_axis, h_sinc, t_unit, "Amplitude", "FIR coefficients computed with sinc")
        curve.subplot(222, w_sinc, spectrum_amp_sinc, f_unit, "Amplitude (dB)", "FIR frequency response computed with sinc")
        curve.subplot(223, t_axis, h_compare, t_unit, "Amplitude", "FIR coefficients computed with " + comp_str)
        curve.subplot(224, w_comp, spectrum_amp_comp, f_unit, "Amplitude (dB)", "FIR frequency response computed with " + comp_str)
    else:
        curve = mod_figure.Plot(show_after = 7)
        curve.plot(1, t_axis, h_sinc, t_unit, "Amplitude", "FIR coefficients computed with sinc")
        curve.plot(2, t_axis, h_compare, t_unit, "Amplitude", "FIR coefficients computed with " + comp_str)
        curve.plot(3, w_sinc, spectrum_amp_sinc, f_unit, "Amplitude (dB)", "FIR frequency response computed with sinc")
        curve.plot(4, w_comp, spectrum_amp_comp, f_unit, "Amplitude (dB)", "FIR frequency response computed with " + comp_str)
        curve.plot(5, t_axis, delta, t_unit, "bits", "Quantization noise sinc vs " + comp_str)
        curve.multiplot(6, [w_sinc, spectrum_amp_sinc, 'r--', w_comp, spectrum_amp_comp, 'b--', 'sinc', comp_str], f_unit, "Amplitude (dB)", "FIR frequency response sinc vs " + comp_str)
        curve.multiplot(7, [t_axis, h_sinc, 'r--', t_axis, h_compare, 'b--', 'sinc', comp_str], t_unit, "Amplitude", "FIR coefficients sinc vs " + comp_str)
        
#main entry
if __name__ == "__main__":
    #get input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--order',      type=int,   help="""FIR order""")
    parser.add_argument('--cutoff',     type=int,   help="""Cuttof frequency in Hz""")
    parser.add_argument('--sampfreq',   type=int,   help="""Sampling frequency in Hz""")
    parser.add_argument('--window',                 help="""Window type: hann, hamming or blackman""")
    parser.add_argument('--beta',       type=float, help="""beta value for kaiser window (default: 3.2)""")
    parser.add_argument('--interpfact', type=int,   help="""Interpolation factor for polyphase FIR (default: 0)""")
    parser.add_argument('--interptaps', type=int,   help="""Interpolation FIR taps count for polyphase FIR (default: 0)""")
    parser.add_argument('--quant',      type=int,   help="""Quantizing in bits: coeff will be quantized to 2^quant""")
    parser.add_argument('--byte',       type=int,   help="""Number of bytes per coefficient: 1, 2, 3 or 4 bytes""")
    args = parser.parse_args()
    
    #call main function
    main(args.order, args.cutoff, args.sampfreq, args.window, args.quant, args.byte, args.interpfact, args.interptaps, args.beta)