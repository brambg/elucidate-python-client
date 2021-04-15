# -*- coding: utf-8 -*-
import unittest

from icecream import ic

from core import ElucidateClient, ElucidateSuccess, ElucidateResponse
from .context import elucidate_client


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

    def test_elucidate_client(self):
        ec = ElucidateClient("http://localhost:8080/annotation")
        container_id = get_result(ec.create_container(label='Annotation Container'))
        assert container_id != None
        ic(container_id.url)
        ic(container_id.uuid)

        body = {
            "type": "TextualBody",
            "value": "I like this page!"
        }
        target = "http://www.example.com/index.html"
        annotation_id = get_result(ec.create_annotation(container_id=container_id, body=body, target=target))
        assert annotation_id != None
        ic(annotation_id.url)
        ic(annotation_id.container_uuid)
        ic(annotation_id.uuid)

        annotation = get_result(ec.get_annotation(annotation_id))
        ic(annotation)

        w3c_container = get_result(ec.get_container(container_id))
        assert w3c_container != None
        ic(w3c_container)
        ic(w3c_container['id'])
        assert '/w3c/' in w3c_container['id']

        ec.use_oa()
        oa_container = get_result(ec.get_container(container_id))
        assert oa_container != None
        ic(oa_container)
        ic(oa_container['id'])
        assert '/oa/' in oa_container['id']


def get_result(response: ElucidateResponse):
    assert isinstance(response, ElucidateSuccess)
    return response.result


if __name__ == '__main__':
    unittest.main()
