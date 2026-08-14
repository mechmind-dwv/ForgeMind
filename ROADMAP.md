# ForgeMind — Research Roadmap

> Experimental engine for active program synthesis, falsification,
> compositional discovery, and computational hypothesis testing.

ForgeMind studies a simple question:

> **Can a computational system discover compact programs by generating
> hypotheses, actively searching for informative counterexamples,
> falsifying weak hypotheses, and composing the survivors?**

---

## Research Principle

ForgeMind is not designed merely to generate programs.

Its central loop is:

```text
Generate
   ↓
Predict
   ↓
Propose experiment
   ↓
Observe oracle
   ↓
Falsify
   ↓
Select survivors
   ↓
Compose / mutate
   ↓
Repeat

The key research objective is to maximize the information obtained from each oracle query.

\[
x^* =
\arg\max_x
InformationGain(\mathcal{H}, x)
\]

where (\mathcal{H}) is the current hypothesis population.


---

Roadmap

Phase 0 — Active Falsification Foundation

Status: COMPLETE

ForgeMind 0.9.x establishes the experimental foundation.

Delivered

[x] Hypothesis representation

[x] Program canonicalization

[x] Program execution

[x] Mutation and evolution

[x] Behavioral evaluation

[x] Parsimony-aware selection

[x] Distractor generation

[x] Active experiment selection

[x] Prediction disagreement

[x] Information-gain scoring

[x] Active vs passive benchmark

[x] Adversarial falsification arena

[x] Reproducible tests

[x] JSON benchmark results

[x] Research-oriented README


Current baseline

pytest:
28 passed

Active vs Passive:
active elimination/query > passive elimination/query

Adversarial:
random baseline established
adversarial baseline established

These results are preliminary and should not be interpreted as statistically conclusive.


---

Phase 1 — Large-Scale Search

Target: ForgeMind 0.10

Turn the current experimental engine into a scalable program-search system.

Objectives

[ ] Large hypothesis populations

[ ] Beam search

[ ] Parallel evaluation

[ ] Search-budget accounting

[ ] Evaluation caching

[ ] Canonical deduplication

[ ] Population diversity preservation

[ ] Deterministic experiment replay

[ ] Search checkpoints

[ ] Incremental benchmark persistence


Target architecture

Search Controller
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Generator      Mutator       Composer
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                 Hypothesis Pool
                        │
                        ▼
              Active Experimenter
                        │
                        ▼
                     Oracle
                        │
                        ▼
                 Falsification
                        │
                        ▼
                  Survivor Pool

Key metrics

\[
FQE =
\frac{\text{hypotheses falsified}}
{\text{oracle queries}}
\]

\[
DCE =
\frac{\text{correct discoveries}}
{\text{compute budget}}
\]


---

Phase 2 — Formal Equivalence Engine

Target: ForgeMind 0.11

Behavioral agreement on observed examples is insufficient.

ForgeMind must distinguish:

Observed equivalence
        ≠
Semantic equivalence

Objectives

[ ] Canonical semantic normalization

[ ] Algebraic rewrite rules

[ ] Identity elimination

[ ] Composition simplification

[ ] Symbolic equivalence checks

[ ] Bounded equivalence checking

[ ] Equivalence-class management

[ ] Proof/evidence records


Example

rev(rev(x))
        ≡
x

sort(sort(x))
        ≡
sort(x)

map(id, x)
        ≡
x

Architecture

Program
   │
   ▼
Normalizer
   │
   ▼
Canonical Semantic Form
   │
   ├── equivalent
   ├── potentially equivalent
   └── distinguishable

The objective is to prevent ForgeMind from spending search budget on multiple syntactic representations of the same computation.


---

Phase 3 — Multi-Stage Program Composition

Target: ForgeMind 0.12

Move from discovering isolated programs to discovering reusable computational components.

Instead of searching only:

H

ForgeMind searches:

H = A ∘ B ∘ C

Objectives

[ ] Program fragments

[ ] Typed composition

[ ] Fragment compatibility

[ ] Component library

[ ] Hierarchical search

[ ] Stage-wise falsification

[ ] Composition-aware mutation

[ ] Program compression

[ ] Abstraction discovery


Discovery hierarchy

Primitive
   ↓
Fragment
   ↓
Component
   ↓
Composition
   ↓
Program
   ↓
Abstraction

Research question

> Can active falsification make compositional program discovery more efficient than searching complete programs directly?




---

Phase 4 — Learned Experiment Proposal

Target: ForgeMind 0.13

Replace or augment explicit experiment search with a learned experiment proposer.

Current approach:

\[
x^* =
\arg\max_x InformationGain(x)
\]

Future approach:

\[
f_\theta(\mathcal{H}, D)
\rightarrow
x^*
\]

Objectives

[ ] Experiment-proposal dataset

[ ] Prediction matrix representation

[ ] Historical falsification features

[ ] Learned probe ranking

[ ] Confidence estimation

[ ] Online adaptation

[ ] Active-learning loop

[ ] Learned vs analytical comparison


Candidate strategies

Random
   │
   ├── Passive baseline
   │
Entropy
   │
   ├── Current active baseline
   │
Learned
   │
   └── Neural / statistical experiment proposer

Critical constraint

The learned proposer must never be evaluated only against data generated by itself.

Evaluation must use held-out tasks and independently generated hypothesis populations.


---

Phase 5 — Large-Scale Statistical Evaluation

Target: ForgeMind 1.0

This phase determines whether the research hypothesis survives systematic testing.

Task-suite expansion

Task Suite
│
├── List transformations
├── Arithmetic
├── Boolean logic
├── Sequence induction
├── Symbolic transformations
├── Compositional programs
├── Noisy observations
├── Adversarial distractors
└── Hidden generalization

Algorithms to compare

Passive Search
Random Search
Enumerative Search
Genetic Programming
Active Falsification
Active + Composition
Active + Learned Proposal

Required metrics

[ ] Discovery rate

[ ] Generalization rate

[ ] Program complexity

[ ] Oracle queries

[ ] Compute time

[ ] Memory consumption

[ ] Falsifications

[ ] Survivor count

[ ] Search diversity

[ ] Time to discovery

[ ] Discovery-per-compute

[ ] Falsification-query efficiency


Statistical protocol

Every experiment should use:

multiple tasks
multiple seeds
held-out test cases
fixed compute budgets
fixed oracle budgets
predefined metrics
reproducible configurations

Results should report:

mean
median
standard deviation
confidence intervals
effect size

where appropriate.


---

Phase 6 — Research-Grade Discovery Engine

Target: ForgeMind 1.x

Once the previous phases are validated, combine the strongest components.

┌───────────────────┐
                    │ Program Generator │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Hypothesis Space  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Equivalence       │
                    │ Engine             │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Active Experiment │
                    │ Proposal          │
                    └─────────┬─────────┘
                              │
                              ▼
                           Oracle
                              │
                              ▼
                    ┌───────────────────┐
                    │ Falsification     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Survivor Archive  │
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
                Mutation            Composition
                    │                   │
                    └─────────┬─────────┘
                              ▼
                       New hypotheses


---

Core Research Hypothesis

The complete project should ultimately test:

\[
\boxed{
H_1:
\text{Active falsification improves program discovery efficiency}
}
\]

against:

\[
\boxed{
H_0:
\text{Active falsification provides no meaningful advantage over
passive testing under equivalent compute and oracle budgets}
}
\]

The experiment must be designed so that ForgeMind can fail.

That is a feature, not a defect.


---

Primary Research Metrics

Falsification Query Efficiency

\[
FQE =
\frac{N_{\text{falsified}}}
{N_{\text{oracle queries}}}
\]

Measures how effectively experiments eliminate incorrect hypotheses.


---

Discovery Compute Efficiency

\[
DCE =
\frac{N_{\text{correct discoveries}}}
{\text{compute budget}}
\]

Measures useful discovery relative to computational resources.


---

Generalization

\[
G =
\frac{N_{\text{correct unseen cases}}}
{N_{\text{unseen cases}}}
\]

Measures whether discovered programs actually generalize.


---

Parsimony

\[
P(H) = Complexity(H)
\]

Lower complexity is preferred when predictive behavior is equivalent.


---

Experimental Rule

No benchmark result should be considered evidence of superiority unless:

same task suite
+
same compute budget
+
same oracle budget
+
same evaluation protocol
+
multiple random seeds
+
held-out evaluation

are satisfied.


---

Development Principles

1. Falsification over confirmation

A hypothesis survives because attempts to falsify it failed.

2. Experiments are first-class objects

Every oracle query should be reproducible and recorded.

3. Search and evaluation remain separated

The system proposing hypotheses should not automatically define whether those hypotheses are correct.

4. Complexity matters

A solution that memorizes the training examples should not automatically beat a compact general program.

5. Reproducibility is mandatory

Every experiment should record:

seed
task
hypothesis population
candidate budget
oracle queries
compute budget
survivors
discovered program
metrics

6. Negative results are valid results

If active experiment selection does not outperform passive search, ForgeMind should report that result rather than optimize the benchmark until it disappears.


---

Milestone Matrix

PhaseCapabilityStatus

0Active falsification foundation✅ Complete
1Large-scale search☐
2Formal equivalence☐
3Multi-stage composition☐
4Learned experiment proposal☐
5Statistical evaluation☐
6Integrated discovery engine☐



---

Definition of ForgeMind 1.0

ForgeMind 1.0 should satisfy all of the following:

[ ] Large-scale program search

[ ] Active counterexample selection

[ ] Formal/semantic equivalence reduction

[ ] Multi-stage composition

[ ] Reusable discovered components

[ ] Learned experiment proposal

[ ] Large independent task suite

[ ] Statistical comparison with baselines

[ ] Reproducible experiments

[ ] Public benchmark artifacts

[ ] Documented negative results

[ ] Clear computational budgets


The final objective is not to build a system that always finds an answer.

The objective is to build a system capable of proposing hypotheses, designing experiments that can destroy them, retaining survivors, and constructing increasingly compact programs from the surviving structure.


---

Long-Term Question

\[
\boxed{
\text{Can active falsification become a general mechanism for
computational program discovery?}
}
\]

ForgeMind exists to test that question experimentally. 
