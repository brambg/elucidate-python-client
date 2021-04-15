from http import HTTPStatus
from typing import Any

import requests
from requests import Response


def hello():
    '''hello...'''
    print('hello')


headers = {
    'Accept': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"',
    'Content-Type': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"'
}


class ElucidateResponse():
    def __init__(self, response: Response):
        self.response = response


class ElucidateSuccess(ElucidateResponse):
    def __init__(self, response: Response, result: Any):
        super().__init__(response)
        self.result = result


class ElucidateFailure(ElucidateResponse):
    def __init__(self, response: Response):
        super().__init__(response)


class ContainerIdentifier():
    def __init__(self, url: str):
        self.url = url
        self.uuid = url.split('/')[-2]


class AnnotationIdentifier():
    def __init__(self, url: str):
        self.url = url
        url_split = url.split('/')
        self.uuid = url_split[-1]
        self.container_uuid = url_split[-2]


class ElucidateClient():
    def __init__(self, base_uri: str):
        self.base_uri = base_uri
        self.version = 'w3c'

    def use_w3c(self):
        self.version = 'w3c'

    def use_oa(self):
        self.version = 'oa'

    def create_container(self, label: str = 'A Container for Web Annotations') -> ElucidateResponse:
        body = {
            "@context": [
                "http://www.w3.org/ns/anno.jsonld",
                "http://www.w3.org/ns/ldp.jsonld"
            ],
            "type": [
                "BasicContainer",
                "AnnotationCollection"
            ],
            "label": label
        }
        response = requests.post(url=f'{self.base_uri}/w3c/',
                                 headers=headers,
                                 json=body)
        result_producer = lambda r: ContainerIdentifier(r.headers['location'])
        return self.handle_response(response, HTTPStatus.CREATED, result_producer)

    def get_container(self, container_identifier: ContainerIdentifier) -> ElucidateResponse:
        response = requests.get(f'{self.base_uri}/{self.version}/{container_identifier.uuid}/')
        return self.handle_response(response, HTTPStatus.OK, lambda r: r.json())

    def create_annotation(self, container_id: ContainerIdentifier, body, target) -> ElucidateResponse:
        annotation = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "type": "Annotation",
            "body": body,
            "target": target
        }
        response = requests.post(
            url=container_id.url,
            headers=headers,
            json=annotation)
        return self.handle_response(response, HTTPStatus.CREATED, lambda r: AnnotationIdentifier(r.json()['id']))

    def get_annotation(self, annotation_identifier: AnnotationIdentifier) -> ElucidateResponse:
        response = requests.get(
            f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}')
        return self.handle_response(response, HTTPStatus.OK, lambda r: r.json())

    def handle_response(self, response: Response, expected_status_code: int, result_producer) -> ElucidateResponse:
        if (response.status_code == expected_status_code):
            return ElucidateSuccess(response, result_producer(response))
        else:
            return ElucidateFailure(response)
