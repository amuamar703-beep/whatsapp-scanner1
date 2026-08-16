import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from app.workers.exceptions import WorkerError, WorkerNotStartedError
from app.workers.queue import QueueManager

class BaseWorker(ABC):
    def __init__(self, queue_manager: QueueManager):
        self.queue_manager = queue_manager
        self._is_running = False
        self._should_stop = False
        self._task = None
        self._name = self.__class__.__name__

    async def start(self):
        if self._is_running:
            raise WorkerError("Worker is already running")
        
        self._should_stop = False
        self._is_running = True
        self._task = asyncio.create_task(self._run_loop())
        
        return self

    async def stop(self):
        if not self._is_running:
            return
        
        self._should_stop = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._is_running = False

    async def _run_loop(self):
        while not self._should_stop:
            try:
                await self.process_job()
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.handle_error(e)
                await asyncio.sleep(1)

    @abstractmethod
    async def process_job(self):
        pass

    async def handle_error(self, error: Exception):
        pass

    def is_running(self) -> bool:
        return self._is_running

    def get_name(self) -> str:
        return self._name