# CAM Lab: Continuity-Aware Memory for Trace-Derived Context

This folder contains the experiment code for **Continuity-Aware Memory (CAM)**, a lightweight research prototype for managing execution-trace-derived context in LLM agents.

CAM treats each distilled experience as a structured object rather than a flat text bullet. Each object records:

- provenance: where the experience came from in the execution trace;
- applicability boundaries: when the experience should and should not be used;
- conflict/version metadata: which other memories it refines or conflicts with;
- runtime hooks: when the memory should be injected during an agent run;
- smoothed utility: an exponentially updated score that prevents one trace from dominating future decisions.

## Layout

```text
src/cam_lab/              Core CAM prototype
scripts/                  Reproducible experiment and figure scripts
tests/                    Minimal tests for memory behavior
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_experiments.py --out results
python scripts/generate_figures.py --results results --figures figures
```

The included experiments are a compact, deterministic reproduction of the paper tables. They are intended for method development and paper prototyping, not a complete AppWorld/FiNER benchmark reproduction.
