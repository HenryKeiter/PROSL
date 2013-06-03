'''Unit testing module for prosl'''

import sys
import os
import unittest
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
import prosl
import prosl_utils
import _resources

# A preposterous sentence from Moby Dick
lorem_ipsum = ('Though in many natural objects, whiteness refiningly enhances '
               'beauty, as if imparting some special virtue of its own, as in '
               'marbles, japonicas, and pearls; and though various nations '
               'have in some way recognised a certain royal preeminence in this'
               ' hue; even the barbaric, grand old kings of Pegu placing the '
               'title "Lord of the White Elephants" above all their other '
               'magniloquent ascriptions of dominion; and the modern kings of '
               'Siam unfurling the same snow white quadruped in the royal '
               'standard; and the Hanoverian flag bearing the one figure of a '
               'snow white charger; and the great Austrian Empire, Caesarian, '
               'heir to overlording Rome, having for the imperial colour the '
               'same imperial hue; and though this pre eminence in it applies '
               'to the human race itself, giving the white man ideal mastership'
               ' over every dusky tribe; and though, besides, all this, '
               'whiteness has been even made significant of gladness, for among'
               ' the Romans a white stone marked a joyful day; and though in '
               'other mortal sympathies and symbolizings, this same hue is made'
               ' the emblem of many touching, noble things the innocence of '
               'brides, the benignity of age; though among the Red Men of '
               'America the giving of the white belt of wampum was the deepest '
               'pledge of honour; though in many climes, whiteness typifies the'
               ' majesty of Justice in the ermine of the Judge, and contributes'
               ' to the daily state of kings and queens drawn by milk white '
               'steeds; though even in the higher mysteries of the most august '
               'religions it has been made the symbol of the divine '
               'spotlessness and power; by the Persian fire worshippers, the '
               'white forked flame being held the holiest on the altar; and in '
               'the Greek mythologies, Great Jove himself being made incarnate '
               'in a snow white bull; and though to the noble Iroquois, the '
               'midwinter sacrifice of the sacred White Dog was by far the '
               'holiest festival of their theology, that spotless, faithful '
               'creature being held the purest envoy they could send to the '
               'Great Spirit with the annual tidings of their own fidelity; and'
               ' though directly from the Latin word for white, all Christian '
               'priests derive the name of one part of their sacred vesture, '
               'the alb or tunic, worn beneath the cassock; and though among '
               'the holy pomps of the Romish faith, white is specially employed'
               ' in the celebration of the Passion of our Lord; though in the '
               'Vision of St. John, white robes are given to the redeemed, and '
               'the four and twenty elders stand clothed in white before the '
               'great white throne, and the Holy One that sitteth there white '
               'like wool; yet for all these accumulated associations, with '
               'whatever is sweet, and honourable, and sublime, there yet lurks'
               ' an elusive something in the innermost idea of this hue, which '
               'strikes more of panic to the soul than that redness which '
               'affrights in blood.')

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_estimate_syllables(self):
        self.assertEqual(0, prosl._estimate_syllables(''))

        self.assertEqual(1, prosl._estimate_syllables('a'))
        self.assertEqual(1, prosl._estimate_syllables('an'))
        self.assertEqual(1, prosl._estimate_syllables('I'))

        self.assertEqual(1, prosl._estimate_syllables('the'))
        self.assertEqual(1, prosl._estimate_syllables('ate'))
        self.assertEqual(1, prosl._estimate_syllables('oat'))
        
        self.assertEqual(1, prosl._estimate_syllables('nn'))
        self.assertEqual(1, prosl._estimate_syllables('tree'))
        self.assertEqual(1, prosl._estimate_syllables('fire'))
        self.assertEqual(1, prosl._estimate_syllables('pale'))
        self.assertEqual(1, prosl._estimate_syllables('gross'))
        self.assertEqual(1, prosl._estimate_syllables('strengths'))
        self.assertEqual(5, prosl._estimate_syllables('archaeopterix'))
        self.assertEqual(4, prosl._estimate_syllables('pterodactyl'))
        self.assertEqual(1, prosl._estimate_syllables('hound'))
        self.assertEqual(2, prosl._estimate_syllables('hounded'))
        self.assertEqual(2, prosl._estimate_syllables('vacuum'))
        self.assertEqual(3, prosl._estimate_syllables('continuum'))
        self.assertEqual(4, prosl._estimate_syllables('superfluous'))

        # And a couple of incorrect results
        self.assertEqual(1, prosl._estimate_syllables('apple'))
        self.assertEqual(2, prosl._estimate_syllables('faced'))
        self.assertEqual(2, prosl._estimate_syllables('james'))

    def test_count_syllables(self):
        self.assertEqual(0, prosl._count_syllables(''))

        self.assertEqual(1, prosl._count_syllables('a'))
        self.assertEqual(1, prosl._count_syllables('an'))
        self.assertEqual(1, prosl._count_syllables('I'))

        self.assertEqual(1, prosl._count_syllables('the'))
        self.assertEqual(1, prosl._count_syllables('ate'))
        self.assertEqual(1, prosl._count_syllables('oat'))
        
        self.assertEqual(1, prosl._count_syllables('fire'))
        self.assertEqual(1, prosl._count_syllables('pale'))
        self.assertEqual(1, prosl._count_syllables('gross'))
        self.assertEqual(1, prosl._count_syllables('strengths'))
        self.assertEqual(5, prosl._count_syllables('archaeopterix'))
        self.assertEqual(4, prosl._count_syllables('pterodactyl'))
        self.assertEqual(1, prosl._count_syllables('hound'))
        self.assertEqual(2, prosl._count_syllables('hounded'))
        self.assertEqual(3, prosl._count_syllables('vacuum')) #vac-u-um
        self.assertEqual(4, prosl._count_syllables('continuum'))
        self.assertEqual(4, prosl._count_syllables('superfluous'))

        self.assertEqual(2, prosl._count_syllables('apple'))
        self.assertEqual(1, prosl._count_syllables('james'))

        # Definitely not found in the dictionary; fall through to estimation.
        self.assertEqual(2, prosl._count_syllables('qwerty'))
        self.assertEqual(4, prosl._count_syllables('CAPITALIZE'))

    def test_gunning_fog_index(self):
        # Just some fake small stats
        stats = {
            'Syllable Distribution' : {1: 7, 2: 2, 3: 9},
            'Syllable Count' : 38,
            'Average Sentence Length' : 9
        }
        self.assertAlmostEqual(3.905263157894737,
                               prosl._gunning_fog_index(stats))

        # lorem ipsum dolor sit amet (etc etc etc)
        stats = {
            'Syllable Distribution' : {1: 21, 2: 23, 3: 17, 4: 5, 5: 3},
            'Syllable Count' : 153,
            'Average Sentence Length' : 17.25
        }
        self.assertAlmostEqual(7.184967320261439,
                               prosl._gunning_fog_index(stats))

        # lorem_ipsum
        stats = {
            'Syllable Distribution' : {1: 307, 2: 108, 3: 40, 4: 18, 5: 2},
            'Syllable Count' : 725,
            'Average Sentence Length' : 475
        }
        self.assertAlmostEqual(190.1710344827586,
                               prosl._gunning_fog_index(stats))

    def test_coleman_liau_index(self):
        # Just some fake small stats
        stats = {
            'Word Count' : 18,
            'Sentence Count' : 2,
            'Average Word Length' : 4
        }
        self.assertAlmostEqual(4.431111111111111,
                               prosl._coleman_liau_index(stats))

        # lorem ipsum dolor sit amet (etc etc etc)
        stats = {
            'Word Count' : 69,
            'Sentence Count' : 4,
            'Average Word Length' : 5.478260869565218
        }
        self.assertAlmostEqual(14.696231884057969,
                               prosl._coleman_liau_index(stats))

        # lorem_ipsum
        stats = {
            'Word Count' : 475,
            'Sentence Count' : 1,
            'Average Word Length' : 4.827368421052632
        }
        self.assertAlmostEqual(12.522610526315791,
                               prosl._coleman_liau_index(stats))

    def test_flesch_kincaid_index(self):
        # Just some fake small stats
        stats = {
            'Word Count' : 18,
            'Syllable Count' : 38,
            'Average Sentence Length' : 9
        }
        self.assertAlmostEqual(19.100000000000023,
                               prosl._flesch_kincaid_index(stats))

        # lorem ipsum dolor sit amet (etc etc etc)
        stats = {
            'Word Count' : 69,
            'Syllable Count' : 153,
            'Average Sentence Length' : 17.25
        }
        self.assertAlmostEqual(1.7349456521739341,
                               prosl._flesch_kincaid_index(stats))

        # lorem_ipsum
        stats = {
            'Word Count' : 475,
            'Syllable Count' : 725,
            'Average Sentence Length' : 475
        }
        self.assertAlmostEqual(-404.41631578947363,
                               prosl._flesch_kincaid_index(stats))


