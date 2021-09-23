def split_annotation(annotation: dict):
    context = annotation['@context']
    body = annotation['body']
    target = annotation['target']
    custom_keys = [
        key
        for key in annotation
        if key not in ['body', 'target', '@context', 'id', 'type']
    ]
    custom = {k: annotation[k] for k in custom_keys}
    if isinstance(context, list) and len(context) > 1:
        custom_contexts = [c for c in context if c != "http://www.w3.org/ns/anno.jsonld"]
    else:
        custom_contexts = None
    return body, target, custom, custom_contexts
