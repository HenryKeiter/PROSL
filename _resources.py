'''Contains various resources for prosl.

@author: Henry Keiter
'''

import os
import string
import gzip

NWS_DELIMITERS = ['--','-','\x97']
PUNCTUATION = ''.join([string.punctuation, '\x92','\x93','\x94','\x97'])
TERMINATORS = ['.', '?', '!']
NON_TERMINATORS = {'Dr.', 'Ms.', 'Mrs.', 'Mr.', 'Mme.', 'Jr.', 'Sr.', 'St.'}

COMMON_WORDS = {"","a","about","all","an","and","are","as","at",
    "be","been","but","by","call","can","come","could","day","did",
    "do","down","each","find","first","for","from","go","had","has",
    "have","he","her","him","his","hot","how","i","if","in","is","it",
    "know","like","long","look","make","many","may","more","most",
    "my","no","now","number","of","on","one","or","other","out",
    "over","people","said","see","she","side","so","some","sound",
    "than","that","the","their","them","then","there","these","they",
    "thing","this","time","to","two","up","use","was","water","way",
    "we","were","what","when","which","who","will","with","word",
    "would","write","you","your"}

COMMON_WORDS_EXTENSION = {"able","above","act","add","afraid","after",
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
    "wrong","wrote","yard","year","yellow","yes","yet","young"}

VOWELS = {'a', 'e', 'i', 'o', 'u', 'y', 'A', 'E', 'I', 'O', 'U', 'Y'}

def common_words(**opts):
    if opts.get('track_all_words'):
        return set()
    if opts.get('extended_list'):
        return COMMON_WORDS.union(COMMON_WORDS_EXTENSION)
    return set(COMMON_WORDS)

def get_syllable_dict():
    '''Get a dict from (lowercase) words/phrases to syllable-count.'''

    syl_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                           'syll_dict.txt.gz')
    try:
        with gzip.open(syl_loc, 'rt', encoding='utf-8') as z:
            env = {}
            exec(z.read(), env)
            return env['SYLLABLE_LOOKUP']
    except IOError as e:
        print('Unable to open syllable file at {}'.format(syl_loc))
        return None

def main():
    d = get_syllable_dict()
    print(d.get('a cappella'))

if __name__ == '__main__':
    main()