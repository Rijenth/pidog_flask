#!/usr/bin/env python3
from pidog import Pidog
from flask import Flask, request, jsonify
from time import sleep
import os, json
import socket
import asyncio
import websockets
import threading
import queue
from preset_actions import pant
from preset_actions import body_twisting



# Queue for sending messages to the WebSocket client
message_queue = queue.Queue()

# Shared variable for stopping the client gracefully
stop_event = threading.Event()

my_dog = Pidog(head_init_angles=[0, 0, -30])
sleep(1)
#my_dog = Pidog()
#sleep(0.5)

def wake_up():
    # stretch
    my_dog.rgb_strip.set_mode('listen', color='yellow', bps=0.6, brightness=0.8)
    my_dog.do_action('stretch', speed=50)
    my_dog.head_move([[0, 0, 30]]*2, immediately=True)
    my_dog.wait_all_done()
    sleep(0.2)
    body_twisting(my_dog)
    my_dog.wait_all_done()
    sleep(0.5)
    my_dog.head_move([[0, 0, -30]], immediately=True, speed=90)
    # sit and wag_tail
    my_dog.do_action('sit', speed=25)
    my_dog.wait_legs_done()
    my_dog.do_action('wag_tail', step_count=10, speed=100)
    my_dog.rgb_strip.set_mode('breath', color=[245, 10, 10], bps=2.5, brightness=0.8)
    pant(my_dog, pitch_comp=-30, volume=80)
    my_dog.wait_all_done()
    # hold
    my_dog.do_action('wag_tail', step_count=10, speed=30)
    my_dog.rgb_strip.set_mode('breath', 'pink', bps=0.5)
    while True:
        sleep(1)

# Define actions
actions = [
    ['stand', 0, 50],
    ['sit', -30, 50],
    ['lie', 0, 20],
    ['lie_with_hands_out', 0, 20],
    ['trot', 0, 95],
    ['forward', 0, 98],
    ['backward', 0, 98],
    ['turn_left', 0, 98],
    ['turn_right', 0, 98],
    ['doze_off', -30, 90],
    ['stretch', 20, 20],
    ['push_up', -30, 50],
    ['shake_head', -1, 90],
    ['tilting_head', -1, 60],
    ['wag_tail', -1, 100],
]

actions_len = len(actions)
STANDUP_ACTIONS = ['trot', 'forward', 'backward', 'turn_left', 'turn_right']

# Load sound effects
sound_effects = []
sound_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './sounds'))
os.chdir(sound_path)
for name in os.listdir(sound_path):
    sound_effects.append(name.split('.')[0])
sound_effects.sort()

sound_len = min(len(sound_effects), actions_len)
sound_effects = sound_effects[:sound_len]

# Globals
last_index = 0
last_head_pitch = 0


def do_function(index):
    global last_index, last_head_pitch
    my_dog.body_stop()

    if index < 0:
        return "Invalid action index", 400

    if index < actions_len:
        name, head_pitch_adjust, speed = actions[index]

        if last_index < len(actions) and actions[last_index][0] == 'push_up':
            last_head_pitch = 0
            my_dog.do_action('lie', speed=60)

        if name in STANDUP_ACTIONS and (last_index >= len(actions) or actions[last_index][0] not in STANDUP_ACTIONS):
            last_head_pitch = 0
            my_dog.do_action('stand', speed=60)

        if head_pitch_adjust != -1:
            last_head_pitch = head_pitch_adjust

        my_dog.head_move_raw([[0, 0, last_head_pitch]], immediately=False, speed=60)
        my_dog.do_action(name, step_count=10, speed=speed, pitch_comp=last_head_pitch)
        last_index = index
        return f"Action '{name}' executed.", 200

    elif index < actions_len + sound_len:
        sound_name = sound_effects[index - actions_len]
        my_dog.speak(sound_name, volume=80)
        last_index = index
        return f"Sound '{sound_name}' played.", 200
    else:
        return "Index out of range", 400


@app.route("/run_action", methods=["POST", "GET"])
def run_action():
    try:
        index = int(request.args.get("index", -1)) if request.method == "GET" else request.json.get("index", -1)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    if index == -1 or index == '-1':
        wake_up()
    else:
        result, status = do_function(index)
    return jsonify({"message": result}), status


@app.route("/")
def index():
    return jsonify({
        "message": "Pidog Flask API ready.",
        "endpoints": ["/run_action?index=<int>", "POST /run_action {index: int}"]
    })



async def websocket_handler():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipAddress=s.getsockname()[0]
    s.close()

    uri = f"wss://connect.speedpresta.com:7890/ws/VBRAIN-{ipAddress}-MimicDOG-Simba"  # Public echo server

    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server!")

        async def send_messages():
            while not stop_event.is_set():
                try:
                    msg = message_queue.get_nowait()
                    await websocket.send(msg)
                    print(f"> Sent: {msg}")
                except queue.Empty:
                    await asyncio.sleep(0.1)  # Avoid tight loop

        async def receive_messages():
            while not stop_event.is_set():
                try:
                    message = await websocket.recv()
                    type = json.loads(message).get("type")
                    print(f"< Received: {message}")
                    print(f"< Received: {type}")
                    #print(f"< Received: {message}")

                    if type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                        print("Sent pong response.")

                    elif type == "message":
                        # Handle incoming messages here
                        print(f"Message content: {json.loads(message).get('content')}")

                    elif type == "command":

                        index = (json.loads(message).get("message")).get("index")

                        if index == -1 or index == '-1':

                            wake_up()

                        else:

                            try:
                              
                                if index:
                                    result, status = do_function(index)
                                    print(f"Command executed: {result}")
                            except Exception as e:
                                print(f"Error executing command: {str(e)}")
                                await websocket.send(json.dumps({"type": "error", "message": str(e)}))

                        return jsonify({"message": result}), status

                    # You could also store it in a shared queue or variable
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed.")
                    break

        await asyncio.gather(send_messages(), receive_messages())

# Thread target for running the async WebSocket
def run_websocket_client():
    asyncio.run(websocket_handler())

# Flask route to send a message
@app.route("/send")
def send_message():
    msg = request.args.get("msg", "")
    if msg:
        message_queue.put(msg)
        return f"Message queued: {msg}"
    else:
        return "Please provide a message using /send?msg=your_message"
