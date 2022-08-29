import redis
import prometheus_client
from motor import Motor
from metrics import Metrics

motor = None

def motor_left(message):
  global motor
  speed = float(message['data'])
  if motor.left_spd != speed:
    motor.left_spd = speed
    metrics.update_left_motor(speed)

def motor_right(message):
  global motor
  speed = float(message['data'])
  if motor.right_spd != speed:
    motor.right_spd = speed
    metrics.update_right_motor(speed)


def main():
  global motor, metrics
  motor = Motor()
  metrics = Metrics()
  r = redis.Redis(host='192.168.1.123', port=30002)
  pubsub = r.pubsub()
  pubsub.subscribe(**{'motor_left': motor_left})
  pubsub.subscribe(**{'motor_right': motor_right})
  thread = pubsub.run_in_thread(sleep_time=0.001)


  while True:
    motor.left_spd = float(input('left: '))/100
    motor = r.right_spd = float(input('right: '))/100

if __name__ == '__main__':
  main()
