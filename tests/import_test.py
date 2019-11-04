import unittest


class ImportTest(unittest.TestCase):

    def test(self):
        saturn = __import__('saturn', globals=globals(), fromlist=[''])
        self.assertTrue(hasattr(saturn, 'engine'))
        self.assertTrue(hasattr(saturn, 'protocol'))
        self.assertTrue(hasattr(saturn, 'socks'))
        self.assertTrue(hasattr(saturn, 'auth'))
        self.assertTrue(hasattr(saturn, 'dispatcher'))
        self.assertTrue(hasattr(saturn, 'state'))
