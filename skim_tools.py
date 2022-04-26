import ROOT

def EventSelection(rdf, final_state):
    """ Minimal selection of the events
    """

    """Definition of the significance of the impact parameter sip 
    as the ratio between the impact parameter 
    at the point of closest approach to the vertex and its uncertainty
    """
    ROOT.gInterpreter.ProcessLine('''
        using Vec = const ROOT::RVec<float>&;
        auto sipDef= [] (Vec dxy, Vec dz, Vec sigma_dxy, Vec sigma_dz){
            auto ip=sqrt(dxy*dxy + dz*dz);
            auto sigma_ip=sqrt((sigma_dxy)*(sigma_dxy) + (sigma_dz)*(sigma_dz));
            //auto sigma_ip=sqrt((sigma_dxy*dxy/ip)*(sigma_dxy*dxy/ip) + (sigma_dz*dz/ip)*(sigma_dz*dz/ip));
            auto sip=ip/sigma_ip;
            return sip;
        };
        ''')    

    if final_state == "FourMuons":
        return rdf.Filter("nMuon==4",
                          "Four muons")\
                  .Filter("Sum(Muon_charge==1)==2 && Sum(Muon_charge==-1)==2",
                          "Two positive and two negative muons")\
                  .Filter("All(abs(Muon_pfRelIso04_all)<0.40)",
                          "Good isolation of the muons")\
                  .Filter("All(Muon_pt>5) && All(abs(Muon_eta)<2.4)",
                          "Good muon kinematics")\
                  .Define("Muon_3d_sip",
                          "sipDef(Muon_dxy, Muon_dz, Muon_dxyErr, Muon_dzErr)")\
                  .Filter("All(Muon_3d_sip<4) && All(abs(Muon_dxy)<0.5) && All(abs(Muon_dz)<1.0)",
                          "Muons originate from the same primary vertex")

    elif final_state == "FourElectrons":
        return rdf.Filter("nElectron==4",
                          "Four electrons")\
                  .Filter("Sum(Electron_charge==1)==2 && Sum(Electron_charge==-1)==2",
                          "Two positive and two negative electrons")\
                  .Filter("All(abs(Electron_pfRelIso03_all)<0.40)",
                          "Good isolation of the electrons")\
                  .Filter("All(Electron_pt>7) && All(abs(Electron_eta)<2.5)",
                          "Good electron kinematics")\
                  .Define("Electron_3d_sip",
                          "sipDef(Electron_dxy, Electron_dz, Electron_dxyErr, Electron_dzErr)")\
                  .Filter("All(Electron_3d_sip<4) && All(abs(Electron_dxy)<0.5) && All(abs(Electron_dz)<1.0)",
                          "Electrons originate from the same primary vertex")

    elif final_state == "TwoMuonsTwoElectrons":        
        ROOT.gInterpreter.ProcessLine('''
            auto ptCuts= [] (Vec mu_pt, Vec el_pt){
                if (ROOT::VecOps::Max(mu_pt)>20 && ROOT::VecOps::Min(mu_pt)>10) return true;
                if (ROOT::VecOps::Max(el_pt)>20 && ROOT::VecOps::Min(el_pt)>10) return true;
                return false;
            };
        ''')
        return rdf.Filter("nMuon==2 && nElectron==2",
                          "Two muons and two electrons")\
                  .Filter("Sum(Electron_charge)==0 && Sum(Muon_charge)==0",
                          "Two opposite charged electron and muon pairs")\
                  .Filter("All(abs(Electron_eta)<2.5) && All(abs(Muon_eta)<2.4)",
                          "Eta cuts")\
                  .Filter("All(abs(Muon_pfRelIso04_all)<0.40) && All(abs(Electron_pfRelIso03_all)<0.40)",
                          "Require good isolation")\
                  .Filter("ptCuts(Muon_pt, Electron_pt)", "Pt cuts")\
                  .Define("Muon_dr",
                          "ROOT::VecOps::DeltaR(Muon_eta[0], Muon_eta[1], Muon_phi[0], Muon_phi[1])")\
                  .Define("Electron_dr",
                          "ROOT::VecOps::DeltaR(Electron_eta[0], Electron_eta[1], Electron_phi[0], Electron_phi[1])")\
                  .Filter("Muon_dr>0.02 && Electron_dr>0.02",
                          "Delta R cuts")\
                  .Define("Muon_3d_sip",
                          "sipDef(Muon_dxy, Muon_dz, Muon_dxyErr, Muon_dzErr)")\
                  .Filter("All(Muon_3d_sip<4) && All(abs(Muon_dxy)<0.5) && All(abs(Muon_dz)<1.0)",
                          "Muons originate from the same primary vertex")\
                  .Define("Electron_3d_sip",
                          "sipDef(Electron_dxy, Electron_dz, Electron_dxyErr, Electron_dzErr)")\
                  .Filter("All(Electron_3d_sip<4) && All(abs(Electron_dxy)<0.5) && All(abs(Electron_dz)<1.0)",
                          "Electrons originate from the same primary vertex")\

    else: raise RuntimeError("Unknown final state --> {}".format(final_state))

