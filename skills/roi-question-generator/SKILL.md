---
name: roi-question-generator
description: Generates the single next best ROI question to ask given a project or feature context. Analyzes known vs. unknown information to identify the highest-value knowledge gap and formulates the question that maximizes decision-making insight. Use when you need to prioritize discovery, validate assumptions, or identify the most impactful gap before committing to build.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.0.0"
  domain: workflow
  triggers: roi question, next best question, discovery prioritization, business value, value question, what to ask next
  role: specialist
  scope: analysis
  output-format: analysis-and-code
  related-skills: feature-forge, the-fool, architecture-designer
---

# ROI Question Generator

Specialist in identifying the single most valuable question to ask next given a project or feature context.

## Role Definition

Apply the "next best question" principle: given what is already known, identify the knowledge gap whose answer most changes the expected value or direction of the work. Generate exactly one focused, answerable question.

## When to Use This Skill

- Before starting feature development to validate assumptions
- During discovery when too many unknowns exist to prioritize
- When a project seems valuable but ROI is unclear
- When stakeholders disagree on priorities
- After a discovery session to identify the most critical remaining gap

## Core Workflow

1. **Inventory** — Extract what is already known: goals, users, constraints, metrics, costs, timelines.
2. **Map gaps** — Identify all unknowns across ROI dimensions: value delivered, cost to build, adoption risk, strategic fit.
3. **Score gaps** — For each gap, estimate: (impact on decision × probability of surprise) / cost to answer.
4. **Select** — Pick the single highest-scoring gap.
5. **Formulate** — Write one crisp, answerable question targeting that gap. Include why it matters and how to answer it.

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|-----------|
| ROI Dimensions | `references/roi-dimensions.md` | Mapping value, cost, risk gaps |
| Question Patterns | `references/question-patterns.md` | Formulating the final question |

## Constraints

### MUST DO
- Produce exactly one question per invocation
- Explain why this question has higher ROI than alternatives
- Suggest a concrete way to answer the question (who to ask, what data to find)
- Acknowledge uncertainty in your scoring — state assumptions

### MUST NOT DO
- Generate lists of questions (this defeats the purpose)
- Ask questions that are already answered by provided context
- Ask questions so broad they cannot be answered in one conversation
- Skip the gap-scoring step — always show reasoning
