"""Names of the datasets to be found in the base path and the 
final states considered in each dataset. 
The analysis searches for the decay of the Higgs boson in the
four leptons final state, which can be arranged in four electrons,
four muons or two electrons and two muons.
"""

SAMPLES={
    "Run2012B_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleMuParked": ["FourMuons", "TwoMuonsTwoElectrons"],
    "Run2012B_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"],
    "Run2012C_DoubleElectron": ["FourElectrons", "TwoMuonsTwoElectrons"],
    "SMHiggsToZZTo4L": ["FourMuons", "FourElectrons", "TwoMuonsTwoElectrons"],
    "ZZTo4mu": ["FourMuons"],
    "ZZTo4e": ["FourElectrons"],
    "ZZTo2e2mu": ["TwoMuonsTwoElectrons"],

}

