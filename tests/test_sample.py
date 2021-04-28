# -*- coding: utf-8 -*-
import datetime
import unittest
import urllib.parse

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
        annotation_id = ec.create_annotation(container_id=container_id, body=body, target=target,
                                             custom={"motivation": "tagging"})
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


class StatisticsTestSuite(unittest.TestCase):

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


class SearchTestSuite(unittest.TestCase):

    def test_search_by_body_id(self):
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_id('http://example.org')
        # ic(results)
        assert results != None

    def test_search_by_body_source(self):
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_source('http://example.org')
        # ic(results)
        assert results != None

    def test_search_by_target_id(self):
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_id('http://example.org')
        # ic(results)
        assert results != None

    def test_search_by_target_source(self):
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_source('http://example.org')
        # ic(results)
        assert results != None

    def assert_search_by_part_results(self, results,
                                      expected_levels: str, expected_part: str, expected_type: str,
                                      value: str):
        # ic(results)
        assert results != None

        id = results['id']
        assert f'/search/{expected_part}?' in id
        assert f'levels={expected_levels}' in id
        assert f'type={expected_type}' in id
        encoded_value = urllib.parse.quote(value, safe='')
        assert f'value={encoded_value}' in id
        ic(results['total'])

    def test_search_by_annotation_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_creator_id(value)
        # ic(results)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_annotation_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_creator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_annotation_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_creator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_annotation_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_creator_email(value)

        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_annotation_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_creator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_annotation_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generator_id(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_annotation_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_annotation_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_annotation_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generator_email(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_annotation_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='annotation',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_body_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_creator_id(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_body_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_creator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_body_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_creator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_body_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_creator_email(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_body_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_creator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_body_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generator_id(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_body_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_body_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_body_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generator_email(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_body_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='body',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_target_creator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_id(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_target_creator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_target_creator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_target_creator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_email(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_target_creator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_creator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='creator',
                                           expected_type='emailsha1',
                                           value=value)

    def test_search_by_target_generator_id(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generator_id(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='id',
                                           value=value)

    def test_search_by_target_generator_name(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generator_name(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='name',
                                           value=value)

    def test_search_by_target_generator_nickname(self):
        value = 'http://example.org'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generator_nickname(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='nickname',
                                           value=value)

    def test_search_by_target_generator_email(self):
        value = 'someone@example.com'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generator_email(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='email',
                                           value=value)

    def test_search_by_target_generator_emailsha1(self):
        value = 'xyz'
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generator_emailsha1(value)
        self.assert_search_by_part_results(results=results,
                                           expected_levels='target',
                                           expected_part='generator',
                                           expected_type='emailsha1',
                                           value=value)


class TemporalSearchTestSuite(unittest.TestCase):

    def assert_search_by_temporal_results(self, results,
                                          expected_levels: str, expected_types: str, since: datetime):
        # ic(results)
        assert results != None

        id = results['id']
        assert f'/search/temporal?' in id
        assert f'levels={expected_levels}' in id
        assert f'types={expected_types}' in id
        expected_since = since.isoformat() + '.000Z'
        assert f'since={expected_since}' in id
        ic(results['total'])

    def test_search_by_annotation_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        result = ec.search_by_annotation_created_since(since)
        results = result.result
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='annotation',
                                               expected_types='created',
                                               since=since)

    def test_search_by_annotation_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1, microsecond=314)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_modified_since(since)
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='annotation',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_annotation_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_annotation_generated_since(since)
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='annotation',
                                               expected_types='generated',
                                               since=since)

    def test_search_by_body_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        result = ec.search_by_body_created_since(since)
        results = result.result
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='body',
                                               expected_types='created',
                                               since=since)

    def test_search_by_body_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1, microsecond=314)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_modified_since(since)
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='body',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_body_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_body_generated_since(since)
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='body',
                                               expected_types='generated',
                                               since=since)

    def test_search_by_target_created_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI, raise_exceptions=False)
        result = ec.search_by_target_created_since(since)
        results = result.result
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='target',
                                               expected_types='created',
                                               since=since)

    def test_search_by_target_modified_since(self):
        since = datetime.datetime(year=2000, month=1, day=1, microsecond=314)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_modified_since(since)
        self.assert_search_by_temporal_results(results=results,
                                               expected_levels='target',
                                               expected_types='modified',
                                               since=since)

    def test_search_by_target_generated_since(self):
        since = datetime.datetime(year=2000, month=1, day=1)
        ec = ElucidateClient(BASE_URI)
        results = ec.search_by_target_generated_since(since)
        self.assert_search_by_temporal_results(results=results,
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
