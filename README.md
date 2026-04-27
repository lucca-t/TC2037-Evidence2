# Evidence 2: Implementation of Lexical Analysis

**Author:** Lucca Traslosheros Abascal (A01713944)  
**Course:** TC2037 Implementation of Computational Methods  

---
## Description
I use a small subset of Esperanto.

Its regular morphology suits context-free grammar modeling. The project models simple noun phrases, verbs, and conjunctions.

I modeled the following linguistic context:

- Determiner: `la`
- Noun roots: `kat`, `procion`, `plant`, `flor`, `arb`
- Subject endings: `o`, `oj`
- Object endings (accusative): `on`, `ojn`
- Verb structure: verb root + `as` (present tense)
- Conjunctions: `kaj` (and), `aŭ` (or)

### Vocabulary and Translations

#### Determiner
- `la` = the

#### Noun roots
- `kat` = cat
- `procion` = raccoon
- `plant` = plant
- `flor` = flower
- `arb` = tree

#### Noun endings
- `o` = singular noun (subject form)
- `oj` = plural noun (subject form)
- `on` = singular noun (direct object / accusative)
- `ojn` = plural noun (direct object / accusative)

#### Verb ending
- `as` = present tense

#### Verb roots
- `kresk` = grow
- `kapt` = catch
- `vid` = see
- `am` = love

#### Conjunctions
- `kaj` = and
- `aŭ` = or

#### Example sentence translations
- `la kato vidas floron` = the cat sees a flower
- `katoj kaj plantoj kreskas` = cats and plants grow

With this vocabulary I analyze sentences like `la kato vidas floron` and `katoj kaj plantoj kreskas`. The goal is a controlled CFG I can generate, test, and clean.

## Models

I started with the following grammar before cleaning:

```
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
```

Rule summary:

- `S` generates either a subject + verb + object sentence or a subject + verb sentence.
- `NSC_Subj` and `NSC_Obj` let me chain conjunctions in subject or object position.
- `NS_Subj` and `NS_Obj` generate noun phrases with or without a determiner.
- `N_Subj_End` encodes nominative number (`o`, `oj`).
- `N_Obj_End` encodes accusative number (`on`, `ojn`).
- `VS` generates present-tense verbs from a root plus `as`.
- `Conj` provides coordination with `kaj` or `aŭ`.

## Eliminating Ambiguity

My original coordination rules were ambiguous because the same sequence of conjunctions could be grouped in more than one way. For example, a phrase like `kato kaj prociono aŭ planto` could produce different trees depending on whether I grouped the first conjunction or the second one first.

To remove that ambiguity, I changed the coordination part into a single list structure with an auxiliary tail symbol. That way, I only allow one right-branching tree for each coordinated sequence:

```text
NSC_Subj -> NS_Subj NSC_Subj_A
NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty

NSC_Obj -> NS_Obj NSC_Obj_A
NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty
```

This yields a single canonical structure for coordination and removes multiple parse trees.

```
Parsing: 'kato kaj prociono aŭ planto kreskas'
----------------------------------------
                                                          S                                                      
                                        __________________|______________________________________________         
                                    NSC_Subj                                                             |       
                               ________|________________________________________                         |        
                           NSC_Subj                               |             |                        |       
           ___________________|_________________                  |             |                        |        
       NSC_Subj               |              NSC_Subj             |          NSC_Subj                    |       
          |                   |                 |                 |             |                        |        
       NS_Subj                |              NS_Subj              |          NS_Subj                     VS      
   _______|_________          |         ________|_________        |      _______|_________          _____|____    
N_Root          N_Subj_End   Conj    N_Root           N_Subj_End Conj N_Root          N_Subj_End V_Root     V_End
  |                 |         |        |                  |       |     |                 |        |          |   
 kat                o        kaj    procion               o       aŭ  plant               o      kresk        as 
```
```
                                                      S                                                          
                                    __________________|__________________________________________________         
                                NSC_Subj                                                                 |       
           ________________________|____________________________                                         |        
          |                 |                                NSC_Subj                                    |       
          |                 |                ___________________|_______________                         |        
       NSC_Subj             |            NSC_Subj               |            NSC_Subj                    |       
          |                 |               |                   |               |                        |        
       NS_Subj              |            NS_Subj                |            NS_Subj                     VS      
   _______|_________        |       ________|_________          |        _______|_________          _____|____    
N_Root          N_Subj_End Conj  N_Root           N_Subj_End   Conj   N_Root          N_Subj_End V_Root     V_End
  |                 |       |      |                  |         |       |                 |        |          |   
 kat                o      kaj  procion               o         aŭ    plant               o      kresk        as 

Total trees generated (Ambiguity count): 2
```

