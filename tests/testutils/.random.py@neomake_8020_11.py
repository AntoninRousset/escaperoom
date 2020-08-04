def gen_by_name(name):

    generators = {
        'str': random_string,
        'int': random_int,
        'float': random_float,
        'dict': random_dict,
    }

    if name == 'random':
        name = list(generators.values())

    if isinstance(name, list):
        from random import choice
        return generators[choice(name)]
    else:
        return generators[name]


def random_int():
    from random import randint
    return randint(1, 1 << 64) - 1


def random_float():
    from random import random
    return random() * random_int()


def random_string(nmin=4, nmax=32):
    from random import randint, choices
    from string import printable
    return ''.join(choices(printable, k=randint(nmin, nmax)))


def random_hex(exclude=None):
    from random import randint

    exclude = exclude or set()

    while True:
        key = randint(1, 1 << 64) - 1
        return f'{key:016x}'


def random_key():
    return 'test/' + random_hex()


def random_list(content_type='random', n=None):

    gen = gen_by_name(content_type)

    if n is None:
        from random import randint
        n = randint(0, 1024)

    return [gen() for _ in range(n)]


def random_dict():
    return {random_string(): 42
            for i in range(32)}
