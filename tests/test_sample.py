# -*- coding: utf-8 -*-

from .context import elucidate_client

import unittest


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True

class ProjectTestSuite(unittest.TestCase):
    """project test cases."""

    def test_hello(self):
        elucidate_client.hello()


if __name__ == '__main__':
    unittest.main()