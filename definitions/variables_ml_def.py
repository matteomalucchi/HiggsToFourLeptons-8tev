"""List of the possible variables used for the machine learning algorithm
"""

VARIABLES_TOT_ML=["Z1_mass", "Z2_mass", "cos_theta_star", "Phi", "Phi1", "cos_theta1", "cos_theta2"]
VARIABLES_PART_ML=["cos_theta_star", "Phi", "Phi1", "cos_theta1", "cos_theta2"]
VARIABLES_HIGGS_ML=["Higgs_mass"]

VARIABLES_ML_DICT={
    "tot": VARIABLES_TOT_ML,
    "part": VARIABLES_PART_ML,
    "higgs": VARIABLES_HIGGS_ML
}