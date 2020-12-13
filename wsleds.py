import os, time, json, colorsys, zmq, math
from rpi_ws281x import ws, Adafruit_NeoPixel

# LEDs hardware config:
LED_COUNT      = 299     # Number of LED pixels.
LED_PIN        = 13      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 160     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # Set to 1 for GPIOs 13, 19, 41, 45 or 53
LED_MODE_GRB   = True    # Set color mode RGB (False) or GRB (True)

rainbow_table = []

def run():
    global rainbow_table
    for i in range(360):
        rainbow_table.append(color_hsv(i, 100, 40))

    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://127.0.0.1:5593")

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    ws_state = get_state()
    ws_scenes = get_scenes()
    ws_modes = get_modes()

    wait_ms = 100
    timer_effect = 0
    timer_state = 0
    offset = 0
    mod = 0
    value = 0


    while(True):
        # Update scene
        if timer_state >= 200:
            try:
                m = receiver.recv_string(zmq.NOBLOCK)
            except zmq.ZMQError as e:               
                if e.errno == zmq.EAGAIN:
                    pass
            else:
                if m == "UPDATE":
                    ws_state = get_state()
                    ws_scenes = get_scenes()
                    offset = 0
                    mod = 0
                    value = 0
                    timer_effect = wait_ms
            timer_state = 0

        # Generate effect
        if timer_effect >= wait_ms:
            if ws_state['enable'] == 1:
                for i in ws_scenes['scenes']:
                    if i['id'] is ws_state['scene']:
                        m = i['mode_id']
                        wait_ms = i['wait_ms']
                        if i['def'] is True:
                            colors = i['colors']

                        # Mode 0 (static)
                        if m is 0:
                            if i['def'] is True:
                                cycle(strip, colors)
                            else:
                                rainbow(strip)

                        # Mode 1 (cyclic)
                        elif m is 1:
                            if i['def'] is True:
                                offset = (offset + 1) % LED_COUNT
                                cycle(strip, colors, offset)
                            else:
                                offset = (offset + 1) % LED_COUNT
                                rainbow(strip, offset)
                        
                        # Mode 2 (fading)
                        elif m is 2:
                            if i['def'] is True:
                                num = len(colors)
                                if mod is 0:
                                    value += 1
                                    if value is colors[offset]['v']:
                                        mod = 1
                                elif mod is 1:
                                    value -= 1
                                    if value is 0:
                                        offset = (offset + 1) % num
                                        mod = 0
                                fading(strip, colors, offset, value)

            # Clear strip if enable is 0
            else:
                clear(strip)
                wait_ms = 100
            timer_effect = 0

        time.sleep(1/1000.0)
        timer_effect += 1
        timer_state += 1

def get_state():
    """Read state.json file"""
    f = open("json/state.json", "r")
    st = json.load(f)
    f.close()
    return st

def get_scenes():
    """Read scenes.json file"""
    f = open("json/scenes.json", "r")
    sc = json.load(f)
    f.close()
    return sc

def get_modes():
    """Read modes.json file"""
    f = open("json/modes.json", "r")
    mo = json.load(f)
    f.close()
    return mo

def color_hsv(h,s,v):
    """Convert HSV to RGB"""
    rgb = colorsys.hsv_to_rgb(h/360.0, s/100.0, v/100.0)
    return color_rgb(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def color_rgb(r, g, b):
    """Convert RGB to int"""
    if LED_MODE_GRB is True:
        return ((g << 16) | (r << 8) | b)
    else:
        return ((r << 16) | (g << 8) | b)

def clear(strip, wait_ms=0):
    """Clear strip"""
    col = [{"h": 0, "s": 0, "v": 0}]
    cycle(strip, col)

def rainbow(strip, offset=0):
    """Draw rainbow that uniformly distributes it across all pixels"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, rainbow_table[int((i+offset)*360.0/LED_COUNT)%360])
    strip.show()

def cycle(strip, colors, offset=0):
    """Draw that uniformly distributes it across all pixels"""
    num = len(colors)
    for i in range(strip.numPixels()):
        c = colors[(i + offset) % num]
        strip.setPixelColor(i, color_hsv(c['h'], c['s'], c['v']))
    strip.show()

def fading(strip, colors, offset, value):
    """Draw that fades across all pixels at once"""
    for i in range(strip.numPixels()):
        j = colors[offset]
        strip.setPixelColor(i, color_hsv(j['h'], j['s'], value))
    strip.show()

if __name__ == "__main__":
    run()