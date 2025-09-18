from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window, ConditionalContainer
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.patch_stdout import patch_stdout
from core.network import Network
from attacks.botnet import Botnet
from attacks.ddos import launch_ddos
from attacks.exploits import exploit_buffer_overflow
from utils.logger import log_event
import asyncio
import threading
import time

#command completer
command_completer = WordCompleter(
    ["scan", "connect", "exploit", "ddos", "botnet", "status", "exit"],
    ignore_case=True
)

#style for devil's aesthetic
style = Style.from_dict({
    "prompt": "fg:#D2042D bg:#000000 bold",
    "output": "fg:#D2042D bg:#000000",
    "log": "fg:#D2042D bg:#000000",
    "error": "fg:#D2042D bg:#000000 bold",
    "status": "fg:#D2042D bg:#000000 italic",
})

class HackerInterface:
    def __init__(self, network, botnet):
        self.network = network
        self.botnet = botnet
        self.running = True

        # UI Components
        self.log_area = TextArea(
            text="Initializing...\n",
            style="class:log",
            height=5,
            scrollbar=True,
            read_only=True
        )
        self.output_area = TextArea(
            text="Welcome to Devil's Dream\nType 'status' to begin\n",
            style="class:output",
            height=5,
            read_only=True
        )
        self.input_area = TextArea(
            height=1,
            prompt="Hacker> ",
            style="class:prompt",
            completer=command_completer,
            accept_handler=self.handle_input,
            multiline=False,
            focus_on_click=True  
        )
        self.status_bar = TextArea(
            text=self._get_status(),
            style="class:status",
            height=1,
            read_only=True
        )

        self.layout = Layout(
            HSplit([
                ConditionalContainer(
                    Frame(self.log_area, title="Network Logs"),
                    filter=Condition(lambda: self.app.output.get_size().rows > 10)
                ),
                Frame(self.output_area, title="Output"),
                VSplit([
                    Window(width=8),
                    HSplit([
                        ConditionalContainer(
                            self.status_bar,
                            filter=Condition(lambda: self.app.output.get_size().rows > 8)
                        ),
                        self.input_area
                    ])
                ])
            ]),
            focused_element=self.input_area  #set initial focus
        )

        
        bindings = KeyBindings()
        @bindings.add("c-c")
        def _(event):
            self.running = False
            event.app.exit()

        self.app = Application(
            layout=self.layout,
            key_bindings=bindings,
            style=style,
            full_screen=True,
            refresh_interval=1,
            mouse_support=False  #disabling mouse to make it more keyboard focused
        )

        self.log_thread = threading.Thread(target=self._update_logs, daemon=True)

    def _get_status(self):
        active = sum(1 for d in self.network.devices.values() if d.active)
        compromised = sum(1 for d in self.network.devices.values() if d.compromised)
        return f"Active: {active}/{len(self.network.devices)} | Compromised: {compromised}"

    def _update_logs(self):
        while self.running:
            try:
                with open("network_events.log", "r") as f:
                    logs = f.read()
                self.log_area.text = logs[-500:]
                self.status_bar.text = self._get_status()
                self.app.invalidate()
            except Exception as e:
                self.log_area.text += f"\nLog error: {e}"
            time.sleep(1)  

    def handle_input(self, buffer):
        command = buffer.text.strip()
        if not command:
            return True
        
        try:
            current_output = self.output_area.text.splitlines()[-4:]
            self.output_area.text = "\n".join(current_output) + f"\n> {command}"
            log_event(f"User entered: {command}")

            parts = command.split()
            cmd = parts[0].lower()

            if cmd == "scan":
                self._do_scan(parts[1] if len(parts) > 1 else "1-10")
            elif cmd == "connect":
                if len(parts) >= 3:
                    self._do_connect(parts[1], int(parts[2]))
                else:
                    self.output_area.text += "\nUsage: connect <ip> <port>"
            elif cmd == "exploit":
                self._do_exploit(parts[1], parts[2] if len(parts) > 2 else "buffer_overflow")
            elif cmd == "ddos":
                self._do_ddos(parts[1])
            elif cmd == "botnet":
                self._do_botnet(parts[1])
            elif cmd == "status":
                self._do_status()
            elif cmd == "exit":
                self.running = False
                self.app.exit()
            else:
                self.output_area.text += "\nUnknown command"
        except Exception as e:
            self.output_area.text += f"\nError: {e}"
            log_event(f"Command error: {e}")

        self.app.invalidate()
        return True

    def _do_scan(self, ip_range):
        results = self.network.scan(ip_range)
        output = "\nScan Results:\n"
        for ip, info in results.items():
            output += f"{ip}: Ports {info['ports']}, Active: {info['active']}\n"
        self.output_area.text += output
        log_event(f"Scanned {ip_range}")

    def _do_connect(self, ip, port):
        device = self.network.get_device(ip)
        if device and int(port) in device.ports:
            self.output_area.text += f"\nConnected to {ip}:{port}."
            response = device._handle_ssh("admin123")
            self.output_area.text += f"\n{response}"
            log_event(f"Connection attempt to {ip}:{port}")
        else:
            self.output_area.text += f"\nNo service on {ip}:{port}"
            log_event(f"Connection attempt to {ip}:{port}")

    def _do_exploit(self, ip, exploit_type):
        device = self.network.get_device(ip)
        if device:
            self.output_area.text += f"\nAttempting exploit on {ip} (Vulnerable: {device.vulnerable})"
            result = exploit_buffer_overflow(device, "A" * 600)
            self.output_area.text += f"\n{result}"
            if "granted" in result:
                self.botnet.add_bot(device)
                self.output_area.text += f"\nDevice {ip} added to botnet"
        else:
            self.output_area.text += f"\nNo device at {ip}"

    def _do_ddos(self, ip):
        launch_ddos(ip, self.network)
        self.output_area.text += f"\nDDoS launched on {ip}"

    def _do_botnet(self, ip):
        self.botnet.attack(ip, self.network)
        self.output_area.text += f"\nBotnet attack launched on {ip}"

    def _do_status(self):
        self.output_area.text += f"\n{self._get_status()}"

    def run(self):
        try:
            rows, cols = self.app.output.get_size()
            if rows < 7 or cols < 40:
                print("Terminal too small! Minimum size: 7 rows, 40 columns")
                print(f"Current size: {rows} rows, {cols} columns")
                return
            log_event("Starting UI...")
            self.log_thread.start()
            with patch_stdout():
                self.app.run(set_exception_handler=True)
            log_event("UI stopped")
        except Exception as e:
            print(f"UI Error: {e}")
            log_event(f"UI Error: {e}")

def start_interface(network, botnet):
    ui = HackerInterface(network, botnet)
    ui.run()
