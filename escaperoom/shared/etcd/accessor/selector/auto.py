def selector(selector):

    from .group import EtcdGroupSelector
    from .regex import EtcdRegexSelector
    from .wildcard import EtcdWildcardSelector
    from .key import EtcdKey

    selector = str(selector)

    if ',' in selector:
        return EtcdGroupSelector(selector)

    if selector.startswith('^'):
        return EtcdRegexSelector(selector)

    if '*' in selector:
        return EtcdWildcardSelector(selector)

    return EtcdKey(selector)
