
def accessor(etcd, sel):

    from .selector import selector
    from .selector.group import EtcdGroupSelector
    from .selector.regex import EtcdRegexSelector
    from .selector.wildcard import EtcdWildcardSelector
    from .selector.unique import EtcdUniqueSelector
    from .group import EtcdGroupSelector
    from .regex import EtcdRegexSelector
    from .wildcard import EtcdWildcardSelector
    from .node import EtcdNode

    sel = selector(sel)

    if isinstance(sel, EtcdGroupSelector):
        return EtcdGroupAccessor(sel)

    if isinstance(sel, EtcdRegexSelector):
        return EtcdRegexAccessor(sel)

    if isinstance(sel, EtcdWildcardSelector):
        return EtcdWildcardAccessor(sel)

    if isinstance(sel, EtcdUniqueSelector):
        return EtcdNodeAccessor(sel)
