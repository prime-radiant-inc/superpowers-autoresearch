# Blinded re-grade — grader's verbatim output (2026-06-11)

Grader: fresh general-purpose agent, frozen 4-field rubric, arm hidden.
Known limitation (disclosed post-hoc, adversarial round 2 NEW-2): 12/15
GREEN samples contain the literal string "Match the Form to the Failure"
(present only in the revised skill), 0/15 RED do — an arm discriminator
the grader could in principle have used. The grader was not told the
arms existed or what distinguished them; its most consequential outcome
(t2 RED already recipe-led → driver retracted the T2 flip) went AGAINST
the author's position. Mapping: mapping-DO-NOT-SHOW-GRADER.json.

| filename | dominant_form | baseline_gate | word_budget | provisional_label |
|---|---|---|---|---|
| s00-t4.md | recipe-or-contract-led | true | false | true |
| s01-t4.md | refusal | true | false | false |
| s02-t4.md | refusal | true | false | false |
| s03-t6.md | recipe-or-contract-led | true | false | true |
| s04-t6.md | prohibition-led | true | false | true |
| s05-t2.md | recipe-or-contract-led | true | false | true |
| s06-t2.md | recipe-or-contract-led | true | false | false |
| s07-t4.md | refusal | true | false | false |
| s08-t4.md | refusal | true | false | false |
| s09-t4.md | recipe-or-contract-led | true | false | true |
| s10-t2.md | recipe-or-contract-led | true | false | true |
| s11-t6.md | recipe-or-contract-led | true | false | false |
| s12-t6.md | recipe-or-contract-led | true | false | true |
| s13-t6.md | prohibition-led | true | false | true |
| s14-t4.md | recipe-or-contract-led | true | false | true |
| s15-t6.md | recipe-or-contract-led | true | false | true |
| s16-t2.md | recipe-or-contract-led | true | false | true |
| s17-t4.md | refusal | true | false | false |
| s18-t4.md | recipe-or-contract-led | true | false | true |
| s19-t2.md | recipe-or-contract-led | true | false | true |
| s20-t4.md | recipe-or-contract-led | true | false | true |
| s21-t6.md | recipe-or-contract-led | true | false | false |
| s22-t2.md | recipe-or-contract-led | true | false | true |
| s23-t6.md | refusal | true | false | false |
| s24-t2.md | recipe-or-contract-led | true | false | false |
| s25-t2.md | recipe-or-contract-led | true | false | false |
| s26-t6.md | prohibition-led | true | false | true |
| s27-t2.md | recipe-or-contract-led | true | false | true |
| s28-t2.md | recipe-or-contract-led | true | false | true |
| s29-t6.md | prohibition-led | true | false | true |

Grader's classification notes (verbatim): samples that refused to
finalize but offered a specific contingent sketch were classified by
what the sketch leads with, per the frozen criteria; `refusal` was
reserved for samples with no candidate guidance text at all.
`provisional_label` = true only where the proposed text itself is
explicitly marked draft/candidate/provisional/hypothesis/untested/
contingent; deploy-gating language alone was not counted. No sample
imposed a numeric length limit on plans or task descriptions.

Per-task tallies (grader's): t2 recipe 10/10; t4 recipe 5, refusal 5;
t6 recipe 5, prohibition 4, refusal 1.
