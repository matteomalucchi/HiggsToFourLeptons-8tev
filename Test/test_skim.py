""" Tests for the functions used in the file ``skim_tools.py`` during
the skimming process defined in the header file ``skim_functions.h``.
"""

import os
import unittest

import ROOT


class TestSkim(unittest.TestCase):
    """ Test class for the functions used in ``skim_tools.py``
        and defined in the header file ``skim_functions.h``.
    """

    def __init__(self, *args, **kwargs):
        """ Include the header files where the functions and the variables are defined.
        """
        super().__init__(*args, **kwargs)

        func_path = os.path.join("Analysis", "Skimming", "skim_functions.h")
        var_path = os.path.join("Test", "test_variables.h")

        ROOT.gInterpreter.ProcessLine(f'#include "{func_path}"' )
        ROOT.gInterpreter.ProcessLine(f'#include "{var_path}"' )

    def test_sip(self):
        """ Test the definition of the significance of the impact parameter sip
            as the ratio between the impact parameter at the point of closest
            approach to the vertex and its uncertainty.
        """
        self.assertAlmostEqual(ROOT.sipDef(
            ROOT.dxy, ROOT.dz, ROOT.sigma_dxy, ROOT.sigma_dz)[0], ROOT.sip[0], 5)

    def test_pt_cuts(self):
        """ Test the lepton pt cuts that require that in at least one of the lepton couples
            the highest energy particle has Pt > 20 GeV while the other one Pt > 10 GeV.
        """
        self.assertTrue(ROOT.ptCuts(ROOT.mu_pt, ROOT.e_pt))
        self.assertTrue(ROOT.ptCuts(ROOT.mu_pt, ROOT.not_e_pt))
        self.assertTrue(ROOT.ptCuts(ROOT.not_mu_pt, ROOT.e_pt))
        self.assertFalse(ROOT.ptCuts(ROOT.not_mu_pt, ROOT.not_e_pt))

    def test_lep_fourvec(self):
        """ Test the reconstruction of the lepton fourvectors.
        """
        self.assertAlmostEqual((ROOT.lepFourVec(
            ROOT.lep_pt, ROOT.lep_eta, ROOT.lep_phi, ROOT.lep_mass)[0]
            - ROOT.lep_fourvec[0]).Mag(), 0)

    def test_z_idx_samekind(self):
        """ Test the reconstruction of the same kind lepton pair whose
            invariant mass is closest to the Z mass.
        """
        for i in range(2):
            for j in range(2):
                self.assertEqual(ROOT.zIdxSamekind(
                    ROOT.el_fourvecs_4, ROOT.el_charges)[i][j], ROOT.el_idx[i][j])

    def test_z_fourvec_samekind(self):
        """ Test the reconstruction of the two Z fourvectors in the case of leptons
            of the same kind and their ascending distance to Z mass organization.
        """
        for i in range(2):
            self.assertAlmostEqual((ROOT.zFourvecSamekind(
                ROOT.el_idx, ROOT.el_fourvecs_4)[i] - ROOT.z_fourvecs_4[i]).Mag(), 0)

    def test_z_fourvec_2mu2el(self):
        """ Test the reconstruction of the two Z fourvectors in the case of leptons
            of different kind and their ascending distance to Z mass organization.
        """
        for i in range(2):
            self.assertAlmostEqual((ROOT.zFourvec2mu2el(
                ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2)[i] - ROOT.z_fourvecs_2[i]).Mag(), 0)

    def test_deltar(self):
        """ Test the angular separation of particles building the Z systems.
        """
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.eta, ROOT.phi))
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.not_eta, ROOT.phi))
        self.assertTrue(ROOT.filterDeltaR(ROOT.el_idx, ROOT.eta, ROOT.not_phi))
        self.assertFalse(ROOT.filterDeltaR(ROOT.el_idx, ROOT.not_eta, ROOT.not_phi))

    def test_order_idx_z(self):
        """ Test the order of the Z fourvectors so that the first Z is the heaviest one.
        """
        for i in range(2):
            for j in range(2):
                self.assertEqual(ROOT.order_idx_Z(
                    ROOT.el_idx, ROOT.z_fourvecs_4)[i][j], ROOT.el_idx[i][j])
                self.assertEqual(ROOT.order_idx_Z(
                    ROOT.el_idx, ROOT.rev_z_fourvecs_4)[i][j], ROOT.rev_el_idx[i][j])

    def test_split_lep_samekind(self):
        """ Test the order of the leptons in the case of 4 leptons of the same kind.
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
        """ Test the selection of the lepton/anti-lepton belonging
            to the heaviest boson Z1 in case of leptons of different kinds.
        """
        self.assertEqual((ROOT.lep1(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, ROOT.mu_charges_2, ROOT.el_charges_2)
            - ROOT.el3).Mag(), 0)
        self.assertEqual((ROOT.lep1(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, -ROOT.mu_charges_2, -ROOT.el_charges_2)
            - ROOT.el2).Mag(), 0)

    def test_lep2(self):
        """ Test the selection of the lepton/anti-lepton belonging
            to the lighter boson Z2 in case of leptons of different kinds.
        """
        self.assertEqual((ROOT.lep2(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, ROOT.mu_charges_2, ROOT.el_charges_2)
            - ROOT.el0).Mag(), 0)
        self.assertEqual((ROOT.lep2(
            ROOT.mu_fourvecs_2, ROOT.el_fourvecs_2, -ROOT.mu_charges_2, -ROOT.el_charges_2)
            - ROOT.el1).Mag(), 0)

    def test_z_heavy(self):
        """ Test the selection of the heavier Z.
        """
        self.assertEqual((ROOT.Z_heavy(
            ROOT.z_fourvecs_4)- ROOT.z1).Mag(), 0)

    def test_z_light(self):
        """ Test the selection of the lighter Z.
        """
        self.assertEqual((ROOT.Z_light(
            ROOT.z_fourvecs_4)- ROOT.z0).Mag(), 0)

    def test_boost(self):
        """ Test the boost of the fourvectors in a given frame.
        """
        self.assertAlmostEqual((ROOT.boostFourvec(
            ROOT.el0, ROOT.v_long)- ROOT.el0_boost_long).Mag(), 0, 5)
        self.assertAlmostEqual((ROOT.boostFourvec(
            ROOT.el0, ROOT.v_trasv)- ROOT.el0_boost_trasv).Mag(), 0, 5)

    def test_cross(self):
        """ Test the normalized cross product between two vectors.
        """
        self.assertAlmostEqual((ROOT.crossNorm(
            ROOT.v_long, ROOT.v_trasv)- ROOT.v_cross).Mag(), 0, 5)

    def test_phi(self):
        """ Test the definition of Phi and Phi1.
        """
        self.assertAlmostEqual(ROOT.defPhi(
            ROOT.v3, ROOT.v1, ROOT.v2), ROOT.phi_angle, 5)

    def test_theta(self):
        """ Test the definition of theta_star, theta1 and theta2.
        """
        self.assertAlmostEqual(ROOT.defTheta(
            ROOT.v4, ROOT.v5), ROOT.theta_angle, 5)

    def test_cos_theta(self):
        """ Test the definition of cos(theta_star), cos(theta1) and cos(theta2).
        """
        self.assertAlmostEqual(ROOT.defCosTheta(
            ROOT.v4, ROOT.v5), ROOT.cos_theta_angle, 5)

if __name__ == "__main__":
    unittest.main()
