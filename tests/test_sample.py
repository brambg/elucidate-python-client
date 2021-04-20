# -*- coding: utf-8 -*-
import unittest
from icecream import ic
from core import ElucidateClient, ElucidateSuccess, ElucidateResponse, ContainerIdentifier, AnnotationIdentifier

BASE_URI = "http://localhost:8080/annotation"


class ElucidateClientTestSuite(unittest.TestCase):
    """Elucidate Client test cases."""

    def test_elucidate_client(self):
        ec = ElucidateClient(BASE_URI)
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
        ec = ElucidateClient(BASE_URI)
        container_id = ContainerIdentifier("http://example.org/fake-container")
        try:
            container = ec.read_container(container_id)
            ic(container)
            self.fail("expected a 404")
        except Exception as e:
            print(e)

    def test_statistics(self):
        ec = ElucidateClient(BASE_URI)
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


class AuthorizationTestSuite(unittest.TestCase):

    def test_read_current_user(self):
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = ec.read_current_user()
        assert isinstance(response, ElucidateSuccess)
        ic(response.result)

    def test_group(self):
        ec = ElucidateClient(BASE_URI)
        group_id = ec.create_group("test_group")
        ic(group_id)
        assert isinstance(group_id, str)
        assert group_id != None

    def test_annotation_group(self):
        ec = ElucidateClient(BASE_URI)

        group_id = ec.create_group("test_group")
        ic(group_id)
        assert isinstance(group_id, str)
        assert group_id != None

        annotation_url = f'{BASE_URI}/group_id/annotation_id'

        group_annotations = ec.read_group_annotations(group_id)
        ic(group_annotations)
        assert isinstance(group_annotations, list)
        assert annotation_url not in group_annotations

        annotation_id = AnnotationIdentifier(annotation_url)
        success = ec.create_group_annotation(group_id=group_id, annotation_identifier=annotation_id)
        assert success == True

        group_annotations = ec.read_group_annotations(group_id)
        ic(group_annotations)
        assert isinstance(group_annotations, list)
        assert annotation_url in group_annotations

        success = ec.delete_group_annotation(group_id=group_id, annotation_identifier=annotation_id)
        assert success == True

        group_annotations = ec.read_group_annotations(group_id)
        ic(group_annotations)
        assert isinstance(group_annotations, list)
        assert annotation_url not in group_annotations


def get_result(response: ElucidateResponse):
    assert isinstance(response, ElucidateSuccess)
    return response.result


if __name__ == '__main__':
    unittest.main()
