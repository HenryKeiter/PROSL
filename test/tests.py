'''Unit testing module for prosl'''

import sys
import os
import unittest
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
import prosl
import prosl_utils
import _resources


class TestAnalytics(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_string(self):
        pass

    def test_search(self):
        pass

    def test_insensitive_string_search(self):
        pass


class TestCore(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_string(self):
        pass

    def test_search(self):
        pass

    def test_insensitive_string_search(self):
        pass


class TestFormatting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_string(self):
        pass

    def test_search(self):
        pass

    def test_insensitive_string_search(self):
        pass


class TestResources(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_syllable_dict(self):
        syll_lu = prosl._resources.get_syllable_dict()
        self.assertIsInstance(syll_lu, dict)

        self.assertEqual(2, syll_lu.get('aa'))
        self.assertEqual(4, syll_lu.get('a cappella'))
        self.assertEqual(3, syll_lu.get('zyrian'))
        self.assertIsNone(syll_lu.get('Ahab'))


class TestUtils(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_string(self):
        s = 'abcdefg'
        self.assertEqual(prosl_utils.split_string(s), [s])
        self.assertEqual(prosl_utils.split_string(s, ' '), [s])
        self.assertEqual(prosl_utils.split_string(s, 
                                                        split_whitespace=False),
                         [s])
        ###
        s = 'abc  defg'
        self.assertEqual(prosl_utils.split_string(s), ['abc', 'defg'])
        self.assertEqual(prosl_utils.split_string(s, ' '), 
                         ['abc', 'defg'])
        self.assertEqual(prosl_utils.split_string(s,' ',split_whitespace=False), 
                         ['abc', '', 'defg'])
        ###
        s = 'a b`c!d--e><f\\g  '
        self.assertEqual(prosl_utils.split_string(s),
                         ['a', 'b`c!d--e><f\\g'])
        self.assertEqual(prosl_utils.split_string(s, '`', '--', '\\'),
                         ['a', 'b', 'c!d', 'e><f', 'g'])
        self.assertEqual(prosl_utils.split_string(s, '><', 
                                                        split_whitespace=False),
                         ['a b`c!d--e', 'f\\g  '])
        ###
        s = ''
        self.assertEqual(prosl_utils.split_string(s), [])
        self.assertEqual(prosl_utils.split_string(s, ' '), [])
        self.assertEqual(prosl_utils.split_string(s, split_whitespace=False),[])
        self.assertEqual(prosl_utils.split_string(s, 'a', 'b'), [])

    def test_search(self):
        self.assertEqual(-1, prosl_utils.search(3, []))
        self.assertEqual(-1, prosl_utils.search(3, [1]))
        self.assertEqual(0,  prosl_utils.search(1, [1]))
        ###
        self.assertEqual(0,  prosl_utils.search(1, [1, 3, 5]))
        self.assertEqual(1,  prosl_utils.search(3, [1, 3, 5]))
        self.assertEqual(2,  prosl_utils.search(5, [1, 3, 5]))
        self.assertEqual(-1, prosl_utils.search(0, [1, 3, 5]))
        self.assertEqual(-1, prosl_utils.search(2, [1, 3, 5]))
        self.assertEqual(-1, prosl_utils.search(4, [1, 3, 5]))
        self.assertEqual(-1, prosl_utils.search(6, [1, 3, 5]))
        ###
        self.assertEqual(0,  prosl_utils.search(1, [1, 3, 5, 7]))
        self.assertEqual(1,  prosl_utils.search(3, [1, 3, 5, 7]))
        self.assertEqual(2,  prosl_utils.search(5, [1, 3, 5, 7]))
        self.assertEqual(3,  prosl_utils.search(7, [1, 3, 5, 7]))
        self.assertEqual(-1, prosl_utils.search(0, [1, 3, 5, 7]))
        self.assertEqual(-1, prosl_utils.search(2, [1, 3, 5, 7]))
        self.assertEqual(-1, prosl_utils.search(4, [1, 3, 5, 7]))
        self.assertEqual(-1, prosl_utils.search(6, [1, 3, 5, 7]))
        self.assertEqual(-1, prosl_utils.search(8, [1, 3, 5, 7]))

    def test_insensitive_string_search(self):
        self.assertEqual(-1, prosl_utils.insensitive_string_search('a', []))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('b', ['a']))
        self.assertEqual(0,  prosl_utils.insensitive_string_search('a', ['a']))
        ###
        self.assertEqual(0,  prosl_utils.insensitive_string_search('a', 
                         ['a', 'c', 'e']))
        self.assertEqual(1,  prosl_utils.insensitive_string_search('c', 
                         ['a', 'c', 'e']))
        self.assertEqual(2,  prosl_utils.insensitive_string_search('e', 
                         ['a', 'c', 'e']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('z', 
                         ['a', 'c', 'e']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('b', 
                         ['a', 'c', 'e']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('d', 
                         ['a', 'c', 'e']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('f', 
                         ['a', 'c', 'e']))
        ###
        self.assertEqual(0,  prosl_utils.insensitive_string_search('a',
                         ['a','c','e','g']))
        self.assertEqual(1,  prosl_utils.insensitive_string_search('c',
                         ['a','c','e','g']))
        self.assertEqual(2,  prosl_utils.insensitive_string_search('e',
                         ['a','c','e','g']))
        self.assertEqual(3,  prosl_utils.insensitive_string_search('g',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('z',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('b',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('d',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('f',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('h',
                         ['a','c','e','g']))
        ###
        self.assertEqual(0,  prosl_utils.insensitive_string_search('A',
                         ['a','c','e','g']))
        self.assertEqual(1,  prosl_utils.insensitive_string_search('C',
                         ['a','c','e','g']))
        self.assertEqual(2,  prosl_utils.insensitive_string_search('E',
                         ['a','c','e','g']))
        self.assertEqual(3,  prosl_utils.insensitive_string_search('G',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('Z',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('B',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('D',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('F',
                         ['a','c','e','g']))
        self.assertEqual(-1, prosl_utils.insensitive_string_search('H',
                         ['a','c','e','g']))
        ###
        self.assertRaises(AttributeError, prosl_utils.insensitive_string_search,
                          1, ['a','c','e','g'])

    def test_memoized(self):
        pass


if __name__ == '__main__':
    unittest.main()
