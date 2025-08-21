import asyncio
from typing import Generic, TypeVar

T = TypeVar("T")


class ManualPromise(Generic[T]):
    def __init__(self):
        self._future: asyncio.Future[T] = asyncio.Future()
        self._is_done = False

    def is_done(self) -> bool:
        return self._is_done

    def resolve(self, value: T) -> None:
        if not self._is_done:
            self._is_done = True
            if not self._future.done():
                self._future.set_result(value)

    def reject(self, error: Exception) -> None:
        if not self._is_done:
            self._is_done = True
            if not self._future.done():
                self._future.set_exception(error)

    async def as_coroutine(self) -> T:
        return await self._future

    def __await__(self):
        return self._future.__await__()
