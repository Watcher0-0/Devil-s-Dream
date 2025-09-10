import socket
import threading
import random
from config.settings import PORT_RANGE, VULN_CHANCE, DEFAULT_PASSWORD
from utils.encryption import encrypt_message, decrypt_message
from utils.logger import log_event

class Device:
    used_ports = set()  

    def __init__(self, ip, ports=None, vulnerable=False):
        self.ip = ip
        self.ports = ports or self._assign_unique_ports()
        self.vulnerable = vulnerable or (random.random() < VULN_CHANCE)
        self.password = DEFAULT_PASSWORD if self.vulnerable else f"pass{random.randint(1000, 9999)}"
        self.active = True
        self.compromised = False
        self.server_threads = []

    def _assign_unique_ports(self):
        available_ports = [p for p in PORT_RANGE if p not in Device.used_ports]
        if len(available_ports) < 2:
            raise ValueError("Not enough unique ports available")
        random.shuffle(available_ports)
        ssh_port = available_ports.pop()
        http_port = available_ports.pop()
        Device.used_ports.add(ssh_port)
        Device.used_ports.add(http_port)
        return {ssh_port: "ssh", http_port: "http"}

    def start(self):
        for port, service in self.ports.items():
            thread = threading.Thread(target=self._run_service, args=(port, service), daemon=True)
            thread.start()
            self.server_threads.append(thread)

    def _run_service(self, port, service):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("127.0.0.1", port))
            server.listen(5)
            log_event(f"Device {self.ip}:{port} started {service}")
            while self.active:
                client, addr = server.accept()
                threading.Thread(target=self._handle_client, args=(client, addr, service)).start()
        except OSError as e:
            log_event(f"Port {port} on {self.ip} failed: {e}")
        finally:
            server.close()

    def _handle_client(self, client, addr, service):
        data = client.recv(1024).decode()
        if service == "ssh":
            response = self._handle_ssh(data)
        elif service == "http":
            response = self._handle_http(data)
        else:
            response = "Unknown service"
        
        if self.vulnerable and len(data) > 500:
            response = "CRASH! Shell access granted."
            self.compromised = True
            log_event(f"{self.ip} compromised via buffer overflow from {addr}")
        
        client.send(encrypt_message(response.encode()))
        client.close()

    def _handle_ssh(self, data):
        if data.strip() == self.password:
            return "Login successful"
        return "Access denied"

    def _handle_http(self, data):
        return f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n<h1>Welcome to {self.ip}</h1>"

    def shutdown(self):
        self.active = False
        log_event(f"Device {self.ip} shutting down")