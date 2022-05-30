import warnings
from typing import TypeVar, overload

from sonolus.backend.callback import CallbackType
from sonolus.backend.evaluation import CompilationInfo
from sonolus.engine.interpreter import run_statement, CFGInterpreter
from sonolus.frontend.primitive import Num, Bool

T = TypeVar("T")


class ConstContext:
    def __init__(self):
        self.called = False

    def __call__(self, value):
        if self.called:
            raise RuntimeError("Const.of called twice.")
        blocks = {}
        run_statement(value, blocks=blocks)
        interpreter = CFGInterpreter(blocks=blocks, allow_uninitialized_reads=True)
        CompilationInfo._current = None
        self.called = True
        return value._const_evaluate_(interpreter.run_node)

    def __del__(self):
        if not self.called:
            warnings.warn("Const.of referenced but not called.")


class Const:
    @overload
    def of(self, value: float) -> Num:
        pass

    @overload
    def of(self, value: bool) -> Bool:
        pass

    @overload
    def of(self, value: T) -> T:
        pass

    @property
    def of(self) -> T:
        if CompilationInfo.active:
            raise RuntimeError(
                "Const.of() cannot be used while another compilation is active."
            )
        CompilationInfo._current = self.new_compilation()
        return ConstContext()

    @staticmethod
    def new_compilation():
        return CompilationInfo(
            CallbackType("const", set(), set()),
            {},
        )


const = Const()
