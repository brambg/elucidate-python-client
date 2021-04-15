import requests


def hello():
    '''hello...'''
    print('hello')


headers = {
    'Accept': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"',
    'Content-Type': 'application/ld+json; profile="http://www.w3.org/ns/anno.jsonld"'
}


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

    def create_container(self, label: str = 'A Container for Web Annotations'):
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
        container_id = response.headers['location']
        return ContainerIdentifier(container_id)

    def get_container(self, container_identifier: ContainerIdentifier):
        return requests.get(f'{self.base_uri}/{self.version}/{container_identifier.uuid}/').json()

    def create_annotation(self, container_id: ContainerIdentifier, body, target):
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
        annotation_id = response.json()['id']
        return AnnotationIdentifier(annotation_id)

    def get_annotation(self, annotation_identifier: AnnotationIdentifier):
        return requests.get(
            f'{self.base_uri}/{self.version}/{annotation_identifier.container_uuid}/{annotation_identifier.uuid}').json()
