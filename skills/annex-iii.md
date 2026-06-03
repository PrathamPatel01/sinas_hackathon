# EU AI Act — Annex III high-risk use cases

A system is high-risk (Article 6(2)) if its intended purpose falls under one of these eight
areas. For SMEs, **#4 (employment)** and **#5 (essential services)** are by far the most common
exposure — that is where a CV-screener, a credit/eligibility scorer, or an insurance pricing
model lands. Cite the specific point when you classify.

## 1. Biometrics
- Remote biometric identification (excluding pure verification/authentication, e.g. unlocking a
  phone, which is not high-risk).
- Biometric categorisation by sensitive/protected attributes.
- Emotion recognition.
(Note: several biometric uses are *prohibited* under Article 5 — check that tier first.)

## 2. Critical infrastructure
Safety components in the management/operation of critical digital infrastructure, road traffic,
or supply of water, gas, heating, electricity.

## 3. Education and vocational training
- Determining admission or assignment to institutions/programmes.
- Evaluating learning outcomes (including steering the learning process).
- Assessing the appropriate level of education a person will receive.
- **Monitoring and detecting prohibited behaviour during tests** (AI proctoring).

## 4. Employment, workers management, access to self-employment ← most common for SMEs
- **Recruitment / selection**: placing targeted job ads, **filtering/screening applications,
  evaluating candidates** (CV-screening, ranking, automated shortlisting, video-interview scoring).
- Decisions affecting terms of work: **promotion, termination**, task allocation based on
  behaviour/traits, and **monitoring/evaluating performance** of people at work.

> If the company uses ANY tool that screens, ranks, scores, or evaluates job candidates or
> employees — that surface is high-risk. This is the headline finding for most SMEs.

## 5. Access to essential private and public services ← common for SMEs in fintech/insurance
- **Creditworthiness / credit scoring** of natural persons (excluding detection of financial fraud).
- **Risk assessment and pricing** in **life and health insurance**.
- Eligibility decisions for public assistance benefits and services.
- Dispatching / prioritising emergency services.

## 6. Law enforcement
Risk assessments, polygraph-type tools, evidence reliability, profiling in the course of detection,
investigation, prosecution. (Rarely relevant to ordinary SMEs.)

## 7. Migration, asylum, border control
Risk assessments, application examination, detection tooling for border management.
(Rarely relevant to ordinary SMEs.)

## 8. Administration of justice and democratic processes
Assisting judicial authorities in researching/interpreting facts and law; influencing election or
referendum outcomes / voting behaviour. (Rarely relevant to ordinary SMEs.)

## The Article 6(3) "not significant risk" carve-out

A system listed above is NOT high-risk if it does not pose a significant risk to health, safety or
fundamental rights, because it only does one of: (a) a narrow procedural task; (b) improve the
result of a finished human activity; (c) detect decision patterns / deviations without replacing or
influencing the human assessment without proper review; (d) a preparatory task.
**Profiling of natural persons is always high-risk** — the carve-out can never apply to it.

When you apply this carve-out, you must record which limb and why. Default to high-risk if the tool
makes or materially shapes a decision about a person.
