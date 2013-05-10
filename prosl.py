'''Flag potential problems in the text of a file.

Currently this can look for three types of things that are known to make prose 
more difficult to read: sentences with too many words, sentences with too many
characters, and words repeated in close proximity. All parameters can be 
configured at runtime.

Run with -h for detailed options.

Created on Nov 26, 2012

@author: Henry Keiter
@version: Python 3.3

@TODO: Publish
@TODO: use string.punctuation!!
'''

import collections
import os
import sys
from _resources improt NWS_DELIMITERS, TERMINATORS, NON_TERMINATORS, PUNCTUATION

def _common_words(**opts):
    if opts.get('track_all_words'):
        return ['']
    from _resources import COMMON_WORDS
    if opts.get('extended_list'):
        from _resources improt COMMON_WORDS_EXTENSION
        w = [x for x in COMMON_WORDS + COMMON_WORDS_EXTENSION]
        w.sort()
        return w
    return [x for x in COMMON_WORDS]

def _search(a, x):
    '''Quick & dirty binary search for the common word list.'''
    if not a:
        raise ValueError("Key not found.")
    midpt = len(a)//2
    if a[midpt] > x:
        return _search(a[:midpt], x)
    elif a[midpt] < x:
        return midpt+1+_search(a[midpt+1:], x)
    return midpt

def _option_parser():
    '''
    TODO:
    Other options: 
        identify multiple speakers in one paragraph?
        track & identify repeated punctuation?
    '''
    from optparse import OptionParser
    parser = OptionParser('usage: %prog filename [options], or '
                          '%prog -h to display help')
    parser.add_option('-a','--track-all-words', action='store_true', 
                      default=False, help='Run proximity check even for common '
                      'words.')
    parser.add_option('-c', '--char-count', dest='char_thresh', type='int', 
        default=0,
        help='Flag sentences with a character count of CHAR-COUNT or more')
    parser.add_option('-e','--extended-list',action='store_true',default=False,
                      help='Use extended common word filter for proximity '
                      'checking (overrides "-a").')
    parser.add_option('-f','--file',dest='out_file',help='Write results to the '
                      'given file instead of to the screen.')
    parser.add_option('-m','--line-nums',action='store_true',
                      default=False,help='Store line numbers with flags.(TODO)')
    parser.add_option('-n','--nostats',dest='stats',action='store_false',
                      default=True,help='Turn off the general statistics.')
    parser.add_option('-p','--prox', dest='proximity', type='int', default=0,
        help='Flag passages using the same word repeatedly (unless it is a '
        'common word in English). The argument is the minimum proximity for '
        'uncommon words.')
    parser.add_option('-w', '--word-count', dest='word_thresh', type='int', 
        default=0, 
        help='Flag sentences with a word count of WORD-COUNT or more')
    return parser

def _split_text(text):
    tokens = text.split()
    for d in NWS_DELIMITERS:
        tokens = reduce(lambda a,b:a+b,map(lambda x:x.split(d),tokens),[])
    return tokens


