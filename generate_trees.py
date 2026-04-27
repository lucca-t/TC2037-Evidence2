import nltk
from nltk import CFG

original_grammar = CFG.fromstring("""
    S -> NSC_Subj VS NSC_Obj | NSC_Subj VS 

    NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj
    NSC_Obj -> NSC_Obj Conj NSC_Obj | NS_Obj

    NS_Subj -> Det N_Root N_Subj_End | N_Root N_Subj_End
    NS_Obj -> Det N_Root N_Obj_End | N_Root N_Obj_End

    Det -> 'la'
    N_Root -> 'kat' | 'procion' | 'plant' | 'flor' | 'arb'
    N_Subj_End -> 'o' | 'oj'
    N_Obj_End -> 'on' | 'ojn'

    VS -> V_Root V_End
    V_Root -> 'kresk' | 'kapt' | 'vid' | 'am'
    V_End -> 'as'

    Conj -> 'kaj' | 'au'
""")

cleaned_grammar = CFG.fromstring("""
    S -> NSC_Subj VS NSC_Obj | NSC_Subj VS

    NSC_Subj -> NS_Subj NSC_Subj_A
    NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty
    NSC_Obj -> NS_Obj NSC_Obj_A
    NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty

    NS_Subj -> Det N_Root N_Subj_End | N_Root N_Subj_End
    NS_Obj -> Det N_Root N_Obj_End | N_Root N_Obj_End

    Det -> 'la'
    N_Root -> 'kat' | 'procion' | 'plant' | 'flor' | 'arb'
    N_Subj_End -> 'o' | 'oj'
    N_Obj_End -> 'on' | 'ojn'

    VS -> V_Root V_End
    V_Root -> 'kresk' | 'kapt' | 'vid' | 'am'
    V_End -> 'as'

    Conj -> 'kaj' | 'au'
    Empty ->
""")

orig_parser = nltk.ChartParser(original_grammar)
clean_parser = nltk.ChartParser(cleaned_grammar)


def separate(sentence):
    sentence = sentence.lower()
    sentence = sentence.replace('a\u017e','au')
    sentence = sentence.replace('aŭ','au')
    endings = {
        'kato': 'kat o', 'katoj': 'kat oj',
        'prociono': 'procion o', 'procionoj': 'procion oj',
        'planto': 'plant o', 'plantoj': 'plant oj',
        'floro': 'flor o', 'floroj': 'flor oj',
        'arbo': 'arb o', 'arboj': 'arb oj',
        
        'katon': 'kat on', 'katojn': 'kat ojn',
        'procionon': 'procion on', 'procionojn': 'procion ojn',
        'planton': 'plant on', 'plantojn': 'plant ojn',
        'floron': 'flor on', 'florojn': 'flor ojn',
        'arbon': 'arb on', 'arbojn': 'arb ojn',
        
        'kreskas': 'kresk as',
        'kaptas': 'kapt as',
        'vidas': 'vid as',
        'amas': 'am as'
    }
    words = sentence.split()
    separated_words = [endings.get(word, word) for word in words]
    return " ".join(separated_words).split()

sentences = [
    "kato kaj prociono aŭ planto kreskas",
    "la kato vidas floron kaj procionon aŭ arbon",
    "katoj kaj plantoj kaj arboj kreskas"
]

out = []
for s in sentences:
    out.append(f"--- ORIGINAL GRAMMAR: {s}\n")
    toks = separate(s)
    count = 0
    for tree in orig_parser.parse(toks):
        out.append(tree.pformat(margin=100))
        out.append('\n')
        count += 1
    out.append(f"Total trees generated (Ambiguity count): {count}\n\n")

for s in sentences:
    out.append(f"--- CLEANED GRAMMAR: {s}\n")
    toks = separate(s)
    count = 0
    for tree in clean_parser.parse(toks):
        out.append(tree.pformat(margin=100))
        out.append('\n')
        count += 1
    out.append(f"Total trees generated (Ambiguity count): {count}\n\n")

print('\n'.join(out))
