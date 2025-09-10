import random

def generate_random_ip(base):
    return f"{base}{random.randint(1, 255)}"

def simulate_packet_loss():
    return random.random() < 0.05  #5% chance