class TestCore(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_split_text(self):
        split = prosl._split_text(lorem_ipsum)
        self.assertRaises(TypeError, len, split)
        split_words = []
        for line_num, token in split:
            self.assertEqual(1, line_num)
            split_words.append(token)
        self.assertEqual(475, len(split_words))
        self.assertEqual('Though', split_words[0])
        self.assertEqual('blood.', split_words[-1])
        self.assertEqual('in', split_words[-2])
        self.assertEqual('of', split_words[200])

    def test_analyze(self):
        
        # No testing extended_list option here, since that's 
        # tested more effectively in TestResources.

        flags = prosl.analyze(lorem_ipsum, proximity=15, word_thresh=0,
                                     char_thresh=0)
        self.assertEqual(6, len(flags))
        self.assertEqual(prosl.PROXIMITY_FLAG, flags[0][0])

        flags = prosl.analyze(lorem_ipsum, proximity=15, word_thresh=0,
                                     char_thresh=0, track_all_words=True)
        self.assertEqual(92, len(flags))
        self.assertEqual(prosl.PROXIMITY_FLAG, flags[0][0])

        flags = prosl.analyze(lorem_ipsum, proximity=0, word_thresh=20,
                                     char_thresh=0)
        self.assertEqual(1, len(flags))
        self.assertEqual(prosl.WTHRESH_FLAG, flags[0][0])

        flags = prosl.analyze(lorem_ipsum, proximity=0, word_thresh=0,
                                     char_thresh=100)
        self.assertEqual(1, len(flags))
        self.assertEqual(prosl.CTHRESH_FLAG, flags[0][0])

    def test_get_stats(self):
        stats = prosl.get_stats(lorem_ipsum)
        
        self.assertEqual(len(lorem_ipsum), stats.get('Character Count'))
        self.assertEqual(2235, stats.get('Letter Count'))
        self.assertEqual(1, stats.get('Sentence Count'))
        self.assertEqual(475, stats.get('Word Count'))
        self.assertEqual(475, stats.get('Average Sentence Length'))
        self.assertAlmostEqual(4.827368421052632, 
                               stats.get('Average Word Length'))
        self.assertEqual(252, stats.get('Unique Words'))
        self.assertEqual([('the',56),('of',30),('and',21),('in',17),
                          ('white',16),('though',12),('to',7),('a',5),
                          ('this',5),('all',4),('for',4),('great',4),
                          ('hue',4),('made',4),('their',4),('among',3),
                          ('being',3),('by',3),('even',3),('is',3)], 
                         stats.get('Top Twenty Words'))
        self.assertAlmostEqual(53.05263157894737, stats.get('Lexical Density'))

        # With indices
        stats = prosl.get_stats(lorem_ipsum, indices=True)
        
        self.assertEqual(len(lorem_ipsum), stats.get('Character Count'))
        self.assertEqual(2235, stats.get('Letter Count'))
        self.assertEqual(1, stats.get('Sentence Count'))
        self.assertEqual(725, stats.get('Syllable Count'))
        self.assertEqual({1: 307, 2: 108, 3: 40, 4: 18, 5: 2},
                         stats.get('Syllable Distribution'))
        self.assertEqual(475, stats.get('Word Count'))
        self.assertEqual(475, stats.get('Average Sentence Length'))
        self.assertAlmostEqual(4.827368421052632, 
                               stats.get('Average Word Length'))
        self.assertEqual(252, stats.get('Unique Words'))
        self.assertEqual([('the',56),('of',30),('and',21),('in',17),
                          ('white',16),('though',12),('to',7),('a',5),
                          ('this',5),('all',4),('for',4),('great',4),
                          ('hue',4),('made',4),('their',4),('among',3),
                          ('being',3),('by',3),('even',3),('is',3)], 
                         stats.get('Top Twenty Words'))
        self.assertAlmostEqual(53.05263157894737, stats.get('Lexical Density'))


class TestFormatting(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_format_flag(self):
        self.assertEqual('Line 1: Proximity threshold exceeded for the '
                         'word "foo": "foo bar baz foo"', 
                         prosl._format_flag((prosl.PROXIMITY_FLAG, 1, 'foo',
                                             'foo bar baz foo')))
        self.assertEqual('Line 1: Character-count threshold exceeded (1000 '
                         'characters) in the following sentence: '
                         '"foo bar baz foo"', 
                         prosl._format_flag((prosl.CTHRESH_FLAG, 1, 1000,
                                             'foo bar baz foo')))
        self.assertEqual('Line 1: Word-count threshold exceeded (1000 '
                         'words) in the following sentence: '
                         '"foo bar baz foo"', 
                         prosl._format_flag((prosl.WTHRESH_FLAG, 1, 1000,
                                             'foo bar baz foo')))
        self.assertEqual("(None, 1, 1000, 'foo bar baz foo')", 
                         prosl._format_flag((None, 1, 1000, 'foo bar baz foo')))

    def test_format_stats(self):
        pass

    def test_get_flag_desc(self):
        self.assertEqual('Flags are for sentence length > 21 words, or '
                         'sentence length > 99 characters, or two occurrences '
                         'of an uncommon word < 16 words apart.',
                         prosl._get_flag_desc(word_thresh=22, char_thresh=100,
                                              proximity=17))
        self.assertEqual('Flags are for '
                         'sentence length > 99 characters, or two occurrences '
                         'of an uncommon word < 16 words apart.',
                         prosl._get_flag_desc(word_thresh=0, char_thresh=100,
                                              proximity=17))
        self.assertEqual('Flags are for sentence length > 21 words, or '
                         'two occurrences '
                         'of an uncommon word < 16 words apart.',
                         prosl._get_flag_desc(word_thresh=22, char_thresh=0,
                                              proximity=17))
        self.assertEqual('Flags are for sentence length > 21 words, or '
                         'sentence length > 99 characters.',
                         prosl._get_flag_desc(word_thresh=22, char_thresh=100,
                                              proximity=0))
        self.assertEqual('Flags are for sentence length > 21 words.',
                         prosl._get_flag_desc(word_thresh=22, char_thresh=0,
                                              proximity=0))
        self.assertEqual('Flags are for sentence length > 99 characters.',
                         prosl._get_flag_desc(word_thresh=0, char_thresh=100,
                                              proximity=0))
        self.assertEqual('Flags are for two occurrences '
                         'of an uncommon word < 16 words apart.',
                         prosl._get_flag_desc(word_thresh=0, char_thresh=0,
                                              proximity=17))

        self.assertEqual('No flags were defined.',
                         prosl._get_flag_desc(word_thresh=0, char_thresh=0,
                                              proximity=0))

    def test_write_results(self):
        stats = {}
        flags = []
        out = './testout.txt'
        try:
            prosl.write_results(flags, stats, out_file=out, indices=False)
            with open(out, 'r', encoding='utf-8') as t:
                self.assertEqual(3, len(t.readlines()))

            flags = [(prosl.PROXIMITY_FLAG, 1, 'foo', 'foo bar baz foo'),
                     (prosl.WTHRESH_FLAG, 1, 1000, 'foo bar baz foo')]
            prosl.write_results(flags, stats, out_file=out, indices=False)
            with open(out, 'r', encoding='utf-8') as t:
                self.assertEqual(4, len(t.readlines()))
        except IOError as e:
            fail(e)
        finally:
            if os.path.exists(out):
                try:
                    os.remove(out)
                except Exception as e:
                    print('\nUnable to delete file {}\n'.format(out))


class TestResources(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_common_words(self):
        self.assertEqual(set(), _resources.common_words(track_all_words=True))
        self.assertEqual(_resources.COMMON_WORDS, _resources.common_words())
        self.assertCountEqual((_resources.COMMON_WORDS.union(
                               _resources.COMMON_WORDS_EXTENSION)),
                              _resources.common_words(extended_list=True))

    def test_get_syllable_dict(self):
        syll_lu = _resources.get_syllable_dict()
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
        import time
        try:
            @prosl_utils.memoized
            def t(n):
                s = '0'*1000
                for i in range(n):
                    s = s + str(i)
                return s

            for i in range(50):
                t0 = time.time()
                r1 = t(200000 + i)
                t1 = time.time()
                r2 = t(200000 + i)
                t2 = time.time()

                # Ensure correct result
                self.assertEqual(r1, r2)

                # Ensure cache access is faster than computation
                self.assertLess((t2 - t1), (t1 - t0))

            self.assertEqual(50, len(t.cache))
            t.cache.clear()
            self.assertEqual(0, len(t.cache))
        except AssertionError as ae:
            raise ae
        except Exception as e:
            self.fail(e)


if __name__ == '__main__':
    unittest.main()
    # print(prosl.get_stats(lorem_ipsum, True))
