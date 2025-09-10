import time
import random
from config.settings import AI_CHECK_INTERVAL, AI_PATCH_CHANCE
from utils.logger import log_event

class AIDefender:
    def __init__(self, network):
        self.network = network
        self.running = False

    def start(self):
        self.running = True
        log_event("AI Defender activated")
        while self.running:
            self._monitor_network()
            time.sleep(AI_CHECK_INTERVAL)

    def _monitor_network(self):
        for ip, device in self.network.devices.items():
            if device.compromised:
                log_event(f"AI detected compromise on {ip}")
                self._quarantine(ip)
            elif device.vulnerable and random.random() < AI_PATCH_CHANCE:
                device.vulnerable = False
                log_event(f"AI patched vulnerability on {ip}")

    def _quarantine(self, ip):
        device = self.network.get_device(ip)
        if device:
            device.active = False
            log_event(f"AI quarantined {ip}")
            time.sleep(5)  # Simulate recovery
            device.active = True
            device.compromised = False
            log_event(f"{ip} restored from quarantine")

    def stop(self):
        self.running = False