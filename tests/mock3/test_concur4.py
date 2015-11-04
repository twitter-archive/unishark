from time import sleep
import unittest
from unishark import contexts

__context__ = 'tests.mock3'
mod_resource = 0
mod_name = __name__.split('.')[-1]


def setUpModule():
    fixture = '%s.setUpModule' % mod_name
    contexts.get(__context__).append(fixture)
    global mod_resource
    mod_resource += 1
    assert mod_resource == 1
    sleep(0.1)


def tearDownModule():
    fixture = '%s.tearDownModule' % mod_name
    contexts.get(__context__).append(fixture)
    global mod_resource
    mod_resource -= 1
    assert mod_resource == 0
    sleep(0.1)


class Class1(unittest.TestCase):
    cls_resource = 0

    @classmethod
    def setUpClass(cls):
        fixture = '%s.%s.setUpClass' % (mod_name, cls.__name__)
        contexts.get(__context__).append(fixture)
        raise RuntimeError('Let setUpClass fail.')

    @classmethod
    def tearDownClass(cls):
        fixture = '%s.%s.tearDownClass' % (mod_name, cls.__name__)
        contexts.get(__context__).append(fixture)
        cls.cls_resource -= 1
        assert cls.cls_resource == 0
        sleep(0.1)

    def setUp(self):
        fixture = '%s.setUp' % '.'.join(self.id().split('.')[-3:])
        contexts.get(__context__).append(fixture)
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.1)

    def tearDown(self):
        fixture = '%s.tearDown' % '.'.join(self.id().split('.')[-3:])
        contexts.get(__context__).append(fixture)
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.1)

    def test_case_1(self):
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.5)

    def test_case_2(self):
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.5)


@unittest.skip('')
class Class2(unittest.TestCase):
    cls_resource = 0

    @classmethod
    def setUpClass(cls):
        sleep(0.1)
        fixture = '%s.%s.setUpClass' % (mod_name, cls.__name__)
        contexts.get(__context__).append(fixture)
        cls.cls_resource += 1
        assert cls.cls_resource == 1

    @classmethod
    def tearDownClass(cls):
        sleep(0.1)
        fixture = '%s.%s.tearDownClass' % (mod_name, cls.__name__)
        contexts.get(__context__).append(fixture)
        cls.cls_resource -= 1
        assert cls.cls_resource == 0

    def setUp(self):
        sleep(0.1)
        fixture = '%s.setUp' % '.'.join(self.id().split('.')[-3:])
        contexts.get(__context__).append(fixture)
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)

    def tearDown(self):
        sleep(0.1)
        fixture = '%s.tearDown' % '.'.join(self.id().split('.')[-3:])
        contexts.get(__context__).append(fixture)
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)

    def test_case_1(self):
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.3)

    def test_case_2(self):
        self.assertEqual(mod_resource, 1)
        self.assertEqual(self.__class__.cls_resource, 1)
        sleep(0.3)
