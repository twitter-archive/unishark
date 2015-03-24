import unittest
import unishark


class UtilTestCase(unittest.TestCase):
    def test_contexts(self):
        unishark.contexts.set('mydata', [1, 2, 3, 4])
        my_contexts = unishark.ContextManager()
        my_contexts.set('mydata', {'a': 1})
        self.assertDictEqual(unishark.contexts.get('mydata'), {'a': 1})


if __name__ == '__main__':
    unittest.main(verbosity=2)