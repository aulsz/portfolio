---
name: parallel-deep-research
description: Run multi-source research in parallel, then synthesize findings with source triangulation, confidence labeling, and action-oriented outputs.
---

# Parallel Deep Research

## Purpose
Use this skill when the user asks for broad research that benefits from parallel collection and synthesis.

## Core Workflow
1. Define scope (question, constraints, output format)
2. Launch parallel source collection
3. Normalize findings
4. Triangulate claims across independent sources
5. Produce concise conclusions + actionable next steps

## Required Output Structure
- **Summary** (high signal, low fluff)
- **Key findings** (bulleted)
- **Confidence level** (High / Medium / Low)
- **Sources** (clear links)
- **Next actions** (practical)

## Quality Rules
- Prefer primary/official sources when possible
- Avoid single-source conclusions on important claims
- Distinguish facts vs inference
- Mark uncertainty explicitly

## Reliability Rules
- If sources conflict: present both and explain divergence
- If evidence is weak: say so and avoid overclaiming
- If user asks for ongoing monitoring: recommend cadence + triggers

## Cost/Rate-Limit Discipline
- Batch requests where possible
- Avoid one-item tight loops
- Respect 429/Retry-After
- Prefer fewer, larger writes

## Safety
- No secret exfiltration
- No unauthorized external actions
- Ask before high-impact actions

## Deliverable Tone
- Clear, direct, decision-ready
- Keep verbose detail optional
