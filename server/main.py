import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import os
import ijson
import simplejson as json

app = FastAPI()

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
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Driving', 'Participant_1', 'AFE_000_CONFIDENTIAL.json')

    async def event_generator():
        with open(file_path, "rb") as f:
            for record in ijson.items(f, "item"):
                if await request.is_disconnected():
                    break
                print("Sending event", record)
                yield {
                    "event": "data",
                    #"id": "message_id",
                    "data": json.dumps(record)
                }

                # TODO: figure out the right sleep time
                await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
