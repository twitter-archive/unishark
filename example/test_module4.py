import math
import unittest
import unishark

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
]


def is_prime(n):
    if n % 2 == 0:
        return False
    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


class Test1(unittest.TestCase):
    def setUp(self):
        conf = unishark.contexts.get('example.config')
        print('setUp(): got context "example.config": %r' % conf)

    def test_primes_1(self):
        self.assertTrue(is_prime(PRIMES[0]))

    @unittest.expectedFailure
    def test_primes_2(self):
        self.assertTrue(is_prime(PRIMES[1]))
        raise AssertionError

    def test_primes_3(self):
        self.assertTrue(is_prime(PRIMES[2]))
        raise RuntimeError('Let it throw error.')

    @unittest.expectedFailure
    def test_primes_4(self):
        self.assertTrue(is_prime(PRIMES[3]))

    @unittest.skip('')
    def test_primes_5(self):
        self.assertTrue(is_prime(PRIMES[4]))

    def test_primes_6(self):
        self.assertTrue(is_prime(PRIMES[5]))