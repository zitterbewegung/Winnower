.PHONY: all data figures tikz paper test clean

all: data figures paper

install:
	pip install -e .

data:
	PYTHONPATH=src python scripts/alife/alife_run_all.py \
		--output-root outputs/alife_2026 --paper-dir paper

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

test:
	PYTHONPATH=src pytest tests/ -q

clean:
	find . -name '*.aux' -o -name '*.log' -o -name '*.out' -o -name '*.synctex.gz' | xargs rm -f
	find . -name '__pycache__' -type d | xargs rm -rf
