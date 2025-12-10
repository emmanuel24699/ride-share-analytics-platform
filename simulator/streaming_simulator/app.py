from fastapi import FastAPI, WebSocket
from .simulator_engine import SimulatorEngine
from .state_loader import load_state
from .models import DriverLocationPing, TripEvent, SurgeEvent

app = FastAPI(title="Ride-Share Streaming Simulator")

state = load_state()
engine = SimulatorEngine(state)

@app.get("/stream/pings/{count}")
async def get_pings(count: int = 1):
    events = engine.run_simulation("ping", count)
    return [e.dict() for e in events]

@app.get("/stream/trip_events/{count}")
async def get_trip_events(count: int = 1):
    events = engine.run_simulation("trip", count)
    return [e.dict() for e in events]

@app.get("/stream/surge/{count}")
async def get_surge(count: int = 1):
    events = engine.run_simulation("surge", count)
    return [e.dict() for e in events]

# Optional: WebSocket for push streaming
@app.websocket("/ws/stream/{event_type}")
async def websocket_endpoint(websocket: WebSocket, event_type: str):
    await websocket.accept()
    while True:
        event = engine.run_simulation(event_type, 1)[0]
        await websocket.send_json(event.dict())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)