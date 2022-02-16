import ROOT
import time

import skim 

def FourvecBoost(rdf):
    ROOT.gInterpreter.ProcessLine('''   
    auto boostFourvec = [](TLorentzVector fourvec, TVector3 boost) {
        fourvec.Boost(-boost);
        return fourvec;
    };
    ''')
    return rdf.Define("Z1_HRest", 
                      "boostFourvec(Z1_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Z2_HRest", 
                      "boostFourvec(Z2_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Lep11_HRest", 
                      "boostFourvec(Lep11_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Lep12_HRest", 
                      "boostFourvec(Lep12_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Lep21_HRest", 
                      "boostFourvec(Lep21_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Lep22_HRest", 
                      "boostFourvec(Lep22_fourvec,Higgs_fourvec.BoostVector())")\
              .Define("Lep11_Z1Rest", 
                      "boostFourvec(Lep11_fourvec,Z1_fourvec.BoostVector())")\
              .Define("Z2_Z1Rest", 
                      "boostFourvec(Z2_fourvec,Z1_fourvec.BoostVector())")\
              .Define("Lep21_Z2Rest", 
                      "boostFourvec(Lep21_fourvec,Z2_fourvec.BoostVector())")\
              .Define("Z1_Z2Rest", 
                      "boostFourvec(Z1_fourvec,Z2_fourvec.BoostVector())")\

def DefAngles(rdf):
    ROOT.gInterpreter.ProcessLine('''   
    auto crossNorm = [](TVector3 vec1, TVector3 vec2) {
        return vec1.Cross(vec2) * pow((vec1.Cross(vec2)).Mag(),-1);
    };
    auto defAzimuthal = [](TVector3 momentum, TVector3 vec1, TVector3 vec2) {
        return momentum*vec1.Cross(vec2) * pow(std::abs(momentum*vec1.Cross(vec2)),-1) * acos(-vec1*vec2);
    }; 
    auto defTheta = [](TVector3 vec1, TVector3 vec2) {
        return acos(-vec1 * vec2 * pow(vec1.Mag()*vec2.Mag(),-1));
    };   
    ''')


    return rdf.Define("theta_star", 
                      "acos(Z1_HRest.Pz() * pow(Z1_HRest.P(),-1))")\
              .Define("n1",
                      "crossNorm(Lep11_HRest.Vect(), Lep12_HRest.Vect())")\
              .Define("n2",
                      "crossNorm(Lep21_HRest.Vect(), Lep22_HRest.Vect())")\
              .Define("n_coll",
                      "crossNorm(TVector3(0,0,1), Z1_HRest.Vect())")\
              .Define("Phi",
                      "defAzimuthal(Z1_HRest.Vect(), n1, n2)")\
              .Define("Phi1",
                      "defAzimuthal(Z1_HRest.Vect(), n1, n_coll)")\
              .Define("theta1",
                      "defTheta(Z2_Z1Rest.Vect(), Lep11_Z1Rest.Vect())")\
              .Define("theta2",
                      "defTheta(Z1_Z2Rest.Vect(), Lep21_Z2Rest.Vect())")

finalVariables = ROOT.vector("std::string")()
finalVariables.push_back("run")
finalVariables.push_back("Weight")
finalVariables.push_back("theta_star")
finalVariables.push_back("Phi")
finalVariables.push_back("Phi1")
finalVariables.push_back("theta1")
finalVariables.push_back("theta2")


if __name__ == "__main__":
    # Set up multi-threading capability of ROOT
    ROOT.ROOT.EnableImplicitMT()
    poolSize = ROOT.ROOT.GetThreadPoolSize()
    print(">>> Thread pool size for parallel processing: {}".format(poolSize))

    for sample_name, final_states in skim.samples.items():
        for final_state in final_states:
            print(">>> Process skimmed sample {} and final state {}".format(sample_name, final_state))
            rdf = ROOT.ROOT.RDataFrame("Events", "skim_data/" + sample_name + final_state + "Skim.root")
            rdf2 = FourvecBoost(rdf)
            rdf3 = DefAngles(rdf2)
            
            
            start_time = time.time()
            #print(rdf3.GetColumnNames())
            #print(rdf3.GetColumnType("theta1"))



            rdf3.Snapshot("Events", "angles/" + sample_name + final_state + "Angles.root")

            print("Execution time: %s s" %(time.time() - start_time))
