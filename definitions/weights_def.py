""" Add weights for the normalisation of the simulated samples in the histograms.
    The event weight reweights the full dataset so that the sum of the weights
    is equal to the expected number of events in data. The expectation is given by
    multiplying the integrated luminosity (11.58 fb^-1) of the data with the cross-section of
    the process in the datasets (expressed in pb) divided by the number of simulated events. The simulated
    background datasets are further multiplied by a scale factor which acts as a 
    correction of the simulation.
"""

integrated_luminosity = 11.58 * 1000.0 # pb^-1
scale_factor_ZZ_4l = 1.386

WEIGHTS = {
	"SMHiggsToZZTo4L": integrated_luminosity * 0.0065 / 299973.0,
	"ZZTo4mu": integrated_luminosity * 0.077 / 1499064.0 * scale_factor_ZZ_4l,
	"ZZTo4e": integrated_luminosity * 0.077 / 1499093.0 * scale_factor_ZZ_4l,
	"ZZTo2e2mu": integrated_luminosity * 0.18 / 1497445.0 * scale_factor_ZZ_4l,
	"Run2012B_DoubleMuParked": 1.0,
	"Run2012C_DoubleMuParked": 1.0,
	"Run2012B_DoubleElectron": 1.0,
	"Run2012C_DoubleElectron": 1.0
}
