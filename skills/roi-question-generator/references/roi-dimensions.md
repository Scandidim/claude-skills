# ROI Dimensions

Use this reference to map knowledge gaps across the four ROI dimensions. For each dimension, common unknowns are listed with their typical impact on decision-making.

## The Four ROI Dimensions

### 1. Value Delivered (Numerator — Benefits)

What users or the business gains if the work succeeds.

| Sub-dimension | Key unknowns | High-impact signals |
|---------------|-------------|---------------------|
| User value | How many users affected, frequency of use, severity of pain | Usage data, support ticket volume, user interviews |
| Business value | Revenue impact, cost reduction, compliance risk avoidance | Finance data, competitive analysis, legal requirements |
| Strategic value | Alignment with roadmap, platform leverage, optionality created | Roadmap documents, OKRs, leadership intent |
| Time value | Urgency, competitive window, seasonal dependency | Market deadlines, competitor activity |

**Questions that reveal value:**
- "How many users experience this problem weekly?"
- "What is the cost of the current workaround per user per month?"
- "Is this blocking a specific customer deal or renewal?"

---

### 2. Cost to Build (Denominator — Investment)

Engineering time, infrastructure, maintenance burden, opportunity cost.

| Sub-dimension | Key unknowns | High-impact signals |
|---------------|-------------|---------------------|
| Build cost | Complexity, unknowns, team familiarity | Spike results, architecture review, prior estimates |
| Operational cost | Infra spend, on-call burden, support load | Cloud cost models, SRE estimates |
| Maintenance cost | Churn rate of dependencies, tech debt introduced | Codebase health, library stability |
| Opportunity cost | What else could the team build in this time | Backlog priority, team capacity |

**Questions that reveal cost:**
- "Has anyone spiked this? What did they find?"
- "Does this require changes to core services owned by another team?"
- "What ongoing operational burden does this add?"

---

### 3. Adoption Risk (Probability Adjustment)

The chance that delivered value is actually realized.

| Sub-dimension | Key unknowns | High-impact signals |
|---------------|-------------|---------------------|
| User adoption | Awareness path, behavior change required, onboarding friction | UX research, past feature adoption rates |
| Technical risk | Integration unknowns, performance at scale, security gaps | Spike results, load testing, security review |
| Dependency risk | External API reliability, third-party changes, team availability | SLA data, roadmap conflicts |
| Scope creep risk | Requirements clarity, stakeholder alignment | Spec completeness, stakeholder sign-off |

**Questions that reveal adoption risk:**
- "Will users discover this feature on their own, or does it require a campaign?"
- "Is there a behavior change required for users to benefit?"
- "What is the reliability SLA of the external API this depends on?"

---

### 4. Strategic Fit (Multiplier)

How well the work aligns with where the product and company are headed.

| Sub-dimension | Key unknowns | High-impact signals |
|---------------|-------------|---------------------|
| Roadmap alignment | Does this advance or conflict with the 12-month plan | Product roadmap, OKR review |
| Platform leverage | Does this enable future work or is it a dead end | Architecture docs, platform team input |
| Technical debt | Does this increase or decrease system complexity | Code review, architectural patterns |
| Competitive moat | Does this differentiate or just match competitors | Competitive analysis, market positioning |

---

## Gap Scoring Formula

For each gap, estimate:

```
gap_score = (decision_impact × surprise_probability) / answer_cost
```

Where:
- `decision_impact` (1–5): How much would the answer change the build/don't-build decision?
- `surprise_probability` (0.0–1.0): How likely is the answer to be different from the current assumption?
- `answer_cost` (1–5): How hard is it to get the answer? (1 = ask one person today, 5 = months of research)

**Example scoring:**

| Gap | decision_impact | surprise_probability | answer_cost | score |
|-----|----------------|---------------------|-------------|-------|
| How many users affected | 5 | 0.6 | 1 | **3.0** |
| Build complexity | 3 | 0.4 | 2 | 0.6 |
| Competitor has this | 2 | 0.3 | 1 | 0.6 |
| Infrastructure cost | 4 | 0.5 | 3 | 0.67 |

The highest score identifies the next best question.

---

## When Gaps Are Tied

If two gaps score similarly, prefer the one that:
1. **Unblocks other gaps** — answering it makes other unknowns clearer
2. **Is time-sensitive** — external deadline or data will disappear
3. **Is cheaper to answer now** — cost increases over time

---

## Common High-ROI Questions by Stage

### Pre-Discovery (Before Any Work)
- "Is anyone already solving this internally or externally?"
- "Who is the most impacted user — can we talk to them today?"
- "What does success look like in 6 months, measurably?"

### During Design
- "What is the simplest version that validates the core assumption?"
- "Which technical decision, if wrong, would require a complete rewrite?"

### During Build
- "Has the acceptance criterion for the highest-risk requirement been tested?"

### Pre-Launch
- "What is the rollback plan if adoption is below 10% after 30 days?"
