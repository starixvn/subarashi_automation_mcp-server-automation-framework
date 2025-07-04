import asyncio
import logging
import re
from typing import Set, Callable, Optional, TypeVar, TYPE_CHECKING
from playwright.async_api import Request, Frame

if TYPE_CHECKING:
    from context import ServerContext
    from core.tab import Tab

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ManualPromise:
    
    def __init__(self):
        self._future = asyncio.Future()
        self._is_done = False
    
    def is_done(self) -> bool:
        return self._is_done
    
    def resolve(self, value=None):
        if not self._is_done:
            self._is_done = True
            if not self._future.done():
                self._future.set_result(value)
    
    def reject(self, error: Exception):
        if not self._is_done:
            self._is_done = True
            if not self._future.done():
                self._future.set_exception(error)
    
    def __await__(self):
        return self._future.__await__()
    
    async def as_coroutine(self):
        return await self


async def wait_for_completion(context: "ServerContext", tab: "Tab", callback: Callable):
    requests: Set[Request] = set()
    frame_navigated = False
    wait_barrier = ManualPromise()
    
    def wait_callback():
        wait_barrier.resolve()
    
    def request_listener(request: Request):
        requests.add(request)
    
    def request_finished_listener(request: Request):
        requests.discard(request)
        if not requests:
            wait_callback()
    
    def frame_navigate_listener(frame: Frame):
        nonlocal frame_navigated
        if frame.parent_frame:
            return
        frame_navigated = True
        dispose()
        asyncio.create_task(_wait_for_load_and_callback(tab, wait_callback))
    
    async def _wait_for_load_and_callback(tab, callback):
        try:
            await tab.wait_for_load_state('load')
        except Exception:
            pass
        callback()
    
    def on_timeout():
        dispose()
        wait_callback()
    
    tab.page.on('request', request_listener)
    tab.page.on('requestfinished', request_finished_listener)
    tab.page.on('framenavigated', frame_navigate_listener)
    
    timeout_task = asyncio.create_task(asyncio.sleep(10))
    timeout_task.add_done_callback(lambda _: on_timeout())
    
    def dispose():
        try:
            tab.page.remove_listener('request', request_listener)
            tab.page.remove_listener('requestfinished', request_finished_listener)
            tab.page.remove_listener('framenavigated', frame_navigate_listener)
            if not timeout_task.done():
                timeout_task.cancel()
        except Exception as e:
            logger.debug(f"Error disposing listeners: {e}")
    
    try:
        result = await callback()
        
        if not requests and not frame_navigated:
            wait_callback()
        
        await wait_barrier
        
        await context.wait_for_timeout(1.0)
        
        return result
    finally:
        dispose()


def sanitize_for_file_path(s: str) -> str:
    
    def sanitize_part(part: str) -> str:
        return re.sub(r'[\x00-\x2C\x2E-\x2F\x3A-\x40\x5B-\x60\x7B-\x7F]+', '-', part)
    
    separator = s.rfind('.')
    if separator == -1:
        return sanitize_part(s)
    
    name_part = s[:separator]
    ext_part = s[separator + 1:]
    return sanitize_part(name_part) + '.' + sanitize_part(ext_part)


async def call_on_page_no_trace(page, callback):
    try:
        return await callback(page)
    except Exception as e:
        logger.debug(f"Error in page call: {e}")
        raise 