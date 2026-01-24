import serial
import serial.tools.list_ports
import threading
import time

class SerialLink:
    def __init__(self, logger=None):
        self.ser = None
        self.running = False
        self.thread = None
        self.logger_callback = logger
        
        # Shared Data
        self.current_position = 0.0
        self.status_message = "DISCONNECTED"
        self.is_connected = False
        self.last_p_time = 0

    def _log(self, msg):
        if self.logger_callback:
            self.logger_callback(msg)
        else:
            print(msg)

    def get_ports(self):
        """Return list of available COM ports."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.is_connected = True
            self.running = True
            self.status_message = "CONNECTED"
            self._log(f"Connected to {port}")
            
            # Reset Arduino on connect (DTR toggle)
            self.ser.dtr = False
            time.sleep(1)
            self.ser.flushInput()
            self.ser.dtr = True
            time.sleep(2) # Wait for bootloader

            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            self.status_message = f"ERROR: {str(e)}"
            self.is_connected = False
            self._log(f"Connection Failed: {e}")
            return False

    def disconnect(self):
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
        self.status_message = "DISCONNECTED"
        self._log("Disconnected")

    def send_command(self, cmd):
        """Send a string command to Arduino."""
        if self.ser and self.ser.is_open:
            if not cmd.endswith('\n'):
                cmd += '\n'
            try:
                self.ser.write(cmd.encode('utf-8'))
                self._log(f"TX: {cmd.strip()}")
            except Exception as e:
                self._log(f"TX ERROR: {e}")

    def _read_loop(self):
        """Background thread to read serial line by line."""
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self._parse_line(line)
            except Exception as e:
                self._log(f"RX ERROR: {e}")
                self.running = False
                break
            time.sleep(0.01) # Yield

    def _parse_line(self, line):
        # Position Report: P12.345
        if line.startswith('P'):
            try:
                self.current_position = float(line[1:])
                self.last_p_time = time.time()
            except ValueError:
                pass
        # Status Report: STATUS:READY
        elif line.startswith('STATUS:'):
            self.status_message = line.split(':')[1]
            self._log(f"RX STATUS: {self.status_message}")
        # Other debug messages
        else:
            self._log(f"RX RAW: {line}")
