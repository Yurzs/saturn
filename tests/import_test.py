import unittest


class ImportTest(unittest.TestCase):

    def test(self):
        saturn = __import__('saturn', globals=globals(), fromlist=[''])
        self.assertTrue(hasattr(saturn, 'engine'))
