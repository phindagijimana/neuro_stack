# Transitions: academia, industry, clinical, startup

> The hard part of changing roles is not the new job; it's giving up the identity of the old one. Read the realities below before you optimise the resume.

This page covers the four moves most commonly made in and out of neuroimaging: postdoc → faculty, postdoc → industry research, PhD → industry MLE, and MD → research. It also covers the MD-PhD / clinician-scientist hybrid, the interview formats you'll meet, what actually transfers, and the role taxonomy you'll need to navigate job listings.

It does not tell you which path is better. People who tell you that are usually selling the path they took.

## The four common moves

### 1. Postdoc → faculty (tenure-track)

The traditional academic path. The reality check:

- **What changes.** You go from doing the work to *managing* the work. You will hire, mentor, write grants, teach, sit on committees, and run a lab. Bench time collapses; calendar time fragments.
- **What carries over.** Methodological depth, paper-writing, mentee management at small scale, presentation skill.
- **What you'll need to add fast.** Grant writing at scale (see [Grant writing](grant-writing.md)), people management (hiring, firing, performance conversations), budget management, lab politics.
- **The honest timeline.** 5–8 years to tenure in most R1 systems. First R01 typically in years 2–4. The first three years are the high-burn / high-risk window.

This path makes sense if: you want methodological autonomy, you accept the salary cap (US faculty: $90–180 k typical, depending on field and institution), and you genuinely enjoy the mix of writing, teaching, and managing.

### 2. Postdoc → industry research (research scientist)

Big-tech and big-pharma research labs (Google Brain / DeepMind, Meta FAIR, Microsoft Research, MSR Health Futures, Genentech, Roche, Novartis, GSK, Verily, Isomorphic, Insitro) hire postdocs into research-scientist roles.

- **What changes.** You'll publish less, ship more. Stakeholders include product managers and clinicians, not just reviewers. Cycles are quarterly, not 3-year.
- **What carries over.** Modelling skill, statistical rigour, paper-writing for the labs that still publish, deep-domain expertise for medical / biotech labs.
- **What you'll need to add.** Engineering rigour (code review, tests, CI), product thinking, on-call culture for labs that ship to internal products, sometimes regulatory exposure (see [AI/ML → Regulatory](../ai/regulatory.md)).
- **Salary range (US, 2024).** $200–400 k total comp for entry-level research-scientist roles at big tech; biotech is lower base but more bonus / equity dependent on outcomes.

This path makes sense if: you want better resources and pay than academia, you tolerate less publication, and you can accept that the company defines the problem.

### 3. PhD → industry ML engineer (MLE) / data scientist

The most common move out of a neuroimaging PhD. Less prestige than research-scientist roles, but vastly more open positions and faster ramp.

- **What changes.** You will write production code. You will own pipelines, dashboards, and deployments. You will be on-call. You will read other people's code more than your own.
- **What carries over.** Numerical literacy, modelling instincts, statistical sanity-checking, pipeline operating experience (more than you think — see [Data engineering → HPC → industry](../data-engineering/hpc-to-industry.md)).
- **What you'll need to add.** Production software engineering (Git workflows, testing, code review at scale), system-design vocabulary, SQL, A/B testing intuition, business framing of model performance.
- **Salary range (US, 2024).** $180–350 k total comp for entry-level MLE / DS at big tech; $130–220 k at startups and non-tech enterprises.

This path makes sense if: you want to ship, you're willing to leave the imaging domain (most MLE roles will not be imaging-specific), and you're prepared to be more junior on the engineering side than your PhD suggests.

### 4. MD → research / MD-PhD / clinician-scientist

The reverse direction. Practising clinicians moving into research, or MD-PhDs returning to research after clinical training.

- **What changes.** You go from immediate-feedback (the patient improves or does not) to delayed-feedback (the paper is accepted or not). You will write grants. You will compete with full-time researchers who have not been in clinic for a decade.
- **What carries over.** Clinical credibility — the *single* most undervalued asset in translational research. Bedside intuition. Access to patient cohorts. Co-authorship leverage.
- **What you'll need to add.** Computational skill (more than you think, especially if you intend to do imaging), grant-writing fluency, the patience for the academic timeline.
- **The mechanism that fits.** K23 in the US for patient-oriented research; K08 for laboratory-based; Wellcome Clinical PhD and ACL/ACF in the UK; equivalent national programmes elsewhere.

This path makes sense if: you want to keep clinical practice as part of your identity, you have a patient population you understand deeply, and you can secure protected research time (typically 50–80%).

