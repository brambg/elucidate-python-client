# -*- coding: utf-8 -*-
import unittest

from elucidate_client.core import ElucidateSuccess, ElucidateResponse, split_annotation

BASE_URI = "http://localhost:18080/annotation"


class WebAnnotationSplitterTestSuite(unittest.TestCase):
    def test_split(self):
        annotation = {'@context': 'http://www.w3.org/ns/anno.jsonld',
                      'body': [{'purpose': 'classifying',
                                'type': 'TextualBody',
                                'value': 'location'},
                               {'type': 'Dataset',
                                'value': {'category': 'location',
                                          'match_phrase': 'Karel',
                                          'match_score': 0.8387096774193549,
                                          'match_variant': 'Farel'}}],
                      'created': '2021-07-27T16:13:09.078457',
                      'generator': {'id': 'https://github.com/knaw-huc/golden-agents-htr',
                                    'name': 'GoldenAgentsNER',
                                    'type': 'Software'},
                      'id': 'f264f34a-5e52-4f4c-831a-8fee0a734f6d',
                      'motivation': 'classifying',
                      'target': [{'selector': {'end': 24,
                                               'start': 19,
                                               'type': 'TextPositionSelector'},
                                  'source': 'urn:golden-agents:2408_A16098:scan=a16098000013:textline=r2l110'},
                                 {'selector': {'conformsTo': 'http://tools.ietf.org/rfc/rfc5147',
                                               'type': 'FragmentSelector',
                                               'value': 'char=19,24'},
                                  'source': 'urn:golden-agents:2408_A16098:scan=a16098000013:textline=r2l110'},
                                 {'selector': {'conformsTo': 'http://tools.ietf.org/rfc/rfc3023',
                                               'type': 'FragmentSelector',
                                               'value': 'xpointer(id(r2l110)/TextEquiv/Unicode)'},
                                  'source': 'http://localhost:8080/textrepo/versions/x/contents',
                                  'type': 'xml'},
                                 {'source': 'http://localhost:8080/textrepo/versions/x/chars/19/24'},
                                 {'selector': {'conformsTo': 'http://www.w3.org/TR/media-frags/',
                                               'type': 'FragmentSelector',
                                               'value': 'xywh=850,3620,1510,86'},
                                  'source': 'https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg',
                                  'type': 'image'}],
                      'type': 'Annotation'}
        (body, target, custom) = split_annotation(annotation)
        expected_body = [{'purpose': 'classifying',
                          'type': 'TextualBody',
                          'value': 'location'},
                         {'type': 'Dataset',
                          'value': {'category': 'location',
                                    'match_phrase': 'Karel',
                                    'match_score': 0.8387096774193549,
                                    'match_variant': 'Farel'}}]
        expected_target = [{'selector': {'end': 24,
                                         'start': 19,
                                         'type': 'TextPositionSelector'},
                            'source': 'urn:golden-agents:2408_A16098:scan=a16098000013:textline=r2l110'},
                           {'selector': {'conformsTo': 'http://tools.ietf.org/rfc/rfc5147',
                                         'type': 'FragmentSelector',
                                         'value': 'char=19,24'},
                            'source': 'urn:golden-agents:2408_A16098:scan=a16098000013:textline=r2l110'},
                           {'selector': {'conformsTo': 'http://tools.ietf.org/rfc/rfc3023',
                                         'type': 'FragmentSelector',
                                         'value': 'xpointer(id(r2l110)/TextEquiv/Unicode)'},
                            'source': 'http://localhost:8080/textrepo/versions/x/contents',
                            'type': 'xml'},
                           {'source': 'http://localhost:8080/textrepo/versions/x/chars/19/24'},
                           {'selector': {'conformsTo': 'http://www.w3.org/TR/media-frags/',
                                         'type': 'FragmentSelector',
                                         'value': 'xywh=850,3620,1510,86'},
                            'source': 'https://files.transkribus.eu/iiif/2/MOQMINPXXPUTISCRFIRKIOIX/full/max/0/default.jpg',
                            'type': 'image'}]
        expected_custom = {'created': '2021-07-27T16:13:09.078457',
                           'generator': {'id': 'https://github.com/knaw-huc/golden-agents-htr',
                                         'name': 'GoldenAgentsNER',
                                         'type': 'Software'},
                           'motivation': 'classifying'}
        self.assertEqual(expected_body, body)
        self.assertEqual(expected_target, target)
        self.assertEqual(expected_custom, custom)


def get_result(response: ElucidateResponse):
    assert isinstance(response, ElucidateSuccess)
    return response.result


if __name__ == '__main__':
    unittest.main()
