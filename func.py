import ROOT

def EventSelection(rdf, final_state):
    """ minimal selection of the events
    """
    ROOT.gInterpreter.ProcessLine('''
        using Vec = const ROOT::RVec<float>&;
        auto sipDef= [] (Vec dxy, Vec dz, Vec sigma_dxy, Vec sigma_dz){
            auto ip=sqrt(dxy*dxy + dz*dz);
            auto sigma_ip=sqrt((sigma_dxy*dxy/ip)*(sigma_dxy*dxy/ip) + (sigma_dz*dz/ip)*(sigma_dz*dz/ip));
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
    """reconstruct four vector for leptons z and higgs
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
    auto zIdxSamekind = [&z_mass](FourVec fourvec, VecI charge){
        ROOT::RVec<ROOT::RVec<int>> idx(2);
        idx[0].reserve(2); 
        idx[1].reserve(2);
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
        for (size_t i = 0; i < 4; i++) {
            if (i != best_i1 && i != best_i2) {
                idx[1].emplace_back(i);
            }
        }
        return idx;
    };
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
    auto zFourvec2mu2el = [&z_mass](FourVec mu_fourvec, FourVec el_fourvec) {
        ROOT::RVec<TLorentzVector> z_fourvecs = {mu_fourvec[0] + mu_fourvec[1], el_fourvec[0] + el_fourvec[1]};
        if (std::abs(z_fourvecs[0].M() - z_mass) < std::abs(z_fourvecs[1].M() - z_mass)) {
            return z_fourvecs;
        } else {
            return ROOT::VecOps::Reverse(z_fourvecs);
        }
    };
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
        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                    .Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")\
                    .Define("Z_fourvecs",
                            "zFourvec2mu2el(Muon_fourvec, Electron_fourvec)")

    else: raise RuntimeError("Unknown final state --> {}".format(final_state))

    df_cut = rdf_fv.Filter("Z_fourvecs[0].M() > 40 && Z_fourvecs[0].M() < 120",
                                 "Mass of first Z candidate in [40, 120]")\
                         .Filter("Z_fourvecs[1].M() > 12 && Z_fourvecs[1].M() < 120",
                                 "Mass of second Z candidate in [12, 120]")
    return df_cut.Define("Higgs_fourvec",
                         "Z_fourvecs[0] + Z_fourvecs[1]")

def OrderFourVec(rdf, final_state):
    """put the four vectors in order
    """
    ROOT.gInterpreter.ProcessLine('''    
    const auto z_mass = 91.2;
    auto splitLepSamekind = [](const ROOT::RVec<int>& idx_pair, FourVec fourvec, VecI charge) {
        if (charge[idx_pair[0]] == -1)  return fourvec[idx_pair[0]];
        return fourvec[idx_pair[1]];
    };
    auto lep1 = [&z_mass](FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
        if (std::abs((fourvec_mu[0]+fourvec_mu[1]).M() - z_mass) < std::abs((fourvec_el[0]+fourvec_el[1]).M() - z_mass)) {
            if (charge_mu[0] == -1) return fourvec_mu[0];
            else return fourvec_mu[1];
        } else {
            if (charge_el[0] == -1) return fourvec_el[0];
            else return fourvec_el[1];  
        }
    };
    auto lep2 = [&z_mass](FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
        if (std::abs((fourvec_mu[0]+fourvec_mu[1]).M() - z_mass) > std::abs((fourvec_el[0]+fourvec_el[1]).M() - z_mass)) {
            if (charge_mu[0] == -1) return fourvec_mu[0];
            else return fourvec_mu[1];
        } else {
            if (charge_el[0] == -1) return fourvec_el[0];
            else return fourvec_el[1];  
        }
    };
    ''')

    if final_state == "FourMuons":
        return rdf.Define("Lep11_fourvec",
                          "splitLepSamekind(Z_idx[0], Muon_fourvec, Muon_charge)" )\
                  .Define("Lep12_fourvec",
                          "splitLepSamekind(Z_idx[0], Muon_fourvec, -Muon_charge)" )\
                  .Define("Lep21_fourvec",
                          "splitLepSamekind(Z_idx[1], Muon_fourvec, Muon_charge)" )\
                  .Define("Lep22_fourvec",
                          "splitLepSamekind(Z_idx[1], Muon_fourvec, -Muon_charge)" )\
                  .Define("Z1_fourvec",
                          "Z_fourvecs[0]")\
                  .Define("Z2_fourvec", 
                          "Z_fourvecs[1]")                      
    
    elif final_state == "FourElectrons":
        return rdf.Define("Lep11_fourvec",
                          "splitLepSamekind(Z_idx[0], Electron_fourvec, Electron_charge)" )\
                  .Define("Lep12_fourvec",
                          "splitLepSamekind(Z_idx[0], Electron_fourvec, -Electron_charge)" )\
                  .Define("Lep21_fourvec",
                          "splitLepSamekind(Z_idx[1], Electron_fourvec, Electron_charge)" )\
                  .Define("Lep22_fourvec",
                          "splitLepSamekind(Z_idx[1], Electron_fourvec, -Electron_charge)" )\
                  .Define("Z1_fourvec",
                          "Z_fourvecs[0]")\
                  .Define("Z2_fourvec",
                          "Z_fourvecs[1]")                           
    
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
                          "Z_fourvecs[0]")\
                  .Define("Z2_fourvec",
                          "Z_fourvecs[1]") 
    
    else: raise RuntimeError("Unknown final state --> {}".format(final_state))

def AddEventWeight(rdf, sample_name):
    """add weights for the normalisation of the simulated samples
    """
    if sample_name == "SMHiggsToZZTo4L":
        return rdf.Define("Weight", "0.0065 / 299973.0 * (11.58 * 1000.0)")

    elif sample_name == "ZZTo4mu":
        return rdf.Define("Weight", "0.077 / 1499064.0 * (11.58 * 1000.0) * 1.386")

    elif sample_name == "ZZTo4e":
        return rdf.Define("Weight", "0.077 / 1499093.0 * (11.58 * 1000.0) * 1.386")

    elif sample_name == "ZZTo2e2mu":
        return rdf.Define("Weight", "0.18 / 1497445.0 * (11.58 * 1000.0) * 1.386")

    else: return rdf.Define("Weight", "1.0")