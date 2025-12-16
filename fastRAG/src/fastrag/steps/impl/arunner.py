import asyncio
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Iterable, override

from fastrag.events import Event
from fastrag.steps.steps import IStepRunner


class IAsyncStepRunner(IStepRunner, ABC):

    @abstractmethod
    def get_tasks(self) -> Iterable[AsyncGenerator[Event, None]]: ...

    def callback(self, event: Event) -> None:
        self._callback(event)

    @override
    def run(cls):
        async def runner_loop():
            runners = cls.get_tasks()
            tasks = [asyncio.create_task(run.__anext__()) for run in runners]

            while tasks:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                for d in done:
                    idx = tasks.index(d)

                    try:
                        event = d.result()
                    except StopAsyncIteration:
                        tasks.pop(idx)
                        runners.pop(idx)
                        cls.progress.advance(cls.task_id)
                        continue

                    cls.callback(event)
                    tasks[idx] = asyncio.create_task(runners[idx].__anext__())

        asyncio.run(runner_loop())
