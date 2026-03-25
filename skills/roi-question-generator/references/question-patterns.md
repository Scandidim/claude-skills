# Question Patterns

Once the highest-ROI gap is identified, use these patterns to formulate the final question and its supporting context.

## The Output Structure

Every generated question must include:

```
## Next Best ROI Question

**Question:** [One crisp, answerable sentence ending in a question mark]

**Why this question:** [1–2 sentences explaining which ROI gap this targets and why it outscores alternatives]

**What changes if the answer is surprising:** [1 sentence describing the decision impact]

**How to answer it:** [Concrete next step — who to ask, what data to pull, what spike to run]
```

---

## Question Formulation Patterns

### Pattern 1: Quantify the Assumed Value

Use when value is assumed but not measured.

```
Template: "How many [users/teams/transactions] experience [problem] per [time period]?"

Examples:
- "How many enterprise customers hit the 100-seat license limit per month?"
- "How many support tickets per week mention the export workflow?"
- "How many teams have more than 50 projects in the current data model?"
```

**When to use:** Value dimension gap, surprise probability ≥ 0.5, answer cost = 1–2.

---

### Pattern 2: Expose the Hidden Dependency

Use when a technical assumption is unvalidated.

```
Template: "Does [system/service/team] support [capability] at [scale/condition]?"

Examples:
- "Does the payments API support idempotent retries at 10x current transaction volume?"
- "Does the mobile SDK support background sync on iOS 15 and below?"
- "Does the data warehouse team's SLA allow real-time queries from the product backend?"
```

**When to use:** Cost or risk dimension gap, surprise probability ≥ 0.4, answer cost = 1–3.

---

### Pattern 3: Validate the Adoption Path

Use when delivery is assumed but user behavior change is not validated.

```
Template: "Will [user type] [take action] without [onboarding/training/nudge]?"

Examples:
- "Will ops managers run the new compliance report weekly without a Slack reminder?"
- "Will developers adopt the new SDK without a migration guide?"
- "Will users discover the bulk delete option without a tooltip?"
```

**When to use:** Adoption risk gap, surprise probability ≥ 0.4.

---

### Pattern 4: Challenge the Scope Assumption

Use when the scope is vague and could expand or collapse the project.

```
Template: "Is [feature/behavior] in scope for the MVP, or deferred?"

Examples:
- "Is offline support in scope for the mobile MVP, or deferred to v2?"
- "Is multi-currency support required for the payment flow launch, or US-only first?"
- "Does 'search' mean full-text, filtered list, or semantic similarity?"
```

**When to use:** Scope creep risk gap, ambiguous requirements.

---

### Pattern 5: Find the Decision Owner

Use when it's unclear who can commit to a choice that blocks design or build.

```
Template: "Who owns the decision on [topic] and when can they commit?"

Examples:
- "Who owns the data retention policy decision, and when is it finalized?"
- "Who approves the API contract changes — platform team or product?"
- "Who has authority to de-scope the dashboard from the MVP?"
```

**When to use:** Stakeholder alignment gap, answer cost = 1.

---

### Pattern 6: Surface the Cost of Delay

Use when urgency is unclear and prioritization is being debated.

```
Template: "What happens if we ship [feature] 3 months later than planned?"

Examples:
- "What happens if we ship GDPR export 3 months after the EU deadline?"
- "What happens if the competitor ships audit logs before we do?"
- "What happens if we defer multi-tenant support to Q3?"
```

**When to use:** Time value gap, strategic fit gap.

---

## Anti-Patterns to Avoid

### Too Broad
```
BAD:  "What does success look like?"
GOOD: "What is the target weekly active usage rate at 90 days post-launch?"
```

### Already Answered
```
BAD:  "Who are the target users?" (when already stated: enterprise admins)
GOOD: "How many enterprise admins per account — 1, or up to 20?"
```

### Unanswerable Without Months of Work
```
BAD:  "What is the total addressable market for this feature?"
GOOD: "How many of our current customers have requested this in support tickets?"
```

### Two Questions Disguised as One
```
BAD:  "What's the expected adoption rate and how will we measure it?"
GOOD: "What is our minimum acceptable adoption rate at 30 days to consider this a success?"
```

---

## Example: Full Output

**Context provided:** Team is building a CSV export feature for enterprise customers. Timeline is 6 weeks. No usage data on how often users manually copy-paste data today.

**Gap scored highest:** Value dimension — actual frequency of manual data extraction is unknown. decision_impact=5, surprise_probability=0.7, answer_cost=1 → score=3.5

---

## Next Best ROI Question

**Question:** How many enterprise customers manually export or copy data from the dashboard at least once per week?

**Why this question:** The entire ROI case rests on frequency of use. If fewer than 5% of enterprise customers do this weekly, the 6-week investment may not be justified. This outscores all other gaps because it is highly likely to surprise us (we're assuming high frequency) and can be answered today by querying support tickets or a 5-minute Slack survey to CSMs.

**What changes if the answer is surprising:** If usage frequency is low, we either de-scope to a lighter implementation (copy to clipboard) or defer entirely — a 6-week project becomes a 1-day task.

**How to answer it:** Ask the 3 most active CSMs to check their Slack DMs for "export" or "download" mentions from enterprise accounts over the last 30 days. Alternatively, check Intercom/Zendesk for "export" in enterprise ticket titles. Takes 30 minutes.
