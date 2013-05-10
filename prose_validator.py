'''Flag potential problems in the text of a file.

Currently this can look for three types of things that are known to make prose 
more difficult to read: sentences with too many words, sentences with too many
characters, and words repeated in close proximity. All parameters can be 
configured at runtime.

Run prose_validator.py -h for detailed options.

Created on Nov 26, 2012

@author: DrBwaa

@TODO: Publish this version (github maybe?)
@TODO: use string.punctuation!!
'''

import collections
import os
import sys

_COMMON_WORDS = ["","a","about","all","an","and","are","as","at",
    "be","been","but","by","call","can","come","could","day","did",
    "do","down","each","find","first","for","from","go","had","has",
    "have","he","her","him","his","hot","how","i","if","in","is","it",
    "know","like","long","look","make","many","may","more","most",
    "my","no","now","number","of","on","one","or","other","out",
    "over","people","said","see","she","side","so","some","sound",
    "than","that","the","their","them","then","there","these","they",
    "thing","this","time","to","two","up","use","was","water","way",
    "we","were","what","when","which","who","will","with","word",
    "would","write","you","your"]

_COMMON_WORDS_EXTENSION = ["able","above","act","add","afraid","after",
    "again","against","age","ago","agree","air","allow","also",
    "always","am","among","anger","animal","answer","any","appear",
    "apple","area","arm","arrange","arrive","art","ask","atom",
    "baby","back","bad","ball","band","bank","bar","base","basic",
    "bat","bear","beat","beauty","bed","before","began","begin",
    "behind","believe","bell","best","better","between","big","bird",
    "bit","black","block","blood","blow","blue","board","boat",
    "body","bone","book","born","both","bottom","bought","box","boy",
    "branch","bread","break","bright","bring","broad","broke",
    "brother","brought","brown","build","burn","busy","buy","came",
    "camp","capital","captain","car","card","care","carry","case",
    "cat","catch","caught","cause","cell","cent","center","century",
    "certain","chair","chance","change","character","charge","chart",
    "check","chick","chief","child","children","choose","chord",
    "circle","city","claim","class","clean","clear","climb","clock",
    "close","clothe","cloud","coast","coat","cold","collect","colony",
    "color","column","common","company","compare","complete",
    "condition","connect","consider","consonant","contain","continent",
    "continue","control","cook","cool","copy","corn","corner",
    "correct","cost","cotton","count","country","course","cover",
    "cow","crease","create","crop","cross","crowd","cry","current",
    "cut","dad","dance","danger","dark","dead","deal","dear","death",
    "decide","decimal","deep","degree","depend","describe","desert",
    "design","determine","develop","dictionary","die","differ",
    "difficult","direct","discuss","distant","divide","division",
    "doctor","does","dog","dollar","don't","done","door","double",
    "draw","dream","dress","drink","drive","drop","dry","duck",
    "during","ear","early","earth","ease","east","eat","edge",
    "effect","egg","eight","either","electric","element","else","end",
    "enemy","energy","engine","enough","enter","equal","equate",
    "especially","even","evening","event","ever","every","exact",
    "example","except","excite","exercise","expect","experience",
    "experiment","eye","face","fact","fair","fall","family","famous",
    "far","farm","fast","fat","father","favor","fear","feed","feel",
    "feet","fell","felt","few","field","fig","fight","figure","fill",
    "final","fine","finger","finish","fire","fish","fit","five",
    "flat","floor","flow","flower","fly","follow","food","foot",
    "force","forest","form","forward","found","four","fraction",
    "free","fresh","friend","front","fruit","full","fun","game",
    "garden","gas","gather","gave","general","gentle","get","girl",
    "give","glad","glass","gold","gone","good","got","govern",
    "grand","grass","gray","great","green","grew","ground","group",
    "grow","guess","guide","gun","hair","half","hand","happen",
    "happy","hard","hat","head","hear","heard","heart","heat",
    "heavy","held","help","here","high","hill","history","hit",
    "hold","hole","home","hope","horse","hour","house","huge",
    "human","hundred","hunt","hurry","ice","idea","imagine","inch",
    "include","indicate","industry","insect","instant","instrument",
    "interest","invent","iron","island","job","join","joy","jump",
    "just","keep","kept","key","kill","kind","king","knew","lady",
    "lake","land","language","large","last","late","laugh","law",
    "lay","lead","learn","least","leave","led","left","leg","length",
    "less","let","letter","level","lie","life","lift","light","line",
    "liquid","list","listen","little","live","locate","log","lone",
    "lost","lot","loud","love","low","machine","made","magnet",
    "main","major","man","map","mark","market","mass","master",
    "match","material","matter","me","mean","meant","measure","meat",
    "meet","melody","men","metal","method","middle","might","mile",
    "milk","million","mind","mine","minute","miss","mix","modern",
    "molecule","moment","money","month","moon","morning","mother",
    "motion","mount","mountain","mouth","move","much","multiply",
    "music","must","name","nation","natural","nature","near",
    "necessary","neck","need","neighbor","never","new","next","night",
    "nine","noise","noon","nor","north","nose","note","nothing",
    "notice","noun","numeral","object","observe","occur","ocean",
    "off","offer","office","often","oh","oil","old","once","only",
    "open","operate","opposite","order","organ","original","our",
    "own","oxygen","page","paint","pair","paper","paragraph","parent",
    "part","particular","party","pass","past","path","pattern","pay",
    "perhaps","period","person","phrase","pick","picture","piece",
    "pitch","place","plain","plan","plane","planet","plant","play",
    "please","plural","poem","point","poor","populate","port","pose",
    "position","possible","post","pound","power","practice","prepare",
    "present","press","pretty","print","probable","problem","process",
    "produce","product","proper","property","protect","prove",
    "provide","pull","push","put","quart","question","quick","quiet",
    "quite","quotient","race","radio","rail","rain","raise","ran",
    "range","rather","reach","read","ready","real","reason","receive",
    "record","red","region","remember","repeat","reply","represent",
    "require","rest","result","rich","ride","right","ring","rise",
    "river","road","rock","roll","room","root","rope","rose","round",
    "row","rub","rule","run","safe","sail","salt","same","sand",
    "sat","save","saw","say","scale","school","science","score",
    "sea","search","season","seat","second","section","seed","seem",
    "segment","select","self","sell","send","sense","sent","sentence",
    "separate","serve","set","settle","seven","several","shall",
    "shape","share","sharp","sheet","shell","shine","ship","shoe",
    "shop","shore","short","should","shoulder","shout","show","sight",
    "sign","silent","silver","similar","simple","since","sing",
    "single","sister","sit","six","size","skill","skin","sky",
    "slave","sleep","slip","slow","small","smell","smile","snow",
    "soft","soil","soldier","solution","solve","son","song","soon",
    "south","space","speak","special","speech","speed","spell",
    "spend","spoke","spot","spread","spring","square","stand","star",
    "start","state","station","stay","stead","steam","steel","step",
    "stick","still","stone","stood","stop","store","story","straight",
    "strange","stream","street","stretch","string","strong","student",
    "study","subject","substance","subtract","success","such","sudden",
    "suffix","sugar","suggest","suit","summer","sun","supply",
    "support","sure","surface","surprise","swim","syllable","symbol",
    "system","table","tail","take","talk","tall","teach","team",
    "teeth","tell","temperature","ten","term","test","thank","thick",
    "thin","think","third","those","though","thought","thousand",
    "three","through","throw","thus","tie","tiny","tire","together",
    "told","tone","too","took","tool","top","total","touch","toward",
    "town","track","trade","train","travel","tree","triangle","trip",
    "trouble","truck","true","try","tube","turn","twenty","type",
    "under","unit","until","us","usual","valley","value","vary",
    "verb","very","view","village","visit","voice","vowel","wait",
    "walk","wall","want","war","warm","wash","watch","wave","wear",
    "weather","week","weight","well","went","west","wheel","where",
    "whether","while","white","whole","whose","why","wide","wife",
    "wild","win","wind","window","wing","winter","wire","wish",
    "woman","women","won't","wonder","wood","work","world","written",
    "wrong","wrote","yard","year","yellow","yes","yet","young"]

