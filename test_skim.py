import unittest
import ROOT

ROOT.gInterpreter.ProcessLine('#include "skim_functions.h"' )

class TestSkim(unittest.TestCase):

    def test_sip(self):
        ROOT.gInterpreter.ProcessLine('''
            ROOT::RVec<float> dxy{1}, dz{0}, sigma_dxy{0.1}, sigma_dz{0};
        ''')
        self.assertEqual(ROOT.sipDef(
            ROOT.dxy, ROOT.dz, ROOT.sigma_dxy, ROOT.sigma_dz)[0], 11)



if __name__ == '__main__':
    unittest.main()