def FourVec(rdf, final_state):
    """Reconstruct fourvector for leptons z and higgs
    """

    """Reconstruct the fourvector of the leptons
    """
    ROOT.gInterpreter.ProcessLine('''
        const auto z_mass = 91.2;
        using VecI = const ROOT::RVec<int>&;
        using FourVec = const ROOT::RVec<TLorentzVector>&;
        using Idx = const ROOT::RVec<ROOT::RVec<int>>&; 
        auto lepFourVec = [] (Vec lep_pt, Vec lep_eta, Vec lep_phi, Vec lep_mass){
            ROOT::RVec<TLorentzVector> lep_fourvecs(lep_pt.size());
            for (size_t i = 0; i < lep_pt.size(); i++) {
                TLorentzVector p;
                p.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], lep_mass[i]);
                lep_fourvecs[i] = p ;
            }
            return lep_fourvecs;
        };
    ''')

    """Find the pair of leptons of the same kind whose invariant mass is closest to z_mass
    """
    ROOT.gInterpreter.ProcessLine('''
        const auto z_mass = 91.2;

        auto zIdxSamekind = [&z_mass](FourVec fourvec, VecI charge){
            ROOT::RVec<ROOT::RVec<int>> idx(2);
            idx[0].reserve(2); 
            idx[1].reserve(2);

            // Find first lepton pair with invariant mass closest to Z mass
            auto idx_cmb = Combinations(fourvec, 2);
            auto best_mass = -1;
            size_t best_i1 = 0; 
            size_t best_i2 = 0;
            for (size_t i = 0; i < idx_cmb[0].size(); i++) {
                const auto i1 = idx_cmb[0][i];
                const auto i2 = idx_cmb[1][i];
                if (charge[i1] != charge[i2]) {
                    const auto this_mass = (fourvec[i1] + fourvec[i2]).M();
                    if (std::abs(z_mass - this_mass) < std::abs(z_mass - best_mass)) {
                        best_mass = this_mass;
                        best_i1 = i1;
                        best_i2 = i2;
                    }
                }
            }
            idx[0].emplace_back(best_i1);
            idx[0].emplace_back(best_i2);

            // Reconstruct second Z from remaining lepton pair
            for (size_t i = 0; i < fourvec.size(); i++) {
                if (i != best_i1 && i != best_i2) {
                    idx[1].emplace_back(i);
                }
            }

            // Return indices of the pairs building two Z bosons
            return idx;
        };
    ''')

    """Reconstruct the two Z fourvectors in the case of leptons of the same kind
    and sort them in ascending distance to Z mass.
    """
    ROOT.gInterpreter.ProcessLine('''
        const auto z_mass = 91.2;

        auto zFourvecSamekind = [&z_mass](Idx idx, FourVec fourvec) {
            ROOT::RVec<TLorentzVector> z_fourvecs(2);
            for (size_t i = 0; i < 2; i++) {
                const auto i1 = idx[i][0];
                const auto i2 = idx[i][1];
                z_fourvecs[i] = fourvec[i1]+fourvec[i2];
            }
            if (std::abs(z_fourvecs[0].M() - z_mass) < std::abs(z_fourvecs[1].M() - z_mass)) {
                return z_fourvecs;
            } else {
                return ROOT::VecOps::Reverse(z_fourvecs);
            }
        };
    ''')
    
    """Reconstruct the two Z fourvectors in the case of leptons of different kind
    and sort them in ascending distance to Z mass
    """
    ROOT.gInterpreter.ProcessLine('''
        const auto z_mass = 91.2;
        auto zFourvec2mu2el = [&z_mass](FourVec mu_fourvec, FourVec el_fourvec) {
            ROOT::RVec<TLorentzVector> z_fourvecs = {mu_fourvec[0] + mu_fourvec[1], el_fourvec[0] + el_fourvec[1]};
            if (std::abs(z_fourvecs[0].M() - z_mass) < std::abs(z_fourvecs[1].M() - z_mass)) {
                return z_fourvecs;
            } else {
                return ROOT::VecOps::Reverse(z_fourvecs);
            }
        };
    ''')

    """	Angular separation of particles building the Z systems
    """    
    ROOT.gInterpreter.ProcessLine('''
        auto filterDeltaR = [](Idx idx, Vec eta, Vec phi) {
            for (size_t i = 0; i < 2; i++) {
                const auto i1 = idx[i][0];
                const auto i2 = idx[i][1];
                const auto dr = ROOT::VecOps::DeltaR(eta[i1], eta[i2], phi[i1], phi[i2]);
                if (dr < 0.02) return false;
            }
            return true;
        };
    ''')

    """Reconstruct the ZZ system for all final states
    """
    if final_state == "FourMuons":
        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                    .Define("Z_idx",
                            "zIdxSamekind(Muon_fourvec, Muon_charge)")\
                    .Filter("filterDeltaR(Z_idx, Muon_eta, Muon_phi)",
                            "Delta R separation of particles building the Z systems")\
                    .Define("Z_fourvecs",
                            "zFourvecSamekind(Z_idx, Muon_fourvec)")

    elif final_state == "FourElectrons":
        rdf_fv = rdf.Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")\
                    .Define("Z_idx",
                            "zIdxSamekind(Electron_fourvec, Electron_charge)")\
                    .Filter("filterDeltaR(Z_idx, Electron_eta, Electron_phi)",
                            "Delta R separation of particles building the Z systems")\
                    .Define("Z_fourvecs",
                            "zFourvecSamekind(Z_idx, Electron_fourvec)")

    elif final_state == "TwoMuonsTwoElectrons":

        """With two muons and two electrons, the reconstruction is trivial 
        (each Z is built from two of the same kind).
        """
        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                    .Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")\
                    .Define("Z_fourvecs",
                            "zFourvec2mu2el(Muon_fourvec, Electron_fourvec)")

    else: raise RuntimeError("Unknown final state --> {}".format(final_state))
    
    """Apply cut on the reconstructed Z masses
    """
    df_cut = rdf_fv.Filter("Z_fourvecs[0].M() > 40 && Z_fourvecs[0].M() < 120",
                           "Mass of first Z candidate in [40, 120]")\
                   .Filter("Z_fourvecs[1].M() > 12 && Z_fourvecs[1].M() < 120",
                           "Mass of second Z candidate in [12, 120]")

    """Sum the fourvectors of the two Z bosons and reconstruct the fourvector of Higgs boson
    """
    return df_cut.Define("Higgs_fourvec",
                         "Z_fourvecs[0] + Z_fourvecs[1]")

