#ifndef SkimFunctionsHfile_
#define SkimFunctionsHfile_

#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;

using VecF = const RVec<float>&;
using VecI = const RVec<int>&;
using FourVec = const RVec<TLorentzVector>&;
using Idx = const RVec<RVec<int>>&; 

const auto Z_MASS = 91.2;


RVec<float> sipDef(VecF dxy, VecF dz, VecF sigma_dxy, VecF sigma_dz){
/*
 * Definition of the significance of the impact parameter sip 
 * as the ratio between the impact parameter 
 * at the point of closest approach to the vertex and its uncertainty.
*/
    auto ip=sqrt(dxy*dxy + dz*dz);
    auto sigma_ip=sqrt((sigma_dxy)*(sigma_dxy) + (sigma_dz)*(sigma_dz));
    //auto sigma_ip=sqrt((sigma_dxy*dxy/ip)*(sigma_dxy*dxy/ip) + (sigma_dz*dz/ip)*(sigma_dz*dz/ip));
    auto sip=(ip/sigma_ip);
    return sip;
};

/* 
 * Require that in at least one of the lepton couples the higher 
 * energy particle has Pt > 20 GeV while the other one Pt > 10 GeV.  
*/
bool ptCuts(VecF mu_pt, VecF el_pt){
    if (Max(mu_pt)>20 && Min(mu_pt)>10) return true;
    if (Max(el_pt)>20 && Min(el_pt)>10) return true;
    return false;
};

/*
 * Reconstruct the fourvector of the leptons.
*/
RVec<TLorentzVector> lepFourVec(VecF lep_pt, VecF lep_eta, VecF lep_phi, VecF lep_mass){
    RVec<TLorentzVector> lep_fourvecs(lep_pt.size());
    for (size_t i = 0; i < lep_pt.size(); i++) {
        TLorentzVector p;
        p.SetPtEtaPhiM(lep_pt[i], lep_eta[i], lep_phi[i], lep_mass[i]);
        lep_fourvecs[i] = p ;
    }
    return lep_fourvecs;
};

