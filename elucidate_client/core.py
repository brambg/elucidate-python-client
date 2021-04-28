from datetime import datetime
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

    def create_annotation(self, container_id: ContainerIdentifier, body, target, custom: dict = {}):
        annotation = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "type": "Annotation",
            "body": body,
            "target": target
        }
        annotation.update(custom)
        response = requests.post(
            url=container_id.url,
            headers=jsonld_headers,
            json=annotation)
        return self.__handle_response(response, HTTPStatus.CREATED,
                                      lambda r: AnnotationIdentifier(r.headers['location'], r.headers['etag'][3:-1]))

    # TODO: Annotation Histories
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

    def __search_by_part(self, part: str, fields: str, value: str, strict: bool = False, xywh: str = None,
                         t: str = None, creator: str = None, generator: str = None):
        url = f'{self.base_uri}/w3c/services/search/{part}'
        params = dict(fields=fields, value=value, strict=strict)
        if (xywh != None):
            params['xywh'] = xywh
        if (t != None):
            params['t'] = t
        if (creator != None):
            params['creator'] = creator
        if (generator != None):
            params['generator'] = generator
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def search_by_body_id(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                          creator: str = None, generator: str = None):
        return self.__search_by_part('body', 'id', value, strict, xywh, t, creator, generator)

    def search_by_body_source(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                              creator: str = None, generator: str = None):
        return self.__search_by_part('body', 'source', value, strict, xywh, t, creator, generator)

    def search_by_target_id(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                            creator: str = None, generator: str = None):
        return self.__search_by_part('target', 'id', value, strict, xywh, t, creator, generator)

    def search_by_target_source(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                                creator: str = None, generator: str = None):
        return self.__search_by_part('target', 'source', value, strict, xywh, t, creator, generator)

    def __search_by_role(self, role: str, levels: str, type: str, value: str, strict: bool = False):
        url = f'{self.base_uri}/w3c/services/search/{role}'
        params = dict(levels=levels, type=type, value=value, strict=strict)
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def search_by_annotation_creator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='annotation', type='id', value=value, strict=strict)

    def search_by_annotation_creator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='annotation', type='name', value=value, strict=strict)

    def search_by_annotation_creator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='annotation', type='nickname', value=value, strict=strict)

    def search_by_annotation_creator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='annotation', type='email', value=value, strict=strict)

    def search_by_annotation_creator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='annotation', type='emailsha1', value=value, strict=strict)

    def search_by_annotation_generator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='annotation', type='id', value=value, strict=strict)

    def search_by_annotation_generator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='annotation', type='name', value=value, strict=strict)

    def search_by_annotation_generator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='annotation', type='nickname', value=value, strict=strict)

    def search_by_annotation_generator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='annotation', type='email', value=value, strict=strict)

    def search_by_annotation_generator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='annotation', type='emailsha1', value=value,
                                     strict=strict)

    def search_by_body_creator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='body', type='id', value=value, strict=strict)

    def search_by_body_creator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='body', type='name', value=value, strict=strict)

    def search_by_body_creator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='body', type='nickname', value=value, strict=strict)

    def search_by_body_creator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='body', type='email', value=value, strict=strict)

    def search_by_body_creator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='body', type='emailsha1', value=value, strict=strict)

    def search_by_body_generator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='body', type='id', value=value, strict=strict)

    def search_by_body_generator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='body', type='name', value=value, strict=strict)

    def search_by_body_generator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='body', type='nickname', value=value, strict=strict)

    def search_by_body_generator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='body', type='email', value=value, strict=strict)

    def search_by_body_generator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='body', type='emailsha1', value=value, strict=strict)

    def search_by_target_creator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='target', type='id', value=value, strict=strict)

    def search_by_target_creator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='target', type='name', value=value, strict=strict)

    def search_by_target_creator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='target', type='nickname', value=value, strict=strict)

    def search_by_target_creator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='target', type='email', value=value, strict=strict)

    def search_by_target_creator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='creator', levels='target', type='emailsha1', value=value, strict=strict)

    def search_by_target_generator_id(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='target', type='id', value=value, strict=strict)

    def search_by_target_generator_name(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='target', type='name', value=value, strict=strict)

    def search_by_target_generator_nickname(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='target', type='nickname', value=value, strict=strict)

    def search_by_target_generator_email(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='target', type='email', value=value, strict=strict)

    def search_by_target_generator_emailsha1(self, value: str, strict: bool = False):
        return self.__search_by_role(role='generator', levels='target', type='emailsha1', value=value, strict=strict)

    def __search_by_temporal(self, levels: str, types: str, since: datetime):
        url = f'{self.base_uri}/w3c/services/search/temporal'
        since_param = since.isoformat()
        if (since.microsecond == 0):
            since_param += ".00000"
        since_param += 'Z'
        params = dict(levels=levels, types=types, since=since_param)
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def search_by_annotation_created_since(self, since: datetime):
        return self.__search_by_temporal(levels='annotation', types='created', since=since)

    def search_by_annotation_modified_since(self, since: datetime):
        return self.__search_by_temporal(levels='annotation', types='modified', since=since)

    def search_by_annotation_generated_since(self, since: datetime):
        return self.__search_by_temporal(levels='annotation', types='generated', since=since)

    def search_by_body_created_since(self, since: datetime):
        return self.__search_by_temporal(levels='body', types='created', since=since)

    def search_by_body_modified_since(self, since: datetime):
        return self.__search_by_temporal(levels='body', types='modified', since=since)

    def search_by_body_generated_since(self, since: datetime):
        return self.__search_by_temporal(levels='body', types='generated', since=since)

    def search_by_target_created_since(self, since: datetime):
        return self.__search_by_temporal(levels='target', types='created', since=since)

    def search_by_target_modified_since(self, since: datetime):
        return self.__search_by_temporal(levels='target', types='modified', since=since)

    def search_by_target_generated_since(self, since: datetime):
        return self.__search_by_temporal(levels='target', types='generated', since=since)

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

    def do_batch_update(self, body, target):
        url = f'{self.base_uri}/w3c/services/batch/update'
        json = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "body": body,
            "target": target
        }
        response = requests.post(
            url=url,
            headers=jsonld_headers,
            json=json
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def do_batch_delete(self, body, target):
        url = f'{self.base_uri}/w3c/services/batch/delete'
        json = {
            "@context": "http://www.w3.org/ns/anno.jsonld",
            "body": body,
            "target": target
        }
        response = requests.post(
            url=url,
            headers=jsonld_headers,
            json=json
        )
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def read_current_user(self):
        url = f'{self.base_uri}/user/current'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def create_group(self, label: str):
        url = f'{self.base_uri}/group'
        response = requests.post(
            url=url,
            headers=json_headers,
            json={"label": label})
        return self.__handle_response(response, HTTPStatus.CREATED,
                                      lambda r: r.json()['id'])

    def read_group(self, group_id: str):
        url = f'{self.base_uri}/group/{group_id}'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json())

    def read_group_users(self, group_id: str):
        url = f'{self.base_uri}/group/{group_id}/users'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json()['users'])

    def create_group_user(self, group_id: str, user_id: str):
        url = f'{self.base_uri}/group/{group_id}/users/{user_id}'
        response = requests.post(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.ok)

    def delete_group_user(self, group_id: str, user_id: str):
        url = f'{self.base_uri}/group/{group_id}/users/{user_id}'
        response = requests.delete(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.ok)

    def read_group_annotations(self, group_id: str):
        url = f'{self.base_uri}/group/{group_id}/annotations'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, HTTPStatus.OK,
                                      lambda r: r.json()['annotations'])

    def create_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        expected_status = HTTPStatus.OK
        response = requests.post(url=url)
        return self.__handle_response(response, expected_status,
                                      lambda r: r.ok)

    def delete_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        expected_status = HTTPStatus.OK
        response = requests.delete(url=url)
        return self.__handle_response(response, expected_status,
                                      lambda r: r.ok)

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
