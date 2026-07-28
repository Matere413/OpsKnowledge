# OpsKnowledge local CI gate — PR2A: Make/uv/order contract.
# Ordered fail-fast; each stage must pass before the next. Frozen uv.
# PR2A stages are retained; PR2B scans before Pytest and stops at PR3 audit.

UV ?= uv
export UV
EXPECTED_UV_VERSION := 0.11.29

# `UV` is exported as data then consumed by an argv-only Python launcher.
# Never interpolate a configurable executable in shell command position.
UV_RUN := python3 scripts/ci/run_uv_command.py

.PHONY: ci ci-pr2a check-uv-version sync-env check-focused-tests check-evaluation-dataset ruff-check ruff-format pyright-check pytest-check check-dependency-boundaries check-audit license-inventory eval-quality

ci: check-uv-version
	@echo "=== uv version OK ==="
	$(MAKE) sync-env
	$(MAKE) check-evaluation-dataset
	$(MAKE) check-focused-tests
	$(MAKE) ruff-check
	$(MAKE) ruff-format
	$(MAKE) pyright-check
	$(MAKE) pytest-check
	$(MAKE) check-dependency-boundaries
	$(MAKE) check-audit
	$(MAKE) license-inventory
	@echo "=== make ci complete ==="

ci-pr2a: check-uv-version
	@echo "=== uv version OK ==="
	$(MAKE) sync-env
	$(MAKE) ruff-check
	$(MAKE) ruff-format
	$(MAKE) pyright-check
	$(MAKE) pytest-check
	@echo "=== ci-pr2a complete (scanner/audit/license pending PR2B/PR3) ==="

# Assert complete `uv self version --short` stdout equals "0.11.29".
# Rejects mismatch, suffix, multiline, malformed, unavailable, command error.
check-uv-version:
	@actual=$$($(UV_RUN) self version --short 2>/dev/null || echo "unavailable"); \
	if [ "$$actual" != "$(EXPECTED_UV_VERSION)" ]; then \
		printf "ERROR: uv version mismatch; expected 0.11.29, found %s.\n" "$$actual"; \
		printf "Remediation: install uv 0.11.29 and rerun make ci.\n"; \
		exit 1; \
	fi

sync-env:
	$(UV_RUN) sync --frozen --extra dev
	@echo "=== frozen sync OK ==="

check-focused-tests:
	$(UV_RUN) run --frozen python scripts/ci/check_focused_tests.py .
	@echo "=== focused-test guard OK ==="

check-dependency-boundaries:
	$(UV_RUN) run --frozen python scripts/ci/check_dependency_boundaries.py .
	@echo "=== dependency boundaries OK ==="

check-audit:
	$(UV_RUN) run --frozen python scripts/ci/run_vulnerability_audit.py
	@echo "=== vulnerability audit OK ==="

license-inventory:
	$(UV_RUN) run --frozen pip-licenses --from=expression --format=json
	@echo "=== license inventory OK ==="

ruff-check:
	$(UV_RUN) run --frozen ruff check .
	@echo "=== ruff check OK ==="

ruff-format:
	$(UV_RUN) run --frozen ruff format --check .
	@echo "=== ruff format OK ==="

pyright-check:
	$(UV_RUN) run --frozen pyright
	@echo "=== pyright OK ==="

pytest-check:
	$(UV_RUN) run --frozen pytest
	@echo "=== pytest OK ==="

# Evaluation-dataset structural validator. Wired into `ci` before
# check-focused-tests so a malformed dataset fails the canonical gate early.
check-evaluation-dataset:
	$(UV_RUN) run --frozen python scripts/ci/validate_evaluation_dataset.py evaluation-dataset
	@echo "=== evaluation-dataset validator OK ==="

# Opt-in quality evaluation harness (NOT part of `ci`). Runs the 34-case
# evaluation through the development kernel and promotes a reviewed safe
# baseline under evaluation-runs/current/ (previous/ on replacement).
eval-quality:
	$(UV_RUN) run --frozen python -m backend.features.evaluation.cli evaluation-dataset
	@echo "=== eval-quality OK ==="
