# -*- coding: utf-8 -*-
from icecream import ic

from core import ElucidateClient
from .context import elucidate_client

import unittest
import icecream


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_absolute_truth_and_meaning(self):
        assert True


class ProjectTestSuite(unittest.TestCase):
    """project test cases."""

    def test_hello(self):
        elucidate_client.hello()


class ElucidateClientTestSuite(unittest.TestCase):
    """Elucidate Client test cases."""


    def test_container(self):
        ec = ElucidateClient("http://localhost:8080/annotation")
        container_id = ec.create_container(label='Annotation Container')
        assert container_id != None
        ic(container_id.url)
        ic(container_id.uuid)

        w3c_container = ec.get_container(container_id)
        assert w3c_container != None
        ic(w3c_container)
        ic(w3c_container['id'])
        assert '/w3c/' in w3c_container['id']

        ec.use_oa()
        oa_container = ec.get_container(container_id)
        assert oa_container != None
        ic(oa_container)
        ic(oa_container['id'])
        assert '/oa/' in oa_container['id']


if __name__ == '__main__':
    unittest.main()
