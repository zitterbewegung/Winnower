.PHONY: all data data-fresh figures tikz paper review test clean

all: data figures paper

install:
	pip install -e .

# Resumes by default: rows already present in outputs/alife_2026 are REUSED,
# not recomputed, so this is fast on a fresh checkout and does almost nothing
# on a complete one. Use it to continue an interrupted sweep. The run now
# prints a resume report saying exactly what it reused.
data:
	PYTHONPATH=src python scripts/alife/alife_run_all.py \
		--output-root outputs/alife_2026 --paper-dir paper

# Recomputes everything from scratch. This is the target to use when
# VERIFYING reproducibility -- `make data` on a complete checkout reuses the
# committed CSVs and would report success without recomputing a single row.
data-fresh:
	PYTHONPATH=src python scripts/alife/alife_run_all.py \
		--output-root outputs/alife_2026 --paper-dir paper --no-resume

figures:
	PYTHONPATH=src python scripts/alife/alife_rule_diagrams.py \
		--output-root outputs/alife_2026 --paper-dir paper
	PYTHONPATH=src python scripts/alife/alife_algorithm_figure.py
	PYTHONPATH=src python scripts/alife/alife_stabilization_summary.py

tikz:
	cd poster/figures && pdflatex algorithm_detailed_tikz.tex
	cd poster/figures && pdflatex selector_ablation_tikz.tex
	cd poster/figures && pdflatex stabilization_summary_tikz.tex
	cd poster/figures && pdflatex entropy_rate_comparison_tikz.tex

paper:
	cd paper && pdflatex paper_alife2026.tex

poster:
	cd poster && pdflatex alife_2026_poster.tex

review:
	python scripts/build_review_site.py

verify-webdemo:
	PYTHONPATH=src python scripts/verify_webdemo_bootstrap.py --block-numba

test:
	PYTHONPATH=src pytest tests/ -q

clean:
	find . -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.synctex.gz' | xargs rm -f
	find . -name '__pycache__' -type d | xargs rm -rf
