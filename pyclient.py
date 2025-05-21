import sys
import argparse
import socket
# import driver
import driver_model as driver
import msgParser
import csv
import os
import time

# Argument parser setup
parser = argparse.ArgumentParser(description='TORCS Python client with confirm-on-save telemetry logging.')
parser.add_argument('--host', default='localhost', help='Server IP address')
parser.add_argument('--port', type=int, default=3001, help='Server port')
parser.add_argument('--id', default='SCR', help='Bot ID')
parser.add_argument('--maxEpisodes', type=int, default=1, help='Number of episodes')
parser.add_argument('--maxSteps', type=int, default=1000, help='Max steps per episode')
parser.add_argument('--track', default='unknown', help='Track name')
parser.add_argument('--stage', type=int, default=3, help='Stage: 0=WarmUp, 1=Qual, 2=Race, 3=Unknown')
args = parser.parse_args()

# UDP socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)

# Instantiate driver in manual mode
d = driver.Driver(args.stage, manual_mode=True)
mp = msgParser.MsgParser()

# Prepare metadata
csv_filename = f'telemetry_log_{args.track}.csv'
fieldnames = [
    'timestamp', 'trackName', 'angle', 'curLapTime', 'damage', 'distFromStart', 'distRaced',
    'fuel', 'gear', 'lastLapTime', 'racePos', 'rpm', 'speedX', 'speedY', 'speedZ',
    'trackPos', 'z',
    *[f'track_{i}' for i in range(19)],
    *[f'opponent_{i}' for i in range(36)],
    *[f'focus_{i}' for i in range(5)],
    'accel', 'brake', 'gear_cmd', 'steer', 'clutch', 'meta'
]

# We'll buffer all rows here
buffered_rows = []

shutdownClient = False
curEpisode = 0

while not shutdownClient:
    # Handshake with server
    while True:
        init_msg = args.id + d.init()
        sock.sendto(init_msg.encode(), (args.host, args.port))
        try:
            buf, _ = sock.recvfrom(1000)
            buf = buf.decode()
        except socket.error:
            continue
        if '***identified***' in buf:
            print('Identified by server')
            break

    currentStep = 0
    while True:
        try:
            buf, _ = sock.recvfrom(1000)
            buf = buf.decode()
        except socket.error:
            continue

        if '***shutdown***' in buf:
            d.onShutDown()
            shutdownClient = True
            break
        if '***restart***' in buf:
            d.onRestart()
            break

        sensors = mp.parse(buf)
        action_msg = d.drive(buf)
        ctrl = d.control

        # Build the row dict exactly as before
        row = {
            'timestamp': time.time(),
            'trackName': args.track,
            'angle': sensors.get('angle', [''])[0],
            'curLapTime': sensors.get('curLapTime', [''])[0],
            'damage': sensors.get('damage', [''])[0],
            'distFromStart': sensors.get('distFromStart', [''])[0],
            'distRaced': sensors.get('distRaced', [''])[0],
            'fuel': sensors.get('fuel', [''])[0],
            'gear': sensors.get('gear', [''])[0],
            'lastLapTime': sensors.get('lastLapTime', [''])[0],
            'racePos': sensors.get('racePos', [''])[0],
            'rpm': sensors.get('rpm', [''])[0],
            'speedX': sensors.get('speedX', [''])[0],
            'speedY': sensors.get('speedY', [''])[0],
            'speedZ': sensors.get('speedZ', [''])[0],
            'trackPos': sensors.get('trackPos', [''])[0],
            'z': sensors.get('z', [''])[0],
            'accel': ctrl.getAccel(),
            'brake': ctrl.getBrake(),
            'gear_cmd': ctrl.getGear(),
            'steer': ctrl.getSteer(),
            'clutch': ctrl.getClutch(),
            'meta': ctrl.getMeta()
        }
        # Expand arrays
        for i, v in enumerate(sensors.get('track', [0]*19)):
            row[f'track_{i}'] = v
        for i, v in enumerate(sensors.get('opponents', [0]*36)):
            row[f'opponent_{i}'] = v
        for i, v in enumerate(sensors.get('focus', [0]*5)):
            row[f'focus_{i}'] = v

        # Buffer it, instead of writing immediately
        buffered_rows.append(row)

        currentStep += 1
        if currentStep >= args.maxSteps:
            sock.sendto('(meta 1)'.encode(), (args.host, args.port))
        else:
            sock.sendto(action_msg.encode(), (args.host, args.port))

    curEpisode += 1
    if curEpisode >= args.maxEpisodes:
        shutdownClient = True

sock.close()

# --- After the run, ask the user ---
if not buffered_rows:
    print("No data was collected.")
    sys.exit(0)

resp = input(f"\nCollected {len(buffered_rows)} rows of data. Save to '{csv_filename}'? (y/N): ").strip().lower()
if resp == 'y':
    write_header = not os.path.exists(csv_filename)
    with open(csv_filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(buffered_rows)
    print(f"✓ Data saved to {csv_filename}")
else:
    print("Discarded collected data.")

