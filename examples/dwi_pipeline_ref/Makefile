.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help dryrun run report test lint clean

help:
	@echo "make dryrun  — snakemake -n (what would run)"
	@echo "make run     — snakemake --cores 4"
	@echo "make report  — snakemake report.html"
	@echo "make test    — pytest the helpers"
	@echo "make lint    — ruff + snakefmt"
	@echo "make clean   — remove cohort/ outputs"

dryrun:
	snakemake -n

run:
	snakemake --cores 4 --use-singularity

report:
	snakemake --report cohort/snakemake_report.html

test:
	pytest -q tests/

lint:
	ruff check scripts/ tests/
	snakefmt Snakefile

clean:
	rm -rf cohort/
