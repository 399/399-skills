# Distillation Method

Use this reference for deep or long-form work. The method preserves the strongest parts of whole-source reading, multi-lens extraction, verification, executable interpretation, and critical analysis without producing downstream agent skills.

## Contents

1. Source acquisition and coverage
2. Global model
3. Five extraction lenses
4. Verification model
5. Construction patterns
6. Content-type adaptations
7. Long-source reconciliation
8. Quality failures

## 1. Source acquisition and coverage

Record a compact source manifest:

| Field | Record |
|---|---|
| Identity | title, creator or speaker, date, edition |
| Location | URL or file name |
| Representation | transcript, captions, OCR, document text, audio transcription |
| Coverage | complete, known interval, selected chapters, or unknown |
| Reliability | official, user-provided, machine-generated, OCR, or secondary |
| Locator | timestamp, page, chapter, heading, paragraph, or item ID |

Treat source quality as part of the conclusion. Machine captions can corrupt names, numbers, negation, and speaker attribution. Recheck high-impact passages against audio, video, page images, or redundant context when possible.

For partial sources, state exactly what was examined. Avoid phrases such as “the video argues” when only a clip or excerpt was available.

## 2. Global model

Create a source map before detailed extraction:

1. Classify the content: methodological, explanatory, investigative, narrative, instructional, argumentative, conversational, or mixed.
2. State the central problem and thesis in one sentence each.
3. Identify 3–7 major units and the relations between them: sequence, dependency, contrast, escalation, cause, rebuttal, or examples of one claim.
4. Restate 5–15 central claims in neutral language.
5. Trace the reasoning: claim → evidence → warrant → conclusion.
6. Define source-specific terms and distinguish them from ordinary meanings.
7. Build the strongest criticism: outdated premises, positional blind spots, missing evidence, alternative causes, selection effects, incentives, or unresolved contradictions.

Do not confuse chronology with argument structure. A podcast may wander chronologically while still revolving around three stable questions.

## 3. Five extraction lenses

### Frameworks

Look for named models, repeated reasoning structures, conditional paths, decision sequences, and reusable decompositions. Reject labels that merely rename a topic.

Minimum record:

- short title;
- problem addressed;
- mechanism or reasoning sequence;
- evidence locators;
- relation to adjacent concepts.

### Principles

Look for explicit should/should-not claims, thresholds, criteria, checklists, constraints, and recurring rules. Distinguish a principle from a description: “people are cautious” describes; “do not proceed until X is known” guides action.

### Cases

Extract cases only when they support, challenge, or clarify a claim. Capture:

- initial situation;
- action or reasoning used;
- conclusion;
- observed outcome;
- the claim the case is supposed to support;
- plausible alternative interpretation.

An anecdote demonstrates possibility, not frequency or causation.

### Failures and counterexamples

Capture the failure mode, causal mechanism, observable warning signs, consequences, and the positive claim it limits. Separate a demonstrated failure from a rhetorical warning.

### Terms

Keep terms that are repeatedly used, explicitly defined, central to the argument, or misleading under their ordinary meaning. Record the source-specific definition, distinctions, and why the distinction matters.

## 4. Verification model

Score nothing merely for administrative neatness. Use reasoned classification.

### Evidence stability

Ask:

- Is there an explicit passage?
- Is the interpretation consistent with its surrounding context?
- Does the source repeat or apply it independently?
- Is it the author's claim, another speaker's claim, or a quoted opponent's claim?
- Does contrary evidence appear elsewhere in the same source?

Multiple repetitions are not independent evidence when they repeat the same anecdote or citation.

### Transferability

For methods and explanatory models, pose a novel but relevant situation and derive a conclusion. A useful model should change what one notices, predicts, decides, or does. Reject outputs that reduce to “work hard,” “think carefully,” or another generic maxim.

Do not require transferability from a fact report, literary theme, eyewitness account, or historical chronology unless the user explicitly wants lessons or applications.

### Information value

An item deserves prominence when it is at least one of:

- source-defining;
- consequential to the overall conclusion;
- counterintuitive or discriminating;
- unusually actionable;
- strongly evidenced;
- essential to understanding disagreement or uncertainty.

Common knowledge may still be necessary context, but label it as context rather than a novel insight.

### Confidence language

Use calibrated labels where helpful:

- **Direct:** explicitly stated or shown in the source.
- **Strong inference:** not stated verbatim but follows from multiple source elements.
- **Tentative:** plausible interpretation with meaningful alternatives.
- **Unverified:** factual claim made by the source but not externally checked.

## 5. Construction patterns

Choose the pattern that fits each unit:

### Method or framework

Problem → interpretation → evidence → representative application → executable steps → stop condition → failure modes → limits.

Only derive steps that the source supports. Mark any practical adaptation as your synthesis.

### Explanatory claim

Question → claim → mechanism → evidence → alternative explanations → confidence.

### Event or investigation

Verified timeline → actors → claims by actor → evidence → disputed points → unresolved questions.

### Tutorial

Goal → prerequisites → ordered procedure → expected result → verification → common failures → recovery.

### Narrative or literary work

Central themes → narrative movement → representative passages or scenes → interpretive alternatives → historical or authorial context. Do not force advice or productivity lessons.

## 6. Content-type adaptations

| Source | Emphasize | Avoid |
|---|---|---|
| Method book/course | frameworks, rules, cases, boundaries | chapter-by-chapter paraphrase |
| Interview/podcast | speaker attribution, claims, experience, disagreement | treating every anecdote as evidence |
| News/investigation | chronology, sourcing, disputed facts, uncertainty | extracting timeless “methods” |
| Tutorial/demo | prerequisites, exact steps, checks, failure recovery | abstract thematic summary |
| Lecture/explainer | concept hierarchy, causal chain, examples | isolated definitions without relations |
| Meeting | decisions, rationale, owners, unresolved issues | polishing ambiguity into false agreement |
| Literary/narrative | themes, structure, voice, interpretation | manufactured action items |
| Low-signal marketing | verifiable claims, assumptions, omissions | preserving hype or inventing depth |

## 7. Long-source reconciliation

Split on natural boundaries rather than arbitrary token counts when possible. For every chunk:

1. carry the current global map;
2. record local claims and locators;
3. note additions, contradictions, and revisions to the map;
4. merge duplicate candidates while preserving all independent evidence;
5. run a final whole-source pass for conclusions that depend on distant sections.

Do not let early chunks permanently anchor the interpretation. Later evidence may revise the thesis or reveal that an earlier statement was hypothetical, quoted, or rebutted.

## 8. Quality failures

- **Transcript summary:** follows source order but never reconstructs the argument. Fix the global model.
- **Quote collection:** selects memorable lines without claims or context. Bind each quote to a role.
- **Insight inflation:** presents generic advice as original. Apply information-value and transfer tests.
- **Method coercion:** invents frameworks from narrative material. Switch construction pattern.
- **Author worship:** omits contrary evidence and limitations. Build the strongest criticism.
- **False precision:** supplies timestamps, numbers, or wording not verified in the source. Mark unknowns.
- **Voice collapse:** merges interviewer, guest, narrator, cited source, and analyst. Preserve attribution.
- **Coverage bluff:** implies full review of partial material. Add a coverage statement.
- **Template obedience:** fills every heading despite no supporting content. Remove empty sections.
- **Retrieval drift:** searches an entire knowledge base when the request is bounded-source synthesis. Keep the boundary or switch workflows explicitly.
