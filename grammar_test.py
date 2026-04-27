import nltk
from nltk import CFG

grammar = CFG.fromstring("""
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
    
    Conj -> 'kaj' | 'aŭ'
""")

parser = nltk.ChartParser(grammar)

def separate(sentence):
    sentence = sentence.lower()
    
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
    # Generates 2 trees: ((cat and raccoon) or plant) vs (cat and (raccoon or plant))
    "kato kaj prociono aŭ planto kreskas",
    
    # Generates 2 trees for the object phrase.
    "la kato vidas floron kaj procionon aŭ arbon",
    
    # Generates 2 trees depending on which 'kaj' is grouped first.
    "katoj kaj plantoj kaj arboj kreskas"
]

for sentence in sentences:
    print(f"\nParsing: '{sentence}'")
    print("-" * 40)
    tokens = separate(sentence) 
    
    try:
        trees_found = 0
        for tree in parser.parse(tokens):
            tree.pretty_print()
            trees_found += 1
        
        print(f"Total trees generated (Ambiguity count): {trees_found}\n")
            
    except ValueError as e:
        print(f"Error parsing sentence: {e}")