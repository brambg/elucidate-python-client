from http import HTTPStatus
from typing import Any

import requests
from requests import Response

jsonld_headers = {
    'Accept': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"',
    'Content-Type': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"'
}

json_headers = {
    'Accept': 'application/json;charset=UTF-8',
    'Content-Type': 'application/json;charset=UTF-8'
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
    def __init__(self, url: str, etag: str):
        self.url = url
        url_split = url.split('/')
        self.uuid = url_split[-1]
        self.container_uuid = url_split[-2]
        self.etag = etag


class ElucidateClient():
    def __init__(self, base_uri: str, raise_exceptions: bool = True):
        self.base_uri = base_uri
        self.version = 'w3c'
        self.raise_exceptions = raise_exceptions

    def use_w3c(self):
        self.version = 'w3c'

    def use_oa(self):
        self.version = 'oa'

    def create_container(self, label: str = 'A Container for Web Annotations'):
        url = f'{self.base_uri}/w3c/'
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
        response = requests.post(
            url=url,
            headers=jsonld_headers,
            json=body)
        return self.__handle_response(response, HTTPStatus.CREATED,
                                      lambda r: ContainerIdentifier(r.headers['location']))

    def read_container(self, container_identifier: ContainerIdentifier):
        url = f'{self.base_uri}/{self.version}/{container_identifier.uuid}/'
        response = requests.get(
            url=url,
            headers=jsonld_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def create_annotation(self, container_id: ContainerIdentifier, body, target):
        annotation = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "type": "Annotation",
            "body": body,
            "target": target
        }
        response = requests.post(
            url=container_id.url,
            headers=jsonld_headers,
            json=annotation)
        return self.__handle_response(response, HTTPStatus.CREATED,
                                      lambda r: AnnotationIdentifier(r.headers['location'], r.headers['etag'][3:-1]))

    def read_annotation(self, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        response = requests.get(
            url=url,
            headers=jsonld_headers
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def update_annotation(self, annotation_identifier: AnnotationIdentifier, body, target):
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        annotation = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "type": "Annotation",
            "body": body,
            "target": target
        }
        put_headers = {'If-Match': (annotation_identifier.etag)}
        put_headers.update(jsonld_headers)
        response = requests.put(
            url=url,
            headers=put_headers,
            json=annotation)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def delete_annotation(self, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        del_headers = {'If-Match': (annotation_identifier.etag)}
        del_headers.update(jsonld_headers)
        response = requests.delete(
            url=url,
            headers=del_headers)
        return self.__handle_response(response, HTTPStatus.NO_CONTENT,
                                      lambda r: r.ok)

    def search_by_body(self):
        pass

    def search_by_target(self):
        pass

    def search_by_creator(self):
        pass

    def search_by_generator(self):
        pass

    def search_by_created(self):
        pass

    def search_by_modified(self):
        pass

    def search_by_generated(self):
        pass

    def __get_statistics(self, part: str, field: str):
        url = f'{self.base_uri}/{self.version}/services/stats/{part}'
        response = requests.get(
            url=url,
            headers=jsonld_headers,
            params={"field": field})
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def get_body_id_statistics(self):
        return self.__get_statistics('body', 'id')

    def get_body_source_statistics(self):
        return self.__get_statistics('body', 'source')

    def get_target_id_statistics(self):
        return self.__get_statistics('target', 'id')

    def get_target_source_statistics(self):
        return self.__get_statistics('target', 'source')

    def do_batch_update(self):
        pass

    def do_batch_delete(self):
        pass

    def read_current_user(self):
        pass

    def create_group(self):
        pass

    def read_group(self):
        pass

    def read_group_users(self):
        pass

    def create_group_user(self):
        pass

    def delete_group_user(self):
        pass

    def read_group_annotations(self, group_id: str):
        url = f'{self.base_uri}/group/{group_id}/annotations'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def create_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        expected_status = HTTPStatus.OK
        response = requests.post(url=url)
        return self.__handle_response(response, HTTPStatus.CREATED,
                                      lambda r: r.json())

    def delete_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        expected_status = HTTPStatus.OK
        response = requests.delete(url=url)
        return self.__handle_response(response, HTTPStatus.NO_CONTENT,
                                      lambda r: r.json())

    def __handle_response(self, response: Response, expected_status_code: int, result_producer):
        if (response.status_code == expected_status_code):
            result = result_producer(response)
            if (self.raise_exceptions):
                return result
            else:
                return ElucidateSuccess(response, result)
        else:
            if (self.raise_exceptions):
                raise Exception(f'{response.status_code} : {response.text}')
            else:
                return ElucidateFailure(response)
