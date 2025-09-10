from utils.logger import log_event

class Botnet:
    def __init__(self):
        self.bots = []

    def add_bot(self, device):
        if device not in self.bots and device.compromised:
            self.bots.append(device)
            log_event(f"Added {device.ip} to botnet")

    def attack(self, target_ip, network):
        target = network.get_device(target_ip)
        if not target or len(self.bots) < 5:
            log_event("Botnet attack failed: insufficient bots or invalid target")
            return
        log_event(f"Botnet attacking {target_ip} with {len(self.bots)} bots")
        for bot in self.bots:
            # Simulate sending packets
            if target.active:
                target.active = False
                log_event(f"Bot {bot.ip} downed {target_ip}")
                break