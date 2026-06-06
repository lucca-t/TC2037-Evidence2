# Evidence 2: Implementation of Lexical Analysis

**Author:** Lucca Traslosheros Abascal (A01713944)  
**Course:** TC2037 Implementation of Computational Methods  

---
## Description
Esperanto is the most widely spoken constructed language in the world. It was initially proposed in 1887 with the hopes of becoming the world's international auxiliary language to be able to unite the world with a common tongue (Manero, 2022). It was designed to be simple and easy to learn from the start which is partly why I chose it. The grammar is simple, no verbs are irregular and all spelling is phonetic. Its popularity declined as English grew to become the defacto second language accross the world.

I use a small subset of Esperanto.

### Language Structure

Its regular morphology suits context-free grammar modeling. Esperanto has a highly regular, agglutinative morphology. This means that words are made up of combining roots with specific suffixes to indicate certain meaning. This affects the part of speech, number, and case. To keep the Context-Free grammar manageable for this project, the scope is narrowed to analyze basic present-tense verbs, and the noun case system. 

#### Noun Rules:
All nounds end with `-o`. To form different meaning, suffixes are then glued to the end of the word with strict rules.

1. **Base:** The root plus `-o` forms a singular subject. `kat` + `o` = `kato` (cat).
2. **Plurality:** Adding `-j` makes the noun plural. `kato` + `j` = `katoj` (cats).
2. **Accusative Case:** Adding `-n` makes the noun the subject for both singular and plural without having to debend on word order like in English. 
   - Singular Object `kato` + `n` = `katon`
   - Plural Object `katoj` + `n` = `katojn`

Because of this `-n` ending, a sentence like `la kato vidas floron` (the cat sees the flower) is mathematically distinct from `la katon vidas floro` (the flower sees the cat). My grammar model explicitly separates these nominative (o, oj) and accusative (on, ojn) endings to ensure the parser correctly identifies the subject and object of transitive verbs.

#### Verb Rules:
Unlike English or Spanish, Esperanto verbs are completely regular and do not changes based on the subject. The verb ending strictly dictates the tense of the action. To maintain the project's scope, only verbs with present tense are modeled. 
   - **Present Tense:** All present-tense verbs are formed by attaching the suffix `-as` to the verb root.
   - **Example:** The root `kresk` (grow) combined with `-as` becomes `krekas` (grows/ is growing). Regardless of the subject's tense, singular (`la kato kreskas`) or plural (`katoj kreskas`), the verb form stays the same and simplifies the rules for verb sequences.

### Conjunctions: 
Conjunctions in Esperante are the same as English for linking words or phrases together. In this project two are used:
- `kaj` = and
- `aŭ` = or

While on paper these are the simplest to add, the complexity they add with its possibility for adding ambiguity and recursive chaining is the most computationally complex. 


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

- `S` A complete sentences must contain a complex subject phrase and a verb sequence, and it can ooptionally take a complex object phrase. 
- `NSC_Subj` and `NSC_Obj` let me chain conjunctions in subject or object position.
- `NS_Subj` and `NS_Obj` generate noun phrases with or without a determiner.
- `N_Subj_End` encodes nominative number (`o`, `oj`).
- `N_Obj_End` encodes accusative number (`on`, `ojn`).
- `VS` generates present-tense verbs from a root plus `as`.
- `Conj` provides coordination with `kaj` or `aŭ`.

## Eliminating Ambiguity

My original coordination rules were ambiguous because the same sequence of conjunctions could be grouped in more than one way. For example, a phrase like `kato kaj prociono aŭ planto kreskas` (cat and raccoon or plant grow) could produce different trees depending on whether I grouped the first conjunction or the second one first.

```
--- ORIGINAL GRAMMAR: kato kaj prociono aŭ planto kreskas (cat and procion or plant grow )


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
 kat                o        kaj    procion               o       au  plant               o      kresk        as 


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
 kat                o      kaj  procion               o         au    plant               o      kresk        as 

```

Step-by-step ambiguity removal:

1. **Start with the ambiguous rules** that allow coordination to recurse on both sides:
   - `NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj`
   - `NSC_Obj -> NSC_Obj Conj NSC_Obj | NS_Obj`
2. **Pick a sentence with two conjunctions** so grouping choices are visible:
   - `kato kaj prociono aŭ planto kreskas`
3. **Show the two possible groupings** that both satisfy the original rules:
   - `(kato kaj prociono) au planto kreskas`
   - `kato kaj (prociono au planto kreskas)`
