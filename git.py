import traceback
import time
import sys
import pulsectl

from inkkeys import *
from serial import SerialException
import serial.tools.list_ports
from PIL import Image


device = Device()

def show_volume():
	with pulsectl.Pulse("inkkeys") as pulse:
		sinks = pulse.sink_list()
		name = pulse.server_info().default_sink_name
		for sink in sinks:
			if sink.name == name:
				vol = sink.volume.value_flat
		off = 0x00ff00
		on = 0xff0000
		leds = [on if vol > i/(device.nLeds-1) else off for i in range(device.nLeds)]
		device.setLeds(leds)


def test():
	pass


def setup():
	device.assignKey(KeyCode.JOG_CW, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_UP)])
	device.assignKey(KeyCode.JOG_CCW, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_DOWN)])

	device.assignKey(KeyCode.JOG_PRESS, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_MUTE)])
	device.assignKey(KeyCode.JOG_RELEASE, [])

	device.assignKey(KeyCode.SW2_PRESS, [])
	device.assignKey(KeyCode.SW2_RELEASE, [])

	device.assignKey(KeyCode.SW3_PRESS, [])
	device.assignKey(KeyCode.SW3_RELEASE, [])

	device.assignKey(KeyCode.SW4_PRESS, [])
	device.assignKey(KeyCode.SW4_RELEASE, [])

	device.assignKey(KeyCode.SW5_PRESS, [])
	device.assignKey(KeyCode.SW5_RELEASE, [])

	device.assignKey(KeyCode.SW6_PRESS, [])
	device.assignKey(KeyCode.SW6_RELEASE, [])

	device.assignKey(KeyCode.SW7_PRESS, [])
	device.assignKey(KeyCode.SW7_RELEASE, [])

	device.assignKey(KeyCode.SW8_PRESS, [])
	device.assignKey(KeyCode.SW8_RELEASE, [])

	device.assignKey(KeyCode.SW9_PRESS, [])
	device.assignKey(KeyCode.SW9_RELEASE, [])

	bg = Image.open("git.png")
	device.sendImage(0, 0, bg)
	device.updateDisplay(fullRefresh=True)

	device.registerCallback(test, KeyCode.SW2_PRESS)

	while True:
		now = time.time() #Time of this iteration
		device.poll()
		show_volume()

		timeTo30fps = time.time() - now + 0.0333
		if timeTo30fps > 0:
			time.sleep(timeTo30fps)

def connect(port):
	try:
		if device.connect(port):
			setup()
	except SerialException as e:
		print("Serial error: ", e)
	except:
		print(traceback.format_exc())
		print("Error: ", sys.exc_info()[0])


def find_port():
	VID = 0x1b4f      #USB Vendor ID for a Pro Micro
	PID = 0x9206      #USB Product ID for a Pro Micro
	for port in serial.tools.list_ports.comports():
		if port.vid != VID or port.pid != PID:
			continue
		return port.device
	return None

connect(find_port() or "/dev/pts/2")
show_volume()
