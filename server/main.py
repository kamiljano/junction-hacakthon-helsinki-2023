import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import os
import ijson
import simplejson as json
import time

app = FastAPI()

def current_milli_time():
    return round(time.time() * 1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "OK"}


@app.get("/stream/driving")
async def data_stream(request: Request):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', '2023-11-11T16-57-48_Pixie27023_Junction-sushicat', 'AFE_000_uploaded.json')

    async def event_generator():
        with open(file_path, "rb") as f:
            last_timestamp = -1
            for record in ijson.items(f, "item"):
                if await request.is_disconnected():
                    break
                current_timestamp = record['afe'][0]['i'][1]
                time_to_wait_microseconds = current_timestamp - last_timestamp if last_timestamp != -1 else 0
                last_timestamp = current_timestamp
                await asyncio.sleep(time_to_wait_microseconds / 1000000)
                yield {
                    "event": "data",
                    "data": json.dumps({
                        'raw': record
                    })
                }

    return EventSourceResponse(event_generator())
