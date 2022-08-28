""" Definitions of the functions used in the skimming step of the analysis.
"""

from Definitions.weights_def import  WEIGHTS


def event_selection(rdf, final_state):
    """ Minimal selection of the events.

    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :param final_state: Final state to be analysed
    :type final_state: str
    :raises RuntimeError: Raised when an unknown final state is passed
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """

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

    if final_state == "FourElectrons":
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
                  .Filter("All(Electron_3d_sip<4) && All(abs(Electron_dxy)<0.5) \
                          && All(abs(Electron_dz)<1.0)",
                          "Electrons originate from the same primary vertex")

    if final_state == "TwoMuonsTwoElectrons":
        return rdf.Filter("nMuon==2 && nElectron==2",
                          "Two muons and two electrons")\
                  .Filter("Sum(Electron_charge)==0 && Sum(Muon_charge)==0",
                          "Two opposite charged electron and muon pairs")\
                  .Filter("All(abs(Electron_eta)<2.5) && All(abs(Muon_eta)<2.4)",
                          "Eta cuts")\
                  .Filter("All(abs(Muon_pfRelIso04_all)<0.40) && \
                          All(abs(Electron_pfRelIso03_all)<0.40)",
                          "Require good isolation")\
                  .Filter("ptCuts(Muon_pt, Electron_pt)", "Pt cuts")\
                  .Define("Muon_dr",
                          "ROOT::VecOps::DeltaR(Muon_eta[0], Muon_eta[1], \
                           Muon_phi[0], Muon_phi[1])")\
                  .Define("Electron_dr",
                          "ROOT::VecOps::DeltaR(Electron_eta[0], Electron_eta[1], \
                          Electron_phi[0], Electron_phi[1])")\
                  .Filter("Muon_dr>0.02 && Electron_dr>0.02",
                          "Delta R cuts")\
                  .Define("Muon_3d_sip",
                          "sipDef(Muon_dxy, Muon_dz, Muon_dxyErr, Muon_dzErr)")\
                  .Filter("All(Muon_3d_sip<4) && All(abs(Muon_dxy)<0.5) && All(abs(Muon_dz)<1.0)",
                          "Muons originate from the same primary vertex")\
                  .Define("Electron_3d_sip",
                          "sipDef(Electron_dxy, Electron_dz, Electron_dxyErr, Electron_dzErr)")\
                  .Filter("All(Electron_3d_sip<4) && All(abs(Electron_dxy)<0.5) \
                          && All(abs(Electron_dz)<1.0)",
                          "Electrons originate from the same primary vertex")\

    raise RuntimeError(f"Unknown final state --> {final_state}")

def four_vec(rdf, final_state):
    """Reconstruct fourvector for leptons, Z and Higgs candidates.

    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :param final_state: Final state to be analysed
    :type final_state: str
    :raises RuntimeError: Raised when an unknown final state is passed
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """

    # Reconstruct the ZZ system for all final states
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

        # With two muons and two electrons, the reconstruction is trivial
        # (each Z is built from two of the same kind).

        rdf_fv = rdf.Define("Muon_fourvec",
                            "lepFourVec(Muon_pt, Muon_eta, Muon_phi, Muon_mass)")\
                    .Define("Electron_fourvec",
                            "lepFourVec(Electron_pt, Electron_eta, Electron_phi, Electron_mass)")\
                    .Define("Z_fourvecs",
                            "zFourvec2mu2el(Muon_fourvec, Electron_fourvec)")

    else: raise RuntimeError(f"Unknown final state --> {final_state}")

    # Apply cut on the reconstructed Z masses
    df_cut = rdf_fv.Filter("Z_fourvecs[0].M() > 40 && Z_fourvecs[0].M() < 120",
                           "Mass of first Z candidate in [40, 120]")\
                   .Filter("Z_fourvecs[1].M() > 12 && Z_fourvecs[1].M() < 120",
                           "Mass of second Z candidate in [12, 120]")

    # Sum the fourvectors of the two Z bosons and reconstruct the fourvector of Higgs boson
    return df_cut.Define("Higgs_fourvec",
                         "Z_fourvecs[0] + Z_fourvecs[1]")

def order_four_vec(rdf, final_state):
    """ Put the four vectors in order according to the following criteria:

            * Z1 = heavier boson candidate
            * Z2 = lighter boson candidate
            * Lep11 = lepton belonging to the heavier boson Z1
            * Lep12 = anti-lepton belonging to the heavier boson Z1
            * Lep21 = lepton belonging to the lighter boson Z2
            * Lep22 = anti-lepton belonging to the lighter boson Z2

    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :param final_state: Final state to be analysed
    :type final_state: str
    :raises RuntimeError: Raised when an unknown final state is passed
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """

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

    if final_state == "FourElectrons":
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

    if final_state == "TwoMuonsTwoElectrons":
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

    raise RuntimeError(f"Unknown final state --> {final_state}")

def def_mass_pt_eta_phi(rdf):
    """ Define Mass, Pt, Eta and Phi of Higgs boson and Z candidates.

    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
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
                      "Z_fourvecs[1].Pt()")\
              .Define("Higgs_eta",
                      "Higgs_fourvec.Eta()")\
              .Define("Z1_eta",
                      "Z1_fourvec.Eta()")\
              .Define("Z2_eta",
                      "Z2_fourvec.Eta()")\
              .Define("Z_close_eta",
                      "Z_fourvecs[0].Eta()")\
              .Define("Z_far_eta",
                      "Z_fourvecs[1].Eta()")\
              .Define("Higgs_phi",
                      "Higgs_fourvec.Phi()")\
              .Define("Z1_phi",
                      "Z1_fourvec.Phi()")\
              .Define("Z2_phi",
                      "Z2_fourvec.Phi()")\
              .Define("Z_close_phi",
                      "Z_fourvecs[0].Phi()")\
              .Define("Z_far_phi",
                      "Z_fourvecs[1].Phi()")

def four_vec_boost(rdf):
    """ Boost the various fourvectors in different frames.


    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """

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

def def_angles(rdf):
    """ Define the five angles that allow discrimination between signal and background.


    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """

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
                      "defPhi(Z1_HRest.Vect(), n2, -n1)")\
              .Define("Phi1",
                      "defPhi(Z1_HRest.Vect(), n1, n_coll)")\
              .Define("theta1",
                      "defTheta(Z2_Z1Rest.Vect(), Lep11_Z1Rest.Vect())")\
              .Define("cos_theta1",
                      "defCosTheta(Z2_Z1Rest.Vect(), Lep11_Z1Rest.Vect())")\
              .Define("theta2",
                      "defTheta(Z1_Z2Rest.Vect(), Lep21_Z2Rest.Vect())")\
              .Define("cos_theta2",
                      "defCosTheta(Z1_Z2Rest.Vect(), Lep21_Z2Rest.Vect())")

def add_event_weight(rdf, sample_name):
    """ Add weights for the normalisation of the simulated samples in the histograms.

    :param rdf: Input RDataFrame
    :type rdf: ROOT.RDataFrame
    :return: Output RDataFrame
    :rtype: ROOT.RDataFrame
    """
    return rdf.Define("Weight", f"{WEIGHTS[sample_name]}")
