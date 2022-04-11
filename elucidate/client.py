import http.client
import requests
from datetime import datetime
from http import HTTPStatus
from requests import Response
from typing import Union

from elucidate.model import AnnotationCollection, ElucidateFailure, ElucidateSuccess, AnnotationIdentifier, \
    ContainerIdentifier, ElucidateResponse

default_anno_context = "http://www.w3.org/ns/anno.jsonld"

jsonld_headers = {
    'Accept': f'application/ld+json; profile="{default_anno_context}"',
    'Content-Type': f'application/ld+json; profile="{default_anno_context}"'
}

json_headers = {
    'Accept': 'application/json;charset=UTF-8',
    'Content-Type': 'application/json;charset=UTF-8'
}


class ElucidateClient:
    def __init__(self, base_uri: str, raise_exceptions: bool = True, verbose: bool = False):
        self.base_uri = base_uri
        self.version = 'w3c'
        self.raise_exceptions = raise_exceptions
        self.verbose = verbose

    def __str__(self):
        return f"ElucidateClient:\n  base_uri = {self.base_uri}\n  version = {self.version}\n  raise_exceptions = {self.raise_exceptions}"

    def __repr__(self):
        return self.__str__()

    def use_w3c(self):
        """Switch to using the W3C Web Annotation format"""
        self.version = 'w3c'

    def use_oa(self):
        """Switch to using the Open Annotation format"""
        self.version = 'oa'

    def create_container(self, label: str = 'A Container for Web Annotations', container_id: str = None):
        """
        Create a new container for annotations

        :param label: The label of the Container, to distinguish this container from others. The default label is 'A Container for Web Annotations'
        :type label: str
        :param container_id: The id of the Container, when omitted, elucidate autogenerates a uuid
        :type label: str
        :return: The identifier of the created container
        :rtype: ContainerIdentifier
        """
        url = f'{self.base_uri}/w3c/'
        body = {
            "@context": [
                default_anno_context,
                "http://www.w3.org/ns/ldp.jsonld"
            ],
            "type": [
                "BasicContainer",
                "AnnotationCollection"
            ],
            "label": label
        }
        headers = jsonld_headers.copy()
        if container_id:
            headers['slug'] = container_id
        response = requests.post(
            url=url,
            headers=headers,
            json=body)
        return self.__handle_response(response, {
            HTTPStatus.CREATED: lambda r: ContainerIdentifier(r.headers['location'])
        })

    def read_container(self, container_identifier: ContainerIdentifier) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """
        Read the container identified by the given ContainerIdentifier

        :param container_identifier:
        :type container_identifier: ContainerIdentifier
        :return: The AnnotationCollection
        :rtype: dict
        """
        url = f'{self.base_uri}/{self.version}/{container_identifier.uuid}/'
        response = requests.get(
            url=url,
            headers=jsonld_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: as_annotation_collection
        })

    def read_container_identifier(self, name: str) -> Union[None, ContainerIdentifier]:
        """
        Read the ContainerIdentifier of the container identified by the given container name, or None if not found

        :param name:
        :type name:
        :return: The ContainerIdentifier, or None
        :rtype: Union[None, ContainerIdentifier]
        """
        url = f'{self.base_uri}/{self.version}/{name}/'
        response = requests.get(
            url=url,
            headers=jsonld_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: ContainerIdentifier(r.json()['id']),
            HTTPStatus.NOT_FOUND: lambda r: None
        })

    # def delete_container(self, container_identifier: str):
    #     """
    #     Delete the container identified by the given ContainerIdentifier
    #
    #     :param container_identifier:
    #     :type container_identifier: ContainerIdentifier
    #     :return: A Boolean indicating whether the delete succeeded
    #     :rtype: bool
    #     """
    #     url = f'{self.base_uri}/{self.version}/{container_identifier}/'
    #     response = requests.delete(url=url)
    #     return self.__handle_response(response, HTTPStatus.NO_CONTENT,
    #                                   lambda r: True)

    def create_annotation(self, container_id: ContainerIdentifier, body, target, custom=None, custom_contexts=None,
                          annotation_id: str = None):
        """
        Create an annotation in the container with the given ContainerIdentifier
        You must provide at least a body and a target, and optionally provide additional (root) elements in custom

        :param annotation_id:
        :type annotation_id:
        :param container_id:
        :type container_id: ContainerIdentifier
        :param body:
        :type body: Any
        :param target:
        :type target: Any
        :param custom:
        :type custom: dict
        :return: The identifier of the generated annotation
        :rtype: AnnotationIdentifier
        """
        if custom is None:
            custom = {}
        context = default_anno_context
        if custom_contexts:
            if isinstance(custom_contexts, (str, dict)):
                context = [default_anno_context, custom_contexts]
            elif isinstance(custom_contexts, list):
                context = [default_anno_context, *custom_contexts]
        annotation = {
            "@context": context,
            "type": "Annotation",
            "body": body,
            "target": target
        }
        annotation.update(custom)
        headers = jsonld_headers.copy()
        if annotation_id:
            headers['slug'] = annotation_id
        response = requests.post(
            url=container_id.url,
            headers=headers,
            json=annotation)

        return self.__handle_response(response, {
            HTTPStatus.CREATED: lambda r: AnnotationIdentifier(r.headers['location'], r.headers['etag'][3:-1])
        })

    # TODO: Annotation Histories
    def read_annotation(self, annotation_identifier: AnnotationIdentifier):
        """

        :param annotation_identifier:
        :type annotation_identifier:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        response = requests.get(
            url=url,
            headers=jsonld_headers
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def update_annotation(self, annotation_identifier: AnnotationIdentifier, body, target, custom=None,
                          custom_contexts=None):
        """

        :param annotation_identifier:
        :type annotation_identifier:
        :param body:
        :type body:
        :param target:
        :type target:
        :param custom:
        :type custom:
        :return:
        :rtype:
        """
        if custom is None:
            custom = {}
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        annotation = {
            "@context": default_anno_context,
            "type": "Annotation",
            "body": body,
            "target": target
        }
        annotation.update(custom)
        put_headers = {'If-Match': annotation_identifier.etag}
        put_headers.update(jsonld_headers)
        response = requests.put(
            url=url,
            headers=put_headers,
            json=annotation)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: AnnotationIdentifier(annotation_identifier.url, r.headers['etag'][3:-1])
        })

    def delete_annotation(self, annotation_identifier: AnnotationIdentifier):
        """

        :param annotation_identifier:
        :type annotation_identifier:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        del_headers = {'If-Match': annotation_identifier.etag}
        del_headers.update(jsonld_headers)
        response = requests.delete(
            url=url,
            headers=del_headers)
        return self.__handle_response(response, {
            HTTPStatus.NO_CONTENT: lambda r: r.ok
        })

    def __search_by_part(self, part: str, fields: str, value: str, strict: bool = False, xywh: str = None,
                         t: str = None, creator: str = None, generator: str = None):
        url = f'{self.base_uri}/w3c/services/search/{part}'
        params = dict(fields=fields, value=value, strict=strict)
        if xywh:
            params['xywh'] = xywh
        if t:
            params['t'] = t
        if creator:
            params['creator'] = creator
        if generator:
            params['generator'] = generator
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_annotation_collection
        })

    def search_by_body_id(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                          creator: str = None, generator: str = None) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :param xywh:
        :type xywh:
        :param t:
        :type t:
        :param creator:
        :type creator:
        :param generator:
        :type generator:
        :return:
        :rtype:
        """
        return self.__search_by_part('body', 'id', value, strict, xywh, t, creator, generator)

    def search_by_body_source(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                              creator: str = None, generator: str = None) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :param xywh:
        :type xywh:
        :param t:
        :type t:
        :param creator:
        :type creator:
        :param generator:
        :type generator:
        :return:
        :rtype:
        """
        return self.__search_by_part('body', 'source', value, strict, xywh, t, creator, generator)

    def search_by_target_id(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                            creator: str = None, generator: str = None) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :param xywh:
        :type xywh:
        :param t:
        :type t:
        :param creator:
        :type creator:
        :param generator:
        :type generator:
        :return:
        :rtype:
        """
        return self.__search_by_part('target', 'id', value, strict, xywh, t, creator, generator)

    def search_by_target_source(self, value: str, strict: bool = False, xywh: str = None, t: str = None,
                                creator: str = None, generator: str = None) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :param xywh:
        :type xywh:
        :param t:
        :type t:
        :param creator:
        :type creator:
        :param generator:
        :type generator:
        :return:
        :rtype:
        """
        return self.__search_by_part('target', 'source', value, strict, xywh, t, creator, generator)

    def __search_by_role(self, role: str, levels: str, type: str, value: str,
                         strict: bool = False) -> Union[AnnotationCollection, ElucidateResponse]:
        url = f'{self.base_uri}/w3c/services/search/{role}'
        params = dict(levels=levels, type=type, value=value, strict=strict)
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_annotation_collection
        })

    def search_by_annotation_creator_id(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='annotation', type='id', value=value, strict=strict)

    def search_by_annotation_creator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='annotation', type='name', value=value, strict=strict)

    def search_by_annotation_creator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='annotation', type='nickname', value=value,
                                     strict=strict)

    def search_by_annotation_creator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='annotation', type='email', value=value, strict=strict)

    def search_by_annotation_creator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='annotation', type='emailsha1', value=value,
                                     strict=strict)

    def search_by_annotation_generator_id(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='annotation', type='id', value=value, strict=strict)

    def search_by_annotation_generator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='annotation', type='name', value=value, strict=strict)

    def search_by_annotation_generator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='annotation', type='nickname', value=value,
                                     strict=strict)

    def search_by_annotation_generator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='annotation', type='email', value=value,
                                     strict=strict)

    def search_by_annotation_generator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='annotation', type='emailsha1', value=value,
                                     strict=strict)

    def search_by_body_creator_id(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='body', type='id', value=value, strict=strict)

    def search_by_body_creator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='body', type='name', value=value, strict=strict)

    def search_by_body_creator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='body', type='nickname', value=value, strict=strict)

    def search_by_body_creator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='body', type='email', value=value, strict=strict)

    def search_by_body_creator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='body', type='emailsha1', value=value, strict=strict)

    def search_by_body_generator_id(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='body', type='id', value=value, strict=strict)

    def search_by_body_generator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='body', type='name', value=value, strict=strict)

    def search_by_body_generator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='body', type='nickname', value=value, strict=strict)

    def search_by_body_generator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='body', type='email', value=value, strict=strict)

    def search_by_body_generator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='body', type='emailsha1', value=value, strict=strict)

    def search_by_target_creator_id(self, value: str, strict: bool = False):
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='target', type='id', value=value, strict=strict)

    def search_by_target_creator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='target', type='name', value=value, strict=strict)

    def search_by_target_creator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='target', type='nickname', value=value, strict=strict)

    def search_by_target_creator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='target', type='email', value=value, strict=strict)

    def search_by_target_creator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value: str
        :param strict:
        :type strict: bool
        :return:
        :rtype:
        """
        return self.__search_by_role(role='creator', levels='target', type='emailsha1', value=value, strict=strict)

    def search_by_target_generator_id(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value:
        :param strict:
        :type strict:
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='target', type='id', value=value, strict=strict)

    def search_by_target_generator_name(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value:
        :param strict:
        :type strict:
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='target', type='name', value=value, strict=strict)

    def search_by_target_generator_nickname(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value:
        :param strict:
        :type strict:
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='target', type='nickname', value=value, strict=strict)

    def search_by_target_generator_email(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value:
        :param strict:
        :type strict:
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='target', type='email', value=value, strict=strict)

    def search_by_target_generator_emailsha1(self, value: str, strict: bool = False) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param value:
        :type value:
        :param strict:
        :type strict:
        :return:
        :rtype:
        """
        return self.__search_by_role(role='generator', levels='target', type='emailsha1', value=value,
                                     strict=strict)

    def __search_by_temporal(self, levels: str, types: str, since: datetime) -> Union[
        AnnotationCollection, ElucidateResponse]:
        url = f'{self.base_uri}/w3c/services/search/temporal'
        since_param = since.isoformat()
        if since.microsecond == 0:
            since_param += ".00000"
        since_param += 'Z'
        params = dict(levels=levels, types=types, since=since_param)
        response = requests.get(
            url=url,
            params=params
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_annotation_collection
        })

    def search_by_annotation_created_since(self, since: datetime) -> Union[ElucidateResponse, AnnotationCollection]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='annotation', types='created', since=since)

    def search_by_annotation_modified_since(self, since: datetime) -> Union[
        ElucidateResponse, AnnotationCollection]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='annotation', types='modified', since=since)

    def search_by_annotation_generated_since(self, since: datetime) -> Union[
        AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='annotation', types='generated', since=since)

    def search_by_body_created_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='body', types='created', since=since)

    def search_by_body_modified_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='body', types='modified', since=since)

    def search_by_body_generated_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='body', types='generated', since=since)

    def search_by_target_created_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='target', types='created', since=since)

    def search_by_target_modified_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='target', types='modified', since=since)

    def search_by_target_generated_since(self, since: datetime) -> Union[AnnotationCollection, ElucidateResponse]:
        """

        :param since:
        :type since:
        :return:
        :rtype:
        """
        return self.__search_by_temporal(levels='target', types='generated', since=since)

    def __get_statistics(self, part: str, field: str):
        url = f'{self.base_uri}/{self.version}/services/stats/{part}'
        response = requests.get(
            url=url,
            headers=jsonld_headers,
            params={"field": field})
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def get_body_id_statistics(self):
        """

        :return:
        :rtype:
        """
        return self.__get_statistics('body', 'id')

    def get_body_source_statistics(self):
        """

        :return:
        :rtype:
        """
        return self.__get_statistics('body', 'source')

    def get_target_id_statistics(self):
        """

        :return:
        :rtype:
        """
        return self.__get_statistics('target', 'id')

    def get_target_source_statistics(self):
        """

        :return:
        :rtype:
        """
        return self.__get_statistics('target', 'source')

    def do_batch_update(self, body, target):
        """

        :param body:
        :type body:
        :param target:
        :type target:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/w3c/services/batch/update'
        json = {
            "@context": default_anno_context,
            "body": body,
            "target": target
        }
        response = requests.post(
            url=url,
            headers=jsonld_headers,
            json=json
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def do_batch_delete(self, body, target):
        """

        :param body:
        :type body:
        :param target:
        :type target:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/w3c/services/batch/delete'
        json = {
            "@context": default_anno_context,
            "body": body,
            "target": target
        }
        response = requests.post(
            url=url,
            headers=jsonld_headers,
            json=json
        )
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def read_current_user(self):
        """

        :return:
        :rtype:
        """
        url = f'{self.base_uri}/user/current'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def create_group(self, label: str):
        """

        :param label:
        :type label:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group'
        response = requests.post(
            url=url,
            headers=json_headers,
            json={"label": label})
        return self.__handle_response(response, {
            HTTPStatus.CREATED: lambda r: r.json()['id']
        })

    def read_group(self, group_id: str):
        """

        :param group_id:
        :type group_id:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: as_json_dict
        })

    def read_group_users(self, group_id: str):
        """

        :param group_id:
        :type group_id:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}/users'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.json()['users']
        })

    def create_group_user(self, group_id: str, user_id: str):
        """

        :param group_id:
        :type group_id:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}/users/{user_id}'
        response = requests.post(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.ok
        })

    def delete_group_user(self, group_id: str, user_id: str):
        """

        :param group_id:
        :type group_id:
        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}/users/{user_id}'
        response = requests.delete(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.ok
        })

    def read_group_annotations(self, group_id: str):
        """

        :param group_id:
        :type group_id:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}/annotations'
        response = requests.get(
            url=url,
            headers=json_headers)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.json()['annotations']
        })

    def create_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        """

        :param group_id: The group id
        :type group_id: str
        :param annotation_identifier: The annotation identifier
        :type annotation_identifier: AnnotationIdentifier
        :return: Whether the creation succeeded
        :rtype: bool
        """
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        response = requests.post(url=url)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.ok
        })

    def delete_group_annotation(self, group_id: str, annotation_identifier: AnnotationIdentifier):
        """

        :param group_id:
        :type group_id:
        :param annotation_identifier:
        :type annotation_identifier:
        :return:
        :rtype:
        """
        url = f'{self.base_uri}/group/{group_id}/annotation/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}'
        response = requests.delete(url=url)
        return self.__handle_response(response, {
            HTTPStatus.OK: lambda r: r.ok
        })

    def __handle_response(self, response: Response, result_producers: dict):
        status_code = response.status_code
        status_message = http.client.responses[status_code]
        if self.verbose:
            print(f'-> {response.request.method} {response.request.url}')
            print(f'<- {status_code} {status_message}')
        if status_code in result_producers:
            result = result_producers[response.status_code](response)
            if self.raise_exceptions:
                return result
            else:
                return ElucidateSuccess(response, result)
        elif self.raise_exceptions:
            raise Exception(
                f'{response.request.method} {response.request.url} returned {status_code} {status_message} : "{response.text}"')
        else:
            return ElucidateFailure(response)


def as_annotation_collection(response: Response) -> Union[AnnotationCollection, ElucidateResponse]:
    json = response.json()
    return AnnotationCollection(json['total'], json['id'], json['first'], json.get('label'))


def as_json_dict(response: Response) -> dict:
    return response.json()
