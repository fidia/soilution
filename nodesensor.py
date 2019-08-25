#!/usr/bin/env python3

import sys
import json
import time
import random
from datetime import datetime
import time
import uuid

import paho.mqtt.client as mqtt

def generate(host, port, username, password, topic, sensors, interval_ms, verbose):

    mqttc = mqtt.Client()

    if username:
        mqttc.username_pw_set(username, password)

    mqttc.connect(host, port)

    keys = list(sensors.keys())
    interval_secs = interval_ms / 10000.0

    while True:
        id = str(uuid.uuid4())
        sensor_id = random.choice(keys)
        sensor = sensors[sensor_id]

        #Temperatur
        min_valtemp, max_valtemp = sensor.get("range1", [0, 100])
        valtemp = random.randint(min_valtemp, max_valtemp)

        #Humidity
        min_valhum, max_valhum = sensor.get("range2", [0, 100])
        valhum = random.randint(min_valhum, max_valhum)

        #pH
        min_valph, max_valph = sensor.get("range3", [0, 100])
        valph = random.randint(min_valph, max_valph)

        waktu = datetime.now()
        data = {
            "id": id,
            "sensor": sensor_id,
            "suhu": valtemp, "kelembapan": valhum, "pH": valph,  "waktu": waktu.strftime("%Y-%m-%d %H:%M:%S")
        }

        for key in ["lat", "lng", "type1", "type2", "type3"]:
            value = sensor.get(key)

            if value is not None:
                data[key] = value

        payload = json.dumps(data)

        if verbose:
            print("%s: %s" % (topic, payload))

        mqttc.publish(topic, payload)
        time.sleep(interval_secs)

def main(config_path):
    """load dan validasi config dan call generate"""
    try:
        with open(config_path) as handle:
            config = json.load(handle)
            mqtt_config = config.get("mqtt", {})
            misc_config = config.get("misc", {})
            sensors = config.get("sensors")

            interval_ms = misc_config.get("interval_ms", 500)
            verbose = misc_config.get("verbose", False)

            if not sensors:
                print("no sensors")
                return

            host = mqtt_config.get("host", "10.0.1.83")
            port = mqtt_config.get("port", 1883)
            username = mqtt_config.get("username", "digitalent2019")
            password = mqtt_config.get("password", "12345678")
            topic = mqtt_config.get("topic", "sensors")

            generate(host, port, username, password, topic, sensors, interval_ms, verbose)
    except IOError as error:
        print("Error opening config file '%s'" % config_path, error)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("usage %s config.json" % sys.argv[0])