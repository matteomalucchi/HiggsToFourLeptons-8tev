#ifndef TestVariablesHfile_
#define TestVariablesHfile_

#include <cmath>

#include "ROOT/RVec.hxx"

using namespace ROOT::VecOps;

// Electron mass [GeV]
const float EL_MASS=0.511/1000;

// Muon mass [GeV] 
const float MU_MASS=106/1000;

// Sip definition
RVec<float> dxy{1.}, dz{1.}, sigma_dxy{0.1}, sigma_dz{0.1}, sip{10.};

// Pt cuts
RVec<float> mu_pt{30,15}, e_pt{30,15}, not_mu_pt{30,5}, not_e_pt{15,13};

// Lepton fourvectors
RVec<float> lep_pt{1.}, lep_eta{0.}, lep_phi{0.}, lep_mass{EL_MASS};
TLorentzVector v(1., 0., 0., sqrt(EL_MASS*EL_MASS+1*1));
RVec<TLorentzVector> lep_fourvec{v};

// Z index same kind + slip lepton same kind
TLorentzVector el0(10., 0., 0., sqrt(EL_MASS*EL_MASS+10*10));
TLorentzVector el1(-15., 0., 0., sqrt(EL_MASS*EL_MASS+15*15));
TLorentzVector el2(50., 0., 0., sqrt(EL_MASS*EL_MASS+50*50));
TLorentzVector el3(-45., 0., 0., sqrt(EL_MASS*EL_MASS+45*45));
RVec<TLorentzVector> el_fourvecs_4{el0, el1, el2, el3};
RVec<int> el_charges{1, -1, 1, -1};
RVec<RVec<int>> el_idx{{2,3}, {0,1}};

// Z fourvectors same kind
TLorentzVector z0(el0.Px()+el1.Px(), 0., 0., el0.E()+el1.E());
TLorentzVector z1(el2.Px()+el3.Px(), 0., 0., el2.E()+el3.E());
RVec<TLorentzVector> z_fourvecs_4{z1, z0};

// Z fourvectors different kind + lep1 + lep2
TLorentzVector mu0(10., 0., 0., sqrt(MU_MASS*MU_MASS+10*10));
TLorentzVector mu1(-15., 0., 0., sqrt(MU_MASS*MU_MASS+15*15));
RVec<TLorentzVector> mu_fourvecs_2{mu0, mu1};
RVec<TLorentzVector> el_fourvecs_2{el2, el3};
TLorentzVector z2(mu0.Px()+mu1.Px(), 0., 0., mu0.E()+mu1.E());
RVec<TLorentzVector> z_fourvecs_2{z1, z2};

// Delta R
RVec<float> eta{0., 1., 2., 3.}, not_eta{0., 1., 2., 2.00001} ;
RVec<float> phi{0., 1., 2., 3.}, not_phi{0., 1., 2., 2.00001} ;


// Order Z idx
RVec<TLorentzVector>  rev_z_fourvecs_4 = Reverse(z_fourvecs_4);
RVec<RVec<int>> rev_el_idx = Reverse(el_idx);

// lep1 + lep2
RVec<int> el_charges_2{1, -1};
RVec<int> mu_charges_2{-1, 1};

// Boost fourvector
TVector3 v_long(0.5, 0, 0);
TVector3 v_trasv(0, 0.5, 0);
float beta_boost=v_long.Mag();
float gamma_boost = 1 / sqrt(1-beta_boost*beta_boost);
TLorentzVector el0_boost_long(gamma_boost*(el0.Px()-beta_boost*el0.E()), 
                    0., 0.,gamma_boost*(el0.E()-beta_boost*el0.Px()));
TLorentzVector el0_boost_trasv(el0.Px(), 
                    -gamma_boost*beta_boost*el0.E(), 0.,gamma_boost*el0.E());

// Cross product
TVector3 v_cross(0, 0, 1);

// Phi definition
TVector3 v1(1/sqrt(2), 1/sqrt(2), 0);
TVector3 v2(1, 0, 0);
TVector3 v3(0, 0, 1/sqrt(2));
float phi_angle = - M_PI / 4;

// Theta definition
TVector3 v4(0, 1, 1);
TVector3 v5(1, 1,0);
float theta_angle = 2./3 * M_PI;

// Cos theta definition
float cos_theta_angle = -1./2;

#endif