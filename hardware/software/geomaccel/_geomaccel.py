"""Optional CPU native extension. No hardware backend is implemented."""
try:
 import _geomaccel_c as native
except ImportError:
 native=None
BACKEND='cpu-native' if native is not None else 'unavailable'
def backend_name():return BACKEND
