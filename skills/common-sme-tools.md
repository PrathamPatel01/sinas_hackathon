# Common SME AI tools → likely classification (fast-path map)

A reference map of AI tools/features typical Dutch SMEs run, with the **likely** tier. This is a
starting point to speed classification — the classifier must still confirm against the company's
actual *use* (the same tool can change tier depending on what it's used for) and cite the regulation.

> Golden rule: classify by **what the tool does in this company**, not by the vendor's brand.
> "ChatGPT" is minimal-risk when drafting emails and high-risk if it's the engine screening CVs.

## Usually MINIMAL risk (transparency may still apply if customer-facing)
| Tool / feature | Typical use | Notes |
|----------------|-------------|-------|
| ChatGPT / Claude / Copilot seats | Internal drafting, summarising, brainstorming | Minimal — but data-hygiene + literacy still apply. High-risk if wired into hiring/credit decisions. |
| Notion AI, Google/M365 Copilot | Notes, docs, slides | Minimal. |
| Grammarly / writing assistants | Proofreading | Minimal. |
| GitHub Copilot / Cursor | Code completion | Minimal. |
| Inventory / demand forecasting | Stock optimisation | Minimal (unless safety-critical infrastructure). |
| Spam / fraud-pattern filters | Email, payments fraud detection | Minimal; credit-fraud detection is explicitly carved out of high-risk credit scoring. |

## Usually LIMITED risk — transparency obligations (Article 50)
| Tool / feature | Typical use | Obligation |
|----------------|-------------|-----------|
| Website / support chatbot | Customer Q&A | Must disclose users are talking to AI. |
| AI voice agents / IVR | Phone support | Disclose AI. |
| Generative image/video/audio for marketing | Content creation | Label synthetic content; disclose deepfakes. |
| AI-generated published text | Public articles | Label as AI-generated where applicable. |

## Usually HIGH risk (Annex III) — the headline findings
| Tool / feature | Typical use | Annex III point |
|----------------|-------------|-----------------|
| CV-screening / applicant ranking (e.g. HireVue-style, ATS auto-shortlisting) | Filter/score job candidates | **§4 employment** |
| AI video-interview scoring | Evaluate candidates | **§4 employment** |
| Employee performance / productivity scoring | Evaluate, allocate, promote/terminate | **§4 employment** |
| Workforce monitoring that drives decisions | Behaviour/performance tracking | **§4 employment** |
| Credit scoring / loan eligibility | Assess creditworthiness of persons | **§5 essential services** |
| Life / health insurance risk & pricing | Underwriting individuals | **§5 essential services** |
| Benefit / eligibility determination | Public assistance access | **§5 essential services** |
| AI proctoring / exam monitoring | Detect cheating in tests | **§3 education** |
| Education admission / grading AI | Admit / evaluate learners | **§3 education** |

## Usually PROHIBITED (Article 5) — stop using
| Tool / feature | Why |
|----------------|-----|
| Emotion recognition of staff/students at work or school | Prohibited (narrow safety/medical exceptions). |
| Social scoring of individuals | Prohibited. |
| Biometric categorisation by sensitive attributes | Prohibited. |
| Facial-image scraping to build recognition DBs | Prohibited. |

## Edge cases that flip tier
- **Pure biometric verification** (unlock device, confirm identity 1:1) is NOT high-risk; remote
  biometric *identification* is.
- **General copilot used to make a hiring/credit decision** → inherits the high-risk tier of that
  decision, not the minimal tier of the generic tool.
- **Fraud detection** is explicitly excluded from the high-risk credit-scoring category.
- A high-risk-listed tool used only for a **narrow procedural / preparatory** step may qualify for
  the Article 6(3) carve-out — but never if it profiles natural persons. Record the reasoning.
