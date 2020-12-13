#!/bin/sh

# Variables
VENV="venv"
WORK_DIR="$PWD"
cd ..
EXEC_API="$PWD/$VENV/bin/uwsgi --socket 0.0.0.0:8080 --protocol=http -w api:app"
EXEC_DRIVER="$PWD/$VENV/bin/python $WORK_DIR/wsleds.py"

# Python config
echo "Virtual environment creating..."
python3 -m venv "$VENV"
echo "Dependencies installing..."
"$VENV/bin/python" -m pip install -r "$WORK_DIR/requirements.txt"

# Services create
echo "Services creating..."
sudo bash -c 'cat > /etc/systemd/system/ws2811-api.service' << EOF
[Unit]
Description=WS2811 REST API
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=$WORK_DIR
ExecStart=$EXEC_API
Requires=ws2811-driver.service

[Install]
WantedBy=multi-user.target
EOF

sudo bash -c 'cat > /etc/systemd/system/ws2811-driver.service' << EOF
[Unit]
Description=WS2811 driver

[Service]
WorkingDirectory=$WORK_DIR
ExecStart=$EXEC_DRIVER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ws2811-api.service ws2811-driver.service
sudo systemctl start ws2811-api.service ws2811-driver.service