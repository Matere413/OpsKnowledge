# OpsKnowledge local CI gate — PR2A: Make/uv/order contract.
# Ordered fail-fast; each stage must pass before the next. Frozen uv.
# PR2A stages are retained; PR2B scans before Pytest and stops at PR3 audit.

UV ?= uv
EXPECTED_UV_VERSION := 0.11.29

.PHONY: ci ci-pr2a check-uv-version sync-env check-focused-tests ruff-check ruff-format pyright-check pytest-check check-audit

ci: check-uv-version
	@echo "=== uv version OK ==="
	$(MAKE) sync-env
	$(MAKE) check-focused-tests
	$(MAKE) ruff-check
	$(MAKE) ruff-format
	$(MAKE) pyright-check
	$(MAKE) pytest-check
	$(MAKE) check-audit

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
	@actual=$$($(UV) self version --short 2>/dev/null || echo "unavailable"); \
	if [ "$$actual" != "$(EXPECTED_UV_VERSION)" ]; then \
		printf "ERROR: uv version mismatch; expected 0.11.29, found %s.\n" "$$actual"; \
		printf "Remediation: install uv 0.11.29 and rerun make ci.\n"; \
		exit 1; \
	fi

sync-env:
	$(UV) sync --frozen --extra dev
	@echo "=== frozen sync OK ==="

check-focused-tests:
	$(UV) run --frozen python scripts/ci/check_focused_tests.py .
	@echo "=== focused-test guard OK ==="

check-audit:
	@echo "ERROR: audit is not yet implemented until PR3." >&2
	@echo "Remediation: merge PR3 and rerun make ci." >&2
	@exit 1

ruff-check:
	$(UV) run --frozen ruff check .
	@echo "=== ruff check OK ==="

ruff-format:
	$(UV) run --frozen ruff format --check .
	@echo "=== ruff format OK ==="

pyright-check:
	$(UV) run --frozen pyright
	@echo "=== pyright OK ==="

pytest-check:
	$(UV) run --frozen pytest
	@echo "=== pytest OK ==="
