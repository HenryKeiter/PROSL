'''Flag potential problems in the text of a file.

Currently this can look for three types of things that are known to make prose 
more difficult to read: sentences with too many words, sentences with too many
characters, and words repeated in close proximity. All parameters can be 
configured at runtime.

Run with -h for detailed options.

Created on Nov 26, 2012

@author: Henry Keiter
@version: Python 3.3
'''

import argparse
import collections
import os
import sys
import _resources
from prosl_utils import insensitive_string_search,search,split_string,memoized

SYLLABLE_LOOKUP = _resources.get_syllable_dict()

PROXIMITY_FLAG = 10
CTHRESH_FLAG = 20
WTHRESH_FLAG = 30


@memoized
def _count_syllables(word):
    '''Get a real or estimated value for the number of syllables in the word.
    
    If the word is present in the mhyph hyphenated corpus,
    return the number of syllables found there. Else, estimate the number of
    syllables as best as (easily) possible (_estimate_syllables(word)).

    @NOTE: The given word should be lowercase, or it will fall through this 
    function to the estimation function.
    '''
    
    count = SYLLABLE_LOOKUP.get(word)
    if count is None:
        return _estimate_syllables(word)
    return count

def _estimate_syllables(word):
    '''Estimate the number of syllables in the given word.

    This method is very crude, but reasonably effective for this use.

    Strategy:
        Count all vowels (aeiouy) in the word.
        Ignore every second vowel in a dipthong+ (ou -> 1; uou -> 2)
        Ignore final 'e'
        Return the greater of <the number of remaining "vowels", or 1>
    '''
    
    if not word:
        return 0

    if len(word) < 3:
        return 1

    sylls = 0
    last_ch = None
    for ch in word:
        if ch in _resources.VOWELS:
            if last_ch in _resources.VOWELS:
                last_ch = None
            else:
                sylls += 1
                last_ch = ch
        else:
            last_ch = ch
    if word.endswith('e') or word.endswith('E'):
        sylls -= 1
    return max(sylls, 1)

def _gunning_fog_index(stats):
    '''
    Higher = more difficult
    
    Reading Level (Grade) = (avg_words_per_sen + 
        percent_words_with_3_or_more_syllables) * 0.4
    '''
    
    sylmap = stats['Syllable Distribution']
    total = stats['Syllable Count']
    three_or_more = total-(sylmap.get(1,0)+sylmap.get(2,0))
    percentage = float(three_or_more)/total
    
    return 0.4 * (stats['Average Sentence Length'] + percentage)

def _coleman_liau_index(stats):
    '''
    Higher = more difficult
    
    Reading Level (grade) = (5.88 * avg_letters_per_word) - (29.6 * 
        (num_sentences/num_words)) - 15.8
    '''
    
    return (5.88 * stats['Average Word Length']) - (29.6 * 
        (float(stats['Sentence Count'])/stats['Word Count'])) - 15.8

def _flesch_kincaid_index(stats):
    '''
    Higher = easier
    
    Reading Ease = 206.835 - (1.015 * avg_words_per_sen) \
        - (84.6 * avg_syll_per_word)
    '''
    
    return (206.835 - (1.015 * stats['Average Sentence Length']) - 
            (84.6 * float(stats['Syllable Count'])/stats['Word Count']))

def _split_text(text):
    '''Split up the given text in a useful way.

    This splits the text into individual tokens. The returned vaule is a 
    generator that yields `(line_num, token)` pairs. `line_num` is 1-indexed.
    '''

    for line_num, line in enumerate(text.split('\n')):
        for token in split_string(line, *_resources.NWS_DELIMITERS):
            yield (line_num + 1, token)