def _common_words(**opts):
    if opts.get('extended_list'):
        w = [x for x in _COMMON_WORDS + _COMMON_WORDS_EXTENSION]
        w.sort()
        return w
    if opts.get('track_all_words'):
        return ['']
    return [x for x in _COMMON_WORDS]

_NWS_DELIMITERS = ['--','-','\x97']
_PUNCTUATION = ''.join(['.',',','?','!',"'",'"',':',';','(',')','/','`','-',
                       '\x92','\x93','\x94','\x97'])
_TERMINATORS = ['.', '?', '!']
_NON_TERMINATORS = ['Dr.', 'Ms.', 'Mrs.', 'Mr.', 'Mme.', 'Jr.', 'Sr.']

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
    for d in _NWS_DELIMITERS:
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
        if any(t in token for t in _TERMINATORS):
            if not any(t in token for t in _NON_TERMINATORS):
                sentences.append(' '.join(current_sen))
                current_sen = []
        
        #Frequency analysis
        # Note that if augmented forms appear before basic ones, they'll both
        # be caught separately. Consider using a wordlist to improve this, e.g.
        # http://www.sil.org/linguistics/wordlists/english/wordlist/wordsEn.txt
        stoken = token.strip(_PUNCTUATION).lower()
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
        simpletoken = token.strip(_PUNCTUATION).lower()
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
        if any(t in token for t in _TERMINATORS):
            if not any(t in token for t in _NON_TERMINATORS):
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
        print 'Unable to open file "%s".'
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
            print 'Error writing flags to file.'
    else:
        print '\n'.join(map(str,flags))
        print 'Total number of flags:\t%s' % len(flags)
        if stats:
            print ('\n\n### Stats ###\n\n')
            print _format_stats(stats)

if __name__ == '__main__':
    main()
