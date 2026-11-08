# RLL Ω · Tribo-X-ray evidence and multilingual semantic compressibility (trial V1)

State: **HOSTED_STRUCTURAL_TRIAL_ONLY**; `claim_allowed=false`; `Bayes posterior=TOKEN_VAZIO`.

## 1. Source distinctions

- **Established in non-biological tape:** Camara, Escobar, Hird & Putterman, Nature 455 (2008), DOI https://doi.org/10.1038/nature07378 : tape peeled **under moderate vacuum** was observed producing X-ray pulses along with visible/radio emissions; the study includes X-ray imaging. Mechanical work drives charge separation/discharge. Vacuum is an experimental condition, **not a free energy source**. Ionizing X-rays are a safety hazard; do not propose a home reproduction.
- **Biology:** oxygen is the terminal electron acceptor in aerobic electron transport; the proton electrochemical gradient enables ATP synthase. Reference https://www.ncbi.nlm.nih.gov/books/NBK26894/ . This established route is independent of tape emission.
- **Ethanol:** alcoholic fermentation in yeast can produce ethanol and CO2 from sugars; it is not an effect of tape triboluminescence. Reference https://www.ncbi.nlm.nih.gov/sites/books/NBK9903/ .
- **Exploratory linkage:** conversion of tape-generated X-rays into biologically useful ATP in a cell has not been established here. `TOKEN_VAZIO_PHYSICAL_MECHANISM` rather than assuming the tape result proves cell coupling.

## 2. Multilingual compression is a measurable hypothesis, not a universal law

Four aligned authored demonstrations: PT, ES, EN, FR, containing the three physical/evidential distinctions above and yeast fermentation. Each translated paragraph is linked to hand-annotated atomic facts (year, condition, polarity, experimental status, mechanism). **This is not machine translation evaluation**; no translator or automatic fact-extractor runs.

Compressed byte gain for language `l`:
`G_l=1 - size(zlib_9(utf8(text_l)))/size(utf8(text_l))`.
This is a **lossless** byte metric and may be negative on small text, because headers have overhead. It depends on language, repetition, UTF-8, compressor, length, subject, and corpus ordering.

Manually annotated semantic fidelity: per language `recall_l = |gold_atoms ∩ reviewed_atoms_l|/|gold_atoms|`.
Across languages a Jaccard overlap may be defined using sets of tagged atoms. This overlap measures **annotation agreement**, not physical truth. If the same mistaken label is applied in every language, a high agreement is misleading; an independent source-grounded auditor is necessary.

NCD (Cilibrasi/Vitányi 2005) may be useful as a secondary exploratory feature, but raw translated strings differ lexically and NCD is sensitive to the window and length of the compressor. Method paper https://www.math.ucdavis.edu/~saito/data/acha.read.w17/cilibrasi-vitanyi_clustering-by-compression.pdf ; caution: https://intlpress.com/site/pub/files/_fulltext/journals/cis/2005/0005/0004/CIS-2005-0005-0004-a001.pdf .
Recent adversarial source: ACL 2026 structured spans in translated web text https://aclanthology.org/2026.wac-1.9/ ; semantic-information-rate precedent https://pmc.ncbi.nlm.nih.gov/articles/PMC12207520/ .

## 3. The falsification protocol

1. Freeze a source paragraph + DOI/version/source hash + fact atoms (including **negation**, **numbers**, **units**, **conditions**, **causal direction**).
2. Translate independently into three or four languages; record system/version/seed and its relationship to original source. Round-trip alone does not prove fidelity.
3. Blind human/source-based validation of atomic propositions. Record false negatives and hallucinated facts.
4. Compress UTF-8 text at fixed settings; compare bits/character, raw bytes, `G_l`; stratify by length and genre. Compare with shuffled topic and repeated-boilerplate nulls.
5. Test independence: paraphrases from the same source are **correlated copies**. They must not be multiplied as Bayesian likelihood terms for the scientific proposition.
6. Reject examples where a polarity flip, year change, vacuum-condition removal, or scientific-status promotion is undetected.
7. Compute empirical uncertainty intervals over many independent primary claims, not just four authored examples; no claim until a preregistered holdout validation.

The current script does **not** parse semantics automatically: a changed translation with an unchanged human annotation may evade detection. `Fidelity=1` in the toy records means the supplied tags agree by construction. It cannot validate real-world translation quality.

## 4. Hosted reproducible scope

`python tools/ci/rll_multilingual_compression_v1.py --require-pass`

`python -m unittest discover -s tests -p test_rll_multilingual_compression_v1.py -v`

Keep this in the existing G4/G5 preflight, read-only, without secrets/network. Original data, 133 archived workflows, WS01 limits, G4/G5 code and main remain unchanged. New workflow count: zero. Status `PASS_SCOPED_MANUAL_ANNOTATIONS` does not imply biological X-ray conversion, real multilingual preservation or RLL cosmological validation.

## 5. Next real experiment

Use a licensed parallel corpus with provenance, independent translation methods, blinded annotators, and preregistered "number/negation/units" corruption probes. Preserve outcomes showing lower accuracy under higher compression. Bayesian calculation requires independently justified priors, likelihood and hierarchical treatment of dependent translations.

R3 = <source tape validated and synthetic measurement code scoped, semantic correctness of real translations NOT_RUN, next independent multilingual corpus with held-out critical facts>.