## Skills that transfer

Across all four moves, three skills travel well from neuroimaging:

1. **Pipeline operations.** If you have shipped a multi-stage processing pipeline (Snakemake, Nextflow, or even a disciplined bash + Slurm), you have skills industry calls "data engineering" and academia calls "method development." The [Data engineering](../data-engineering/index.md) section frames this explicitly.
2. **Reproducibility discipline.** Container hashes, version pinning, parameter files, pre-registration. In academia this is the [methods chapter](methods-writing.md); in industry it is MLOps. The vocabulary differs; the practice is the same.
3. **Communication for mixed audiences.** A good neuroimager already talks to clinicians, statisticians, and engineers. That polyglot habit is rare outside academia and is the basis of every senior IC ("individual contributor") and management role.

## Skills you'll need to add

What does not transfer cleanly:

| Skill | Where it bites |
| --- | --- |
| **Product thinking** | Industry. The first month of every industry job is learning to ask "who is the user?" before "what is the model?" |
| **Regulatory** | Clinical, devices, pharma. See [AI/ML → Regulatory](../ai/regulatory.md). |
| **Engineering rigour at scale** | Industry MLE. Pull-request review, test pyramids, semantic versioning, code-style enforcement. |
| **On-call culture** | Industry, especially production MLE. The pager is real; the run-book matters. |
| **Budget and people management** | Faculty. Nothing in a PhD prepares you for hiring. |
| **Lab / clinic politics** | Faculty, MD-research. Local, not generalisable; find a mentor. |
| **Sales / partnerships** | Startup. If you found one, you will spend more time on customer calls than on modelling. |

## CV / resume by direction

The same career deserves different documents for different audiences. The big shifts:

| Direction | Length | Emphasises | Cuts |
| --- | --- | --- | --- |
| **Academic faculty** | 4–10 pages, "CV" | Publications, grants, teaching, mentoring, service | Code repositories often not listed at all |
| **Industry research-scientist** | 2 pages, hybrid CV/resume | Publications + shipped artefacts + impact metrics | Service, most teaching |
| **Industry MLE / DS** | 1–2 pages, "resume" | Engineering work, shipped systems, scale (data volume, users), tech stack | Most publications (unless landmark); replace with bullets on impact |
| **Clinical / hospital research** | 4–8 pages, "CV" | Publications, clinical experience, IRB / regulatory roles, patient-facing trials | Pure-methods work |
| **Startup** | 1 page resume + 1 paragraph "why this" | Shipping, scrappiness, breadth | Almost everything else |

For industry resumes, the bullet pattern that works:

> *Action verb* + *what you built* + *how big* + *what changed* + *with what stack*.

Example, after rewriting:

> "Designed and shipped a diffusion-MRI connectome pipeline (Snakemake, Apptainer, Slurm, dbt, DuckDB) processing 1 200 subjects in 8 hours; reduced per-subject failure rate from 12% to 1.5%; outputs adopted as the lab's reference dataset for two R01s."

A faculty CV bullet for the same work might read: "Lead developer of the connectome processing pipeline used in [grant numbers and resulting publications]."

## Interview formats

By role family:

| Role | Typical formats |
| --- | --- |
| **Faculty** | Chalk talk (45–60 min on future research vision), job talk (60-min seminar on past work), 1:1 meetings, dinner with the committee |
| **Industry research-scientist** | Research talk (45 min), ML coding (1–2 sessions), system design (1 session), behavioural / collaboration |
| **MLE / DS** | Coding (LeetCode-style), ML coding (Pandas, scikit-learn, PyTorch), system design, ML system design, behavioural |
| **Clinical / hospital research** | Clinical case discussions, research presentation, ethics / IRB experience, fit interviews |
| **Startup** | Founders' technical depth-dive, paid take-home or trial week, references-up |

What each format actually tests:

- **Chalk talk.** Whether you can build a five-year, fundable research programme from a whiteboard. Bring three Aims. Defend them.
- **System design.** Whether you can decompose a vague problem ("design a service that scores brain scans for stroke") into components, data flows, failure modes, and SLAs. The [Data engineering](../data-engineering/index.md) section is the relevant primer.
- **ML coding.** Live coding in Pandas / sklearn / PyTorch. Practise data wrangling, splitting, training a small model, and evaluating it — under time pressure, on a real laptop. Practise it cold; nobody is impressed by a wobble.
- **Job talk.** Tells the committee whether they would trust you to teach a course and run a lab. Polish, polish, polish.

## Negotiation realities

