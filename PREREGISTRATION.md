# WORLD-0 / TRIAL-0 PREREGISTRATION

Status: FROZEN BEFORE OUTCOME ANALYSIS
Date: 2026-09-26

## Question
Does access to truthful, contemporaneous partial observations from other agents improve collective reward when no individual agent observes the full hidden state?

## Fixed design
- Agents: 3 identical deterministic policies.
- World: hidden binary state (x0,x1,x2), sampled independently per tick from a seeded PRNG.
- Observation: agent i observes only xi.
- Task: predict parity x0 XOR x1 XOR x2.
- Reward: +1 correct, 0 incorrect.
- Ticks: 100 per run.
- Confirmatory seeds: integers 0..999.
- No learning across runs.

## Arms
COMM_OFF: no messages delivered.
COMM_ON: truthful current observations from the other agents delivered before action.
COMM_SHUFFLED: same message volume as COMM_ON, but sender values are deterministically permuted across ticks using a separate seed-derived RNG.

## Fixed policy
Same code in all arms: XOR all currently available bits; missing bits are imputed as 0. No roles or specialization.

## Primary estimand
For seed s:
delta_s = mean_reward(COMM_ON,s) - mean_reward(COMM_OFF,s)

Primary support requires mean(delta_s) > 0 and a paired 95% bootstrap CI excluding 0.

## Mechanism control
COMM_ON must also exceed COMM_SHUFFLED under the same paired criterion.

## Integrity
A canonical frozen physics specification is SHA-256 hashed. Every ledger event records physics_hash. Changing physics, policy, metric, seeds, ticks, or arms creates a new trial/version and cannot repair Trial-0.

## Failure
STOP / no support if COMM_ON does not beat COMM_OFF, or COMM_ON does not beat COMM_SHUFFLED.

## Scope
A positive result demonstrates only causal value of contemporaneous decision-relevant communication in this synthetic world. It is not evidence of emergent society, consciousness, AGI, spontaneous specialization, or general multi-agent superiority.
