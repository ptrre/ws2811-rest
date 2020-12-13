import os, json, zmq
from flask import Flask, jsonify, make_response

f = open("json/state.json", "r")
ws_state = json.load(f)
f.close()
f = open("json/scenes.json", "r")
ws_scenes = json.load(f)
f.close()

context = zmq.Context()
sink = context.socket(zmq.PUSH)
sink.connect("tcp://127.0.0.1:5593")

app = Flask(__name__)

def send_update_signal():
    global sink
    sink.send_string("UPDATE")

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/')
def home():
    return "WS2811 driver with REST API"

@app.route('/state/get/')
def get_state():
    return jsonify(ws_state)

@app.route('/scenes/get/')
def get_scenes():
    return jsonify(ws_scenes)

@app.route('/enable/<state>/')    
def enable_leds(state):
    global ws_state
    ws_state['enable'] = int(state)
    f = open("json/state.json", "w")
    json.dump(ws_state, f)
    f.close()
    send_update_signal()
    return make_response(jsonify({'status': 'OK'}), 200)

@app.route('/scene/<scene_id>/')    
def set_scene(scene_id):
    global ws_state
    ws_state['scene'] = int(scene_id)
    f = open("json/state.json", "w")
    json.dump(ws_state, f)
    f.close()
    send_update_signal()
    return make_response(jsonify({'status': 'OK'}), 200)
