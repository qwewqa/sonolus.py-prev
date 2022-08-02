import ast
import functools
import inspect
import re
import sys
import textwrap
from types import FunctionType
from typing import TypeVar, Any, ClassVar

from sonolus.scripting.internal.dataclass_transform import __dataclass_transform__
from sonolus.scripting.internal.struct import Struct


@__dataclass_transform__(eq_default=True)
class GenericStruct(Struct, _no_init_struct_=True):
    type_vars: ClassVar[Any] = None

    def __init__(self, *args, **kwargs):
        if self.type_vars is None:
            raise TypeError("Cannot instantiate generic struct directly.")
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, type_vars=None, _typed_subclass=False, **kwargs):
        if _typed_subclass:
            super().__init_subclass__(**kwargs)
            return
        else:  # cls should be a direct subclass
            if hasattr(cls, "_type_subclasses_"):
                raise TypeError("Cannot subclass a generic struct.")
            if type_vars is None:
                raise ValueError("Generic is missing type_vars argument.")
            cls._typed_subclasses_ = {}
            cls._type_arg_type_ = type_vars
            if not (
                isinstance(cls._type_arg_type_, type)
                and issubclass(cls._type_arg_type_, tuple)
                and hasattr(cls._type_arg_type_, "_fields")
            ):
                raise TypeError("Expected type_vars to be a namedtuple type.")

    def __class_getitem__(cls, item):
        if cls.type_vars is not None:
            raise TypeError("Class is already a constructed generic.")
        if not isinstance(item, tuple):
            item = (item,)
        item = cls._type_arg_type_(*item)
        if item not in cls._typed_subclasses_:
            cls._typed_subclasses_[item] = cls._create_typed_subclass(item)
        return cls._typed_subclasses_[item]

    @classmethod
    def _create_typed_subclass(cls, type_vars):
        globalns = dict(getattr(sys.modules.get(cls.__module__, None), "__dict__", {}))
        localns = dict(vars(cls))
        for field in cls._type_arg_type_._fields:
            if field in cls.__dict__:
                raise ValueError(
                    f"Class has member {field} which conflicts with a type variable."
                )
            localns[field] = getattr(type_vars, field)
        localns["type_vars"] = type_vars
        hints = inspect.get_annotations(
            cls, globals=globalns, locals=localns, eval_str=True
        )
        hints = {k: v for k, v in hints.items() if k in cls.__annotations__}

        for name, hint in hints.items():
            if isinstance(hint, TypeVar):
                if hasattr(type_vars, hint.__name__):
                    hints[name] = getattr(type_vars, hint.__name__)
                else:
                    KeyError(f'No type arg with name "{hint.__name__}" found.')

        class Typed(cls, _typed_subclass=True, _override_fields_=hints):
            pass

        Typed.type_vars = type_vars

        Typed.__name__ = f"{cls.__name__}_{cls._format_type_vars(type_vars)}"
        Typed.__qualname__ = Typed.__name__

        return Typed

    @classmethod
    def _format_type_vars(cls, type_vars: tuple):
        return "_".join(cls._clean_type_arg(arg) for arg in type_vars)

    @classmethod
    def _clean_type_arg(cls, type_arg):
        if hasattr(type_arg, "__name__"):
            return type_arg.__name__
        else:
            return re.sub("[^a-zA-Z0-9]", "", str(type_arg))


T = TypeVar("T", bound=FunctionType)


def generic_method(fn: T = None, /) -> T:
    """
    Decorator to make a method generic.
    Causes the function to be re-evaluated with generic type variables
    injected into the global namespace for each concrete type.
    Should only be used on methods of a generic struct.
    Must be the last decorator applied to a function.
    """

    def wrap(fn):
        return GenericMethod(fn)

    if fn is None:
        return wrap

    return wrap(fn)


class GenericMethod:
    def __init__(self, fn: FunctionType):
        self.fn = fn
        self.original = fn
        while hasattr(self.original, "__wrapped__"):
            self.original = self.original.__wrapped__
        self.source_file = inspect.getsourcefile(self.original)

        lines, lnum = inspect.getsourcelines(fn)
        tree = ast.parse(textwrap.dedent("".join(lines)))
        ast.increment_lineno(tree, lnum - 1)
        self.transformed = GenericMethodTransformer().visit(tree)
        ast.fix_missing_locations(self.transformed)

        self.cache = {}

    def __call__(self, cls, *args, **kwargs):
        raise TypeError("Cannot call generic function directly.")

    def __get__(self, instance, owner=None):
        if not hasattr(owner, "type_vars"):
            raise TypeError("Cannot access generic function on a non-generic class.")
        if owner.type_vars is None:  # Base generic class

            @functools.wraps(self.fn)
            def wrapper(_self, *args, **kwargs):
                return self.__get__(_self, type(_self))(*args, **kwargs)

            return wrapper
        else:  # Concrete generic class
            if owner not in self.cache:
                compiled = compile(self.transformed, self.source_file, "exec")
                closure = inspect.getclosurevars(self.original)
                gbl = {}
                gbl.update(vars(inspect.getmodule(self.original)))
                gbl.update(self.original.__globals__)
                gbl.update(closure.globals)
                gbl.update(closure.nonlocals)
                gbl.update(closure.builtins)
                gbl.update(
                    {k: v for k, v in zip(owner.type_vars._fields, owner.type_vars)}
                )
                gbl["type_vars"] = owner.type_vars
                loc = {}
                exec(compiled, gbl, loc)
                concrete = loc[self.fn.__name__]
                self.cache[owner] = concrete
            return self.cache[owner].__get__(instance, owner)


class GenericMethodTransformer(ast.NodeTransformer):
    # Remove first decorator
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        result = ast.FunctionDef(
            node.name,
            node.args,
            node.body,
            node.decorator_list[1:],
            node.returns,
            node.type_comment,
        )
        return ast.copy_location(result, node)
