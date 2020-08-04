from .group import EtcdGroupSelector
from .wildcard import EtcdWildcardSelector
from .unique import EtcdUniqueSelector
from .regex import EtcdRegexSelector


def selector(selector):

    selector = str(selector)

    if len(selector) > 0 and selector[0] == '^':
        return EtcdRegexSelector(selector)

    if key.count('*') > 0:
        return EtcdWildcardSelector(selector)

    return EtcdUniqueSelector(selector)
