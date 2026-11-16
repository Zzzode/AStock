# U0-to-T2 Derivation-Audit Requirements

- Audit: DPSFS-U0T2-v1.
- Status: **requirements only; no U0 snapshot or T2 derivation has been
  generated.**
- Current comparison rows remain a draft probe with q=0.

## Required proof before a T2 freeze

A frozen audit must bind the U0 snapshot and source-manifest hashes, population
query, expected/actual counts, source-revision cut-off, reviewer and freeze
time. For every U0 class it records population, qualified, unqualified and
unresearched counts; accepted data/protocol module state; and coverage status.

For every item it records its parent U0 class, U0 membership key, pre-frozen
selection-rule ID/hash and timestamp, inclusion/exclusion state and reason,
source/lineage references, override ID and review state. Every U0 item needs a
visible state; no item may disappear because it lacks a dossier.

Manual inclusion, exclusion, substitution or class bypass is prohibited. An
operational correction needs an immutable exception ID, evidence, independent
R0/R1/risk approval and a new freeze record.

## Coverage labeling

A result can use an open domestic multi-asset label only when every in-scope U0
class has a reconciled population and an accepted data/replay module, or a dated
independently approved out-of-scope reason. Otherwise it must be labeled
coverage-restricted by included and omitted class. A missing module never means
economic rejection.

No T2 item can appear unless its parent U0 class has an accepted module and the
item passes the frozen rule. The JSON twin defines the exact acceptance tests
and pass threshold.
