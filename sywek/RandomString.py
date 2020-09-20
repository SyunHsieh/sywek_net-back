import random


def RandomSelectString(sample_letters, count):
    # sample_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678790abcdefghijklmnopqrstuvwxyz'
    result_str = ''.join((random.choice(sample_letters)
                          for i in range(count)))
    return result_str
