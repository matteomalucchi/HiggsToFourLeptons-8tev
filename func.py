import ROOT

def eventSelection(rdf, final_state):
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
        using Vec = const ROOT::RVec<float>&;
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

        
        """def ptCuts(mu_pt, el_pt):
            if (ROOT.ROOT.VecOps.Max(mu_pt) > 20 and ROOT.ROOT.VecOps.Min(mu_pt) > 10): 
                return True
            if (ROOT.ROOT.VecOps.Max(el_pt) > 20 and ROOT.ROOT.VecOps.Min(el_pt) > 10): 
                return True
            return False
        
        def drCuts(mu_eta, mu_phi, el_eta, el_phi):
            mu_dr = ROOT.ROOT.VecOps.DeltaR(mu_eta[0], mu_eta[1], mu_phi[0], mu_phi[1])
            el_dr = ROOT.ROOT.VecOps.DeltaR(el_eta[0], el_eta[1], el_phi[0], el_phi[1])
            if (mu_dr < 0.02 or el_dr < 0.02): 
                return False
            return True
                          .Filter(ptCuts, {"Muon_pt", "Electron_pt"},
                          "Pt cuts")\
                  .Filter(drCuts, {"Muon_eta", "Muon_phi", "Electron_eta", "Electron_phi"},
                          "Delta R cuts")\
        """
    else: raise RuntimeError("Unknown final state --> {}".format(final_state))

def fourVec(rdf, final_state):
    z_mass = 91.2
    ROOT.gInterpreter.ProcessLine('''
    using Vec = const ROOT::RVec<float>&;
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
    if final_state == "FourMuons":
        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")
    if final_state == "FourElectrons":
        rdf_fv = rdf.Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")
    if final_state == "TwoMuonsTwoElectrons":
        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                    .Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")

    return rdf_fv