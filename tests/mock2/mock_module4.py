import unittest


def test_func():
    pass


class MyTestClass5(unittest.TestCase):
    def test_11(self):
        pass

    def te_11(self):
        pass

    def __test(self):
        pass

    @staticmethod
    def test_static():
        pass


class MyTestClass6(MyTestClass5):
    def test_12(self):
        pass


class NotUnitTest(object):
    def test_13(self):
        pass