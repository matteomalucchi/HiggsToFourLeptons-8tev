import math

"""Each entry in the dictionary contains the name of the variable 
saved in the output file to be further studied as key and a tuple 
specifying the histogram details as value.
The tuple sets the number of bins, the lower edge and the upper 
edge of the histogram, as well as a human-readable label for each 
variable on the plot axis and the units of measurement (if any).
"""

VARIABLES = {
        "Weight": (),
        
        "Higgs_mass": (36, 70, 180, "Mass 4 leptons", " [GeV]"),
        "Z1_mass": (36, 40, 160, "Mass Z_{1}", " [GeV]"),
        "Z2_mass": (36, 12, 160, "Mass Z_{2}", " [GeV]"),
        "Z_close_mass": (36, 40, 160, "Mass Z_{close}", " [GeV]"),
        "Z_far_mass": (36, 12, 160, "Mass Z_{far}", " [GeV]"),
        
        "Higgs_pt": (36, 0, 100, "Pt 4 leptons", " [GeV]"),
        "Z1_pt": (36, 0, 100, "Pt Z_{1}", " [GeV]"),
        "Z2_pt": (36, 0, 100, "Pt Z_{2}", " [GeV]"),
        "Z_close_pt": (36, 0, 100, "Pt Z_{close}", " [GeV]"),
        "Z_far_pt": (36, 0, 100, "Pt Z_{far}", " [GeV]"),
        
        "Higgs_eta": (36, -4, 4, "#Eta 4 leptons", ""),
        "Z1_eta": (36, -4, 4, "#Eta Z_{1}", ""),
        "Z2_eta": (36, -4, 4, "#Eta Z_{2}", ""),
        "Z_close_eta": (36, -4, 4, "#Eta Z_{close}", ""),
        "Z_far_eta": (36, -4, 4, "#Eta Z_{far}", ""),
        
        "Higgs_phi": (36, -math.pi, math.pi, "#phi 4 leptons", ""),
        "Z1_phi": (36, -math.pi, math.pi, "#phi Z_{1}", ""),
        "Z2_phi": (36, -math.pi, math.pi, "#phi Z_{2}", ""),
        "Z_close_phi": (36, -math.pi, math.pi, "#phi Z_{close}", ""),
        "Z_far_phi": (36, -math.pi, math.pi, "#phi Z_{far}", ""),
                
        #"theta_star": (36, 0, math.pi, "#theta*", ""),
        "cos_theta_star": (36, -1, 1, "cos #theta*", ""),
        "Phi": (36, -math.pi, math.pi, "#Phi", ""),
        "Phi1": (36, -math.pi, math.pi, "#Phi_{1}", ""),
        #"theta1": (36, 0, math.pi, "#theta_{1}", ""),
        "cos_theta1": (36, -1, 1, "cos #theta_{1}", ""),
        #"theta2": (36, 0, math.pi, "#theta_{2}", ""),
        "cos_theta2": (36, -1, 1, "cos #theta_{2}", ""),
}

VARIABLES_COMPLETE = VARIABLES.copy()

# Define a new column for the DNN discriminant
VARIABLES_COMPLETE["Discriminant"] = (40, 0, 1, "DNN Discriminant", "")

VARIABLES_DICT = {
        "part" : VARIABLES,
        "tot" : VARIABLES_COMPLETE
}