def get_stats(text, indices=False):
    '''Get a bunch of statistics about the text.'''
    
    split = [token for _, token in _split_text(text)]
    stats = {
             'Word Count':len(split),
             'Character Count':len(text),
             'Average Word Length':sum(map(len,split))/float(len(split)),
             'Average Sentence Length':None
             }
    alnum_count = 0
    if indices:
        syllable_dist = {}
    sentences = []
    current_sen = []
    frequency = {}
    for token in split:
        current_sen.append(token)
        if any(t in token for t in _resources.TERMINATORS):
            if not any(t in token for t in _resources.NON_TERMINATORS):
                sentences.append(' '.join(current_sen))
                current_sen = []
        
        #Frequency analysis
        # @Note that if augmented forms appear before basic ones, they'll both
        # be caught separately. Consider using a wordlist to improve this, e.g.
        # http://www.sil.org/linguistics/wordlists/english/wordlist/wordsEn.txt
        stoken = token.strip(_resources.PUNCTUATION).lower()
        alnum_count += len(stoken)
        if indices:
            sylls = _count_syllables(stoken)
            syllable_dist[sylls] = syllable_dist.get(sylls, 0) + 1
        if stoken in frequency:
            frequency[stoken] += 1
        else: 
            if stoken.endswith(('d','s')):
                if stoken[:-1] in frequency:
                    frequency[stoken[:-1]] += 1
                    continue
                elif stoken.endswith(('ed','es',"'s","\x92s")):
                    if stoken[:-2] in frequency:
                        frequency[stoken[:-2]] += 1
                        continue
            elif stoken.endswith('ing'):
                if stoken[:-3] in frequency:
                    frequency[stoken[:-3]] += 1
                    continue
            frequency[stoken] = 1
    
    stats['Letter Count'] = alnum_count
    stats['Average Sentence Length'] = (sum(map(len,map(str.split,sentences)))/
                                        float(len(sentences)))
    stats['Sentence Count'] = len(sentences)
    stats['Unique Words'] = len(frequency)
    top_twenty = sorted(frequency.items(), key=lambda x:(-x[1], x[0]))[:20]
    stats['Top Twenty Words'] = top_twenty
    stats['Lexical Density'] = 100*(float(stats['Unique Words'])/
                                    stats['Word Count'])
    if indices:
        stats['Syllable Distribution'] = syllable_dist
        stats['Syllable Count'] = sum(k*v for k, v in syllable_dist.items())

    return stats

def analyze(text, **opts):
    proximity = opts.get('proximity', 0)
    wthresh = opts.get('word_thresh', 17)
    cthresh = opts.get('char_thresh', 95)
    _common_word_list = _resources.common_words(**opts)
    
    problem_phrases = []
    last_n_simple_tokens = collections.deque([], proximity)
    last_n_tokens = collections.deque([], proximity+1)
    current_sentence = []
    
    for line_num, token in _split_text(text):
        simpletoken = token.strip(_resources.PUNCTUATION).lower()
        if proximity:
            last_n_tokens.append(token)
            if search(simpletoken, _common_word_list) == -1:
                if simpletoken in last_n_simple_tokens:
                    problem_phrases.append((PROXIMITY_FLAG,line_num,simpletoken, 
                                           ' '.join(last_n_tokens)))
            last_n_simple_tokens.append(simpletoken)
        current_sentence.append(token)
        if any(t in token for t in _resources.TERMINATORS):
            if not any(t in token for t in _resources.NON_TERMINATORS):
                # End of sentence; check for problems.
                if wthresh and len(current_sentence) >= wthresh:
                    problem_phrases.append((WTHRESH_FLAG, line_num, 
                                           len(current_sentence),
                                           ' '.join(current_sentence)))
                if cthresh:
                    lsen = sum(len(w) for w in current_sentence)
                    if lsen > cthresh:
                        problem_phrases.append((CTHRESH_FLAG, line_num, lsen, 
                                               ' '.join(current_sentence)))
                # Reset current sentence
                current_sentence = []
    problem_phrases.sort()
    return problem_phrases

def _format_flag(flag):
    '''Format a single flag in a human-readable way.

    Flags consist of four parts: the flag type, the line number, the offending 
    stat (such as length, repeated word, etc), and the full phrase.
    '''

    flag_type = flag[0]
    if flag_type == PROXIMITY_FLAG:
        return ('Line {1:d}: Proximity threshold '
                'exceeded for the word "{2}": "{3}"').format(*flag)
    elif flag_type == CTHRESH_FLAG:
        return ('Line {1:d}: Character-count threshold exceeded ({2:d} '
                'characters) in the following sentence: "{3}"').format(*flag)
    elif flag_type == WTHRESH_FLAG:
        return ('Line {1:d}: Word-count threshold exceeded ({2:d} words) '
                'in the following sentence: "{3}"').format(*flag)
    return str(flag)
 
