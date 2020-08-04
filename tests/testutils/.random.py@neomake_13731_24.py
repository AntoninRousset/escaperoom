def random(content_type='random'):

    generators = {
        'str': random_string,
        'int': random_int,
        'float': random_float,
        'dict': random_dict,
    }

    if content_type == 'random':
        from random import choice
        gen = choice(generators.values())
    else:
        generators[content_type]

    return generators()



def random_int():
    from random import randint
    return randint(1, 1 << 64) - 1


def random_float():
    from random import random
    return random() * random_int()


def random_string(nmin=4, nmax=32):
    from random import randint, choices
    from string import printable
    return choices(printable, k=randint(nmin, nmax))


def random_hex():
    from random import randint
    key = randint(1, 1 << 64) - 1
    return f'{key:016x}'


def random_key():
    return 'test/' + random_hex()


def random_list(content_type, n=None):

    if n is None:
        from random import randint
        n = randint(0, 1024)

    return [random_generators[content_type]() for _ in range(n)]


def random_dict():

    from random import choice
    {random_string(): choice(random_generators)() for _ in range(32)}
