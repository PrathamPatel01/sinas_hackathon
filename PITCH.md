# Pitch script — hawkEYE
*~6 minutes · 9 slides · 1 live demo. Deck: open `web/deck.html` in a browser (←/→ to advance, **N** for speaker notes, the countdown updates itself).*

**Tone:** deadpan, dry, confident. You're a lawyer presenting evidence, not a founder begging.
The jokes work because you *don't* laugh at them. Pause after punchlines — let the room do the work.

---

## SLIDE 1 — "Everyone in this room is breaking EU law.*" (~40s)

> Quick show of hands — who used AI at work this week?
>
> *(hands go up — wait for them)*
>
> Keep them up if you have documented, role-specific AI-literacy training for that.
>
> *(hands drop — pause)*
>
> Article 4 of the EU AI Act. Mandatory. Since February 2nd… **2025**.
>
> *(beat)*
>
> So — lovely to be presenting at a crime scene.
>
> In the next five minutes, one fictional Dutch company is going to become
> legally cleaner than anyone in this room. *(don't name the product yet — slide 3 is the reveal)*

**Delivery:** the show of hands is the whole slide. Don't rush the second question — the comedy is in the hands going down.

---

## SLIDE 2 — "58 days" (~50s)

> And Article 4 was the *warm-up* obligation. The main event —
>
> *(point at the giant number — it's counting down live, mention that)*
>
> — is **August 2nd**. High-risk obligations land. If your company screens CVs, scores loans,
> or proctors exams with AI: that's **Annex III**, that's regulated, and the fines run to
> **€35 million or 7% of turnover** — whichever ruins you more.
>
> The Act is 459 pages. And here's my favourite thing about it: the EU wrote 459 pages
> about artificial intelligence… and everybody's first move was to ask ChatGPT to summarise it.
>
> *(gesture at the three cards)*
>
> Your actual options today: a lawyer — excellent, thorough, **booked until September**.
> An intern with ChatGPT — confident fiction, with citations… *to laws that don't exist*.
> Or denial — free, very popular, works great right up until it doesn't.

**Delivery:** "whichever ruins you more" deadpan. The ChatGPT line should get the biggest laugh of the deck — pause on it.

---

## SLIDE 3 — The reveal: hawkEYE (~15s)

> *(let the logo and the name land — don't talk over the first beat)*
>
> So we built **hawkEYE**.
>
> Compliance, **with receipts**. It doesn't summarize the law — it quotes it.
> And it looks at your AI stack the way the regulator will.

**Delivery:** this is the breath between two joke-heavy slides. Slow, proud, fifteen seconds, advance.

---

## SLIDE 4 — "So we hired five employees who read all 459 pages." (~50s)

> So we hired five employees who actually read all 459 pages.
> They don't bill hours, they don't take holidays, and they finish the whole job in **75 seconds**.
>
> *(walk the pipeline left to right)*
>
> One **classifies** your AI tools against Annex III. Two go and get **the law** — and I mean
> the law, not a summary: the **verbatim EU text**, *and* live **Dutch guidance from the AP and ACM**,
> through Moonlit's legal research API. Two more draft your **oversight policy** and your
> **Article 4 training plan**. Out the other end: a compliance pack you could hand to a regulator.
>
> And this is the part we're genuinely proud of —
>
> *(hover the chip ON the slide — the popup shows the real Annex III text)*
>
> every claim in every document looks like this. Hover it. That is the **actual law**,
> retrieved live. We don't ask you to trust AI.
>
> **We ask you to click.**

**Delivery:** hovering a working citation *inside the slide deck* is a flex — milk it. "We ask you to click" is the thesis of the whole pitch; say it slowly.

---

## SLIDE 5 — The architecture: "Four moves." (~25s, brisk)

> Quick X-ray before the demo — four moves.
>
> *(sweep left to right; the pulses travel with you)*
>
> **Classify** — every AI tool in the company, mapped against Annex III.
> **Ground** — we fetch the *actual law*, mid-pipeline: verbatim EU text plus current Dutch
> AP and ACM guidance. **Draft** — the oversight policy and the training plan, citing both
> layers by name. **Deliver** — the pack. Every claim one click from its source.
>
> The whole thing runs self-hosted on Sinas — company data never leaves the building.
>
> *(point at the footnote)*
>
> And this diagram is a *survivor* — it beat a worker deadlock, a context-compaction bug,
> and four strictly worse versions of itself. Ask us in Q&A. It's a good story.

**Delivery:** brisk — sweep your hand along the pipeline as the dots travel; the slide animates the flow for you. The footnote line is the laugh.

---

## SLIDE 6 — LIVE DEMO (~2 min)

*(switch to `http://localhost:8800` — the input is pre-filled)*

**The runbook, click by click:**

1. **Hit ▶ Run pipeline.** While phase ① spins:
   > Wervenk Recruitment. Sixty humans, four AIs. The classifier is reading their stack
   > right now — and notice Moonlit is already fetching the Act **in parallel**. Agents don't queue politely.
2. **Phase ② lights up:**
   > EU citations grounded… and the Dutch agent just pulled real AP guidance —
   > including a report from **March 2026**. Three months old. Try getting that from a 459-page PDF.
3. **Phase ③:**
   > Now two drafters are writing the oversight policy and the training plan —
   > and they cite that Dutch guidance **by name**.
4. **Done (~75s). Click the Classifier node:**
   > There it is. HireScan — their CV screener — **red. High-risk. Annex III §4(a).**
5. **Click the blue citation chip:**
   > And there's the receipt: the verbatim Act, with a link to the source.
6. **Open the Policy tab, click an amber 🇳🇱 chip:**
   > Same trick, Dutch layer — that's the actual Autoriteit Persoonsgegevens text.
7. **Follow-up box** — type: *"we also started using an AI exam proctoring tool"* → Re-assess:
   > Companies change. Watch — *(NEW badge appears)* — new tool, new high-risk finding, sixty seconds, nobody called a lawyer.
8. *(If time)* **Chat:** ask *"what exactly must the HireScan overseer do?"* —
   > and the chat answers with sources, because of course it does.

**Pacing tip:** steps 4–6 are the demo. If you're at 4 minutes total, skip 7–8.

**FALLBACK (wifi/Sinas dies):** stay calm, open the committed `demo_pack.md` render (or the pre-run replay):
> The demo gods have spoken — fortunately our agents pre-signed their confession.
> This pack was generated live an hour ago; everything you'd have seen is in here.

---

## SLIDE 7 — The business: "Two ways to pay." (~30s)

> How does this make money? Two ways — three, if you count the fine.
>
> **B2C, one-time.** The panic purchase: you're fundraising, you're being audited,
> August is coming. Run hawkEYE, €49, keep the pack, sleep again. TurboTax energy.
>
> **B2B, subscription — priced per module, per employee.** Two euros per head per month.
> The AI Act is module one; GDPR, DORA, NIS2 — every law Moonlit holds becomes a SKU,
> and every hire grows the contract. The subscription buys *continuous* watching:
> your stack changes, the law changes, hawkEYE re-runs and pings you before the regulator does.
>
> Go-to-market: start where the panic is — the deadline — and ride the channels SMEs
> already trust: **accountants, insurers, VC platform teams.** Free scan in, modules out.

**Delivery:** "three, if you count the fine" is the laugh — don't step on it. The module-as-SKU line tees up the vision slide perfectly.

---

## SLIDE 8 — Closing argument (~35s)

> What you just saw: five agents on Sinas. Two layers of real law — EU and Dutch — fetched
> live through Moonlit. A pack you can download as PDF. A chat that cites its sources.
> All of it open source.
>
> Next: Moonlit already holds German, French and Belgian law — **same pipeline, new flags**.
> Then continuous monitoring, so the day your shiny new SaaS tool quietly turns high-risk,
> your phone buzzes before the regulator's does.
>
> *(slow down for the close)*
>
> August 2nd is in **58 days**. The lawyers are booked until September.
>
> **We're not.**
>
> AI got these companies into this mess. We taught it to clean up after itself.

---

## SLIDE 9 — The vision: "one law down" (~25s)

> And here's the real pitch: **nothing in those four moves is AI-Act-specific.**
>
> *(gesture at the grid)*
>
> Classify against a law. Ground in its verbatim text. Draft the controls.
> Point the same pipeline at **GDPR. DORA. NIS2. CSRD.** Moonlit already holds the
> corpora — 15 million documents, thirty-plus jurisdictions. The AI Act was simply
> the law with the loudest deadline.
>
> *(slow, final)*
>
> **hawkEYE — every law, with receipts.** Thank you.

**Delivery:** the zoom-out. Slide 7 was the mic-drop for *this* product; this is the "and it's a platform" beat investors/juries score on. End on the tagline, not on "questions?".
**Timing note:** full script now runs ~6:40 — if the slot is a hard 5:00, cut slide 2's option cards to one line each, demo steps 7–8, and compress slides 4+5 into one breath.

---

## Q&A ammunition

| They ask | You say |
|---|---|
| *"Is this legal advice?"* | "No — it's a draft with receipts. Every output says so, and every claim links to the source so a human can verify in seconds instead of weeks. We make the lawyer's hour cost €300 instead of €25,000." |
| *"Why agents instead of one big prompt?"* | "Because one prompt gives you vibes. Specialists give you verifiable steps: the classifier's output is checkable, the evidence agent's quotes are verbatim, the policy cites both. When something's wrong, you know *which* agent to fix." |
| *"How do you know the citations are right?"* | "We don't trust the model's memory at all — the text comes from Moonlit's legal corpus at runtime, and the click-through goes to the source. The model decides *relevance*; the *text* is retrieval." |
| *"What about hallucinations?"* | "The riskiest output — legal text — is never generated, only retrieved. The classification is reviewable, with the carve-out logic (Article 6(3)) made explicit so a human can disagree." |
| *"Business model?"* | "Per-pack freemium → monitoring subscription. The pack gets you in; the 'your stack changed, here's what it means' alert is what they pay for. Compliance isn't a document, it's a feed." |
| *"Why won't ChatGPT kill this?"* | "Ask ChatGPT for Annex III §4(a) verbatim and click its source. We'll wait. The moat is the grounded legal corpus, the structured pipeline, and the artifact — not the chat." |
| *"GDPR/data concerns?"* | "Sinas is self-hosted — the company description never leaves their instance, and the only external call is to a legal-text API. We send the law a question, not their data." |
| *"What was hardest?"* | (honest, charming) "Making agents reliable. We found a worker deadlock, a context-compaction bug, and learned Sinas executes an agent's tool calls serially — so we redesigned around fewer, fatter calls. The architecture in the slide is the *survivor* of four worse ones." |

## Pre-stage checklist (do this 30 min before)
- [ ] `python3 scripts/server.py` running; **one warm-up run completed** (warms the Moonlit cache → evidence is instant)
- [ ] Browser tabs: ① `web/deck.html` ② `localhost:8800` (fresh, input pre-filled) ③ rendered `demo_pack.md` (fallback)
- [ ] Do Not Disturb on; display sleep off; close Slack
- [ ] Phone hotspot ready as wifi fallback
- [ ] Press **N** once in the deck to confirm notes work
