# -*- coding: utf-8 -*-
import datetime
import unittest
import urllib.parse

from icecream import ic

from elucidate.client import ElucidateClient
from elucidate.model import ElucidateSuccess, ElucidateResponse, ContainerIdentifier, AnnotationIdentifier, \
    AnnotationCollection, ElucidateFailure

BASE_URI = "http://localhost:18080/annotation"


# BASE_URI = "https://elucidate.tt.di.huc.knaw.nl/annotation"


class ElucidateClientTestSuite(unittest.TestCase):
    """Elucidate Client test cases."""

    def test_elucidate_client(self):
        ec = ElucidateClient(BASE_URI)
        container_id = ec.create_container(label='Annotation Container')
        assert container_id is not None
        ic(container_id)

        body = {
            "type": "TextualBody",
            "value": "I like this page!"
        }
        target = "http://www.example.com/index.html"
        annotation_id = ec.create_annotation(container_id=container_id, body=body, target=target,
                                             custom={"motivation": "tagging"})
        assert annotation_id is not None
        ic(annotation_id)

        annotation = ec.read_annotation(annotation_id)
        ic(annotation)

        new_body = {
            "type": "TextualBody",
            "value": "This page is massive!"
        }
        new_target = "http://www.example.com/index.html"
        updated_annotation_id = ec.update_annotation(annotation_id, new_body, new_target)
        ic(updated_annotation_id)

        deleted = ec.delete_annotation(updated_annotation_id)
        assert deleted == True

        try:
            annotation = ec.read_annotation(updated_annotation_id)
            ic(annotation)
        except Exception as e:
            ic(e)

        self._assert_read_container(ec, container_id, '/w3c/')
        ec.use_oa()
        self._assert_read_container(ec, container_id, '/oa/')

    def _assert_read_container(self, ec, container_id, mode):
        w3c_container = ec.read_container(container_id)
        ic(w3c_container.label)
        ic(w3c_container.id)
        ic(w3c_container.total)
        assert mode in w3c_container.id
        for annotation in w3c_container.annotations_as_json():
            assert annotation['id'].starts_with(container_id.url)

    def test_fail(self):
        ec = ElucidateClient(BASE_URI)
        container_id = ContainerIdentifier("http://example.org/fake-container")
        try:
            container = ec.read_container(container_id)
            ic(container)
            self.fail("expected a 404")
        except Exception as e:
            print(e)


class StatisticsTestSuite(unittest.TestCase):

    def test_statistics(self):
        ec = ElucidateClient(BASE_URI)
        stats = ec.get_body_id_statistics()
        assert stats['items'] is not None
        ic(stats['items'])

        stats = ec.get_body_source_statistics()
        assert stats['items'] is not None
        ic(stats['items'])

        stats = ec.get_target_id_statistics()
        assert stats['items'] is not None
        ic(stats['items'])

        stats = ec.get_target_source_statistics()
        assert stats['items'] is not None
        ic(stats['items'])


class SearchTestSuite(unittest.TestCase):

    def test_search_by_body_id(self):
        ec = ElucidateClient(BASE_URI)
        annotation_collection = ec.search_by_body_id('http://example.org')
        ic(annotation_collection)
        ic(annotation_collection.total)
        for annotation in annotation_collection.annotations_as_json():
            assert 'id' in annotation

    def test_search_by_body_source(self):
        ec = ElucidateClient(BASE_URI)
        annotation_collection = ec.search_by_body_source('http://example.org')
        ic(annotation_collection)
        ic(annotation_collection.total)

    def test_search_by_target_id(self):
        ec = ElucidateClient(BASE_URI)
        annotation_collection = ec.search_by_target_id('http://example.org')
        ic(annotation_collection)
        ic(annotation_collection.total)

    def test_search_by_target_source(self):
        ec = ElucidateClient(BASE_URI)
        annotation_collection = ec.search_by_target_source('http://example.org')
        ic(annotation_collection)
        ic(annotation_collection.total)

    def assert_search_by_part_results(self, annotation_collection: AnnotationCollection,
                                      expected_levels: str, expected_part: str, expected_type: str,
                                      value: str):
        # ic(results)

        id = annotation_collection.id
        assert f'/search/{expected_part}?' in id
        assert f'levels={expected_levels}' in id
        assert f'type={expected_type}' in id
        encoded_value = urllib.parse.quote(value, safe='')
        assert f'value={encoded_value}' in id
        for a in annotation_collection.annotations_as_json():
            assert 'id' in a

    def test_search_by_annotation_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=ec.search_by_annotation_creator_id(value),
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_annotation_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_creator_name(value)),
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_annotation_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_creator_nickname(value)),
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_annotation_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_creator_email(value)),
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_annotation_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_creator_emailsha1(value)),
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_annotation_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_generator_id(value)),
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_annotation_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_generator_name(value)),
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_annotation_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_generator_nickname(value)),
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_annotation_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_generator_email(value)),
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_annotation_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_annotation_generator_emailsha1(value)),
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_body_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_creator_id(value)),
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_body_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_creator_name(value)),
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_body_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_creator_nickname(value)),
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_body_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_creator_email(value)),
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_body_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_creator_emailsha1(value)),
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_body_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_generator_id(value)),
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_body_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_generator_name(value)),
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_body_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_generator_nickname(value)),
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_body_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_generator_email(value)),
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_body_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_body_generator_emailsha1(value)),
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_target_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_creator_id(value)),
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_target_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_creator_name(value)),
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_target_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_creator_nickname(value)),
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_target_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_creator_email(value)),
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_target_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_emailsha1(value)
        self.assert_search_by_part_results(annotation_collection=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_target_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_generator_id(value)),
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_target_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_generator_name(value)),
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_target_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_generator_nickname(value)),
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_target_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_generator_email(value)),
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_target_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        self.assert_search_by_part_results(annotation_collection=(ec.search_by_target_generator_emailsha1(value)),
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)


