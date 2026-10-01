# Dissemination designs compared

A companion to the [Cardano PubSub CIP](README.md). It is not normative. The CIP specifies one dissemination design, the symmetric relay link, and its Rationale states why; this document sets out the five designs that were analysed before that choice, how each was parameterised, simulated and costed, and the measurements the CIP's numbers rest on. Every figure is generated from [`cells.json`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/cells.json) by the same script that generates the CIP's, which keeps the generated figures consistent with that data file. Prose and tables require separate cross-checks against the experiment write-ups.

The measurements and predictions below use the [adversary the CIP defends against](README.md#the-adversary-this-proposal-defends-against), at the stated reference configurations. The gated M4 reference remains *B* = 500, *k* = 10, *C* = 23. The CIP separately proposes evaluating *B* = 512, *k* = 10, *C* = 24; that candidate and the limitations of its coverage estimate are described under [The serving cap](README.md#the-serving-cap).

## The family

Five candidate designs were analysed before one was chosen, named M1 to M5:

<div align="center">
<a name="table-1" id="table-1"></a>

| Design | Built from |
| :--: | --- |
| M1 | The push primitive: a node forwards to *F* targets it drew |
| M2 | M1 with the direction inverted: a node draws *RF* forwarders |
| M3 | M2 plus *s* − 1 seeding links carrying only their owner's publications |
| M5 | M1 and M2 run at once, as *k*<sub>in</sub> and *k*<sub>out</sub> tuned separately |
| M4 | M5 with the two link sets merged into one bidirectional link |

<em>Table 1: Structural comparison of the dissemination designs</em>

</div>

The Specification selects M4, the symmetric relay link. The five-design comparison begins with gates and admission limits disabled. Later sections examine gated M3 and M4 reference configurations. These comparisons provide evidence for the proposed design; the candidate M4 profile, including its *B* = 512 bucket count, still needs the validation described under [Sizing the parameters](README.md#sizing-the-parameters).

## What is measured, and by what

Each epoch the protocol derives a dissemination topology for every topic separately: each node registered on a topic is assigned a bounded set of peers there, and the assignment stands for the whole epoch. A node subscribed to several topics draws independently on each, which is why [what a node pays](#per-node-cost-against-subscriptions) multiplies its cost by the number of subscriptions. Nodes following the protocol are *honest*; the rest are the silent adversary set out above. On any topic some nodes publish and others subscribe.

The guarantee is a property of the drawn topology, not of an individual message: a draw is **good** when every honest publisher reaches every honest subscriber, and **bad** when some publisher is cut off for the whole epoch. The criterion is all-or-nothing because an average hides the failure that matters: 99.99 % delivery may be a tolerable trickle of losses or one publisher silenced completely. The central quantity is the probability that a draw is bad, written *p*<sub>bad</sub>.

Two observations help interpret a bad draw.

- **A bad draw need not cause a failed publication.** In the simulated forwarding model, a topology can fail the every-publisher criterion even if the publisher that cannot reach everyone sends no message. The probability of a bad topology therefore bounds topology-induced delivery failure, not losses or delays from a real transport.
- **Failure severity varies.** The [recorded failures](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/cells.json) usually miss one subscriber, or all subscribers when the publisher is isolated. Some sampled failures miss two or three subscribers. These observations do not bound the loss a bad topology can cause.

**Everything below is a way of estimating *p*<sub>bad</sub>, a cost paid to lower it, or a condition under which it rises.**

The ungated coverage work uses two independently built instruments.

- **Analysis** derives, for each design, a closed-form *coverage law* predicting *p*<sub>bad</sub> from the network size, the adversarial fraction and the design's own parameters, with its own simulator to check the law wherever sampling is feasible. The symmetric relay link's is stated under [The coverage law](README.md#the-coverage-law).
- **Measurement** builds populations of the reference implementation's own node logic, the same code the node runs, driven by a deterministic scheduler in place of a network, then disseminates real messages and counts what happens.

A closed form can approximate the wrong model; an implementation can faithfully run a subtly wrong protocol. They fail in unrelated ways, so **their agreement is the evidence offered here**, not either result alone. Every measurement is reproducible byte-for-byte from a tool commit, a configuration and a master seed.[^reproduction]

The gated admission experiments use the reference-node instrument. Their closed forms were independently re-derived and reproduced in review; this is a separate analytical check, not a second implementation of the gated protocol.[^synthesis]

## Performance metrics

A design is characterised here by four things: how often a draw fails, what it costs to run at that failure rate, how many forwarding hops reach every honest subscriber, and how much honest downtime it tolerates while meeting the failure target. Table 2 records the evaluation settings.

<div align="center">
<a name="table-2" id="table-2"></a>

| Constant | Value | What it is | Where it comes from |
| --- | :--: | --- | --- |
| *N* | 20,000, and 4,000 | The registered population on a topic | 4,000 and 20,000 are the main experimental populations; pool-count observations are reported separately[^sponumbers] |
| [*μ*](README.md#param-mu) | 0.2 | Fraction of registered nodes assumed adversarial | An assumption about who registers and what registration costs them, not a measurement. Swept from 0.20 to 0.40 to check the laws hold across it[^musweep] |
| [*δ*](README.md#param-delta) | 10⁻⁴ per epoch | The failure probability a configuration is sized to meet | A choice, and one that cannot be read independently of epoch length |
| [*p*](README.md#param-p) | 0 | Honest downtime during this section's comparisons | Every design is priced with all honest nodes up; downtime enters as a shift in *μ*, and what each design absorbs is its churn budget, the last column of [Table 4](#table-4) |
| [*k*](README.md#param-k) | varies by design | Peers a node picks per topic per link kind | The knob each design is tuned by; the comparison holds *δ* fixed and lets *k* differ |

<em>Table 2: The constants this section is measured at</em>

</div>

**The adversarial fraction and failure target are assumptions rather than results.** [*μ*](README.md#param-mu) and [*δ*](README.md#param-delta) are assumptions about the deployment; every failure probability in this document is conditional on them, and both are posed as open questions in the [CIP](README.md#open-questions). A reader who disagrees with either should read the figures as shape rather than values.

Every design's coverage law can be [evaluated interactively](https://pubsub.cardano-scaling.org/experiments/compare-designs/) with *μ*, *N* and *δ* as controls, and the [parameter surface](https://pubsub.cardano-scaling.org/experiments/parameters/) applies the Specification's sizing rules to a topic size, a target and a downtime rate.

<div align="center">
<a name="table-3" id="table-3"></a>

| Category | Metric | Measurement |
| :--: | --- | --- |
| Coverage | Epoch failure probability, *p*<sub>bad</sub> | Probability that a drawn epoch topology fails to carry some honest publisher's messages to every honest subscriber |
| Cost | Transmissions per publication, *m* | Honest-to-honest message copies sent per published message, duplicates included |
| | Deliveries per node, *c* | Copies of each published message received by an average honest node, duplicates included |
| | Links per node, *d* and *d̂* | Links held for the whole epoch, mean and maximum, counting a node's own picks and the links others opened to it |
| Forwarding depth | Hops to full coverage, *h*<sub>full</sub> | Forwarding depth at which the last honest subscriber receives |
| Resilience | Churn budget, *p*<sub>max</sub> | Largest honest downtime fraction for which a deployed configuration still meets *δ* |

<em>Table 3: Performance metrics</em>

</div>

**_Churn budget._** Reading a design's own [coverage law](README.md#the-coverage-law) at the shifted fraction, the budget is the largest downtime a configuration absorbs while still meeting the target:

$$p_\text{max} = \max \{\, p : p_\text{bad}(\mu + p(1-\mu)) \le \delta \,\}$$

Downtime relates to the drop-out rate and the epoch length by [*p*](README.md#param-p) = 1 − e<sup>−λ·T</sup>, which is why *p*<sub>max</sub> bounds epoch length as well as resilience.

## The five designs

Every design starts from the same constraint: a node may not choose its peers, so it draws them at random from the topic's registered population and carries messages over the links that draw opens. The only knob is how many peers a node draws: the [pick count](README.md#term-pick-count), written *RF* for relay links and *F* under M1. In every design below it is what trades cost against *p*<sub>bad</sub>. Where a design adds a second link kind for a node's own publications, those picks are counted separately: M3 opens *s* − 1 of them, its *s* counting the intended initial holders rather than the links opened. This subsection sets out each mechanism and the failure it leaves open; [Table 4](#table-4) prices the designs, and only the pick budget is quoted here, because its fall is the derivation.

<div align="center">
<a name="figure-1" id="figure-1"></a>

![One node's links under M1](images/model-m1.svg)

<em>Figure 1: One node's links under M1</em>

</div>

**M1 is the smallest thing that works.** One link kind, one direction: a node draws *F* targets from the topic's peers, the downstream layer of [Figure 1](#figure-1), and forwards everything it holds to them, its own publications included. Its upstream layer it does not control: those links are other nodes' draws that happened to include it. It meets [*δ*](README.md#param-delta) = 10⁻⁴ at *F* = 24, the largest pick count in the field. The direction also fixes which failure a node can suffer. The chance that all *F* of its own picks land adversarial is [*μ*](README.md#param-mu)<sup>*F*</sup>, nothing at all at these parameters. The failure that remains is a node whose upstream layer is empty, one no honest peer happened to draw, and such a node cannot **receive**.

<div align="center">
<a name="figure-2" id="figure-2"></a>

![One node's links under M2](images/model-m2.svg)

<em>Figure 2: One node's links under M2</em>

</div>

**M2 inverts the direction, and that is all it does.** A node draws *RF* forwarders and receives from them, the upstream layer of [Figure 2](#figure-2): it controls what it hears, not who hears it. The surviving failure is the mirror image, a publisher nobody drew: its downstream layer is empty, and it cannot be **heard**. An isolated publisher need not cause a failed publication if it sends nothing during that epoch. This is the distinction between a bad topology and a failed publication discussed above.

On cost, inversion buys nothing. M2 meets the same target at the same pick count, *RF* = 24, matches M1 on every cost axis to three figures. **Choosing between the primitives is a choice of which failure to suffer, not a cost decision, so the way out of twenty-four picks has to be structural.**

**Two structures cover both failure directions, and they differ only in what the second link kind carries.** A pull node is silent because nothing pushes on its behalf; giving it push links back closes that.

<div align="center">
<a name="figure-3" id="figure-3"></a>

![One node's links under M3](images/model-m3.svg)

<em>Figure 3: One node's links under M3</em>

</div>

**M3 carries only its owner's own publications.** A node keeps M2's *RF* relay links and adds *s* − 1 standing initiation links, the dashed links of [Figure 3](#figure-3). Over these it hands each of its own messages to its intended initial holders, rather than waiting to be picked. The specialisation is what makes it cheap: a seeding link carries one node's traffic instead of the whole topic's, so the relay fanout can be smaller at the same coverage. At (*RF* = 13, *s* = 7) the budget is 19 picks against M2's 24, and the specialisation makes M3 the cheapest design in the field on bandwidth. What it does not buy is state: 12 of its links carry only their owner's publications, cheap to run but still connection slots to provision and still exposed to churn.

<div align="center">
<a name="figure-4" id="figure-4"></a>

![One node's links under M5](images/model-m5.svg)

<em>Figure 4: One node's links under M5</em>

</div>

**M5 carries everything.** A node opens *k*<sub>in</sub> inbound and *k*<sub>out</sub> outbound links, both general-purpose and both its own draws, as [Figure 4](#figure-4) shows, and tunes the two counts independently. At (9, 8) that is 17 picks against M2's 24, and every cost figure improves together: **covering both failure directions is cheaper on every axis than covering either alone.**

The fork is a genuine trade: M3 and M5 land at the same failure probability and the same churn budget, so specialising the second kind buys bandwidth where generalising it buys connections, and neither dominates. Both are still directional: the floor is *μ*<sup>*k*</sup>, with nothing to rescue a node whose picks all failed.

<div align="center">
<a name="figure-5" id="figure-5"></a>

![One node's links under M4](images/model-m4.svg)

<em>Figure 5: One node's links under M4</em>

</div>

**M4 merges M5's two link sets into one.** M5's best split, 9 and 8, is one link from symmetric, which suggests its two sets do the same work. Under M4 a node draws *RF* peers and opens one link to each, established once for the pair rather than once per direction; in [Figure 5](#figure-5) the layers differ only by who opened the link, and every arrow points both ways. Every message that verifies is flooded on all the node's links for the topic except the one it arrived on, its own publications included, so there is neither a second link kind nor a second count. The failure left open needs both directional failures at once: every peer the node drew adversarial *and* no honest node having drawn it, since a link an honest picker opens carries traffic both ways. One pick buys both directions, so the budget is *RF* = 9 against M5's 17. [Why the symmetric design](#the-two-candidates-under-the-admission-rules) prices the conjunction and the downtime it buys.

<!-- make_cip_figures.py --check checks generated SVG freshness.
     check_cells_against_docs.py separately checks transcribed data against write-ups. -->

## Agreement between analysis and simulation

The initial comparison checked the laws against the measurement framework in 23 cells, spanning all five designs, two and a half orders of magnitude in *p*<sub>bad</sub>, and two network sizes: *N* = 4,000, above any stake-pool population yet registered, and *N* = 20,000 as headroom above it. Each initial cell drew between 150 and 30,000 topologies and counted the bad ones, comparing each count with what that design's [coverage law](#what-is-measured-and-by-what) predicts. Figure 6 also includes two independent deep-tail reruns at existing parameter configurations: 170,000 draws for M3 and 110,000 for M4, giving 25 baseline datasets in total.

The designs also nest, which gives a check that costs nothing. M1 and M2 are the two halves of M5: switching off M5's inbound links leaves pure push, switching off its outbound links pure pull. M3 at *s* = 1 is M2 by construction.[^boundaries] M5 configured at those boundaries must therefore reproduce M1's and M2's results exactly, and any discrepancy is a defect in the analysis or the implementation, not a property of the protocol.

In the figure below each point is one measured sample, its horizontal position the failure rate the law predicts, its vertical the rate observed. A count from finitely many draws scatters around the true rate, so the **bar** through each point spans the rates that would plausibly produce it, at 95 % confidence for that sample's own size;[^wilson] a law inside the bar is consistent with the measurement. The **shaded band** repeats that interval at the size most samples share, as context for the eye. Both axes are logarithmic; the configurations range from failing in roughly one epoch in three hundred to almost every epoch. Filled marks are the configurations above, hollow ones a further 35 measured under honest downtime, described below.

<div align="center">
<a name="figure-6" id="figure-6"></a>

![Measured against predicted epoch failure probability](images/coverage-validation.svg)

<em>Figure 6: Measured against predicted epoch failure probability</em>

</div>

The hollow marks are the same check run under honest downtime. A design's churn budget cannot be sampled directly, since resolving a rate near 10⁻⁴ takes 10⁵ to 10⁶ draws per churn level; what can be tested is the reduction beneath it, downtime entering as a shift in the adversarial fraction, at parameters where failures are frequent enough to count. **In 38 of 40 configurations**, spanning the five designs, downtime to 35 % offline and the two configurations this proposal names, the shifted-fraction prediction lands inside the measurement's 95 % interval, two misses being what forty comparisons at that confidence are expected to produce; the sweep carries the reduction from an adversarial fraction of 0.20 out to 0.48.[^churn] The budgets in [Table 4](#table-4) follow from the laws so validated.

The comparison points lie below the sampled failure rates. Filled marks in Figure 7 are observed rates at weaker configurations; hollow marks are model predictions for the ungated comparison points. The dashed spans show the extrapolation. The CIP separately presents the gated M4 reference experiment and its limitations.

<div align="center">
<a name="figure-7" id="figure-7"></a>

![Sampled failure rates and predicted ungated comparison points for five designs](images/measured-vs-proposed-all.svg)

<em>Figure 7: Sampled failures and predicted ungated comparison points</em>

</div>

## Cost at each design's configuration

Every design is shown at the configuration this proposal names for it, at *N* = 20,000 and [*μ*](README.md#param-mu) = 0.2, and every table and figure in the Rationale carries the same configurations. For M1, M2 and M5 that is the cheapest one meeting [*δ*](README.md#param-delta) = 10⁻⁴. For M3 and M4 it is the preferred split rather than the published one: each has a configuration at the same or nearly the same cost that absorbs several times the downtime, and carrying the superseded ones would mean comparing at parameters the rest of this proposal argues against.

<div align="center">
<a name="table-4" id="table-4"></a>

| Design | Parameters | *p*<sub>bad</sub> | Deliveries per node | Links, mean | Links, busiest node | Mean full-coverage hops | Downtime absorbed |
| :--: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| M3 | RF = 13, *s* = 7 | 4.4 × 10⁻⁵ | **10.4** | 38.0 | 64 | 5.5 | 2.17 % |
| M4 | RF = 9 | 6.1 × 10⁻⁶ | 13.4 | 18.0 | 37 | 5.0 | 7.43 % |
| M5 | (9, 8) | 4.4 × 10⁻⁵ | 13.6 | 34.0 | 58 | 5.0 | 2.18 % |
| M1 | *F* = 24 | 7.3 × 10⁻⁵ | 19.2 | 48.0 | 75 | 5.0 | 1.76 % |
| M2 | RF = 24 | 7.3 × 10⁻⁵ | 19.2 | 48.0 | 75 | **4.8** | 1.70 % |
| | | | | | | | |
| **M4 gated reference** | *RF* = 10, *B* = 500, *C* = 23 | **5.1 × 10⁻⁶** | **13.0** | **17.5** | **33** | 5.0 | **7.57 %** |

<em>Table 4: Cost at each design's configuration</em>

</div>

The first five rows are ungated, at the configurations the coverage models were evaluated at, and they are not equally safe: the *p*<sub>bad</sub> column spans an order of magnitude, so a cost difference between rows at different failure rates is not by itself a verdict. The last row is the gated reference experiment at *B* = 500; the CIP now specifies *B* = 512 and identifies its rerun as outstanding. It is not comparable column-by-column, but given so the proposal's own numbers appear beside the field it was chosen from. Bold marks the best value in each column. The cost and hop-count columns are measured (see the reproduction note); the *p*<sub>bad</sub> column is read off each design's coverage law, for the reason [Limits of this evidence](README.md#limits-of-this-evidence) gives. The busiest-node column is the largest logical-link count any single honest node held over the sampled graphs *at that row's configuration*. The ungated rows are sample extremes rather than bounds. The gated reference's 33 also reaches its admission-derived ceiling, *k* + *C*.[^degrees] Mean full-coverage hops span 4.8 to 5.5 here. A separate historical study reports depth distributions at older M3 and M4 configurations.[^depth]

**M3's split.** The budget of 19 divides between relaying and seeding in several ways, and the published choice of (RF = 12, *s* = 8) is not the best of them. With *s* − 1 seeding links the budget is *RF* + (*s* − 1), so 12 + 7 and 13 + 6 both come to 19, and the split (RF = 13, *s* = 7) holds that same budget and the same 38 links. For 0.8 further deliveries per node it buys a factor of four in downtime tolerance and a halved failure probability, and it is the split every table and figure in this proposal carries; a reader meeting the published split in the earlier literature should expect M3 to look stronger on bandwidth and markedly weaker on the other three axes. The budgets in the last column are read off the laws rather than observed: the churn experiment establishes that the shifted-fraction reduction holds, not the budget values. The measurements sit slightly above their predictions, and the excess pools onto M3 alone, matching a separate finding that M3's law is mildly optimistic wherever its pick count is small;[^finiten] suggestive rather than established, and conservative either way, since it would make M3's budget smaller rather than larger.[^churn]

**Budgets as margins.** A budget for downtime is equally a margin above the adversarial fraction assumed: against the 0.2 assumed, M3 at (13, 7) still meets the target at *μ* = 0.217 and M4 at RF = 9 at *μ* = 0.259. M3's narrower margin is structural rather than incidental: its bandwidth advantage comes through a small number of dedicated seeding links, and a mechanism that is cheap because it is small has the least margin when part of it stops responding.

## The four-way trade-off

The figure below compares measured bandwidth, mean logical links and mean forwarding depth with predicted honest downtime tolerance. No design is best on all four at the compared configurations.[^axes]

<div align="center">
<a name="figure-8" id="figure-8"></a>

![Four-way trade-off between the surviving candidates](images/tradeoff-radar.svg)

<em>Figure 8: Four-way trade-off across the non-dominated designs</em>

</div>

Each contender is drawn at its best parameters rather than its published ones. The published operating points were all chosen as the cheapest configuration meeting the failure target, and re-searching the two contenders against the validated laws shows what that rule costs: M3's re-split is set out under [Table 4](#table-4), and the equivalent step for M4, RF = 8 to RF = 9, buys seven times the churn budget for 1.6 further deliveries per node and two further connections. M1, M2 and M5 remain at their cheapest-meeting-target points.

At those parameters M4 uses less bandwidth, holds fewer links and absorbs more predicted downtime than M5, while tying it on mean full-coverage hops. M5 likewise improves three axes over M1 and ties it on hops. Both are therefore Pareto-dominated: another design is no worse on any plotted axis and better on at least one. They are drawn muted, with their shapes inside or on the boundary of a contending design. Three remain. The figure carries its own reading key; the size of a shape is not a score.

**At these configurations, M4 has the fewest mean logical links and the highest predicted downtime tolerance. M2 has the lowest mean full-coverage hop count; M3 uses the least bandwidth.**

> [!IMPORTANT]
> The general form governs the parameter choice as much as the design choice: **within this family, efficiency is bought with margin.** A configuration tuned to sit just inside the failure target is, by construction, the one with least room to absorb anything the model did not anticipate. That is a property of the rule used to choose parameters, not of any mechanism, which is why M3's brittleness disappears under a different split of the same budget rather than requiring a different design.

## The two candidates under the admission rules

The ungated comparison motivates evaluating M3 and M4 with gates and admission budgets. The following results concern the stated reference configurations and the evaluated gate and admission rules. M1, M2 and M5 were not re-measured under those conditions. Small topics may use the CIP's [gate-off rules](README.md#small-topics).[^synthesis]

<div align="center">
<a name="table-5" id="table-5"></a>

| | M3 gated reference | M4 gated reference (*B* = 500) |
| --- | ---: | ---: |
| Parameters | *RF* = 13, *s* = 7, *B* = 769 | *RF* = 10, *B* = 500, *C* = 23 |
| Predicted failure probability | 5.8 × 10⁻⁵ | **5.1 × 10⁻⁶** |
| Predicted honest downtime absorbed[^m3budget] | 1.58 % | **7.57 %** |
| Expected peers reachable per identity | 52 | **40** |
| At M4's expected eligible reach | **no pick count meets the target** | 5.1 × 10⁻⁶ |
| Seams carrying a gate and a cap | 2 | **1** |

<em>Table 5: The two candidates under the admission rules</em>

</div>

**The comparison metric is expected eligible reach per identity.** The reach figures describe how many peers one identity is expected to be eligible to contact under the evaluated gates. They do not establish the number of identities needed to isolate a chosen node; that depends on the attacker's knowledge, strategy and required success probability. The [CIP's adversary model](README.md#the-adversary-this-proposal-defends-against) distinguishes these questions. The comparison holds this eligibility metric fixed and evaluates the resulting coverage estimates.

**One eligibility decision per pair, or separate decisions per direction.** Under the evaluated M4 gate, one identity is eligible to contact an expected (*N*<sub>T</sub> − 1)/*B* peers. Under the evaluated M3 relay gate, the two directional decisions give approximately 2(*N*<sub>T</sub> − 1)/*B*. Equal bucket counts therefore do not give equal expected eligible reach. At the reference settings, M3's *B* = 769 gives about 52 peers and M4's *B* = 500 gives about 40.[^seam]

**Either endpoint can provide an honest connection.** Under the baseline model without admission refusals, an M4 node is isolated when it selects only adversarial peers and no honest eligible peer selects it. A link selected by either endpoint can avoid isolation. In the ungated approximation this gives [*μ*](README.md#param-mu)<sup>*k*</sup>e<sup>−*k*(1−*μ*)</sup>. M3's hearing failure has no equivalent rescue for every publisher: its seeding links carry only their sender's own publications. The gated estimates must also account for the eligible-pool distribution, and a binding cap requires the [admission-refusal estimate](README.md#including-admission-refusals).

**Comparison at equal expected eligible reach.** E20's model evaluates M3 at *B* = 1,000 to match M4's expected reach of 40 peers per identity. At *N* = 20,000 and *μ* = 0.2, M3's best predicted failure probability is approximately 1.8 × 10⁻³, above the 10⁻⁴ target. Increasing the pick count cannot remove the chance of having no honest eligible peer in the receiving pool under this model. In a separate comparison where failures were frequent enough to count, at expected eligible reach 32, M3 failed 17 of 400 runs and M4 failed none of 400. The zero count does not measure a zero failure probability.[^synthesis]

**Predicted downtime tolerance.** At the compared ungated configurations, M3's predicted honest downtime budget is 2.17 % and M4's is 7.43 %. At the gated reference configurations the budgets are 1.58 % and 7.57 % respectively. These estimates depend on the stated configurations and the [downtime assumptions](README.md#limits-of-this-evidence).

**Interpreting the comparison.** The compared configurations retain a cost trade-off: M3 uses less traffic and M4 fewer logical links. The coverage and downtime estimates support selecting M4 within this family and these assumptions. Deployment choices still need to account for their workloads and delivery requirements.

Mean full-coverage hop count measures forwarding depth in the simulations. It does not establish a wall-clock delivery deadline. Establishing elapsed delivery times requires transport measurements.

## Per-node cost against subscriptions

Both measured costs are per topic, and a node that subscribes to several pays for each; scaling the measured figures is arithmetic over deployment assumptions. For one-kilobyte messages arriving once a second on each topic:

<div align="center">
<a name="table-6" id="table-6"></a>

| Topics a node subscribes to | M3 (13, 7) | | M4 (RF = 9) | |
| :--: | ---: | ---: | ---: | ---: |
| | Ingress | Mean links | Ingress | Mean links |
| 1 | **83 kbit/s** | 38 | 107 kbit/s | **18** |
| 5 | **416 kbit/s** | 190 | 536 kbit/s | **90** |
| 10 | **832 kbit/s** | 380 | 1.1 Mbit/s | **180** |
| 25 | **2.1 Mbit/s** | 950 | 2.7 Mbit/s | **450** |

<em>Table 6: Per-node cost against topics subscribed, at 1 kB and one message per second</em>

</div>

The table shows mean [logical link](README.md#term-link) counts, scaled by the number of subscriptions. Individual nodes may hold more or fewer links. Multiple links to the same peer can [share a transport connection](README.md#link-establishment), reducing the connections needed. These figures do not specify a maximum connection requirement.

At the stated message rate and size, mean ingress and logical link counts scale with subscriptions. At twenty-five topics, M3 averages 950 logical links per node and M4 averages 450. Each transport connection carries buffers, keepalives and supervision, so provisioning also needs to account for nodes above the mean and how many links can share a connection.

The [pick count](README.md#the-relay-link-and-the-pick-count) is specified per topic, so increasing it also adds cost across subscriptions. A deployment sizes it against both its downtime assumptions and its subscription profile.

A node subscribing to *T* topics, each drawing *d* links from a population of *P*, expects to hold (*P*−1)(1−(1−*d*/(*P*−1))<sup>*T*</sup>) distinct peers, and the saving is whatever separates that from *dT*. At *N* = 20,000 and twenty-five topics, this estimate gives M3 929 distinct peers for its 950 mean logical links, and M4 445 for its 450. Sharing one transport connection per peer would therefore reduce the mean connection counts by about 2 % and 1 % respectively under these assumptions.

It bites where the population is small: on a topic drawing from three thousand participants, the same twenty-five subscriptions save M3 14 % and M4 7 %; at five hundred, 55 % and 33 %. Small topics are where connection count stops separating the designs, and the [CPS](https://github.com/input-output-hk/pubsub/blob/main/docs/cps/README.md) use cases include some.

## Isolation risk and epoch length across the designs

The same laws that give *p*<sub>bad</sub> give the risk borne by one named node, and the churn budget of each design bounds the epoch it sustains. Both are tabulated for every design here; the CIP carries the symmetric link's rows only.

**Repeated isolation.** Each epoch gives a subscriber another opportunity to connect to honest peers. If its isolation probability is *q* in each epoch and successive outcomes are independent, isolation in both of two specified consecutive epochs has probability *q*². Different peer selections can still leave the same subscriber isolated; the same set of peers need not recur.

Table 7 illustrates this at the ungated comparison configurations, *N* = 20,000 and [*μ*](README.md#param-mu) = 0.2:

<div align="center">
<a name="table-7" id="table-7"></a>

| | M3 (13, 7) | M4 (RF = 9) |
| --- | ---: | ---: |
| One named node cut off in a given epoch | 2.7 × 10⁻⁹ | 3.8 × 10⁻¹⁰ |
| The same named node cut off in both of two specified consecutive epochs | 7.5 × 10⁻¹⁸ | 1.4 × 10⁻¹⁹ |
| *Some* node cut off, network-wide | 4.4 × 10⁻⁵ | 6.1 × 10⁻⁶ |

<em>Table 7: Per-epoch isolation risk, per node and network-wide</em>

</div>

The first row gives a named node's probability *q*. The second is the joint probability *q*² of isolation in two specified consecutive epochs, assuming independent outcomes. Conditional on already being isolated, the next epoch's probability remains *q*. The third row concerns any honest node in the network. These are predictions for the ungated comparison points, not the proposed gated configuration.

Rotation gives another opportunity to reconnect; it does not impose a maximum isolation duration. Correlated outages and beacon failures can invalidate the independence assumption. See the CIP's discussion of recovery and retention.

Links are not repaired within an epoch, so the longer one runs the more of the population has dropped out by the time the topology is judged. Setting the accumulated downtime equal to a design's churn budget gives the longest epoch it sustains: with *λ* the rate at which a node drops out, *T* = −ln(1 − *p*<sub>max</sub>) / *λ*.

**A chosen epoch length implies a reliability requirement.** For a candidate epoch, each design needs the population to depart no more often than:

<div align="center">
<a name="table-8" id="table-8"></a>

| Proposed configuration | 1 hour | 6 hours | 1 day | 5 days |
| :--: | ---: | ---: | ---: | ---: |
| **M4 RF = 9** | **13 hours** | **3 days** | **13 days** | **2 months** |
| M5 (9, 8) | 2 days | 11 days | 45 days | 7 months |
| M3 (13, 7) | 2 days | 11 days | 46 days | 7 months |
| M1 *F* = 24 | 2 days | 14 days | 56 days | 9 months |
| M2 RF = 24 | 2 days | 15 days | 58 days | 10 months |

<em>Table 8: Departure interval required per epoch length</em>

<em>Every row is computed from that design's churn budget by the relation above, none separately measured; the budgets themselves are read off the coverage laws rather than sampled, for the reason [Agreement between analysis and simulation](#agreement-between-analysis-and-simulation) gives.</em>


</div>

Shorter epochs provide more frequent opportunities to reconnect. The table gives the mean departure intervals required by the dropout model, not measured participant availability.

The interval between fresh, unbiasable randomness values is one constraint on epoch length. The [beacon](README.md#term-beacon) design remains open; a source based on the Cardano ledger epoch nonce would provide fresh values only at the ledger's epoch cadence.

A faster beacon may permit shorter epochs, but epoch length must also accommodate snapshot timing and topology formation. Whether this leaves enough room within the predicted downtime budget depends on the participants' departure rate. These inputs still need validation; choosing a faster beacon alone does not establish a suitable epoch length. See [How long an epoch may be](README.md#how-long-an-epoch-may-be).

## Sensitivity to the adversarial fraction

**The adversarial fraction is chosen, not derived.** The designs are sized at a single [*μ*](README.md#param-mu), an assumption about who registers and what registration costs them. The laws have since been measured from 0.20 to 0.40 natively and to 0.48 through churn, so *reading* a design off its law at another fraction is evidence-backed;[^musweep] *picking* the fraction is not, and the designs do not degrade at equal rates as it varies ([Figure 9](#figure-9)): moving right assumes a more hostile registry, moving up is a worse chance that an epoch's draw cuts some honest node off, and each curve is one design held at its proposed configuration, out of the target once it crosses the dashed line. The horizontal distance from *μ* = 0.2 to a design's crossing is its margin for that assumption being wrong.

<div align="center">
<a name="figure-9" id="figure-9"></a>

![The proposed configurations as the adversarial fraction varies](images/mu-sensitivity.svg)

<em>Figure 9: The proposed configurations as the adversarial fraction varies</em>

</div>

## Where the laws lose accuracy

**Model error varies by design and configuration.** Pooled across the ungated comparisons, the measurements sit about 2 % above the laws, two effects of opposite sign nearly cancelling: M3's law optimistic at low pick counts, M2's pessimistic on small populations.[^finiten] This average is not an error bound for the proposed gated configuration. Some candidate bucket-table entries lie very close to the failure target, so deployment validation needs to establish an allowance for model error and confirm that the chosen parameters still meet the target, as the [CIP's sizing limits](README.md#including-admission-refusals) explain.

## Alternatives to the specified rules

### The either-direction rule

The evaluated hash baseline sorts a pair by identity bytes and computes one eligibility decision. The comparison predicate evaluates each direction separately: each node selects from its own eligible peers, and a pair is eligible for a link if either direction passes. These experiments inform the eligibility rule; the final cryptographic construction remains [open](README.md#the-verifiable-gate).

A pair passes with probability 2/*B* − 1/*B*² rather than 1/*B*, assuming independent directional draws. For large *B*, matching the eligible-pair density therefore requires approximately doubling *B*. Equal eligibility density does not establish equal coverage after selection and admission.

Both predicates use the same [admission budget](README.md#the-serving-cap) and crossing exemption. A node's own selections do not consume its local budget, but a selected peer may refuse a new request when its own budget is exhausted. Crossings remain exempt under both predicates.

In E19 at *N* = 4,000, *k* = 16, *B* = 50, *C* = 16 and 800 adversarial identities, the directional predicate produced fewer mutual selections and more refused honest requests: 5.64 per victim against 3.19 for the unordered pair. Those cells used the same bucket count, giving the predicates different eligible reach; the result does not establish a general doubling of refusals.[^symgate]

### Directional admission anchors

These historical M2 measurements illustrate how an admission limit can reject honest connection requests. They do not establish numerical cap or headroom thresholds for M4. The CIP specifies M4's [admission semantics and provisional sizing recipe](README.md#the-serving-cap); the chosen profile still needs validation.

In the M2 flooding experiment at *N* = 4,000, *B* = 125 and 20 % adversarial identities, raising the cap from 20 to 32 reduced the share of honest nodes losing at least one request to a full acceptor from 30.6 % to 0.36 %. More adversarial links were admitted too: the coverage benefit came from refusing fewer honest requests.[^gate]

## Method notes

[^reproduction]: Reproducing the measurements. Each result is identified by a tool commit, a sweep configuration, and a master seed; those three reproduce the output files byte-for-byte, independently of how many runs execute in parallel. All three are recorded per configuration in [`cells.json`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/cells.json), which is also the source the figures in this section are generated from; the configurations themselves are under [`configs/experiments/`](https://github.com/input-output-hk/pubsub/tree/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/configs/experiments) and the per-design comparisons, including the statistical conventions, under [`docs/experiments/`](https://github.com/input-output-hk/pubsub/tree/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments).

[^sponumbers]: Stake-pool counts read from Blockfrost over epochs 210 to 646: at no epoch were more than 2,696 pools registered at once, and the pools holding 99 % of stake never numbered more than 899.

[^musweep]: The adversarial fraction as a swept axis. Twenty-nine cells across five designs, μ from 0.20 to 0.40, two network sizes, 116,000 draws; the law falls inside the measurement's interval in 24 of them, mean standardised deviation +0.36, pooled ratio 1.017 ± 0.012. What it licenses is narrow: inverting a design's law at a fraction other than 0.2 in order to size it, which every re-provisioning argument does. Method and full results: [`docs/experiments/mu-sweep.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/mu-sweep.md).

[^boundaries]: The boundary is the analysis's own: M3's coverage law at *s* = 1 recovers M2's, stated in [`full_coverage.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/formal_spec/hybrid_dissemination/models/m3/properties/full_coverage.md), and the *s* = 1 limit is re-run as a check at *N* = 20,000 in the reproduction scripts.

[^wilson]: The Wilson score interval, used throughout for a proportion estimated from a finite number of draws. It is preferred to the normal approximation here because the failure rates measured are small and the approximation's coverage degrades badly as a proportion approaches zero. Intervals are quoted at 95 % and computed at each sample's own size.

[^churn]: Churn tolerance, experiment E13. Forty configurations in three rounds: twenty-five across the five designs with downtime swept from 0 to 12 % of the honest population, then nine at the then-published operating points at 20 to 30 %, then six at the two configurations this proposal names, M3 at (13, 7) and M4 at RF = 9, the latter at 25 to 35 %. About 121,000 draws; each scored against its design's coverage law evaluated at the shifted adversarial fraction, which together span 0.20 to 0.48. Method, full results and the residual: [`docs/experiments/churn-tolerance.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/churn-tolerance.md) and [`docs/experiments/churn-proposed-points.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/churn-proposed-points.md).

[^degrees]: Links per node. Counted as the distinct (peer, link kind) pairs a node holds an established link with, in either direction and regardless of the counterparty's class, since an adversary still occupies a connection slot; a symmetric link is counted once. The ungated measurements use 200 graphs per operating point (M2: 40); the gated reference comes from E20's 400-graph cell. The propagation-digraph degrees the framework reports elsewhere are a different and smaller quantity, omitting the publication-seeding links from the relay propagation graph. At M3's current (RF = 13, s = 7) configuration these account for twelve of its thirty-eight mean standing links; the historical (12, 8) configuration in the linked study has fourteen. Seeding links carry their owner's publications, but do not relay other publishers' traffic. Method and the one unresolved discrepancy against the earlier figures: [`docs/experiments/standing-degree.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/standing-degree.md).

[^depth]: Historical propagation-depth study at N = 20,000 and μ = 0.2. M3 used RF = 12, s = 8 and M4 used RF = 8; these differ from Table 4's M3 (13, 7) and M4 RF = 9. At those older configurations, 0.17 % of M3 receipts and 0.0013 % of M4 receipts arrived at hop 6. These percentages do not establish the tail comparison for Table 4. Configurations, distributions and method: [`docs/experiments/depth-distribution.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/depth-distribution.md).

[^finiten]: Where the laws lose accuracy. Sixteen cells at μ = 0.2, 60,000 draws each, isolating what the corpus-wide 2 % optimism actually is. M3 measures 1.059, 1.064 and 1.056 against its law at N = 1,000, 2,000 and 4,000 with the pick count held at RF = 6, so the deviation does not follow the population; sorted by pick count it falls to about 2 % at RF = 12–13. M2 measures 0.961, 0.986 and 0.991 across the same populations at RF = 11, so its deviation does follow the population. Three intermediate readings were overturned, two by control cells and one by a confound in the sweep's own design, and the document keeps them. Method and full results: [`docs/experiments/finite-n.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/finite-n.md).

[^axes]: On the choice of axes. Figure 8 combines measured bandwidth, mean logical links and mean full-coverage hops with predicted honest downtime tolerance at the ungated configurations in [Table 4](#table-4). Failure probability is reported alongside costs in that table; the downtime budget shows how much independent honest downtime the model allows before the failure target is exceeded. [Table 5](#table-5) separately compares gated configurations and their expected eligible reach, without quantifying eclipse cost. Table 4 also reports the highest link count observed in the sampled graphs, not an admission limit. Mean receipt depth is omitted because it overlaps with the forwarding-depth metric already plotted. Other quantities and combinations are plotted in the [design comparison](https://pubsub.cardano-scaling.org/experiments/compare-designs/), which carries nine and lets a reader choose which to show.

[^synthesis]: The gated parameter set at the operating shape these designs propose, experiment E20. Eleven pre-registered cells, the first of the programme at *N* = 20,000, composing the measured results of E10, E12, E18 and E19 through an (*N*, *k*)-parameterised prediction ledger whose forms recover each design's published ungated law at *B* = 1. It is the first pass to measure the gate and the admissions budget at the pick counts these designs use rather than at the larger pick count the directional work was calibrated at, and the bucket-count and serving-cap rules above are its. Its gated closed forms are validated against measurement and were independently re-derived and reproduced number for number in the branch's formal review; a derivation document in the formal specification's style is the named hardening step. Method, cells and full results: [`docs/experiments/m4-synthesis.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/m4-synthesis.md).

[^seam]: One seam rather than two. The surface figures count the directional design's relay seam alone, so the normalisation is generous to it. Its publication-seeding links are a second kind with their own gate, serving cap and sizing rule, whose cap governs what a node will accept from publishers; measured under a binding cap in E20, that seam strangles exactly the links that would have rescued an otherwise-muted publisher. The symmetric design has one channel with one gate, one cap and one budget rule, and every normative statement elsewhere in this proposal is written once rather than twice.

[^symgate]: The admission parameters under symmetric links, experiments E18 and E19 at N = 4,000. E18 prices what the gate costs in coverage once links are symmetric; E19 prices what it buys against a Sybil flooder that dials every honest node the gate admits, over a grid of bucket count, admissions budget and attacker fraction, with 400 runs per cell and the tail arms at 8,000. Every cell's predictions were committed before it ran and the refuted ones are kept as corrections rather than rewritten. The cap semantics are fixed in [ADR 0042](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/decisions/0042-symmetric-acceptance-cap-semantics.md) and the comparison against the direction-dependent gate in [ADR 0043](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/decisions/0043-ordered-symmetric-comparison-predicate.md). Method and full grids: [`docs/experiments/gated-symmetric.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/gated-symmetric.md) and [`docs/experiments/symmetric-flooding.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/symmetric-flooding.md).

[^gate]: The admission parameters, directional case. Both experiments run model M2 at N = 4,000; M4's symmetric handshake is covered separately.[^symgate] Two experiments over the calibrated bulk point: the coverage cost of the verifiable gate across a ladder of bucket counts, and its value against a slot-flooding attacker over a grid of bucket count, serving cap and attacker size; 10,350 runs in the flooding grid alone. Method, full grids and the sizing rules: [`e10-selection-fidelity.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/e10-selection-fidelity.md) and [`e12-flooding-mitigation.md`](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/e12-flooding-mitigation.md).

[^m3budget]: M3 gated downtime is calculated from `m3_isolation(20000, 13, 769, S, 7, 769)` at the shifted adversarial count. The [reproduction note](https://github.com/input-output-hk/pubsub/blob/5d6391813904159a04908dbdd20b03d1a56f85d1/pubsub-node/docs/experiments/m3-gated-downtime.md) records the threshold, rounding and assumptions. This is a baseline model prediction without admission refusals or wholesale flooding.
