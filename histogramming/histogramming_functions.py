""" Definitions of the functions used in the histogramming step of the analysis.
"""

import ROOT

def BookHistogram1D(rdf, variable, range_):
    """Book a 1D histogram for a specific variable.
    
    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :param variable: Name of the variable in the histogram
    :type variable: str
    :param range_: Tuple that contains the number of bins and the lower and upper limits of the histogram
    :type range_: tuple(int)
    :return: Generated histogram
    :rtype: ROOT.TH1D
    """
    return rdf.Histo1D(ROOT.ROOT.RDF.TH1DModel(variable, variable,\
                        range_[0], range_[1], range_[2]),\
                        variable, "Weight")

def BookHistogram2D(dataset, rdf, variables, ranges_x, ranges_y):
    """Book a 2D histogram for a specific variable pair of a given dataset.

    :param variable: Name of the dataset analysed
    :type variable: str    
    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :param variables: Name of the variable in the histogram
    :type variables: str
    :param range_x: Tuple that contains the number of bins and the lower and upper limits of the x axis of the histogram
    :type range_x: tuple(int)
    :param range_y: Tuple that contains the number of bins and the lower and upper limits of the y axis of the histogram
    :type range_y: tuple(int)
    :return: Generated histogram
    :rtype: ROOT.TH2D
    """
    
    return rdf.Histo2D(ROOT.ROOT.RDF.TH2DModel(dataset, dataset,\
                        ranges_x[0], ranges_x[1], ranges_x[2],\
                        ranges_y[0], ranges_y[1], ranges_y[2]),\
                        variables[0], variables[1])

def WriteHistogram(h, name):
    """Write a histogram with a given name in the output file.
    
    :param name: Name of the histogram
    :type name: str    
    :param h: Histogram to be saved
    :type h: ROOT.TH1D
    """
    
    h.SetName(name)
    h.Write()
