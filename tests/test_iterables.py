from hypothesis import given, strategies as st

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

    @given(end=st.integers(0, 100))
    def test_range_start(self, end):
        expected_values = [*range(end)]
        expected = Array[Num, len(expected_values)](expected_values)
        result = run_function(
            self.evaluate_range, end, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)

    @given(start=st.integers(0, 100), end=st.integers(0, 100))
    def test_range_start_end(self, start, end):
        expected_values = [*range(start, end)]
        expected = Array[Num, len(expected_values)](expected_values)
        result = run_function(
            self.evaluate_range, start, end, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)

    @given(
        start=st.integers(0, 1000), end=st.integers(0, 1000), step=st.integers(1, 100)
    )
    def test_range_start_end_step(self, start, end, step):
        expected_values = [*range(start, end, step)]
        expected = Array[Num, len(expected_values)](expected_values)
        result = run_function(
            self.evaluate_range, start, end, step, expected_size=len(expected_values)
        )
        assert dump_value(result) == dump_value(expected)
