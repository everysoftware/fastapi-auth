# Copied from fastapi.concurrency
import functools
import typing

import anyio.to_thread

P = typing.ParamSpec("P")
T = typing.TypeVar("T")


async def run_in_threadpool(
    func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    if kwargs:  # pragma: no cover
        # run_sync doesn't accept 'kwargs', so bind them in here
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)
