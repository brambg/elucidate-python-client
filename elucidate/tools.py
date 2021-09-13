def split_annotation(annotation: dict):
    body = annotation['body']
    target = annotation['target']
    custom_keys = [
        key
        for key in annotation
        if key not in ['body', 'target', '@context', 'id', 'type']
    ]

    custom = {k: annotation[k] for k in custom_keys}
    return body, target, custom