/*
 * Find the pair of leptons of the same kind 
 * whose invariant mass is closest to Z_MASS.
*/
RVec<RVec<int>> zIdxSamekind(FourVec fourvec, VecI charge){
    RVec<RVec<int>> idx(2);
    idx[0].reserve(2); 
    idx[1].reserve(2);

    //    idx[0]=ArgMin(std::abs((fourvec[idx_cmb[0]]+fourvec[idx_cmb[1]]).M()-Z_MASS))
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
            if (std::abs(Z_MASS - this_mass) < std::abs(Z_MASS - best_mass)) {
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

/*
 * Reconstruct the two Z fourvectors in the case of leptons 
 * of the same kind and sort them in ascending distance to Z mass. 
*/
RVec<TLorentzVector> zFourvecSamekind(Idx idx, FourVec fourvec) {
    RVec<TLorentzVector> z_fourvecs(2);
    for (size_t i = 0; i < 2; i++) {
        const auto i1 = idx[i][0];
        const auto i2 = idx[i][1];
        z_fourvecs[i] = fourvec[i1]+fourvec[i2];
    }
    if (std::abs(z_fourvecs[0].M() - Z_MASS) < std::abs(z_fourvecs[1].M() - Z_MASS)) {
        return z_fourvecs;
    } else {
        return Reverse(z_fourvecs);
    }
};

/*
 * Reconstruct the two Z fourvectors in the case of leptons 
 * of different kind and sort them in ascending distance to Z mass.
*/
RVec<TLorentzVector> zFourvec2mu2el(FourVec mu_fourvec, FourVec el_fourvec) {
    RVec<TLorentzVector> z_fourvecs = {mu_fourvec[0] + mu_fourvec[1], el_fourvec[0] + el_fourvec[1]};
    if (std::abs(z_fourvecs[0].M() - Z_MASS) < std::abs(z_fourvecs[1].M() - Z_MASS)) {
        return z_fourvecs;
    } else {
        return Reverse(z_fourvecs);
    }
};

/*
 * Angular separation of particles building the Z systems.
 * DeltaR(eta1, eta2, phi1, phi2)= sqrt((eta1-eta2)^2+(phi1-phi2)^2)
*/
bool filterDeltaR(Idx idx, VecF eta, VecF phi) {
    for (size_t i = 0; i < 2; i++) {
        const auto i1 = idx[i][0];
        const auto i2 = idx[i][1];
        const auto dr = DeltaR(eta[i1], eta[i2], phi[i1], phi[i2]);
        if (dr < 0.02) return false;
    }
    return true;
};

/*
 * Order idx so that the first Z is the heavier one.
*/
RVec<RVec<int>> order_idx_Z(Idx idx, FourVec fourvec) {
    if (fourvec[0].M()>fourvec[1].M()) return idx;
    return Reverse(idx);
};

/*
 * Order the leptons in the case of 4 leptons of the same kind.
*/
TLorentzVector splitLepSamekind(VecI idx_pair, FourVec fourvec, VecI charge) {
    if (charge[idx_pair[0]] == -1)  return fourvec[idx_pair[0]];
    return fourvec[idx_pair[1]];
};

/*
 * Select the lepton/anti-lepton belonging to the heavier boson Z1
 * in case of leptons of different kinds.
*/
TLorentzVector lep1(FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
    if ((fourvec_mu[0]+fourvec_mu[1]).M() > (fourvec_el[0]+fourvec_el[1]).M()){
        if (charge_mu[0] == -1) return fourvec_mu[0];
        else return fourvec_mu[1];
    } else {
        if (charge_el[0] == -1) return fourvec_el[0];
        else return fourvec_el[1];  
    }
};

/*
 * Select the lepton/anti-lepton belonging to the lighter boson Z2
 * in case of leptons of different kinds.
*/
TLorentzVector lep2(FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el) {
    if ((fourvec_mu[0]+fourvec_mu[1]).M() < (fourvec_el[0]+fourvec_el[1]).M()){
        if (charge_mu[0] == -1) return fourvec_mu[0];
        else return fourvec_mu[1];
    } else {
        if (charge_el[0] == -1) return fourvec_el[0];
        else return fourvec_el[1];  
    }
};

/*
 * Return the heavier reconstructed boson.
*/
TLorentzVector Z_heavy(FourVec fourvec) {
    if (fourvec[0].M()>fourvec[1].M()) return fourvec[0];
    return fourvec[1];
};

/*
 * Return the lighter reconstructed boson.
*/
TLorentzVector Z_light(FourVec fourvec) {
    if (fourvec[0].M()<fourvec[1].M()) return fourvec[0];
    return fourvec[1];
};

/*
 * Boost the fourvector in the frame of the given 3-vector.
*/
TLorentzVector boostFourvec(TLorentzVector fourvec, TVector3 boost) {
    fourvec.Boost(-boost);
    return fourvec;
};

/*
 * Normalized cross product between two vector.
*/
TVector3 crossNorm(TVector3 vec1, TVector3 vec2) {
    return vec1.Cross(vec2) * pow((vec1.Cross(vec2)).Mag(),-1);
};

/*
 * Definition of angles Phi and Phi1 as explained in [Phys.Rev.D86:095031,2012].
*/
float defPhi(TVector3 momentum, TVector3 vec1, TVector3 vec2) {
    return momentum.Dot(vec1.Cross(vec2)) *
                            pow(std::abs(momentum.Dot(vec1.Cross(vec2))),-1) * acos(vec1.Dot(vec2));
}; 

/*
 * Definition of angles theta_star, theta1 and theta2 as explained in [Phys.Rev.D86:095031,2012].
*/
float defTheta(TVector3 vec1, TVector3 vec2) {
    return acos(-vec1.Dot(vec2) * pow(vec1.Mag()*vec2.Mag(),-1));
}; 

/*
 * Definition of cos(theta_star), cos(theta1) and cos(theta2).
*/
float defCosTheta(TVector3 vec1, TVector3 vec2) {
    return -vec1.Dot(vec2) * pow(vec1.Mag()*vec2.Mag(),-1);
};  

#endif