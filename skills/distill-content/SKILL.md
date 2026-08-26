---
name: distill-content
description: >-
  Deeply acquire, understand, verify, and synthesize long-form source content
  into a traceable, critical, high-signal result. Use for videos, podcasts,
  interviews, courses, books, articles, transcripts, meeting records, or
  multi-source packets when the user wants more than a surface summary:
  content extraction, structured notes, frameworks, principles, evidence,
  cases, procedures, limitations, or actionable insights. Also use when asked
  to summarize a source faithfully while preserving timestamps, chapters,
  uncertainty, and the author's reasoning. Do not use as a general
  knowledge-base retrieval or question-answering system when no bounded source
  set is being analyzed.
---

# Distill Content

Turn bounded source material into a faithful, useful synthesis. Do not force every source into methods or advice; let the source type determine the result.

## Non-negotiable rules

1. Acquire the source before analyzing it. Never reconstruct unseen content from memory, titles, thumbnails, or search snippets.
2. Preserve provenance. Attach timestamps, page or section markers, speaker names, URLs, or file names to important claims whenever the source permits.
3. Separate source claims, external facts, and your inference. Label uncertainty instead of filling gaps.
4. Recover the whole argument before extracting fragments. Do not turn memorable lines into conclusions without their context.
5. Test important insights against evidence, transferability, and information value. Do not promote repetition, slogans, or common sense as deep insight.
6. Include counterexamples, failure modes, assumptions, and limitations. A uniformly admiring result is incomplete.
7. Match depth to signal. If the source is thin, repetitive, inaccessible, or unsuitable for methodological extraction, say so and produce a smaller faithful result.
8. Do not create or save files unless the user requests it or the active workspace rules authorize it. This skill does not prescribe an application or storage system.

Read [references/distillation-method.md](references/distillation-method.md) before performing a deep or long-form distillation. Use [assets/synthesis-template.md](assets/synthesis-template.md) only when a reusable Markdown structure helps; omit irrelevant sections rather than filling them mechanically.

## Workflow

### 1. Define the source boundary

Identify:

- the exact source or source set;
- the user's desired depth, focus, language, and output form when stated;
- available metadata: title, creator or speakers, date, edition, URL, and file path;
- whether the task is full-source synthesis, focused extraction, comparison, or question-led reading.

For an unspecified but bounded source, default to a full-source critical synthesis. Do not silently expand into the user's wider knowledge base.

### 2. Acquire the best available representation

Prefer, in order:

1. creator- or platform-provided transcript, captions, article text, ebook text, or document text;
2. accessible page text and metadata;
3. user-provided transcript or export;
4. lawful audio transcription when tools and authorization permit it.

For video or audio, retain timestamps during extraction. For documents, retain pages, chapters, headings, or stable section identifiers. If only partial content is available, report the coverage before drawing conclusions.

Do not bypass access controls, DRM, paywalls, or platform restrictions. Do not pretend a description or comments represent the source.

### 3. Normalize without erasing meaning

Remove navigation, ads, repeated intros, sponsor copy, transcription artifacts, and obvious verbal filler. Preserve:

- speaker changes;
- meaningful repetition and emphasis;
- qualifications, negation, and modality;
- examples, objections, and transitions;
- timestamps or structural markers.

Mark uncertain words or missing spans. Do not silently “correct” a claim into something the speaker did not say.

### 4. Build the global model

Before extracting insights, determine:

- content type and intended audience;
- the central problem and one-sentence thesis;
- 3–7 major sections and their relationship;
- key terms in the author's specific usage;
- the main claims and supporting reasoning;
- the strongest internal tensions, assumptions, and opposing view.

For very long sources, split at natural boundaries. Give every chunk the global model as an anchor, then reconcile the chunks into one source-level model.

### 5. Scan through five lenses

Independently inspect the source for:

- **Frameworks:** reusable models, decision structures, and reasoning paths.
- **Principles:** rules, criteria, checklists, and action-guiding claims.
- **Cases:** examples showing problem → use → conclusion → result.
- **Failures:** counterexamples, mechanisms of failure, traps, and warning signs.
- **Terms:** concepts whose source-specific meaning differs from ordinary usage.

Use clean passes or independent agents when available and worthwhile. Parallelism is an accuracy tool, not a requirement. Merge duplicates only after each lens has completed its pass.

### 6. Verify what deserves prominence

Evaluate candidate insights with three tests:

- **Evidence stability:** Is it supported by explicit source evidence, preferably across independent contexts? A single occurrence may still qualify if the source clearly presents it as central; label it as single-source evidence.
- **Transferability:** Does it explain, predict, or guide a relevant situation beyond merely retelling the example? This test is optional for factual, historical, literary, or news content where transfer is not the goal.
- **Information value:** Is it specific, consequential, surprising, or unusually well-supported rather than generic advice?

Classify rather than discard blindly:

- core insight;
- supporting evidence or case;
- useful context;
- contested or uncertain claim;
- low-value repetition.

Do not impose a fixed pass rate or invent enough insights to meet a quota.

### 7. Construct useful units

For every core method or actionable insight, capture:

- the problem it addresses;
- concise interpretation in your own words;
- source evidence and locator;
- representative case;
- execution steps or decision criteria, if supported;
- failure conditions, warning signs, and limits.

For non-method content, use an appropriate unit instead: claim–evidence, event–cause–consequence, concept–distinction, argument–objection, or theme–example. Never manufacture action steps for material that does not support them.

### 8. Synthesize for the reader

Organize the result by the source's conceptual structure or the user's question, not by the extraction machinery. Lead with the central thesis and coverage note, then present the strongest supported material.

Include as relevant:

- executive synthesis;
- argument or narrative map;
- core insights with evidence;
- cases and counterexamples;
- actionable implications;
- assumptions, disputes, and limitations;
- key terms;
- source and locator index.

Use short quotations sparingly and respect applicable quotation limits. Prefer precise paraphrase linked to source locations.

### 9. Run the quality gate

Before delivery, check:

- Can a reader reconstruct the source's central thesis and reasoning?
- Are important conclusions traceable to the source?
- Did any inference become falsely attributed to the author?
- Were counterevidence and limitations represented fairly?
- Does the structure fit the content type?
- Is repetition removed without losing distinct evidence?
- Is the output no longer than its useful information warrants?

If any answer fails, revise once at the source of the problem.

## Boundaries

- For a quick summary request, use the same fidelity rules with fewer sections; do not run a needlessly heavy pipeline.
- For knowledge-base retrieval or open-ended Q&A, use a retrieval workflow. Invoke this skill only when a bounded document set itself needs analysis or synthesis.
- For multiple sources, distinguish consensus, disagreement, and independent corroboration; do not merge incompatible claims into one voice.
- For medical, legal, financial, scientific, or current-affairs claims, verify externally when the user needs factual confidence, and distinguish verification from source summary.
- For saved deliverables, obey the active workspace's location and approval rules.