def _format_stats(stats, indices=False):
    '''
    '''
    s = '\n'.join(['Character Count:\t\t\t{:d}',
                  'Letter Count:   \t\t\t{:d}',
                  'Word Count: \t\t\t\t{:d}',
                  'Sentence Count: \t\t\t{:d}',
                  'Average Sentence Length:\t{:.2f} words',
                  'Average Word Length:\t\t{:.2f} characters',
                  'Unique Words:   \t\t\t{:d}',
                  'Top Twenty Words:   \t\t{:s}',
                  'Lexical Density:\t\t\t{:.1f}%\n'])
    vals = [stats['Character Count'],
            stats['Letter Count'],
            stats['Word Count'], 
            stats['Sentence Count'],
            stats['Average Sentence Length'], 
            stats['Average Word Length'], 
            stats['Unique Words'], 
            ', '.join(map(lambda x:x[0]+' ('+str(x[1])+')',
                          stats['Top Twenty Words'])),
            stats['Lexical Density']]
    if indices:
        s += ('Indices:\n'
              '\tGunning-Fog:\t\t\t{:.3f} (Education Level)\n'
              '\tColeman-Liau:   \t\t{:.3f} (Education Level)\n'
              '\tFlecsh-Kincaid: \t\t{:.3f} (Readability Score)\n'
              )
        vals.extend([
                     _gunning_fog_index(stats),
                     _coleman_liau_index(stats),
                     _flesch_kincaid_index(stats)
                     ])
    return s.format(*vals)

def _get_flag_desc(**opts):
    proximity = opts.get('proximity', 0)
    wthresh = opts.get('word_thresh', 17)
    cthresh = opts.get('char_thresh', 95)
    if not (proximity or wthresh or cthresh):
        return 'No flags were defined.'
    s = 'Flags are for {}.'
    args = []
    if wthresh:
        args.append('sentence length > {} words'.format(wthresh-1))
    if cthresh:
        args.append('sentence length > {} characters'.format(cthresh-1))
    if proximity:
        args.append(
            'two occurrences of an uncommon word < {} words apart'.format(
                                                                proximity-1))
    return s.format(', or '.join(args))

def write_results(flags, statistics, **opts):
    out = sys.stdout
    if opts.get('out_file'):
        try:
            f = open(os.path.abspath(opts['out_file']), 'w', encoding='utf-8')
            out = f
        except IOError:
            print('Error writing to file')
    try:
        print('\n'.join(map(_format_flag,flags)), file=out)
        print('Total number of flags:\t{}'.format(len(flags)), file=out)
        print(_get_flag_desc(**opts), file=out)
        if statistics:
            print('\n\n### Stats ###\n\n', file=out)
            print(_format_stats(statistics, opts.get('indices')), file=out)
    except IOError:
        print('Error writing to file')
    finally:
        if opts.get('out_file'):
            out.close()

def _arg_parser():
    '''
    TODO:
    Other options: 
        identify multiple speakers in one paragraph?
        track & identify repeated punctuation?
    '''
    
    parser = argparse.ArgumentParser('usage: %prog FILENAME [options], or '
                                     '%prog -h to display help')
    parser.add_argument('filename', help="The file to read")
    parser.add_argument('-a','--track-all-words', action='store_true', 
                      default=False, 
                      help='Run proximity check even for common words.')
    parser.add_argument('-c', '--char-count', dest='char_thresh', type=int, 
        default=0, metavar='CHAR_COUNT',
        help='Flag sentences with a character count of CHAR_COUNT or more')
    parser.add_argument('-e','--extended-list',action='store_true',default=False,
                      help='Use extended common word filter for proximity '
                      'checking (overrides "-a").')
    parser.add_argument('-f','--file',dest='out_file',help='Write results to the '
                      'given file instead of to the screen.')
    parser.add_argument('-i','--indices', dest='indices', action='store_true',
                        default=False, help='Calculate various'
                        'readability scores for the text.')
    parser.add_argument('-n','--nostats',dest='stats',action='store_false',
                      default=True,help='Turn off the general statistics.')
    parser.add_argument('-p','--prox', dest='proximity', type=int, default=0,
        help='Flag passages using the same word repeatedly (unless it is a '
        'common word in English). The argument is the minimum proximity for '
        'uncommon words.')
    parser.add_argument('-w', '--word-count', dest='word_thresh', type=int, 
        default=0, metavar='WORD_COUNT',
        help='Flag sentences with a word count of WORD_COUNT or more')
    return parser

def main():
    parser = _arg_parser()
    filename = None
    try:
        if testing and len(sys.argv) < 2:
            sys.argv.extend(testing)
        opts = vars(parser.parse_args(sys.argv[1:]))
    except Exception as e:
        print('Error parsing arguments: {!s}'.format(e))
    try:
        filename = os.path.abspath(opts['filename'])
        with open(filename, 'r') as f:
            filename = f.name
            text = f.read()
    except IOError as e:
        print('Unable to read file "{}".'.format(filename))
        parser.print_help()
        return
    
    flags = analyze(text, **opts)
    stats = (get_stats(text, opts.get('indices', False)) if opts.get('stats') 
             else {})
    write_results(flags, stats, **opts)

    _count_syllables.cache.clear()

testing = [r'./test/mobydick.txt','-e','-w','22','-c','100','-p','17','-i']

if __name__ == '__main__':
    main()
