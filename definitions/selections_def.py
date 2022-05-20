""" The keys of the dictionary specify wheter or not the events 
are requested to have a DNN discriminant above the 0.5 threshold,
while the values specify the name of the tree where the data are stored.
"""
SELECTIONS = {
    "NoSelection" : "Events",
    "DNNSelection" : "EventsDNNSelection",
}