## Cleaning the Grammar

After removing the ambiguity, I also needed to make sure the grammar no longer used direct left recursion in the coordination rules:

```text
NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj
NSC_Obj -> NSC_Obj Conj NSC_Obj | NS_Obj
```

This is a problem for top-down parsing because the parser can keep expanding the same nonterminal on the left and never reach a terminal string.

To clean the grammar, I rewrote the recursive structure into a right-recursive list form. I used the same idea as standard left-recursion removal:

1. Keep the base phrase without recursion.
2. Add a new auxiliary nonterminal for the repeated part.
3. Let the auxiliary symbol repeat the conjunction pattern or end with an empty production.

The cleaned rules become:

```text
NSC_Subj -> NS_Subj NSC_Subj_A
NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty

NSC_Obj -> NS_Obj NSC_Obj_A
NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty
```

This removes direct left recursion and keeps the same one-tree structure for coordination. For example, `kato kaj prociono aŭ planto` is now parsed as `kato kaj (prociono aŭ planto)`.

My cleaned implementation keeps the same lexical vocabulary and verb structure, but it no longer loops on the left when parsing conjunction chains.

## Analysis

### Chomsky hierarchy (before / after)
- Before cleaning: the grammar is Context-Free (Type-2). Ambiguity and left recursion do not change its Chomsky level.
- After cleaning: it remains Context-Free (Type-2) but is suitable for top-down parsing.

### Parsing complexity and time implications
- General CFG parsing runs in polynomial time (worst-case O(n^3) for CYK).
- After cleaning, the grammar is easier to handle with top-down parsing.
- I use NLTK's ChartParser to show trees.

### Examples by language class (short)
- Regular (Type-3) example: language {a^* b^*}. Strings like `aaabbb` can be recognized by a finite automaton in O(n).
- Context-Free (Type-2) example: language {a^n b^n | n>=0}. Strings like `aaabbb` require a pushdown automaton; deterministic CFGs can parse in O(n), general CFGs can cost O(n^3).
- Context-Sensitive (Type-1) example: language {a^n b^n c^n | n>=0}. These need a linear-bounded automaton and are more expensive to parse.

### Empirical verification (from this repo)
- I automated tests in `grammar_test.py` that run accepted and rejected sentence lists. The automated suite reports all accepted tests passed and all rejected tests passed on my environment.

## Before / After: Parse Trees (implementation evidence)

I generated parse trees for three representative sentences using both the original (ambiguous) grammar and the cleaned grammar. The output below is taken directly from the parser runs I executed in the project virtual environment.

--- ORIGINAL GRAMMAR: `kato kaj prociono aŭ planto kreskas`

```text
(S
   (NSC_Subj
      (NSC_Subj
         (NSC_Subj (NS_Subj (N_Root kat) (N_Subj_End o)))
         (Conj kaj)
         (NSC_Subj (NS_Subj (N_Root procion) (N_Subj_End o))))
      (Conj au)
      (NSC_Subj (NS_Subj (N_Root plant) (N_Subj_End o))))
   (VS (V_Root kresk) (V_End as)))


(S
   (NSC_Subj
      (NSC_Subj (NS_Subj (N_Root kat) (N_Subj_End o)))
      (Conj kaj)
      (NSC_Subj
         (NSC_Subj (NS_Subj (N_Root procion) (N_Subj_End o)))
         (Conj au)
         (NSC_Subj (NS_Subj (N_Root plant) (N_Subj_End o)))))
   (VS (V_Root kresk) (V_End as)))


Total trees generated (Ambiguity count): 2
```

--- CLEANED GRAMMAR: `kato kaj prociono aŭ planto kreskas`

```text
(S
   (NSC_Subj
      (NS_Subj (N_Root kat) (N_Subj_End o))
      (NSC_Subj_A
         (Conj kaj)
         (NS_Subj (N_Root procion) (N_Subj_End o))
         (NSC_Subj_A (Conj au) (NS_Subj (N_Root plant) (N_Subj_End o)) (NSC_Subj_A (Empty )))))
   (VS (V_Root kresk) (V_End as)))


Total trees generated (Ambiguity count): 1
```

