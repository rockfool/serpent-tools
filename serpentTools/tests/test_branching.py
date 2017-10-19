"""Test the branching reader."""

import os
import unittest

from serpentTools.settings import rc
from serpentTools.tests import TEST_ROOT
from serpentTools.parsers import BranchingReader

REF_FILE = os.path.join(TEST_ROOT, 'ref_branch.txt')


class BranchTester(unittest.TestCase):
    """Classs for testing the branching coefficient file reader."""

    @classmethod
    def setUpClass(cls):
        rc['serpentVersion'] = '2.1.29'
        rc['xs.variableGroups'] = ['gc-meta', 'xs', 'diffusion']
        cls.reader = BranchingReader(REF_FILE)

    def test_variables(self):
        """Verify that the correct settings and variables are obtained."""
        expected = {'GC_UNIVERSE_NAME', 'MICRO_NG', 'MICRO_E', 'MACRO_NG',
                    'MACRO_E', 'INF_MICRO_FLX', 'INF_KINF', 'INF_FLX',
                    'INF_FISS_FLX', 'TOT', 'CAPT', 'ABS', 'FISS', 'NSF',
                    'NUBAR', 'KAPPA', 'INVV', 'TRANSPXS', 'DIFFCOEF',
                    'RABSXS', 'REMXS', 'SCATT0', 'SCATT1', 'SCATT2', 'SCATT3',
                    'SCATT4', 'SCATT5', 'SCATT6', 'SCATT7', 'S0', 'S1', 'S2',
                    'S3', 'S4', 'S5', 'S6', 'S7', 'CHIT', 'CHIP', 'CHID',
                    'CMM_TRANSPXS', 'CMM_TRANSPXS_X', 'CMM_TRANSPXS_Y',
                    'CMM_TRANSPXS_Z', 'CMM_DIFFCOEFF', 'CMM_DIFFCOEFF_X',
                    'CMM_DIFFCOEFF_Y', 'CMM_DIFFCOEFF_Z'}
        self.assertSetEqual(expected, self.reader.settings['variables'])


if __name__ == '__main__':
    unittest.main()