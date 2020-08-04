
def accessor(etcd, sel):

    from .selector import selector
    from .selector.group import EtcdGroupSelector
    from .selector.regex import EtcdRegexSelector
    from .selector.wildcard import EtcdWildcardSelector
    from .selector.key import EtcdKey
    from .group import EtcdGroupAccessor
    from .regex import EtcdRegexAccessor
    from .wildcard import EtcdWildcardAccessor
    from .node import EtcdNodeAccessor

    sel = selector(sel)

    if isinstance(sel, EtcdGroupSelector):
        return EtcdGroupAccessor(etcd, sel)

    if isinstance(sel, EtcdWildcardSelector):
        return EtcdWildcardAccessor(etcd, sel)

    if isinstance(sel, EtcdRegexSelector):
        return EtcdRegexAccessor(etcd, sel)

    if isinstance(sel, EtcdKey):
        return EtcdNodeAccessor(etcd, sel)
