import unittest
import ROOT

ROOT.gInterpreter.ProcessLine('#include "../skim_functions.h"' )
ROOT.gInterpreter.ProcessLine('#include "test_variables.h"' )

class TestSkim(unittest.TestCase):

    def test_sip(self):
        """Test the definition of sip
        """
        self.assertAlmostEqual(ROOT.sipDef(
            ROOT.dxy, ROOT.dz, ROOT.sigma_dxy, ROOT.sigma_dz)[0], ROOT.sip[0], 5)

    def test_pt_cuts(self):
        """Test the lepton pt cuts 
        """
        self.assertTrue(ROOT.ptCuts(ROOT.mu_pt, ROOT.e_pt))
        self.assertTrue(ROOT.ptCuts(ROOT.mu_pt, ROOT.not_e_pt))
        self.assertTrue(ROOT.ptCuts(ROOT.not_mu_pt, ROOT.e_pt))
        self.assertFalse(ROOT.ptCuts(ROOT.not_mu_pt, ROOT.not_e_pt))

    def test_lep_fourvec(self):
        """Test the reconstruction of the fourvector
        """
        self.assertAlmostEqual((ROOT.lepFourVec(
            ROOT.lep_pt, ROOT.lep_eta, ROOT.lep_phi, ROOT.lep_mass)[0] 
            - ROOT.lep_fourvec[0]).Mag(), 0)

    def test_z_idx_samekind(self):
        """Test the reconstruction of the lepton pair whose
        invariant mass is closest to the Z mass.
        """
        for i in range(2):
            for j in range(2):
                self.assertEqual(ROOT.zIdxSamekind(
                    ROOT.el_fourvecs_4, ROOT.el_charges)[i][j], ROOT.el_idx[i][j])
            '''   
            self.assertTrue(ROOT.VecOps.All(ROOT.zIdxSamekind(
            ROOT.el_fourvecs_4, ROOT.el_charges)[i] - ROOT.el_idx[i]))'''
                     
    def test_z_fourvec_samekind(self):
        """Test the reconstruction of the two Z fourvectors 
        in the case of leptons of the same kind.
        """
        for i in range(2):
            self.assertAlmostEqual((ROOT.zFourvecSamekind(
                ROOT.el_idx, ROOT.el_fourvecs_4)[i] - ROOT.z_fourvecs_4[i]).Mag(), 0)

    def test_z_fourvec_2mu2el(self):
        """Test the reconstruction of the two Z fourvectors 
        in the case of leptons of different kind.
        """
        for i in range(2):
            self.assertAlmostEqual((ROOT.zFourvec2mu2el(
                ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2)[i] - ROOT.z_fourvecs_2[i]).Mag(), 0)
            
    def test_deltar(self):
        """Test the angular separation.
        """
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.eta, ROOT.phi))
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.not_eta, ROOT.phi))
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.eta, ROOT.not_phi))
        self.assertFalse(ROOT.filterDeltaR(ROOT.el_idx, ROOT.not_eta, ROOT.not_phi))

    def test_order_idx_z(self):
        """Test the sorting of the z fourvectors.
        """
        for i in range(2):
            for j in range(2):
                self.assertEqual(ROOT.order_idx_Z(
                    ROOT.el_idx, ROOT.z_fourvecs_4)[i][j], ROOT.el_idx[i][j])
                self.assertEqual(ROOT.order_idx_Z(
                    ROOT.el_idx, ROOT.rev_z_fourvecs_4)[i][j], ROOT.rev_el_idx[i][j])

    def test_split_lep_samekind(self):
        """Test the splitting of the leptons 
        in the case of 4 leptons of the same kind.
        """
        self.assertEqual((ROOT.splitLepSamekind(
            ROOT.el_idx[0], ROOT.el_fourvecs_4, ROOT.el_charges)- ROOT.el3).Mag(), 0)
        self.assertEqual((ROOT.splitLepSamekind(
            ROOT.el_idx[0], ROOT.el_fourvecs_4, -ROOT.el_charges)- ROOT.el2).Mag(), 0)
        self.assertEqual((ROOT.splitLepSamekind(
            ROOT.el_idx[1], ROOT.el_fourvecs_4, ROOT.el_charges)- ROOT.el1).Mag(), 0)
        self.assertEqual((ROOT.splitLepSamekind(
            ROOT.el_idx[1], ROOT.el_fourvecs_4, -ROOT.el_charges)- ROOT.el0).Mag(), 0)

    def test_lep1(self):
        """Test the selection of the lepton/anti-lepton belonging 
        to the heavier boson Z1 in case of leptons of different kinds.
        """
        self.assertEqual((ROOT.lep1(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, ROOT.mu_charges_2, ROOT.el_charges_2)- ROOT.el3).Mag(), 0)
        self.assertEqual((ROOT.lep1(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, -ROOT.mu_charges_2, -ROOT.el_charges_2)- ROOT.el2).Mag(), 0)
    
    def test_lep2(self):
        """Test the selection of the lepton/anti-lepton belonging 
        to the lighter boson Z2 in case of leptons of different kinds.
        """
        self.assertEqual((ROOT.lep2(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, ROOT.mu_charges_2, ROOT.el_charges_2)- ROOT.el0).Mag(), 0)
        self.assertEqual((ROOT.lep2(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, -ROOT.mu_charges_2, -ROOT.el_charges_2)- ROOT.el1).Mag(), 0)
         
    def test_z_heavy(self):
        """Test the selection of the heavier Z.
        """
        self.assertEqual((ROOT.Z_heavy(
            ROOT.z_fourvecs_4)- ROOT.z1).Mag(), 0)

    def test_z_light(self):
        """Test the selection of the lighter Z.
        """
        self.assertEqual((ROOT.Z_light(
            ROOT.z_fourvecs_4)- ROOT.z0).Mag(), 0)

    def test_boost(self):
        """Test the boost of the fourvectors.
        """
        self.assertAlmostEqual((ROOT.boostFourvec(
            ROOT.el0, ROOT.v_long)- ROOT.el0_boost_long).Mag(), 0, 5)
        self.assertAlmostEqual((ROOT.boostFourvec(
            ROOT.el0, ROOT.v_trasv)- ROOT.el0_boost_trasv).Mag(), 0, 5)

    def test_cross(self):
        """Test the normalized cross product between two vectors.
        """
        self.assertAlmostEqual((ROOT.crossNorm(
            ROOT.v_long, ROOT.v_trasv)- ROOT.v_cross).Mag(), 0, 5)

    def test_phi(self):
        """Test the definition of the Phi angles.
        """
        self.assertAlmostEqual(ROOT.defPhi(
            ROOT.v3, ROOT.v1, ROOT.v2), ROOT.phi_angle, 5)

    def test_theta(self):
        """Test the definition of the theta angles.
        """
        self.assertAlmostEqual(ROOT.defTheta(
            ROOT.v4, ROOT.v5), ROOT.theta_angle, 5)

    def test_cos_theta(self):
        """Test the definition of the cosine of the theta angles.
        """
        self.assertAlmostEqual(ROOT.defCosTheta(
            ROOT.v4, ROOT.v5), ROOT.cos_theta_angle, 5)

if __name__ == "__main__":
    unittest.main()

