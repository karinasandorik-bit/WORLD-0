# WORLD-0

Minimal executable world for causal multi-agent experiments.

Trial-0 asks whether truthful contemporaneous partial observations communicated among otherwise identical agents causally improve reward.

Arms: COMM_OFF / COMM_ON / COMM_SHUFFLED.

No LLMs. No assigned roles. No learning. No UI. No KISASIGNALS integration.

Run tests:
```bash
python -m unittest discover -s tests -v
```

Run confirmatory experiment:
```bash
python -m world0.experiment --seeds 1000 --ticks 100
```

See PREREGISTRATION.md before interpreting any result.
