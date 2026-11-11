
from hypothesis import given, strategies as st
from processor import (
    validate_height_and_fastpass,
    compute_dispatch_throughput,
    resolve_safety_restraint_code
)


@given(st.text() | st.none())
def test_validate_height_and_fastpass_no_crash(s):
    try:
        validate_height_and_fastpass(s)
    except Exception as e:
        assert False, f"validate_height_and_fastpass crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_compute_dispatch_throughput_safe(s):
    try:
        compute_dispatch_throughput(s)
    except Exception as e:
        assert False, f"compute_dispatch_throughput crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_resolve_safety_restraint_code_safe(s):
    try:
        resolve_safety_restraint_code(s)
    except Exception as e:
        assert False, f"resolve_safety_restraint_code crashed with input {s!r}: {e}"
