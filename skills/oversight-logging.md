# EU AI Act — Human oversight & logging policy (drafting guide)

This skill tells the policy-drafter how to turn a classified inventory into an adoptable
**Human Oversight & Logging Policy** for the company. The policy is the central evidence artifact
a deployer needs for high-risk systems (Article 26) and is good practice for limited-risk ones.

## Structure of the policy document

1. **Purpose & scope** — names the company, lists the AI surfaces in scope, states the policy
   covers deployer obligations under Regulation (EU) 2024/1689.
2. **Roles & accountability** — name an **AI accountable owner** (usually ops/COO) and, per
   high-risk surface, a named **human overseer** who is competent, trained and has authority to
   override or stop the system.
3. **Per-surface controls** — a table: surface → risk tier → overseer → oversight action →
   logging requirement → review cadence.
4. **Human oversight procedures** — for each high-risk surface, the concrete review step:
   what the human checks, the threshold to override, how to escalate, and the rule that the
   system must not be the sole basis for a decision affecting a person without meaningful review.
5. **Logging & record-keeping** — which logs are kept, where, who can access, retention period
   (default: keep automatically-generated logs for at least 6 months unless other law requires
   longer; tie retention to the system's intended purpose).
6. **Transparency commitments** — where the company discloses AI use (chatbots, candidates,
   synthetic content labelling).
7. **Monitoring & incident handling** — how operation is monitored, the serious-incident
   reporting path to the provider and the competent national authority.
8. **Worker information** — confirmation that workers and their representatives are informed
   before a high-risk system is used in the workplace.
9. **Review & version control** — the policy is reviewed when a new AI surface is added or at
   least annually; version, date, approver.

## Drafting rules

- Parametrise to the **actual** inventory — never emit generic boilerplate. Every high-risk
  surface gets its own oversight procedure naming the tool.
- For each obligation, keep it actionable: a sentence the company can actually do on Monday.
- Mark anything the company must decide (who the overseer is, retention length) as
  `[TO BE COMPLETED: ...]` so it's obvious where human input is required.
- End with the standard disclaimer that this is a draft for review, not legal advice.

## Minimum oversight action by tier

| Tier | Oversight action to write into the policy |
|------|-------------------------------------------|
| Prohibited | Decommission. Record decision and date. No oversight workaround makes it lawful. |
| High | Named overseer; mandatory human review before any decision about a person; logging on; monitoring; worker/affected-person information; incident reporting. |
| Limited | Disclosure controls (AI is disclosed; synthetic content labelled); spot-check accuracy. |
| Minimal | No legal control required; cover under general AI-use guidelines and literacy. |