class TemporalSearchTestSuite(unittest.TestCase):

    def assert_search_by_temporal_results(self, annotation_collection: AnnotationCollection,
                                          expected_levels: str, expected_types: str, since: datetime):
        # ic(results)
        assert annotation_collection is not None

        id = annotation_collection.id
        assert f'/search/temporal?' in id
        assert f'levels={expected_levels}' in id
        assert f'types={expected_types}' in id
        expected_since = since.isoformat().replace(':', '%3A')
        assert f'since={expected_since}' in id

    def test_search_by_annotation_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = ec.search_by_annotation_created_since(since)
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='annotation',
                                               expected_types='created',
                                               since=since)

    def test_search_by_annotation_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_annotation_modified_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='annotation',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_annotation_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_annotation_generated_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='annotation',
                                               expected_types='generated',
                                               since=since)

    def test_search_by_body_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_body_created_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='body',
                                               expected_types='created',
                                               since=since)

    def test_search_by_body_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_body_modified_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='body',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_body_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_body_generated_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='body',
                                               expected_types='generated',
                                               since=since)

    def test_search_by_target_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_target_created_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='target',
                                               expected_types='created',
                                               since=since)

    def test_search_by_target_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_target_modified_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='target',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_target_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        response = (ec.search_by_target_generated_since(since))
        annotation_collection = get_result(response)
        self.assert_search_by_temporal_results(annotation_collection=annotation_collection,
                                               expected_levels='target',
                                               expected_types='generated',
                                               since=since)


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
        assert group_id is not None

    def test_annotation_group(self):
        ec = ElucidateClient(BASE_URI)

        group_id = ec.create_group("test_group")
        ic(group_id)
        assert isinstance(group_id, str)
        assert group_id is not None

        annotation_url = f'{BASE_URI}/group_id/annotation_id'

        group_annotations = self._extracted_from_test_annotation_group_11(ec, group_id)
        assert annotation_url not in group_annotations

        annotation_id = AnnotationIdentifier(annotation_url, "")
        success = ec.create_group_annotation(group_id=group_id, annotation_identifier=annotation_id)
        assert success == True

        group_annotations = self._extracted_from_test_annotation_group_11(ec, group_id)
        assert annotation_url in group_annotations

        success = ec.delete_group_annotation(group_id=group_id, annotation_identifier=annotation_id)
        assert success == True

        group_annotations = self._extracted_from_test_annotation_group_11(ec, group_id)
        assert annotation_url not in group_annotations

    def _extracted_from_test_annotation_group_11(self, ec, group_id):
        result = ec.read_group_annotations(group_id)
        ic(result)
        assert isinstance(result, list)
        return result


class SlugTestSuite(unittest.TestCase):

    def test_create_container_and_annotation_with_custom_names(self):
        ec = ElucidateClient(BASE_URI)
        container_name = 'custom_container_name4'

        container_id = ec.read_container_identifier(name=container_name)
        if not container_id:
            container_id = ec.create_container(label='This is the label', container_id=container_name)
        ic(container_id)
        expected_url = f"{BASE_URI}/{ec.version}/{container_name}/"
        self.assertEqual(expected_url, container_id.url)

        annotation_name = "custom_annotation_name"
        annotation_id = ec.create_annotation(container_id=container_id, body={}, target={},
                                             annotation_id=annotation_name)
        ic(annotation_id)
        expected_url = f"{BASE_URI}/{ec.version}/{container_name}/{annotation_name}"
        self.assertEqual(expected_url, annotation_id.url)

        ok = ec.delete_annotation(annotation_identifier=annotation_id)
        assert ok

        # ok = ec.delete_container(container_identifier=container_name)
        # assert ok


class CustomContextTestSuite(unittest.TestCase):

    def test_custom_fields_are_preserved(self):
        ec = ElucidateClient(BASE_URI)
        container_name = 'custom_container_name4'

        container_id = ec.read_container_identifier(name=container_name)
        if not container_id:
            container_id = ec.create_container(label='This is the label', container_id=container_name)
        ic(container_id)
        expected_url = f"{BASE_URI}/{ec.version}/{container_name}/"
        self.assertEqual(expected_url, container_id.url)

        custom_context = {'custom_field': 'urn:custom_field'}
        annotation_id = ec.create_annotation(container_id=container_id, body={"custom_field": "custom_value"},
                                             target={}, custom_contexts=custom_context)
        ic(annotation_id)

        annotation = ec.read_annotation(annotation_identifier=annotation_id)
        ic(annotation)
        self.assertEqual("custom_value", annotation['body']['urn:custom_field'])

        ok = ec.delete_annotation(annotation_identifier=annotation_id)
        assert ok

        # ok = ec.delete_container(container_identifier=container_name)
        # assert ok


def get_result(response: ElucidateResponse):
    response_type = type(response)
    if ElucidateFailure.__class__ == response_type:
        print("error:")
        print(response.response.text)
        return None
    return response.result


if __name__ == '__main__':
    unittest.main()
