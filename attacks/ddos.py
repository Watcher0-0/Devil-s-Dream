import time
import random
import threading
from config.settings import DDOS_PACKET_SIZE, DDOS_RATE
from utils.logger import log_event

def launch_ddos(target_ip, network):
    target = network.get_device(target_ip)
    if not target:
        log_event("DDoS failed: invalid target")
        return
    
    def flood():
        while target.active:
            log_event(f"DDoS flooding {target_ip}")
            time.sleep(DDOS_RATE)
            # Simulate overload
            if random.random() < 0.2:
                target.active = False
                log_event(f"DDoS downed {target_ip}")
                break
    
    threading.Thread(target=flood, daemon=True).start()
