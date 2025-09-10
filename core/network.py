import random
from config.settings import BASE_IP, DEVICE_COUNT
from core.device import Device
from utils.logger import log_event

class Network:
    def __init__(self):
        self.devices = {}
        self._initialize_devices()

    def _initialize_devices(self):
        for i in range(1, DEVICE_COUNT + 1):
            ip = f"{BASE_IP}{i}"
            device = Device(ip)
            self.devices[ip] = device
            device.start()
        log_event(f"Network initialized with {DEVICE_COUNT} devices")

    def get_device(self, ip):
        return self.devices.get(ip)

    def scan(self, ip_range):
        results = {}
        start, end = map(int, ip_range.split("-"))
        for i in range(start, end + 1):
            ip = f"{BASE_IP}{i}"
            if ip in self.devices:
                device = self.devices[ip]
                results[ip] = {"ports": list(device.ports.keys()), "active": device.active}
        return results

    def shutdown(self):
        for device in self.devices.values():
            device.shutdown()