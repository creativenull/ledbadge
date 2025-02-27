#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Program to control a B1248 LED Name Badge (http://www.tbdled.com/en/productshow.asp?ID=P385U64S7U)
# 
# The USB driver is just a generic Virtual Serial port driver from Prolific PL2303
# VID:067B
# PID:2303
# 
# This script depends on the PySerial (2.7) and begins (0.9) modules.
#
# Author: Jeremy Stott (jeremy@stott.co.nz)

import time
import serial
import begin
import logging

COMMAND_BEGIN = [0]
COMMAND_TEXT = [2, 49, 6]
COMMAND_END = [2, 51, 1]

s = None

mirror_chars = {
    'a': 'ɒ',
    'b': 'd',
    'c': 'ɔ',
    'd': 'b',
    'e': 'ɘ',
    'f': 'ʇ',
    'g': 'ϱ',
    'h': 'ʜ',
    'i': 'i',
    'j': 'į',
    'k': 'ʞ',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'o': 'o',
    'p': 'q',
    'q': 'p',
    'r': 'ɿ',
    's': 'ƨ',
    't': 'Ɉ',
    'u': 'u',
    'v': 'v',
    'w': 'w',
    'x': 'x',
    'y': 'y',
    'z': 'z',
}

def send_command(command):
    if s:
        # Send the command
        s.write(command)
        # Sleep for 200ms, this seems to be enough to let the display execute text commands
        time.sleep(0.2)

def send_text(text, speed, mode):
    # Limit the text to 250 characters
    text = text[:250]
    # Prepend the speed, mode and length to the string
    text = str(speed) + "1" + mode + chr(len(text)) + text

    send_command(COMMAND_BEGIN)

    for pos in range(0, 256, 64):
        # Pad our text string with 0's if we need to
        text_segment = text[pos:pos+64].ljust(64, '\x00')
        # Start with the text command
        command = COMMAND_TEXT[:]
        # Append the position to write the text segment to
        command.append(pos)
        # Append the text to the command as a list of integers
        command = command + [ord(c) for c in text_segment]
        # Calculate and append the checksum
        command.append(sum(command[1:]) % 256)
        # Send the command
        send_command(command)

    send_command(COMMAND_END)    

# Send the mirrored equivalent of a text to LED badge
def send_mirror_text(text, speed, mode):
    if text == '':
        return

    mirrored_text = ''
    for char in text:
        mirrored_text += mirror_chars[char]

    send_text(mirrored_text, speed, mode)

@begin.subcommand
@begin.convert(speed=int)
def mirror_text(text, speed=5, mode='B'):
    "Display mirrored text on the LED screen"
    logging.info("Writing mirror of '{}' to display".format(text))
    send_mirror_text(text, speed, mode)
    logging.info("Done")

@begin.subcommand
@begin.convert(speed=int)
def text(text, speed=5, mode='B'):
    "Display text on the LED screen"
    logging.info("Writing '{}' to display".format(text))
    send_text(text, speed, mode)
    logging.info("Done")

@begin.subcommand
def clear():
    "Clear the LED screen"
    logging.info("Clearing the display")
    send_text('', 1, 'A')
    logging.info("Done")

@begin.start
@begin.logging
def run(serial_port='/dev/tty.usbserial'):
    global s
    try:
        s = serial.Serial(serial_port, 38400)
        logging.info("Opened serial port '{}'".format(serial_port))
    except OSError as e:
        logging.error(e)
