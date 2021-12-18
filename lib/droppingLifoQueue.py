import asyncio
from typing import Any


class droppingLifoQueue(asyncio.LifoQueue):
    """
    Modification of the LifoQueue to drop older items as new items
    become available, thereby replacing them. This will prevent blockages,
    and optimize for realtime use.
    """
    def _init(self, maxsize: int) -> None:
        self._queue = []

    def _put(self, item):
        self._queue.append(item)

    def _get(self) -> Any:
        return self._queue.pop()

    def __drop(self):
        # drop the last item from the queue
        self._queue.pop()
        # no consumer will get a chance to process this item, so
        # count must decrement manually
        self.task_done()

    def put_nowait(self, item):
        # Make space for incoming items
        if self.full():
            self.__drop()
        super().put_nowait(item)

    async def put(self, item):
        # Queue.put blocks when full, so it be must overriden.
        # Since the put_nowait declared above never raises QueueFull,
        # it can be called directly
        self.put_nowait(item)
