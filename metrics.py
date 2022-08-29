import prometheus_client

class Metrics:
  def __init__(self, interval_seconds=0):   
    self.left_motor = prometheus_client.Gauge("left_motor_level", "Left motor level")
    self.right_motor = prometheus_client.Gauge("right_motor_level", "Right motor level")
    prometheus_client.start_http_server(9090)

  def update_left_motor(self, number):
    self.left_motor.set(number)

  def update_right_motor(self, number):
    self.right_motor.set(number)
