# OpsKnowledge local CI gate — PR2A: Make/uv/order contract.
# Ordered fail-fast; each stage must pass before the next. Frozen uv.
# PR2A: uv version, sync, ruff, pyright, pytest. ci reuses ci-pr2a then
# fails closed at check-focused-tests (PR2B boundary). No PR3 stages.

UV ?= uv
EXPECTED_UV_VERSION := 0.11.29

.PHONY: ci ci-pr2a check-uv-version sync-env check-focused-tests ruff-check ruff-format pyright-check pytest-check

ci: ci-pr2a
	$(MAKE) check-focused-tests
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
	@echo "ERROR: focused-test guard not yet implemented until PR2B." >&2
	@echo "Remediation: merge PR2B (scripts/ci/check_focused_tests.py) and rerun make ci." >&2
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
