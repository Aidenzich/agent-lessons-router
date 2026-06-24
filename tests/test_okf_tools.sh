#!/usr/bin/env bash
set -euo pipefail

python3 scripts/okf_lint.py --bundle tests/fixtures/alr-okf-valid --profile docs/alr-okf-profile.contract.json --format json >/tmp/alr-okf-valid-lint.json
python3 scripts/okf_refs.py --bundle tests/fixtures/alr-okf-valid --profile docs/alr-okf-profile.contract.json --format json >/tmp/alr-okf-valid-refs.json
python3 - <<'PY'
import json
from pathlib import Path

lint = json.loads(Path("/tmp/alr-okf-valid-lint.json").read_text())
refs = json.loads(Path("/tmp/alr-okf-valid-refs.json").read_text())
codes = {item["code"] for item in lint["diagnostics"]}
assert "OKF_FRONTMATTER_PARSE_ERROR" not in codes
assert refs["summary"]["broken_internal"] == 0
refs_text = Path("/tmp/alr-okf-valid-refs.json").read_text()
assert "valid-fixture-secret" not in refs_text
assert "alice:super-secret" not in refs_text
assert "password=[REDACTED]" in refs_text
assert "https://[REDACTED]@example.com/path" in refs_text
PY

python3 scripts/okf_lint.py --bundle tests/fixtures/alr-okf-missing-type --profile docs/alr-okf-profile.contract.json --format json >/tmp/alr-okf-missing-type-lint.json
python3 scripts/okf_lint.py --bundle tests/fixtures/alr-okf-missing-type --profile docs/alr-okf-profile.contract.json --strict --format json >/tmp/alr-okf-missing-type-strict.json && exit 1 || test "$?" = "2"

python3 scripts/okf_lint.py --bundle tests/fixtures/alr-okf-broken-links --profile docs/alr-okf-profile.contract.json --format json >/tmp/alr-okf-broken-links-lint.json
python3 scripts/okf_lint.py --bundle tests/fixtures/alr-okf-broken-links --profile docs/alr-okf-profile.contract.json --strict-links --format json >/tmp/alr-okf-broken-links-strict.json && exit 1 || test "$?" = "2"
python3 scripts/okf_refs.py --bundle tests/fixtures/alr-okf-broken-links --profile docs/alr-okf-profile.contract.json --format json >/tmp/alr-okf-broken-links-refs.json
python3 - <<'PY'
from pathlib import Path

lint_text = Path("/tmp/alr-okf-broken-links-lint.json").read_text()
refs_text = Path("/tmp/alr-okf-broken-links-refs.json").read_text()
assert "broken-fixture-secret" not in lint_text
assert "broken-fixture-secret" not in refs_text
assert "token=[REDACTED]" in lint_text
assert "token=[REDACTED]" in refs_text
PY

python3 scripts/okf_refs.py --bundle tests/fixtures/alr-okf-valid --profile /tmp/alr-okf-missing-profile.contract.json --format json && exit 1 || test "$?" = "1"
printf '{}\n' >/tmp/alr-okf-invalid-profile.contract.json
python3 scripts/okf_refs.py --bundle tests/fixtures/alr-okf-valid --profile /tmp/alr-okf-invalid-profile.contract.json --format json && exit 1 || test "$?" = "1"

python3 scripts/okf_lint.py --bundle / --profile docs/alr-okf-profile.contract.json --format json && exit 1 || test "$?" = "1"
python3 scripts/okf_refs.py --bundle / --profile docs/alr-okf-profile.contract.json --format json && exit 1 || test "$?" = "1"
