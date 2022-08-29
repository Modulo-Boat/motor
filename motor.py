import serial
import subprocess
import time
from threading import Thread

class Motor:
  LEFT = 1
  RIGHT = 5
  def __init__(self, port='/dev/ttyTHS1'):
    self.int_arr = [0xa6, 0x0, 0x0, 0x0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0, 0x0,
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x0]
    self.left_spd = 0.0
    self.right_spd = 0.0
    self.counter = 0
    self.ser = serial.Serial(port, baudrate=115200, bytesize=8, parity='N', 
                             stopbits=1,timeout=0.2)
    self.wrap_to_data(0, 1)
    self.wrap_to_data(0, 5)
    self.update_check_digit()
    print("send: ", self.int_arr, flush=True)
    print("========================================", flush=True)
    while True:
      try:
        self.ser.write(serial.to_bytes(self.int_arr))
        self.ser.write("\n".encode('utf-8'))
        break
      except:
        continue
    time.sleep(0.2)

    for t in (self.receive, self.send):
      Thread(target=t).start()
    

  def wrap_to_data(self, inta, b):
    inta = int(inta * 1000000) % 2**32
    inta = ''.join([format(inta, '#010x')])[2:]
    for i in range(0,len(inta),2):
      self.int_arr[b+int(i/2)] = int(inta[i:i+2],16)

  def update_check_digit(self):
    self.counter +=1
    if self.counter==256:
      self.counter = 0
    checksum = 0
    self.int_arr[14] = self.counter
    for i in self.int_arr[:-2]:
      checksum += i
    self.int_arr[15] = checksum % 256

  def calculate_checksum(self, split_strings):
    checksum = 0
    for i in split_strings[:-2]:
      checksum += i
    return checksum % 256 == split_strings[15]
    
  def read_motor_spd(split_strings,left_or_right):
    if left_or_right == 0:
      left_or_right = 1
    else:
      left_or_right = 5
    speed = int('0x' + ''.join([format(c, '02X') for c in split_strings[left_or_right:left_or_right+4]]),16)
    speed = (speed+2**31) % 2**32 - 2**31
    return speed / 1000000

  def convert_to_bytes(self):
    s = ''
    for i in self.int_arr:
      s += ('0' if len(hex(i)[2:]) == 1 else '') + hex(i)[2:]
    return bytes.fromhex(s)

  def receive(self):
    while True:
      split_strings = []
      newdata_hex = ""
      newdata_hex=self.ser.readline().hex()
      if newdata_hex[-2:]=="0a" and len(newdata_hex) == 36:
        newdata_hex = newdata_hex[:-2]
      if newdata_hex.startswith("a7") and len(newdata_hex)<32:
        while len(newdata_hex)<32 :
          newdata_hex = ''.join((newdata_hex,self.ser.readline().hex()))
          if newdata_hex[-2:]=="0a" and len(newdata_hex) == 36:
            newdata_hex = newdata_hex[:-2]
          print("combined data=",newdata_hex,"len=", len(newdata_hex), flush=True)
      if not newdata_hex.startswith("a7") or 1<len(newdata_hex)<32:
        print("========================================", flush=True)
      else:
          for index in range(0,len(newdata_hex),2):
            split_strings.append(int(newdata_hex[index : index + 2],16))
          print("read: ",split_strings, flush=True)
          counter = split_strings[14]
          check_check_digit = self.calculate_checksum(split_strings)
          print("valid data=",check_check_digit, flush=True)

  def send(self):
    while True:
      self.wrap_to_data(self.left_spd, Motor.LEFT)
      self.wrap_to_data(self.right_spd, Motor.RIGHT)
      self.update_check_digit()
      while True:
        try:
          self.ser.write(serial.to_bytes(self.int_arr))
          self.ser.write("\n".encode('utf-8'))
          break
        except:
          continue
      time.sleep(0.2)