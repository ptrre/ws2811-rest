# RPI WS2811 REST API

WS2811 leds driver with REST API based on Flask.

RPi WS281x Python: https://github.com/rpi-ws281x/rpi-ws281x-python

## Installation

1. Install requirement packages
    ```sh
    $ sudo apt update
    $ sudo apt install python3-venv
    ```

2. Clone the repo
    ```sh
    $ git clone https://github.com/ptrre/ws2811-rest
    ```

3. Run setup.sh script
    ```sh
    $ cd ws2811-rest
    $ chmod +x setup.sh
    $ ./setup.sh
    ```

## API

### [IP_ADDRESS]:8080/enable/<em>n</em>
   ```
   n = 0 -> turn off leds
   n = 1 -> turn on leds
   ```

### [IP_ADDRESS]:8080/scene/<em>id</em>
   ```
   Activate scene number id.
   ```

### [IP_ADDRESS]:8080/state/get
   ```
   Return the active scene and leds state.
   ````

### [IP_ADDRESS]:8080/scenes/get
   ```
   Return parameters of all scenes.
   ```