def OrderFourVec(rdf, final_state):
    """Put the four vectors in order according to the following criteria:
            -Z1: heavier boson
            -Z2: lighter boson
            -Lep11: lepton belonging to the heavier boson Z1
            -Lep12: anti-lepton belonging to the heavier boson Z1
            -Lep21: lepton belonging to the lighter boson Z2
            -Lep22: anti-lepton belonging to the lighter boson Z2
    """

    """Order idx so that the first Z is the heavier one.
    """
    ROOT.gInterpreter.ProcessLine('''    
        auto order_idx_Z = [](Idx idx, FourVec fourvec) {
            if (fourvec[0].M()>fourvec[1].M()) return idx;
            return ROOT::VecOps::Reverse(idx);
        };
    ''')

    """Order the leptons according to the criteria listed above 
    in the case of 4 leptons of the same kind.
    """
    ROOT.gInterpreter.ProcessLine('''
        auto splitLepSamekind = [](VecI idx_pair, FourVec fourvec, VecI charge) {
            if (charge[idx_pair[0]] == -1)  return fourvec[idx_pair[0]];
            return fourvec[idx_pair[1]];
        };
    ''')
    
    """Order the leptons according to the criteria listed above 
    in the case of lepton pairs of different kind 
    """
    ROOT.gInterpreter.ProcessLine('''
        const auto z_mass = 91.2;		
        auto lep1 = [&z_mass](FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
            if ((fourvec_mu[0]+fourvec_mu[1]).M() > (fourvec_el[0]+fourvec_el[1]).M()){
                if (charge_mu[0] == -1) return fourvec_mu[0];
                else return fourvec_mu[1];
            } else {
                if (charge_el[0] == -1) return fourvec_el[0];
                else return fourvec_el[1];  
            }
        };
        auto lep2 = [&z_mass](FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
            if ((fourvec_mu[0]+fourvec_mu[1]).M() < (fourvec_el[0]+fourvec_el[1]).M()){
                if (charge_mu[0] == -1) return fourvec_mu[0];
                else return fourvec_mu[1];
            } else {
                if (charge_el[0] == -1) return fourvec_el[0];
                else return fourvec_el[1];  
            }
        };
    ''')

    """Return the heavier reconstructed boson
    """
    ROOT.gInterpreter.ProcessLine('''
        auto Z_heavy = [](FourVec fourvec) {
            if (fourvec[0].M()>fourvec[1].M()) return fourvec[0];
            return fourvec[1];
        };
    ''')
    
    """Return the lighter reconstructed boson.
    """
    ROOT.gInterpreter.ProcessLine('''
        auto Z_light = [](FourVec fourvec) {
            if (fourvec[0].M()<fourvec[1].M()) return fourvec[0];
            return fourvec[1];
        };
    ''')

    if final_state == "FourMuons":
        return rdf.Define("Z_idx_order",
                          "order_idx_Z(Z_idx, Z_fourvecs)" )\
                  .Define("Lep11_fourvec",
                          "splitLepSamekind(Z_idx_order[0], Muon_fourvec, Muon_charge)" )\
                  .Define("Lep12_fourvec",
                          "splitLepSamekind(Z_idx_order[0], Muon_fourvec, -Muon_charge)" )\
                  .Define("Lep21_fourvec",
                          "splitLepSamekind(Z_idx_order[1], Muon_fourvec, Muon_charge)" )\
                  .Define("Lep22_fourvec",
                          "splitLepSamekind(Z_idx_order[1], Muon_fourvec, -Muon_charge)" )\
                  .Define("Z1_fourvec",
                          "Z_heavy(Z_fourvecs)")\
                  .Define("Z2_fourvec",
                          "Z_light(Z_fourvecs)")                  
    
    elif final_state == "FourElectrons":
        return rdf.Define("Z_idx_order",
                          "order_idx_Z(Z_idx, Z_fourvecs)" )\
                  .Define("Lep11_fourvec",
                          "splitLepSamekind(Z_idx_order[0], Electron_fourvec, Electron_charge)" )\
                  .Define("Lep12_fourvec",
                          "splitLepSamekind(Z_idx_order[0], Electron_fourvec, -Electron_charge)" )\
                  .Define("Lep21_fourvec",
                          "splitLepSamekind(Z_idx_order[1], Electron_fourvec, Electron_charge)" )\
                  .Define("Lep22_fourvec",
                          "splitLepSamekind(Z_idx_order[1], Electron_fourvec, -Electron_charge)" )\
                  .Define("Z1_fourvec",
                          "Z_heavy(Z_fourvecs)")\
                  .Define("Z2_fourvec",
                          "Z_light(Z_fourvecs)")                             
    
    elif final_state == "TwoMuonsTwoElectrons":
        return rdf.Define("Lep11_fourvec",
                          "lep1(Muon_fourvec, Electron_fourvec, Muon_charge, Electron_charge)" )\
                  .Define("Lep12_fourvec",
                          "lep1(Muon_fourvec, Electron_fourvec, -Muon_charge, -Electron_charge)" )\
                  .Define("Lep21_fourvec",
                          "lep2(Muon_fourvec, Electron_fourvec, Muon_charge, Electron_charge)" )\
                  .Define("Lep22_fourvec",
                          "lep2(Muon_fourvec, Electron_fourvec, -Muon_charge, -Electron_charge)" )\
                  .Define("Z1_fourvec",
                          "Z_heavy(Z_fourvecs)")\
                  .Define("Z2_fourvec",
                          "Z_light(Z_fourvecs)")   

    else: raise RuntimeError("Unknown final state --> {}".format(final_state))

