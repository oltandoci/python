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
def main(file_ref, file_comp, Fs, N, samp_bytes):
    
    #Open binary file
    with open(file_ref, "rb") as binfile:
        x_ref_bin = binfile.read()
        
    with open(file_comp, "rb") as binfile:
        x_ref_comp = binfile.read()
        
    Fs = int(Fs)
    N = int(N)
    samp_bytes = int(samp_bytes)
    
    if samp_bytes == 1:
        sb_idx = 1
    elif samp_bytes == 2:
        sb_idx = 2
    elif samp_bytes == 3:
        format_type = 'B' #unpack as unsigned bytes
    elif samp_bytes == 4:
        sb_idx = 3
    else:
        raise Exception(f'Sample bytes {samp_bytes} is not supported, must be 1, 2, 3 or 4 Bytes')
       
    #little endian by default
    endian = 0
    if (endian == 0):
        endian_type = '<'
        endian_str = 'little'
    else:
        endian_type = '>'
        endian_str = 'big'
        
    if (samp_bytes == 3):
        unpstr = '{0}{1}{2}'.format(endian_type, N*3, format_type) #total of 3xN bytes
        x_temp_ref = list(struct.unpack(unpstr, x_ref_bin))
        x_temp_comp = list(struct.unpack(unpstr, x_ref_comp))
        x_disp_ref = []
        x_disp_comp = []
        for k in range(N):
            val = int.from_bytes(x_temp_ref[3*k:3*k+3], endian_str, signed=True)
            x_disp_ref.append(val)
            val = int.from_bytes(x_temp_comp[3*k:3*k+3], endian_str, signed=True)
            x_disp_comp.append(val)
    else:
        unpstr = '{0}{1}{2}'.format(endian_type, N, {1:'b',2:'h',3:'i'}[sb_idx])
        x_disp_ref = list(struct.unpack(unpstr, x_ref_bin))
        x_disp_comp = list(struct.unpack(unpstr, x_ref_comp))
    
    #Diffs, clip to 1 values <1 in order avoid negative log and have 0 instead
    delta = numpy.absolute(numpy.absolute(x_disp_ref) - numpy.absolute(x_disp_comp))
    delta = numpy.clip(delta, 1, None)
    delta = numpy.log2(delta)
    
    #Plot
    spectrum = mod_spectrum.Spectrum()
    (t_axis, t_unit) = spectrum.build_axis_samples(N)
    (f_axis, f_unit) = spectrum.build_axis_freq(Fs, N, Const.AXIS_DEF["FREQ_HZ"], freq_shift=False)
    
    if (Const.SUBPLOT):
        curve = mod_figure.Plot(1, show_after = 2)
        curve.subplot(211, t_axis, x_disp_ref, t_unit, "Amplitude", "FIR coefficients computed from reference model")
        curve.subplot(212, t_axis, x_disp_comp, t_unit, "Amplitude", "FIR coefficients computed with python toolbox")
    else:
        curve = mod_figure.Plot(show_after = 4)
        curve.plot(1, t_axis, x_disp_ref, t_unit, "Amplitude", "FIR coefficients computed from reference model")
        curve.plot(2, t_axis, x_disp_comp, t_unit, "Amplitude", "FIR coefficients computed with python toolbox")
        curve.plot(3, t_axis, delta, t_unit, "bits", "Quantization noise reference model vs python toolbox")
        curve.multiplot(4, [t_axis, x_disp_ref, 'r--', t_axis, x_disp_comp, 'b--', 'ref', 'py'], t_unit, "Amplitude", "FIR coefficients reference model vs python toolbox")
        
#main entry
if __name__ == "__main__":
    #get input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--coeff_ref',  help='reference coefficient binary file')
    parser.add_argument('--coeff_comp', help='coefficient binary file for comparaison')
    parser.add_argument('--samp_freq',  help="""sampling frequency in Hz""")
    parser.add_argument('--samp_count', help="""number of samples""")
    parser.add_argument('--samp_bytes', help="""sample bytes""")
    args = parser.parse_args()
    
    #call main function
    main(args.coeff_ref, args.coeff_comp, args.samp_freq, args.samp_count, args.samp_bytes)