import nltk
from nltk import CFG

# Grammars
ORIGINAL_GRAMMAR = CFG.fromstring("""
    S -> NSC_Subj VS NSC_Obj | NSC_Subj VS
    NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj
    NSC_Obj  -> NSC_Obj  Conj NSC_Obj  | NS_Obj
    NS_Subj  -> Det N_Root N_Subj_End | N_Root N_Subj_End
    NS_Obj   -> Det N_Root N_Obj_End  | N_Root N_Obj_End
    Det        -> 'la'
    N_Root     -> 'kat' | 'procion' | 'plant' | 'flor' | 'arb'
    N_Subj_End -> 'o' | 'oj'
    N_Obj_End  -> 'on' | 'ojn'
    VS     -> V_Root V_End
    V_Root -> 'kresk' | 'kapt' | 'vid' | 'am'
    V_End  -> 'as'
    Conj   -> 'kaj' | 'aŭ'
""")

CLEANED_GRAMMAR = CFG.fromstring("""
    S -> NSC_Subj VS NSC_Obj | NSC_Subj VS
    NSC_Subj   -> NS_Subj NSC_Subj_A
    NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty
    NSC_Obj    -> NS_Obj NSC_Obj_A
    NSC_Obj_A  -> Conj NS_Obj NSC_Obj_A | Empty
    NS_Subj  -> Det N_Root N_Subj_End | N_Root N_Subj_End
    NS_Obj   -> Det N_Root N_Obj_End  | N_Root N_Obj_End
    Det        -> 'la'
    N_Root     -> 'kat' | 'procion' | 'plant' | 'flor' | 'arb'
    N_Subj_End -> 'o' | 'oj'
    N_Obj_End  -> 'on' | 'ojn'
    VS     -> V_Root V_End
    V_Root -> 'kresk' | 'kapt' | 'vid' | 'am'
    V_End  -> 'as'
    Conj   -> 'kaj' | 'aŭ'
    Empty  ->
""")

orig_parser  = nltk.ChartParser(ORIGINAL_GRAMMAR)
clean_parser = nltk.ChartParser(CLEANED_GRAMMAR)

# Tokeniser

# Map whole Esperanto surface forms to their root + ending tokens.
_ENDINGS: dict[str, list[str]] = {
    "kato":        ["kat", "o"],   "katoj":       ["kat", "oj"],
    "katon":       ["kat", "on"],  "katojn":      ["kat", "ojn"],
    "prociono":    ["procion", "o"],  "procionoj":   ["procion", "oj"],
    "procionon":   ["procion", "on"], "procionojn":  ["procion", "ojn"],
    "planto":      ["plant", "o"], "plantoj":     ["plant", "oj"],
    "planton":     ["plant", "on"],"plantojn":    ["plant", "ojn"],
    "floro":       ["flor", "o"],  "floroj":      ["flor", "oj"],
    "floron":      ["flor", "on"], "florojn":     ["flor", "ojn"],
    "arbo":        ["arb", "o"],   "arboj":       ["arb", "oj"],
    "arbon":       ["arb", "on"],  "arbojn":      ["arb", "ojn"],
    "kreskas":     ["kresk", "as"],
    "kaptas":      ["kapt", "as"],
    "vidas":       ["vid", "as"],
    "amas":        ["am", "as"],
}


# Tokenizer for the language
def separate(sentence):
    """Separate the endings from the words to generate the tree correctly.
    Ignore unknown words. """
    tokens: list[str] = []
    for word in sentence.lower().split():
        tokens.extend(_ENDINGS.get(word, [word]))
    return tokens


def print_trees(sentences, parser, label):
    """Parse each sentence and print all resulting 
    parse trees directly to the console.
    """
    for sentence in sentences:
        print(f"--- {label}: {sentence}")
        tokens = separate(sentence)
        count = 0
        for tree in parser.parse(tokens):
            # Print the tree directly to the console
            tree.pretty_print()
            count += 1
        print(f"Total trees generated (Ambiguity count): {count}\n")



SENTENCES = [
    # Ambiguous: ((kato kaj prociono) aŭ planto) vs (kato kaj (prociono aŭ planto))
    "kato kaj prociono aŭ planto kreskas",
    # Ambiguous in object phrase: (floron kaj procionon) aŭ arbon  vs  floron kaj (procionon aŭ arbon)
    "la kato vidas floron kaj procionon aŭ arbon",
    # Ambiguous: which 'kaj' is grouped first
    "katoj kaj plantoj kaj arboj kreskas",
]

if __name__ == "__main__":
    print_trees(SENTENCES, orig_parser,  "ORIGINAL GRAMMAR")
    print_trees(SENTENCES, clean_parser, "CLEANED GRAMMAR")