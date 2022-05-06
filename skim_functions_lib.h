#ifndef SkimFunctionsLibHfile_
#define SkimFunctionsLibHfile_

#include <ROOT/RVec.hxx>
#include <TLorentzVector.h>

using namespace ROOT::VecOps;

using VecF = const RVec<float>&;
using VecI = const RVec<int>&;
using FourVec = const RVec<TLorentzVector>&;
using Idx = const RVec<RVec<int>>&; 


/*
 * Definition of the significance of the impact parameter sip 
 * as the ratio between the impact parameter 
 * at the point of closest approach to the vertex and its uncertainty.
*/
RVec<float> sipDef(VecF dxy, VecF dz, VecF sigma_dxy, VecF sigma_dz);

/* 
 * Require that in at least one of the lepton couples the higher 
 * energy particle has Pt > 20 GeV while the other one Pt > 10 GeV.  
*/
bool ptCuts(VecF mu_pt, VecF el_pt);

/*
 * Reconstruct the fourvector of the leptons.
*/
RVec<TLorentzVector> lepFourVec(VecF lep_pt, VecF lep_eta, VecF lep_phi, VecF lep_mass);

/*
 * Find the pair of leptons of the same kind 
 * whose invariant mass is closest to Z_MASS.
*/
RVec<RVec<int>> zIdxSamekind(FourVec fourvec, VecI charge);

/*
 * Reconstruct the two Z fourvectors in the case of leptons 
 * of the same kind and sort them in ascending distance to Z mass. 
*/
RVec<TLorentzVector> zFourvecSamekind(Idx idx, FourVec fourvec);

/*
 * Reconstruct the two Z fourvectors in the case of leptons 
 * of different kind and sort them in ascending distance to Z mass.
*/
RVec<TLorentzVector> zFourvec2mu2el(FourVec mu_fourvec, FourVec el_fourvec);

/*
 * Angular separation of particles building the Z systems.
 * DeltaR(eta1, eta2, phi1, phi2)= sqrt((eta1-eta2)^2+(phi1-phi2)^2)
*/
bool filterDeltaR(Idx idx, VecF eta, VecF phi);

/*
 * Order idx so that the first Z is the heavier one.
*/
RVec<RVec<int>> order_idx_Z(Idx idx, FourVec fourvec);

/*
 * Order the leptons in the case of 4 leptons of the same kind.
*/
TLorentzVector splitLepSamekind(VecI idx_pair, FourVec fourvec, VecI charge);

/*
 * Select the lepton/anti-lepton belonging to the heavier boson Z1
 * in case of leptons of different kinds.
*/
TLorentzVector lep1(FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el);

/*
 * Select the lepton/anti-lepton belonging to the lighter boson Z2
 * in case of leptons of different kinds.
*/
TLorentzVector lep2(FourVec fourvec_mu, FourVec fourvec_el, VecI charge_mu, VecI charge_el);

/*
 * Return the heavier reconstructed boson.
*/
TLorentzVector Z_heavy(FourVec fourvec);

/*
 * Return the lighter reconstructed boson.
*/
TLorentzVector Z_light(FourVec fourvec);

/*
 * Boost the fourvector in the frame of the given 3-vector.
*/
TLorentzVector boostFourvec(TLorentzVector fourvec, TVector3 boost);

/*
 * Normalized cross product between two vector.
*/
TVector3 crossNorm(TVector3 vec1, TVector3 vec2);

/*
 * Definition of angles Phi and Phi1 as explained in [Phys.Rev.D86:095031,2012].
*/
float defPhi(TVector3 momentum, TVector3 vec1, TVector3 vec2); 

/*
 * Definition of angles theta_star, theta1 and theta2 as explained in [Phys.Rev.D86:095031,2012].
*/
float defTheta(TVector3 vec1, TVector3 vec2); 

/*
 * Definition of cos(theta_star), cos(theta1) and cos(theta2).
*/
float defCosTheta(TVector3 vec1, TVector3 vec2);  

#endif