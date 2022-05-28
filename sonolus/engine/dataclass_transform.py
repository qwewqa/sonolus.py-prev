from typing import Callable, Any, TypeVar

_T = TypeVar("_T")


def __dataclass_transform__(
    *,
    eq_default: bool = True,
    order_default: bool = False,
    kw_only_default: bool = False,
    field_descriptors: tuple[type | Callable[..., Any], ...] = (),
) -> Callable[[_T], _T]:
    return lambda a: a