4. **Observe that both groupings parse**, which yields two distinct trees (shown below in the original grammar output).
5. **Introduce a right-recursive list** with a tail symbol so the parser always expands in one direction:
   - `NSC_Subj -> NS_Subj NSC_Subj_A`
   - `NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty`
6. **Verify the single derivation path** with the new rules (one canonical grouping):
   - `NSC_Subj => NS_Subj NSC_Subj_A`
   - `=> kat o (Conj NS_Subj NSC_Subj_A)`
   - `=> kat o kaj procion o (Conj NS_Subj NSC_Subj_A)`
   - `=> kat o kaj procion o au plant o (Empty)`

To remove that ambiguity, I changed the coordination part into a single list structure with an auxiliary tail symbol. That way, I only allow one right-branching tree for each coordinated sequence:

```text
NSC_Subj -> NS_Subj NSC_Subj_A
NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty

NSC_Obj -> NS_Obj NSC_Obj_A
NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty
```

This yields a single canonical structure for coordination and removes multiple parse trees.

## Cleaning the Grammar

After removing the ambiguity, I also needed to make sure the grammar no longer used direct left recursion in the coordination rules:

```text
NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj
NSC_Obj -> NSC_Obj Conj NSC_Obj | NS_Obj
```

This is a problem for top-down parsing because the parser can keep expanding the same nonterminal on the left and never reach a terminal string.

To clean the grammar, I rewrote the recursive structure into a right-recursive list form using the standard left-recursion removal pattern (Moreno Maza, 2004).

Step-by-step left recursion removal (subject case shown; object case is identical):

1. Start with the left-recursive rule:
   - `NSC_Subj -> NSC_Subj Conj NSC_Subj | NS_Subj`
2. Match it to the generic pattern $A -> A\alpha | \beta$:
   - $A = NSC_Subj$
   - $\alpha = Conj\ NSC_Subj$
   - $\beta = NS_Subj$
3. Introduce a new tail nonterminal $A'$ to hold repetitions:
   - `NSC_Subj_A`
4. Rewrite using the standard transformation:
   - `NSC_Subj -> NS_Subj NSC_Subj_A`
   - `NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty`
5. Apply the same transformation to the object rule:
   - `NSC_Obj -> NS_Obj NSC_Obj_A`
   - `NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty`

The cleaned rules become:

```text
NSC_Subj -> NS_Subj NSC_Subj_A
NSC_Subj_A -> Conj NS_Subj NSC_Subj_A | Empty

NSC_Obj -> NS_Obj NSC_Obj_A
NSC_Obj_A -> Conj NS_Obj NSC_Obj_A | Empty
```

This removes direct left recursion and keeps the same one-tree structure for coordination. For example, `kato kaj prociono au planto` is now parsed as `kato kaj (prociono au planto)`.

My cleaned implementation keeps the same lexical vocabulary and verb structure, but it no longer loops on the left when parsing conjunction chains.

## Analysis

### Asymptotic Analysis
To analyze a sentence, the input must first pass through a lexical separation phase. In my implementation, the `separate(sentence)` function iterates over each word in the user's string, converts it to lowercase, and matches it against the `_ENDINGS` dictionary to split words into roots and suffixes (e.g., `katojn` becomes `kat` and `ojn`). Because this process requires a single pass over the words in the sentence, the time complexity for tokenization is $O(n)$, where $n$ is the number of words.

Regarding the syntax analysis (parsing), general Context-Free Grammar (CFG) parsers—like the CYK algorithm (GeeksforGeeks 2020) or general chart parsers—run in polynomial time, with a worst-case complexity of $O(n^3)$. However, the steps taken previously to clean the grammar (eliminating ambiguity and removing direct left recursion) ensure that the grammar is deterministic. Because of this cleaning, the grammar qualifies for top-down LL(1) parsing without backtracking. An LL(1) parser can process an input string in linear time, meaning the parsing complexity drops to $O(n)$. Therefore, the combined time complexity for tokenizing and parsing an unambiguous sentence with this grammar is optimal at $O(n)$.

### Chomsky hierarchy (before / after)
- Before cleaning: the grammar is Context-Free (Type-2). Ambiguity and left recursion do not change its Chomsky level (Devopedia 2022).
- After cleaning: it remains Context-Free (Type-2) but is suitable for top-down parsing.

