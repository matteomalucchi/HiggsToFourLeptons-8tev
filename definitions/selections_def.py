""" The keys of the dictionary specify wheter or not the events 
are requested to have a DNN discriminant above the 0.5 threshold,
while the values specify the directory and name of the samples.
"""



SELECTIONS = {
    "NoSelection" : ("machine_learning/ML_data", "ML"),
    "DiscriminantSelection" : ("machine_learning/ML_selection_data", "MLSelection"),
}