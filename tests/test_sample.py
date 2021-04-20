# -*- coding: utf-8 -*-
import unittest

from icecream import ic

from core import ElucidateClient, ElucidateSuccess, ElucidateResponse, ContainerIdentifier


# class BasicTestSuite(unittest.TestCase):
#     """Basic test cases."""
#
#     def test_absolute_truth_and_meaning(self):
#         assert True
#
#
# class ProjectTestSuite(unittest.TestCase):
#     """project test cases."""
#
#     def test_hello(self):
#         elucidate_client.hello()


class ElucidateClientTestSuite(unittest.TestCase):
    """Elucidate Client test cases."""

    def test_elucidate_client(self):
        ec = ElucidateClient("http://localhost:8080/annotation")
        container_id = ec.create_container(label='Annotation Container')
        assert container_id != None
        ic(container_id.url)
        ic(container_id.uuid)

        body = {
            "type": "TextualBody",
            "value": "I like this page!"
        }
        target = "http://www.example.com/index.html"
        annotation_id = ec.create_annotation(container_id=container_id, body=body, target=target)
        assert annotation_id != None
        ic(annotation_id.url)
        ic(annotation_id.container_uuid)
        ic(annotation_id.uuid)
        ic(annotation_id.etag)

        annotation = ec.read_annotation(annotation_id)
        ic(annotation)

        deleted = ec.delete_annotation(annotation_id)
        assert deleted == True

        try:
            annotation = ec.read_annotation(annotation_id)
            ic(annotation)
        except Exception as e:
            ic(e)

        w3c_container = ec.read_container(container_id)
        assert w3c_container != None
        ic(w3c_container)
        ic(w3c_container['id'])
        assert '/w3c/' in w3c_container['id']

        ec.use_oa()
        oa_container = ec.read_container(container_id)
        assert oa_container != None
        ic(oa_container)
        ic(oa_container['id'])
        assert '/oa/' in oa_container['id']

    def test_fail(self):
        ec = ElucidateClient("http://localhost:8080/annotation")
        container_id = ContainerIdentifier("http://example.org/fake-container")
        try:
            container = ec.read_container(container_id)
            ic(container)
            self.fail("expected a 404")
        except Exception as e:
            print(e)

    def test_statistics(self):
        ec = ElucidateClient("http://localhost:8080/annotation")
        stats = ec.get_body_id_statistics()
        assert stats['items'] != None
        ic(stats['items'])

        stats = ec.get_body_source_statistics()
        assert stats['items'] != None
        ic(stats['items'])

        stats = ec.get_target_id_statistics()
        assert stats['items'] != None
        ic(stats['items'])

        stats = ec.get_target_source_statistics()
        assert stats['items'] != None
        ic(stats['items'])


def get_result(response: ElucidateResponse):
    assert isinstance(response, ElucidateSuccess)
    return response.result


if __name__ == '__main__':
    unittest.main()
