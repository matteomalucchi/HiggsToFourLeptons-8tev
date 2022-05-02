import math

"""Each entry in the dictionary contains the name of the variable 
saved in the output file to be further studied as key and a tuple 
specifying the histogram details as value.
The tuple sets the number of bins, the lower edge and the upper 
edge of the histogram, as well as a human-readable label for each 
variable on the plot axis.
"""
VARIABLES_FEATURES = {
        "Weight": (),
        "Higgs_mass": (36, 70, 180, "Mass 4 leptons / GeV"),
        "Z1_mass": (36, 40, 160, "Mass Z_{1} / GeV"),
        "Z2_mass": (36, 12, 160, "Mass Z_{2} / GeV"),
        "Z_close_mass": (36, 40, 160, "Mass Z_{close} / GeV"),
        "Z_far_mass": (36, 12, 160, "Mass Z_{far} / GeV"),
        "Higgs_pt": (36, 0, 100, "Pt 4 leptons / GeV"),
        "Z1_pt": (36, 0, 100, "Pt Z_{1} / GeV"),
        "Z2_pt": (36, 0, 100, "Pt Z_{2} / GeV"),
        "Z_close_pt": (36, 0, 100, "Pt Z_{close} / GeV"),
        "Z_far_pt": (36, 0, 100, "Pt Z_{far} / GeV"),
        "theta_star": (36, 0, math.pi, "#theta*"),
        "cos_theta_star": (36, -1, 1, "cos #theta*"),
        "Phi": (36, -math.pi, math.pi, "#Phi"),
        "Phi1": (36, -math.pi, math.pi, "#Phi_{1}"),
        "theta1": (36, 0, math.pi, "#theta_{1}"),
        "cos_theta1": (36, -1, 1, "cos #theta_{1}"),
        "theta2": (36, 0, math.pi, "#theta_{2}"),
        "cos_theta2": (36, -1, 1, "cos #theta_{2}"),
}

"""
VARIABLES_FEATURES = {
        "Weight": (),
        "theta_star": (36, -1, math.pi+1, "#theta*"),
        "cos_theta_star": (36, -2, 2, "cos #theta*"),
        "Phi": (36, -math.pi-1, math.pi+1, "#Phi"),
        "Phi1": (36, -math.pi-1, math.pi+1, "#Phi_{1}"),
        "theta1": (36, -1,math.pi+1, "#theta_{1}"),
        "cos_theta1": (36, -2, 2, "cos #theta_{1}"),
        "theta2": (36, -1, math.pi+1, "#theta_{2}"),
        "cos_theta2": (36, -2, 2, "cos #theta_{2}"),
}
"""