**Academia (US tenure-track startup package).** Negotiable items: salary (small range, often capped by institution), startup funds (six to seven figures depending on field), lab space, hard money for 1–2 graduate students, course-release for years 1–2, sometimes summer salary, sometimes spousal hire. Get every promise in the offer letter. "We'll find space" is not space.

**Industry.** Negotiable items: level (most powerful lever), base salary, signing bonus, annual bonus target, equity (RSUs / options) and vesting cliff, relocation, remote / hybrid status. Level is the lever that compounds; a one-level bump usually beats a $20 k base increase over a multi-year horizon. Use [levels.fyi](https://www.levels.fyi) for ranges; assume you're at the 60–70th percentile of your level band.

**Clinical / hospital research.** Negotiable items: protected research time (the single most important number), clinical RVU expectations, startup funds (smaller than basic-science startups), mentorship structure, K-mechanism support from the institution.

**Startup.** Negotiable items: equity, title, scope, vesting cliff, refresh policy, board / advisor influence. Equity is mostly worthless in expectation; price the role on cash + learning + optionality, not on the dream exit.

General rules:

- Never accept verbally; always wait for the written offer.
- Always counter at least once. Most candidates leave 5–15% on the table by accepting first offer.
- Compare offers in writing; companies move when there is a credible alternative, not when there is a feeling.

## Networking honestly

The word "networking" hides a useful practice and a useless one.

**Useless.** Adding LinkedIn connections, attending conference receptions to "be seen," asking strangers for jobs.

**Useful.** Asking a specific person a specific question that they are uniquely qualified to answer, and being prepared to be useful to them later.

The "informational interview" is the formal version of this:

> "Hi — I read your paper on X and your move from academia to Y. I'm thinking about the same move; could I ask you 20 minutes of questions about your transition?"

Most people say yes if the ask is short, specific, and not transactional. Do not pitch yourself; ask. Take notes. Send a thank-you. Update them in six months on what you did.

Conferences worth attending (by relevance, not prestige):

| Conference | Why |
| --- | --- |
| **OHBM** (Organisation for Human Brain Mapping) | The neuroimaging community in one room. Best for faculty / postdoc job market in the field. |
| **MICCAI** | Medical-imaging ML. Best for industry research-scientist transitions and biotech recruiting. |
| **ISMRM** | The MR physics and acquisition community. Best for scanner-vendor and methods-development roles. |
| **NeurIPS / ICML / ICLR** | General ML. Best for the MLE / research-scientist track at big tech. |
| **SfN** | Big tent. Best for translational neuroscience and pharma. |
| **AAN / AHA / AHA-ISC** | Clinical. Best for clinician-scientist transitions. |
| **CNS** (Cognitive Neuroscience Society) | Cognitive neuroscience. Best for psychology-flavoured neuroimaging jobs. |

## When NOT to leave academia (and when NOT to stay)

Cases where staying makes sense:

- You have a question only the long timeline can answer, and you've secured the funding.
- You like the mix of teaching and writing.
- You are within 2 years of tenure and the path is clear.

Cases where leaving makes sense:

- You haven't enjoyed the work for 12+ months and the source isn't a single bad project.
- The salary differential matters for a concrete reason (mortgage, family, debt, caregiving).
- You repeatedly find yourself happier building tools than asking the questions the tools serve.

Cases where leaving is a bad reason:

- A single rejected grant or paper.
- Wanting to "do something more impactful" — a vague pull, not a destination. Resolve it before you move.

## The MD-PhD / clinician-scientist track

The hybrid track is its own animal. The realities:

- **Timeline.** Long. MD-PhD: 7–8 years training, then 3–5 years residency, then fellowship, then K-award, then independent. From undergraduate to independent investigator: ~15–18 years.
- **Protected time.** The single defining variable. 50% research is the minimum for a productive lab; 80% is the goal; below 30% the research disappears under clinical load.
- **Career structure.** Most academic medical centres have explicit physician-scientist tracks (separate from the pure-clinical track). Find them at the negotiation step; do not assume they exist.
- **Funding mechanisms.** K08 (laboratory-focused), K23 (patient-oriented), K99/R00 if you finish the PhD postdoc within the eligibility window. The Burroughs Wellcome PSTP and the Doris Duke Physician Scientist Fellowship are highly competitive boost mechanisms.
- **Failure mode.** Slow drift back into full clinical practice because clinical work has near-immediate reward and research does not. Counter by blocking research time on the calendar and protecting it like a clinic shift.

## One-liner role taxonomy

A short field guide to the role titles you'll meet:

| Role | One-line definition |
| --- | --- |
| **RSE (Research Software Engineer)** | Engineer embedded in a research group; builds and maintains the tools the science depends on. Academic or national-lab affiliation; salary between postdoc and industry MLE. |
| **Research scientist** | Publishes papers and prototypes models at a company; closer to academia than to product. Quarterly publication cadence at best. |
| **MLE (Machine Learning Engineer)** | Ships ML systems in production. More engineering than research. Owns pipelines, deployments, monitoring. |
| **Data scientist** | Variable definition. Often: analytics + experimentation + light modelling. Sometimes: junior MLE. Read the JD carefully. |
| **Applied scientist** | Amazon / AWS title; research-scientist work with explicit product alignment. |
| **Clinical informatician** | Builds and operates clinical data systems (EHR, imaging archives, decision-support tools). Hospital-affiliated; sometimes IT-aligned. |
| **AI / ML scientist in pharma** | Drug-discovery or biomarker modelling; image + multi-omic + clinical-trial data. Roche, Novartis, Pfizer, Genentech, AstraZeneca all hire here. |
| **Medical-device engineer** | Builds software / firmware for cleared / cleared-pending devices. SaMD discipline mandatory. Siemens, GE, Philips, Canon, Insightec, Hyperfine, plus the start-up tier. |
| **Computational biologist** | Wet-lab adjacent; omics-heavy; sometimes imaging-adjacent in spatial transcriptomics. |
| **Solutions / forward-deployed engineer** | Customer-facing engineer at an AI startup; ships custom integrations. Underrated entry path into industry. |
| **Founder / co-founder** | High-variance; pays in optionality. Almost never the right first step out of a PhD. |
| **Product manager (AI / ML)** | Defines what to build, why, and for whom; rarely codes. PhDs land here when they discover they like translating between users and engineers. |

## Where to next

[Grant writing](grant-writing.md) — if the destination is faculty or clinician-scientist, this is the next document you'll write. [Methods writing](methods-writing.md) — the artefact every track produces, and the one most often done badly. [Data engineering → HPC → industry](../data-engineering/hpc-to-industry.md) — the mechanical conversion of HPC habits into industry vocabulary, for the MLE-bound. [AI/ML → Regulatory](../ai/regulatory.md) — required reading for the device, pharma, and clinical-informatics tracks.

## References

1. **NIH — Career Development (K) Awards.** [https://researchtraining.nih.gov/programs/career-development](https://researchtraining.nih.gov/programs/career-development)
2. **NIH — Fellowship (F) Awards.** [https://researchtraining.nih.gov/programs/fellowships](https://researchtraining.nih.gov/programs/fellowships)
3. **Levels.fyi — Industry compensation database.** [https://www.levels.fyi](https://www.levels.fyi)
4. **Burroughs Wellcome Fund — Physician-Scientist Institutional Award.** [https://www.bwfund.org/funding-opportunities/biomedical-sciences/physician-scientist-institutional-award/](https://www.bwfund.org/funding-opportunities/biomedical-sciences/physician-scientist-institutional-award/)
5. **Doris Duke Charitable Foundation — Physician Scientist Fellowship.** [https://www.dorisduke.org](https://www.dorisduke.org)
6. **Pickett CL, Corb BW, Matthews CR, Sundquist WI, Berg JM.** Toward a sustainable biomedical research enterprise. *PNAS.* 2015;112(35):10832–10836. [doi:10.1073/pnas.1509901112](https://doi.org/10.1073/pnas.1509901112)
7. **Alberts B, Kirschner MW, Tilghman S, Varmus H.** Rescuing US biomedical research from its systemic flaws. *PNAS.* 2014;111(16):5773–5777. [doi:10.1073/pnas.1404402111](https://doi.org/10.1073/pnas.1404402111)
8. **Ginther DK, Schaffer WT, Schnell J, et al.** Race, ethnicity, and NIH research awards. *Science.* 2011;333(6045):1015–1019. [doi:10.1126/science.1196783](https://doi.org/10.1126/science.1196783)
9. **Hokanson SC, Grinnell F.** A new model for industry-academic partnerships. *Science.* 2017;357(6356):1078. (For the postdoc-to-industry track.) [doi:10.1126/science.aao2962](https://doi.org/10.1126/science.aao2962)
10. **Ten Simple Rules series.** *PLOS Computational Biology.* See "Ten simple rules for choosing between industry and academia" and related entries. [https://collections.plos.org/collection/ten-simple-rules](https://collections.plos.org/collection/ten-simple-rules)
