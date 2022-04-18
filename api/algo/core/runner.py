import asyncio
import functools

import torch
from sanic.log import logger

from api.algo.models.cyclegan import get_pretrained_model

device = torch.device('cpu')
MAX_QUEUE_SIZE = 3
MAX_BATCH_SIZE = 2
MAX_WAIT = 1


class HandlingError(Exception):
    def __init__(self, msg, code=500):
        super().__init__()
        self.handling_code = code
        self.handling_msg = msg


class ModelRunner:
    def __init__(self, app, model_name):
        self.app = app

        self.model_name = model_name
        self.queue = []

        self.queue_lock = None

        self.model = get_pretrained_model(self.model_name,
                                          map_location=device)

        self.needs_processing = None

        self.needs_processing_timer = None

    def schedule_processing_if_needed(self):
        if len(self.queue) >= MAX_BATCH_SIZE:
            logger.debug("next batch ready when processing a batch")
            self.needs_processing.set()
        elif self.queue:
            logger.debug(
                "queue nonempty when processing a batch, setting next timer")
            self.needs_processing_timer = self.app.loop.call_at(
                self.queue[0]["time"] + MAX_WAIT, self.needs_processing.set)

    async def process_input(self, input):
        our_task = {"done_event": asyncio.Event(loop=self.app.loop),
                    "input": input,
                    "time": self.app.loop.time()}
        async with self.queue_lock:
            if len(self.queue) >= MAX_QUEUE_SIZE:
                raise HandlingError("I'm too busy", code=503)
            self.queue.append(our_task)
            logger.debug(
                "enqueued task. new queue size {}".format(len(self.queue)))
            self.schedule_processing_if_needed()

        await our_task["done_event"].wait()
        return our_task["output"]

    def run_model(self, batch):
        return self.model(batch.to(device)).to('cpu')

    async def model_runner(self):
        self.queue_lock = asyncio.Lock(loop=self.app.loop)
        self.needs_processing = asyncio.Event(loop=self.app.loop)
        logger.info("started model runner for {}".format(self.model_name))
        while True:
            await self.needs_processing.wait()
            self.needs_processing.clear()
            if self.needs_processing_timer is not None:
                self.needs_processing_timer.cancel()
                self.needs_processing_timer = None
            async with self.queue_lock:
                if self.queue:
                    longest_wait = self.app.loop.time() - self.queue[0]["time"]
                else:
                    longest_wait = None
                logger.debug(
                    "launching processing. queue size: {}. longest wait: {}".format(
                        len(self.queue), longest_wait))
                to_process = self.queue[:MAX_BATCH_SIZE]
                del self.queue[:len(to_process)]
                self.schedule_processing_if_needed()
            batch = torch.stack([t["input"] for t in to_process], dim=0)

            result = await self.app.loop.run_in_executor(
                None, functools.partial(self.run_model, batch)
            )
            for t, r in zip(to_process, result):
                t["output"] = r
                t["done_event"].set()
            del to_process