--- ORIGINAL GRAMMAR: `la kato vidas floron kaj procionon aŭ arbon`

```text
(S
   (NSC_Subj (NS_Subj (Det la) (N_Root kat) (N_Subj_End o)))
   (VS (V_Root vid) (V_End as))
   (NSC_Obj
      (NSC_Obj
         (NSC_Obj (NS_Obj (N_Root flor) (N_Obj_End on)))
         (Conj kaj)
         (NSC_Obj (NS_Obj (N_Root procion) (N_Obj_End on))))
      (Conj au)
      (NSC_Obj (NS_Obj (N_Root arb) (N_Obj_End on)))))


(S
   (NSC_Subj (NS_Subj (Det la) (N_Root kat) (N_Subj_End o)))
   (VS (V_Root vid) (V_End as))
   (NSC_Obj
      (NSC_Obj (NS_Obj (N_Root flor) (N_Obj_End on)))
      (Conj kaj)
      (NSC_Obj
         (NSC_Obj (NS_Obj (N_Root procion) (N_Obj_End on)))
         (Conj au)
         (NSC_Obj (NS_Obj (N_Root arb) (N_Obj_End on))))))


Total trees generated (Ambiguity count): 2
```

--- CLEANED GRAMMAR: `la kato vidas floron kaj procionon aŭ arbon`

```text
(S
   (NSC_Subj (NS_Subj (Det la) (N_Root kat) (N_Subj_End o)) (NSC_Subj_A (Empty )))
   (VS (V_Root vid) (V_End as))
   (NSC_Obj
      (NS_Obj (N_Root flor) (N_Obj_End on))
      (NSC_Obj_A
         (Conj kaj)
         (NS_Obj (N_Root procion) (N_Obj_End on))
         (NSC_Obj_A (Conj au) (NS_Obj (N_Root arb) (N_Obj_End on)) (NSC_Obj_A (Empty ))))))


Total trees generated (Ambiguity count): 1
```

--- ORIGINAL GRAMMAR: `katoj kaj plantoj kaj arboj kreskas`

```text
(S
   (NSC_Subj
      (NSC_Subj
         (NSC_Subj (NS_Subj (N_Root kat) (N_Subj_End oj)))
         (Conj kaj)
         (NSC_Subj (NS_Subj (N_Root plant) (N_Subj_End oj))))
      (Conj kaj)
      (NSC_Subj (NS_Subj (N_Root arb) (N_Subj_End oj))))
   (VS (V_Root kresk) (V_End as)))


(S
   (NSC_Subj
      (NSC_Subj (NS_Subj (N_Root kat) (N_Subj_End oj)))
      (Conj kaj)
      (NSC_Subj
         (NSC_Subj (NS_Subj (N_Root plant) (N_Subj_End oj)))
         (Conj kaj)
         (NSC_Subj (NS_Subj (N_Root arb) (N_Subj_End oj)))))
   (VS (V_Root kresk) (V_End as)))


Total trees generated (Ambiguity count): 2
```

--- CLEANED GRAMMAR: `katoj kaj plantoj kaj arboj kreskas`

```text
(S
   (NSC_Subj
      (NS_Subj (N_Root kat) (N_Subj_End oj))
      (NSC_Subj_A
         (Conj kaj)
         (NS_Subj (N_Root plant) (N_Subj_End oj))
         (NSC_Subj_A (Conj kaj) (NS_Subj (N_Root arb) (N_Subj_End oj)) (NSC_Subj_A (Empty )))))
   (VS (V_Root kresk) (V_End as)))


Total trees generated (Ambiguity count): 1
```

I include raw parser trees and ambiguity counts for verification.

## Run

I run the project from the local virtual environment:

```bash
source .venv/bin/activate
python grammar_test.py
```

That script prints the accepted and rejected test results.

To regenerate the tree evidence, I run:

```bash
python generate_trees.py > trees_output.txt
```

## References

- Main grammar and tests: [grammar_test.py](grammar_test.py)
- Tree generator: [generate_trees.py](generate_trees.py)
- Saved parser output: [trees_output.txt](trees_output.txt)