import nltk
from nltk import CFG

# Grammar
GRAMMAR = CFG.fromstring("""
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

parser = nltk.ChartParser(GRAMMAR)

# Tokenizer
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


def separate(sentence):
    """
    Each word that matches a known surface form is split into its root and
    inflectional ending.  Unknown words are passed through unchanged.
    """
    tokens: list[str] = []
    for word in sentence.lower().split():
        tokens.extend(_ENDINGS.get(word, [word]))
    return tokens


# The cleaned grammar must accept each of these (>= 1 parse).
ACCEPTED = [
    "la kato vidas floron",
    "kato kaj prociono aŭ planto kreskas",
    "katoj kaj plantoj kaj arboj kreskas",
    "la kato kaptas katon",
]

# The cleaned grammar must reject each of these (0 parses).
REJECTED = [
    "la katoo vidas floron",    # invalid noun ending
    "katoj kaj",                # trailing conjunction, no second conjunct
    "kato ar arbo ar",          # 'ar' is not a valid conjunction
    "la vidas kato",            # wrong word order (verb before subject)
    "kato vidas kato",          # object must take accusative -on, not -o
]

# The cleaned grammar must parse each of these in exactly one way.
# (The original ambiguous grammar produced 2 trees for all three.)
UNAMBIGUOUS = [
    "kato kaj prociono aŭ planto kreskas",
    "la kato vidas floron kaj procionon aŭ arbon",
    "katoj kaj plantoj kaj arboj kreskas",
]

# Tests
def run_tests():
    """Run all test suites and print a final summary."""
    print("Running grammar automated suite\n")
    
    # Define our test suites: (Label, Cases, Passing Condition)
    suites = [
        ("Acceptance tests (grammar must accept)", ACCEPTED, lambda n: n is not None and n > 0),
        ("Rejection tests (grammar must reject)", REJECTED, lambda n: n == 0 or n is None),
        ("Unambiguity tests (must yield exactly 1 parse)", UNAMBIGUOUS, lambda n: n == 1)
    ]

    total_passed = 0
    total_cases = 0

    for label, cases, is_passing in suites:
        # Add num of cases to total
        total_cases = total_cases + len(cases)

    for label, cases, is_passing in suites:
        print(f"=== {label} ===")
        suite_passed = 0
        
        for sentence in cases:
            # Try parsing and count the trees
            try:
                n = len(list(parser.parse(separate(sentence))))
            except ValueError:
                n = None
            
            # Check against the suite's passing condition
            ok = is_passing(n)
            status = "PASS" if ok else "FAIL"
            detail = "token error" if n is None else f"parses={n}"
            
            print(f"  [{status}] {sentence!r}  ({detail})")
            if ok:
                suite_passed += 1
                total_passed += 1
                
        print(f"  {suite_passed}/{len(cases)} passed\n")

    print("=== Summary ===")
    print(f"  Total: {total_passed}/{total_cases} passed")

if __name__ == "__main__":
    run_tests()