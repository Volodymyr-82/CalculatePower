import numpy as np

class PowerCalculator:
  """
   App calculates all the kind of powers
  """
  def __init__(self, voltage: np.ndarray, current: np.ndarray, angles: np.ndarray) -> None:
     self.voltage = voltage
     self.current = current
     self.angles = angles

  def calculate_active_power(self) -> np.ndarray:
    P = self.voltage * self.current * np.cos(np.radians(self.angles))
    return P

  def calculate_apparent_power(self) -> np.ndarray:
    S = self.voltage * self.current 
    return S

  def calculate_reactive_power(self) -> np.ndarray:
    Q = self.voltage * self.current * np.sin(np.radians(self.angles))
    return Q

