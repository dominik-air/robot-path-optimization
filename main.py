import asyncio
from fastapi import FastAPI, WebSocket
import sim

app = FastAPI()
robot = sim.Robot(x=10, y=10, width=10, length=10)
points = [(20, 40), (80, 80)]
moves = iter(sim.create_instruction_set(points, step_size=10))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(1)  # some delay to mock time intervals in the simulation
        robot.move(*next(moves))  # I wanted to plug in here the code for the sim
        await websocket.send_text(f"(x:{robot.x}; y:{robot.y})")
