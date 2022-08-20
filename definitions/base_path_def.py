import os

"""Base path to local filesystem or to EOS containing the datasets
"""
if os.path.exists("../data/"):
    BASE_PATH = "../data"
elif os.path.exists("data/"):
    BASE_PATH = "data"
else:
    BASE_PATH = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/ForHiggsTo4Leptons"
