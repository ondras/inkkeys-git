import traceback
import time
import sys
import pulsectl

from inkkeys import *
from serial import SerialException
import serial.tools.list_ports
from PIL import Image
from pynput.keyboard import Key, Controller


device = Device()
keyboard = Controller()


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


def commit():
	for ch in 'git commit -am ""':
		keyboard.press(ch)
		keyboard.release(ch)
	keyboard.press(Key.left)
	keyboard.release(Key.left)


def ebp():
	for ch in "~/git/util/src/email-buildpackage":
		keyboard.press(ch)
		keyboard.release(ch)
	keyboard.press(Key.enter)
	keyboard.release(Key.enter)


def charToKeycode(ch):
	if ch == " ":
		return KeyboardKeycode.KEY_SPACE
	elif ch == "\n":
		return KeyboardKeycode.KEY_ENTER
	elif ch == "-":
		return KeyboardKeycode.KEYPAD_SUBTRACT
	elif ch == "+":
		return KeyboardKeycode.KEYPAD_ADD
	attr = getattr(KeyboardKeycode, "KEY_" + ch.upper(), None)
	if attr:
		return attr
	raise Exception("Cannot convert {} to keycode".format(ch))


def command(str):
	events = [event(DeviceCode.KEYBOARD, charToKeycode(ch)) for ch in str]
	return events


def setup():
	device.assignKey(KeyCode.JOG_CW, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_UP)])
	device.assignKey(KeyCode.JOG_CCW, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_DOWN)])

	device.assignKey(KeyCode.JOG_PRESS, [event(DeviceCode.CONSUMER, ConsumerKeycode.MEDIA_VOL_MUTE)])
	device.assignKey(KeyCode.JOG_RELEASE, [])

	device.assignKey(KeyCode.SW2_PRESS, command("git merge "))
	device.assignKey(KeyCode.SW2_RELEASE, [])
	device.registerCallback(commit, KeyCode.SW2_PRESS)

	device.assignKey(KeyCode.SW3_PRESS, command("git diff\n"))
	device.assignKey(KeyCode.SW3_RELEASE, [])

	device.assignKey(KeyCode.SW4_PRESS, [])  # commit
	device.assignKey(KeyCode.SW4_RELEASE, [])

	device.assignKey(KeyCode.SW5_PRESS, command("git push\n"))
	device.assignKey(KeyCode.SW5_RELEASE, [])

	device.assignKey(KeyCode.SW6_PRESS, command("git checkout -b "))
	device.assignKey(KeyCode.SW6_RELEASE, [])

	device.assignKey(KeyCode.SW7_PRESS, [])  # EBP
	device.assignKey(KeyCode.SW7_RELEASE, [])
	device.registerCallback(ebp, KeyCode.SW7_PRESS)

	device.assignKey(KeyCode.SW8_PRESS, command("git status\n"))
	device.assignKey(KeyCode.SW8_RELEASE, [])

	device.assignKey(KeyCode.SW9_PRESS, command("git pull\n"))
	device.assignKey(KeyCode.SW9_RELEASE, [])

	bg = Image.open("git.png")
	device.sendImage(0, 0, bg)
	device.updateDisplay(fullRefresh=True)


def loop():
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
			loop()
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

connect(find_port() or "/dev/pts/3")
