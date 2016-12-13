import re
from math import *
from scipy.integrate import quad
import numpy

## csv read

def readcsv(filename):
    data = []
    with open(filename, 'rt') as fID:
        for line_text in fID:
            split_line = re.split(',', line_text)
            nm = float(split_line[0])
            val = float(split_line[1])
            data.append([nm, val])
    
    return data

## read photopic curve data

filename = 'photopic_curve.csv'

photopic_data = readcsv(filename)

wavelengths = [e[0] for e in photopic_data]
photopic_vals = [e[1] for e in photopic_data]

minWavelength_nm = 390    # end of visible spectrum
maxWavelength_nm = 700   # start of visible spectrum


## luminosity funcs
    
def luminosityFcn(wavelength_nm):
    if wavelength_nm < wavelengths[0] or wavelength_nm > wavelengths[-1]:
        return float(0)
    else:
        phototopic_val = numpy.interp([wavelength_nm], 
                                      wavelengths, 
                                      photopic_vals
                                      )[0]
        return phototopic_val


## spectral density functions  
    
# boltzman eqn

c = 2.997925 * 10**8   # speed of light
h = 6.626070 * 10**-34 # plank const.
k = 1.380648 * 10**-23 # boltzman const.
def boltzman(wavelength, blackBodyTemp):
    T = blackBodyTemp
    B = (2 * h * c**2) / (wavelength**5)
    exponent = h*c / (wavelength * k * T)
    B = B / (exp(exponent) - 1)
    return B
    

# return boltzman function with a fixed temperture that accepts wavelengths
# in nanometers
def boltzmanNmTempClosure(temp):
    def closure(wavelength_nm):
        wavelength = wavelength_nm * 10**-9
        return boltzman(wavelength, temp)
    
    return closure
    
    
# measured bulb functions

def spectralDensity(wavelength_nm, wavelengths, vals):
    if wavelength_nm < wavelengths[0]:
        val = vals[0]
    elif wavelength_nm > wavelengths[-1]:
        val = vals[-1]
    else:
        val = numpy.interp([wavelength_nm], 
                            wavelengths, 
                            vals
                            )[0]
    
    return val
    
    
def getSpectralDensityFunction(spectral_filename):
    spectral_data = readcsv(spectral_filename)
    wavelengths = [e[0] for e in spectral_data]
    relative_intensity = [e[1] for e in spectral_data]
    
    def specDensFcn(wavelength_nm):
        return spectralDensity(wavelength_nm, wavelengths, relative_intensity)
        
    return specDensFcn

    
## calculations

spectralFiles = ['LED_2700K.csv',
                 'LED_4000K.csv',
                 'LED_5000K.csv',
                 'Fluorescent_2900K.csv',
                 'Incandescent_60W.csv',
                 'Sun_Fcn'
                ]

tempOfSun = 5777

for f in spectralFiles:
    if f is 'Sun_Fcn':
        specFunc = boltzmanNmTempClosure(tempOfSun)
    else:
        specFunc = getSpectralDensityFunction(f)
    
    # dividing spec eqn by norm_fact will give a power output of 1 watt in the
    # visible spectrum.
    # spectrum is windowed (multiplied) by the photopic curve. This sets all 
    # power contributions outside of visible spectrum to zero 
    norm_fact, err = quad(specFunc, minWavelength_nm, maxWavelength_nm)
    
    total_lumens = 0
    for e in photopic_data:
        watts_per_nm = specFunc(e[0]) / norm_fact
        lumens_per_nm = watts_per_nm * e[1] * 683.002
        # integrating wrt nanometers, and there is one value per nanometer
        # so a good approximation of the integral can be calculated by summation
        total_lumens += lumens_per_nm # * 1nm    

    print(f + ': ' + str(total_lumens) + ' lm per watt of visible light')

    