### Why it is Type-2 (Context-Free): 
A grammar is context-free if every production rule has exactly one non-terminal on its left-hand side. As seen in the cleaned grammar, all rules (e.g., `NSC_Subj -> NS_Subj NSC_Subj_A` or `Det -> 'la'`) follow this strict requirement. The right-hand side can be any combination of terminals and non-terminals. It is not a Type-3 (Regular) grammar because it contains multipe non-terminals on the right side. And it's not a Type-1 (Context-Sensitive) grammar because it only has variables on the left side and not terminals. This also excludes it from being any level higher than a Context-Sensitive grammar. For these reasons it is a Type-2 (Context-Free) grammar.

### Empirical verification (from this repo)
- I automated tests in `grammar_test.py` that run accepted and rejected sentence lists. The automated suite reports all accepted tests passed and all rejected tests passed on my environment. It includes three suites: ACCEPTED, REJECTED, and UNAMBIGUOUS. Which all test seperate aspects of the grammar. Accepted all are supposed to pass and are correctly written. Rejected have different spelling mistakes or incorrect suffixes that should trigger a token error. And the unambiguous tests need to be able to run without generating multiple trees (ambiguity). 

Here is an example from the tests ran in `grammar_test.py`


```
Running grammar automated suite

=== Acceptance tests (grammar must accept) ===
  [PASS] 'la kato vidas floron'  (parses=1)
  [PASS] 'kato kaj prociono aŭ planto kreskas'  (parses=1)
  [PASS] 'katoj kaj plantoj kaj arboj kreskas'  (parses=1)
  [PASS] 'la kato kaptas katon'  (parses=1)
  4/4 passed

=== Rejection tests (grammar must reject) ===
  [PASS] 'la katoo vidas floron'  (token error)
  [PASS] 'katoj kaj'  (parses=0)
  [PASS] 'kato ar arbo ar'  (token error)
  [PASS] 'la vidas kato'  (parses=0)
  [PASS] 'kato vidas kato'  (parses=0)
  5/5 passed

=== Unambiguity tests (must yield exactly 1 parse) ===
  [PASS] 'kato kaj prociono aŭ planto kreskas'  (parses=1)
  [PASS] 'la kato vidas floron kaj procionon aŭ arbon'  (parses=1)
  [PASS] 'katoj kaj plantoj kaj arboj kreskas'  (parses=1)
  3/3 passed

=== Summary ===
  Total: 12/12 passed
```

## Before / After: Parse Trees (implementation evidence)

Here is an example from the trees generated by `generate_trees.py`
Sample output:

