# Evidence 2: Implementation of Lexical Analysis

**Author:** Lucca Traslosheros Abascal (A01713944)  
**Course:** TC2037 Implementation of Computational Methods  

---
## Description
The language used in this evidence is a restricted subset of Esperanto.

Esperanto is a constructed language designed for regularity, so it is a good candidate for grammar modeling in computational methods. This project focuses on a small sentence fragment with simple noun phrases, verb phrases, and conjunctions, instead of the full language.

The grammar models the following linguistic context:

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

With this restricted vocabulary, sentences such as `la kato vidas floron` and coordinated forms such as `katoj kaj plantoj kreskas` can be analyzed. The objective is not to represent all Esperanto grammar, but to build a controlled context-free grammar that can be generated, tested, cleaned from ambiguity, and transformed to remove left recursion.

## Grammar Rules Implemented

The current implemented grammar (before cleaning) is:

```text
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

- `S` generates either subject + verb + object, or subject + verb.
- `NSC_Subj` and `NSC_Obj` allow conjunction chains in subject or object position.
- `NS_Subj` and `NS_Obj` generate noun phrases with or without determiner.
- `N_Subj_End` encodes nominative number (`o`, `oj`).
- `N_Obj_End` encodes accusative number (`on`, `ojn`).
- `VS` generates present-tense verbs from a root plus `as`.
- `Conj` provides coordination with `kaj` or `aŭ`.

This version is intentionally kept as the baseline grammar so ambiguity and left recursion can be shown and then removed in the next section.