def _gunning_fog_index(stats):
    '''
    Higher = harder
    
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
    Higher = harder
    
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

def _count_syllables(word):
    '''Get a real or estimated value for the number of syllables in the word.
    
    If the word is present in the Miscellaneous/res/mhyph10 hyphenated corpus,
    return the number of syllables found there (get an unhyphenated version
    as well, in which to do the lookup?). Otherwise, estimate the number of
    syllables as best as possible (_estimate_syllables(word)).
    '''
    raise NotImplementedError

def _estimate_syllables(word):
    '''
    '''
    raise NotImplementedError

def _get_stats(text):
    '''TODO: More stats!
        
        Syllable Distribution
            map from integers (num_sylls) to integers (count)
        Syllable Count
            total syllable count in the text
    '''
    
    split = _split_text(text)
    stats = {
             'Word Count':len(split),
             'Character Count':len(text),
             'Average Word Length':sum(map(len,split))/float(len(split)),
             'Average Sentence Length':None
             }
    alnum_count = 0
    sentences = []
    current_sen = []
    frequency = {}
    for token in split:
        current_sen.append(token)
        if any(t in token for t in TERMINATORS):
            if not any(t in token for t in NON_TERMINATORS):
                sentences.append(' '.join(current_sen))
                current_sen = []
        
        #Frequency analysis
        # Note that if augmented forms appear before basic ones, they'll both
        # be caught separately. Consider using a wordlist to improve this, e.g.
        # http://www.sil.org/linguistics/wordlists/english/wordlist/wordsEn.txt
        stoken = token.strip(PUNCTUATION).lower()
        alnum_count += len(stoken)
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
    top_twenty = frequency.items()
    top_twenty.sort(key=lambda x:x[1],reverse=1)
    stats['Top Twenty Words'] = top_twenty[:20]
    stats['Lexical Density'] = 100*(float(stats['Unique Words'])/
                                    stats['Word Count'])
    return stats

def validate(text, **opts):
    proximity = opts.get('proximity', 0)
    wthresh = opts.get('word_thresh', 17)
    cthresh = opts.get('char_thresh', 95)
    _common_word_list = _common_words(**opts)
    
    phrases = []
    last_n_simple_tokens = collections.deque([], proximity)
    last_n_tokens = collections.deque([], proximity+1)
    current_sentence = []
    
    for token in _split_text(text):
        simpletoken = token.strip(PUNCTUATION).lower()
        if proximity:
            last_n_tokens.append(token)
            try:
                _search(_common_word_list, simpletoken)
            except ValueError:
                if simpletoken in last_n_simple_tokens:
                    phrases.append(('Proximity threshold exceeded', simpletoken,
                                    ' '.join(last_n_tokens)))
            last_n_simple_tokens.append(simpletoken)
        current_sentence.append(token)
        if any(t in token for t in TERMINATORS):
            if not any(t in token for t in NON_TERMINATORS):
                # End of sentence; check for problems.
                if wthresh and len(current_sentence) >= wthresh:
                    phrases.append(('Word-count threshold exceeded', 
                                    len(current_sentence),
                                    ' '.join(current_sentence)))
                if cthresh and reduce(lambda a,b: a + len(b), 
                                      current_sentence, 0) > cthresh:
                    phrases.append(('Character-count threshold exceeded', 
                                    reduce(lambda a,b: a + len(b), 
                                           current_sentence, 0),
                                    ' '.join(current_sentence)))
                # Reset current sentence
                current_sentence = []
    phrases.sort()
    return phrases, _get_stats(text) if opts.get('stats') else {}
    
def _format_stats(stats, indices=False):
    '''
    @TODO indices currently never True (not implemented)
    '''
    s = ('Character Count:\t\t\t%d\n'
         'Letter Count:   \t\t\t%d\n'
         'Word Count: \t\t\t\t%d\n'
         'Sentence Count: \t\t\t%d\n'
         'Average Sentence Length:\t%.3f words\n'
         'Average Word Length:\t\t%.3f characters\n'
         'Unique Words:   \t\t\t%d\n'
         'Top Twenty Words:   \t\t%s\n'
         'Lexical Density:\t\t\t%.1f%%\n')
    vals = [stats['Character Count'],stats['Letter Count'],stats['Word Count'], 
            stats['Sentence Count'], stats['Average Sentence Length'], 
            stats['Average Word Length'], stats['Unique Words'], 
            ', '.join(map(lambda x:x[0]+' ('+str(x[1])+')',
                          stats['Top Twenty Words'])),
            stats['Lexical Density']]
    if indices:
        s += ('Indices:\n'
              '\tGunning-Fog:\t\t\t%.3f (Education Level)'
              '\tColeman-Liau:   \t\t%.3f (Education Level)'
              '\tFlecsh-Kincaid: \t\t%.f (Readability Score)'
              )
        vals.extend([
                     _gunning_fog_index(stats),
                     _coleman_liau_index(stats),
                     _flesch_kincaid_index(stats)
                     ])
    return s % tuple(vals)

def main():
    parser = _option_parser()
    try:
        opts, args = parser.parse_args(sys.argv)
    except:
        return
    try:
        with open(os.path.abspath(args[1]), 'rb') as f:
            text = f.read()
    except:
        print('Unable to open file "%s".')
        return
    
    flags, stats = validate(text, **opts.__dict__)
    stats['flag_count'] = len(flags) 
    if opts.out_file:
        try:
            with open(os.path.abspath(opts.out_file), 'wb') as f:
                f.write('\n'.join(map(str,flags)))
                f.write('Total number of flags:\t%s\n' % len(flags))
                if stats:
                    f.write('\n\n### Stats ###\n\n')
                    f.write(_format_stats(stats))
        except:
            print('Error writing flags to file.')
    else:
        print('\n'.join(map(str,flags)))
        print('Total number of flags:\t%s' % len(flags))
        if stats:
            print('\n\n### Stats ###\n\n')
            print(_format_stats(stats))

if __name__ == '__main__':
    main()