def DefMassPt(rdf):
    """ Define mass and pt of Higgs boson and Z 
    """
    return rdf.Define("Higgs_mass",
                      "Higgs_fourvec.M()")\
              .Define("Z1_mass",
                      "Z1_fourvec.M()")\
              .Define("Z2_mass",
                      "Z2_fourvec.M()")\
              .Define("Z_close_mass",
                      "Z_fourvecs[0].M()")\
              .Define("Z_far_mass",
                      "Z_fourvecs[1].M()")\
              .Define("Higgs_pt",
                      "Higgs_fourvec.Pt()")\
              .Define("Z1_pt",
                      "Z1_fourvec.Pt()")\
              .Define("Z2_pt",
                      "Z2_fourvec.Pt()")\
              .Define("Z_close_pt",
                      "Z_fourvecs[0].Pt()")\
              .Define("Z_far_pt",
                      "Z_fourvecs[1].Pt()")

def FourvecBoost(rdf):
    """ Boost the various fourvectors in different frames.
    """

    """Boost the fourvector in the frame of the given 3vector.
    """
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
    """ Define the five angles that allow discrimination between signal and background
    """

    """Normalized cross product between two vector
    """
    ROOT.gInterpreter.ProcessLine('''   
        auto crossNorm = [](TVector3 vec1, TVector3 vec2) {
            return vec1.Cross(vec2) * pow((vec1.Cross(vec2)).Mag(),-1);
        };
    ''')

    """Definition of the angles as explained in [Phys.Rev.D86:095031,2012]
    """
    ROOT.gInterpreter.ProcessLine(''' 
        auto defAzimuthal = [](TVector3 momentum, TVector3 vec1, TVector3 vec2) {
            return momentum.Dot(vec1.Cross(vec2)) *
                                 pow(std::abs(momentum.Dot(vec1.Cross(vec2))),-1) * acos(vec1.Dot(vec2));
        }; 
        auto defTheta = [](TVector3 vec1, TVector3 vec2) {
            return acos(-vec1.Dot(vec2) * pow(vec1.Mag()*vec2.Mag(),-1));
        }; 
        auto defCosTheta = [](TVector3 vec1, TVector3 vec2) {
            return -vec1.Dot(vec2) * pow(vec1.Mag()*vec2.Mag(),-1);
        };   
    ''')
    
    return rdf.Define("theta_star", 
                      "acos(Z1_HRest.Pz() * pow(Z1_HRest.P(),-1))")\
              .Define("cos_theta_star", 
                      "Z1_HRest.Pz() * pow(Z1_HRest.P(),-1)")\
              .Define("n1",
                      "crossNorm(Lep11_HRest.Vect(), Lep12_HRest.Vect())")\
              .Define("n2",
                      "crossNorm(Lep21_HRest.Vect(), Lep22_HRest.Vect())")\
              .Define("n_coll",
                      "crossNorm(TVector3(0,0,1), Z1_HRest.Vect())")\
              .Define("Phi",
                      "defAzimuthal(Z1_HRest.Vect(), n2, -n1)")\
              .Define("Phi1",
                      "defAzimuthal(Z1_HRest.Vect(), n1, n_coll)")\
              .Define("theta1",
                      "defTheta(Z2_Z1Rest.Vect(), Lep11_Z1Rest.Vect())")\
              .Define("cos_theta1",
                      "defCosTheta(Z2_Z1Rest.Vect(), Lep11_Z1Rest.Vect())")\
              .Define("theta2",
                      "defTheta(Z1_Z2Rest.Vect(), Lep21_Z2Rest.Vect())")\
              .Define("cos_theta2",
                      "defCosTheta(Z1_Z2Rest.Vect(), Lep21_Z2Rest.Vect())")  

def AddEventWeight(rdf, sample_name):
    """ Add weights for the normalisation of the simulated samples in the histograms.
        The event weight reweights the full dataset so that the sum of the weights
        is equal to the expected number of events in data. The expectation is given by
        multiplying the integrated luminosity (11.58 fb^-1) of the data with the cross-section of
        the process in the datasets divided by the number of simulated events. The simulated
        background datasets are further multiplied by a scale factor which acts as a 
        correction of the simulation.
    """
    if sample_name == "SMHiggsToZZTo4L":
        return rdf.Define("Weight", "(11.58 * 1000.0) * 0.0065 / 299973.0 ")

    elif sample_name == "ZZTo4mu":
        return rdf.Define("Weight", "(11.58 * 1000.0) * 0.077 / 1499064.0 * 1.386")

    elif sample_name == "ZZTo4e":
        return rdf.Define("Weight", "(11.58 * 1000.0) * 0.077 / 1499093.0 * 1.386")

    elif sample_name == "ZZTo2e2mu":
        return rdf.Define("Weight", "(11.58 * 1000.0) * 0.18 / 1497445.0 * 1.386")

    else: return rdf.Define("Weight", "1.0")

