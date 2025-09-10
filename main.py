from core.network import Network
from core.ai_defender import AIDefender
from attacks.botnet import Botnet
from ui.interface import start_interface
import threading

def main():
    network = Network()
    botnet = Botnet()
    ai = AIDefender(network)
    
    threading.Thread(target=ai.start, daemon=True).start()
    
    start_interface(network, botnet)

if __name__ == "__main__":
    main()