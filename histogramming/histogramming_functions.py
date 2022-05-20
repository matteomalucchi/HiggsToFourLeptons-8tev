import ROOT

def BookHistogram1D(rdf, variable, range_):
    """Book a histogram for a specific variable
    """
    return rdf.Histo1D(ROOT.ROOT.RDF.TH1DModel(variable, variable,\
                        range_[0], range_[1], range_[2]),\
                        variable, "Weight")

def BookHistogram2D(dataset, rdf, variables, ranges_x, ranges_y):
    """Book a histogram for a specific dataset of dataset
    """
    return rdf.Histo2D(ROOT.ROOT.RDF.TH2DModel(dataset, dataset,\
                        ranges_x[0], ranges_x[1], ranges_x[2],\
                        ranges_y[0], ranges_y[1], ranges_y[2]),\
                        variables[0], variables[1])

def WriteHistogram(h, name):
    """Write a histogram with a given name in the output file
    """
    h.SetName(name)
    h.Write()