```
--- ORIGINAL GRAMMAR: kato kaj prociono aŭ planto kreskas
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

--- ORIGINAL GRAMMAR: la kato vidas floron kaj procionon aŭ arbon
                                                            S                                                                    
        ____________________________________________________|________________                                                     
       |                        |                                         NSC_Obj                                                
       |                        |                                     _______|_____________________________________               
       |                        |                                 NSC_Obj                            |             |             
       |                        |                   _________________|_______________                |             |              
    NSC_Subj                    |               NSC_Obj              |            NSC_Obj            |          NSC_Obj          
       |                        |                  |                 |               |               |             |              
    NS_Subj                     VS               NS_Obj              |             NS_Obj            |           NS_Obj          
  _____|_________          _____|____       _______|________         |        _______|________       |      _______|________      
Det  N_Root  N_Subj_End V_Root     V_End N_Root         N_Obj_End   Conj   N_Root         N_Obj_End Conj N_Root         N_Obj_End
 |     |         |        |          |     |                |        |       |                |      |     |                |     
 la   kat        o       vid         as   flor              on      kaj   procion             on     aŭ   arb               on   

                                                            S                                                                    
        ____________________________________________________|_____________                                                        
       |                        |                                      NSC_Obj                                                   
       |                        |                   ______________________|_________________________                              
       |                        |                  |               |                             NSC_Obj                         
       |                        |                  |               |               _________________|______________               
    NSC_Subj                    |               NSC_Obj            |           NSC_Obj              |           NSC_Obj          
       |                        |                  |               |              |                 |              |              
    NS_Subj                     VS               NS_Obj            |            NS_Obj              |            NS_Obj          
  _____|_________          _____|____       _______|________       |       _______|________         |       _______|________      
Det  N_Root  N_Subj_End V_Root     V_End N_Root         N_Obj_End Conj  N_Root         N_Obj_End   Conj  N_Root         N_Obj_End
 |     |         |        |          |     |                |      |      |                |        |      |                |     
 la   kat        o       vid         as   flor              on    kaj  procion             on       aŭ    arb               on   

Total trees generated (Ambiguity count): 2

--- ORIGINAL GRAMMAR: katoj kaj plantoj kaj arboj kreskas
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
 kat                oj       kaj     plant                oj     kaj   arb                oj     kresk        as 

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
 kat                oj     kaj   plant                oj       kaj     arb                oj     kresk        as 

Total trees generated (Ambiguity count): 2

--- CLEANED GRAMMAR: kato kaj prociono aŭ planto kreskas
                                                              S                                                               
                                                    __________|_______________________________________________________         
                                                NSC_Subj                                                              |       
           ________________________________________|__________                                                        |        
          |                                               NSC_Subj_A                                                  |       
          |                 __________________________________|__________                                             |        
          |                |              |                          NSC_Subj_A                                       |       
          |                |              |                    __________|_____________________________               |        
       NS_Subj             |           NS_Subj                |                 NS_Subj            NSC_Subj_A         VS      
   _______|________        |       _______|________           |           _________|________           |         _____|____    
N_Root         N_Subj_End Conj  N_Root         N_Subj_End    Conj      N_Root           N_Subj_End   Empty    V_Root     V_End
  |                |       |      |                |          |          |                  |          |        |          |   
 kat               o      kaj  procion             o          aŭ       plant                o         ...     kresk        as 

Total trees generated (Ambiguity count): 1

--- CLEANED GRAMMAR: la kato vidas floron kaj procionon aŭ arbon
                                                                              S                                                                                 
                ______________________________________________________________|_____________________________                                                     
               |                                   |                                                     NSC_Obj                                                
               |                                   |                  ______________________________________|_________                                           
               |                                   |                 |                                            NSC_Obj_A                                     
               |                                   |                 |                ________________________________|_________                                 
            NSC_Subj                               |                 |               |             |                        NSC_Obj_A                           
        _______|____________________               |                 |               |             |                   _________|__________________________      
    NS_Subj                     NSC_Subj_A         VS              NS_Obj            |           NS_Obj               |               NS_Obj           NSC_Obj_A
  _____|_________________           |         _____|____       ______|________       |       ______|________          |          _______|________          |     
Det  N_Root          N_Subj_End   Empty    V_Root     V_End N_Root        N_Obj_End Conj  N_Root        N_Obj_End    Conj     N_Root         N_Obj_End   Empty  
 |     |                 |          |        |          |     |               |      |      |               |         |         |                |         |     
 la   kat                o         ...      vid         as   flor             on    kaj  procion            on        aŭ       arb               on       ...   

Total trees generated (Ambiguity count): 1

--- CLEANED GRAMMAR: katoj kaj plantoj kaj arboj kreskas
                                                             S                                                               
                                                   __________|_______________________________________________________         
                                               NSC_Subj                                                              |       
           _______________________________________|__________                                                        |        
          |                                              NSC_Subj_A                                                  |       
          |                 _________________________________|__________                                             |        
          |                |             |                          NSC_Subj_A                                       |       
          |                |             |                    __________|_____________________________               |        
       NS_Subj             |          NS_Subj                |                 NS_Subj            NSC_Subj_A         VS      
   _______|________        |      _______|________           |           _________|________           |         _____|____    
N_Root         N_Subj_End Conj N_Root         N_Subj_End    Conj      N_Root           N_Subj_End   Empty    V_Root     V_End
  |                |       |     |                |          |          |                  |          |        |          |   
 kat               oj     kaj  plant              oj        kaj        arb                 oj        ...     kresk        as 

Total trees generated (Ambiguity count): 1
```

## Run

I run the project from the local virtual environment:

```bash
source .venv/bin/activate
python grammar_test.py
```

That script prints the accepted and rejected test results.

```bash
source .venv/bin/activate
python generate_trees.py
```

That script prints the trees generated from the original and corrected grammar.


## References

Devopedia. 2021. "Chomsky Hierarchy." Version 9, June 28. Accessed 2024-06-25. https://devopedia.org/chomsky-hierarchy

GeeksforGeeks. (2020, June 19). CYK algorithm for context free grammar. GeeksforGeeks. https://www.geeksforgeeks.org/theory-of-computation/cyk-algorithm-for-context-free-grammar/

Manero, A. (2022, December 15). How Esperanto started and developed - The history of a new international language. Europeana. https://www.europeana.eu/en/stories/how-esperanto-started-and-developed

Moreno Maza , M. (2004, December 2). Elimination of left recursion. https://www.csd.uwo.ca/~mmorenom/CS447/Lectures/Syntax.html/node8.html