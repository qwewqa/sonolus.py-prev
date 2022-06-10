from hypothesis import given, strategies as st, assume, settings, event

from sonolus import Range, Vector
from sonolus.core import *
from sonolus.test import run_function, dump_value


class TestRange:
    @sls_func
    def evaluate_range(self, *args, expected_size):
        results = Vector[Num, expected_size].empty()
        for i in Range(*args):
            results.append(i)
        return results.values

    @sls_func
    def range_contains(self, *args, test):
        return test in Range(*args)

    @given(end=st.integers(0, 200))
    def test_range_start(self, end):
        expected_values = [*range(end)]
        expected = Array[Num, len(expected_values)](expected_values)
        event(f"empty: {not expected_values}")
        result = run_function(
            self.evaluate_range, end, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)

    @given(start=st.integers(0, 100), end=st.integers(0, 100))
    def test_range_start_end(self, start, end):
        expected_values = [*range(start, end)]
        expected = Array[Num, len(expected_values)](expected_values)
        event(f"empty: {not expected_values}")
        result = run_function(
            self.evaluate_range, start, end, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)

    @given(
        start=st.integers(-1000, 1000),
        end=st.integers(-1000, 1000),
        step=st.integers(-100, 100),
    )
    def test_range_start_end_step(self, start, end, step):
        assume(step != 0)
        expected_values = [*range(start, end, step)]
        expected = Array[Num, len(expected_values)](expected_values)
        event(f"empty: {not expected_values}")
        result = run_function(
            self.evaluate_range, start, end, step, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)

    @given(
        start=st.integers(-100, 100),
        end=st.integers(-100, 100),
        step=st.integers(-10, 10),
        test=st.integers(-100, 100),
    )
    @settings(max_examples=500)
    def test_range_contains(self, start, end, step, test):
        assume(step != 0)
        expected = test in range(start, end, step)
        event(f"expected: {expected}")
        result = run_function(self.range_contains, start, end, step, test=test)
        assert dump_value(result) == expected
