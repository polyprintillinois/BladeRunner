import tkinter as tk
from tkinter import ttk, messagebox
from serial_link import SerialLink
import time
import os
import sys
import ctypes
from PIL import Image, ImageTk

# --- Constants ---
WINDOW_TITLE = "BladeRunner"
WINDOW_SIZE = "500x600" # Increased height
MAX_TRAVEL = 45.0
MIN_TRAVEL = 0.0
MAX_SPEED_LIMIT = 30.0
MAX_ACCEL_LIMIT = 1000.0 # Safety cap

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)

class LinearStageApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
    # Set Icon
    # Set Icons
        try:
            base_path = os.path.dirname(__file__)
            images = []

            # 1. Taskbar Icon (Large) -> logo.png
            logo_path = resource_path("logo.png")
            if os.path.exists(logo_path):
                img_logo = Image.open(logo_path)
                images.append(ImageTk.PhotoImage(img_logo)) # High res for taskbar

            # 2. Title Bar Icon (Small) -> icon.png
            icon_path = resource_path("icon.png")
            if os.path.exists(icon_path):
                # Resize specifically for title bar preference
                img_icon = Image.open(icon_path).resize((16, 16), Image.LANCZOS)
                images.append(ImageTk.PhotoImage(img_icon))

            if images:
                self._icon_refs = images # Keep reference
                # Tkinter will choose the best size from the provided list
                self.root.iconphoto(False, *images)
                
        except Exception as e:
            print(f"Icon Error: {e}")

        self.serial = SerialLink(logger=self.log_message) # Pass logger
        self.is_homed = False # Safety flag
        
        # State variables for display
        self.current_speed_setting = 5.0
        self.current_accel_setting = 500.0
        
        self._init_ui()
        self._start_update_loop()

    # ... (rest of methods)

# ...



    def _init_ui(self):
        # 1. Connection Frame
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="Port:").pack(side="left")
        self.port_combo = ttk.Combobox(conn_frame, values=self.serial.get_ports(), width=10)
        self.port_combo.pack(side="left", padx=5)
        self.port_combo.bind("<Button-1>", self._refresh_ports)
        
        ttk.Button(conn_frame, text="Refresh", command=self._refresh_ports).pack(side="left", padx=2)
        
        self.btn_connect = ttk.Button(conn_frame, text="Connect", command=self._toggle_connection)
        self.btn_connect.pack(side="left", padx=5)

        # 2. Status & Position Display
        status_frame = ttk.Frame(self.root, padding=10)
        status_frame.pack(fill="x", padx=10)
        
        # Big Position Number
        self.lbl_pos = ttk.Label(status_frame, text="0.000 mm", font=("Helvetica", 24, "bold"))
        self.lbl_pos.pack()
        
        # Current Settings Display
        self.lbl_settings = ttk.Label(status_frame, text="Speed: -- | Accel: --", font=("Helvetica", 10))
        self.lbl_settings.pack(pady=(0, 5))
        
        self.lbl_status = ttk.Label(status_frame, text="DISCONNECTED", foreground="red")
        self.lbl_status.pack()

        # 3. Emergency Stop (Always Visible)
        stop_frame = ttk.Frame(self.root, padding=5)
        stop_frame.pack(fill="x", padx=10)
        self.btn_estop = tk.Button(stop_frame, text="EMERGENCY STOP", bg="red", fg="white", 
                                   font=("Arial", 12, "bold"), height=2, command=self._emergency_stop)
        self.btn_estop.pack(fill="x")

        # 4. Motion Control Frame (Compacted)
        self.control_frame = ttk.LabelFrame(self.root, text="Motion Control", padding=10)
        self.control_frame.pack(fill="x", padx=10, pady=5) # Removed expand=True
        
        # Homing
        ttk.Button(self.control_frame, text="HOME AXIS (Required)", command=self._cmd_home).pack(fill="x", pady=5)
        
        # Move Absolute
        abs_frame = ttk.Frame(self.control_frame)
        abs_frame.pack(fill="x", pady=5)
        ttk.Label(abs_frame, text="Go To (mm):").pack(side="left")
        self.ent_abs = ttk.Entry(abs_frame, width=10)
        self.ent_abs.pack(side="left", padx=5)
        ttk.Button(abs_frame, text="GO", command=self._cmd_move_abs).pack(side="left")

        # Jog
        jog_frame = ttk.Frame(self.control_frame)
        jog_frame.pack(fill="x", pady=5)
        ttk.Label(jog_frame, text="Jog Step (mm):").pack(side="left")
        self.ent_jog = ttk.Entry(jog_frame, width=10)
        self.ent_jog.insert(0, "1.0")
        self.ent_jog.pack(side="left", padx=5)
        
        self.btn_jog_neg = ttk.Button(jog_frame, text="<< [-]", command=lambda: self._cmd_jog(-1))
        self.btn_jog_neg.pack(side="left")
        self.btn_jog_pos = ttk.Button(jog_frame, text="[+] >>", command=lambda: self._cmd_jog(1))
        self.btn_jog_pos.pack(side="left")
        
        # 5. Motion Parameters (Moved up)
        set_frame = ttk.LabelFrame(self.root, text="Motion Parameters", padding=10)
        set_frame.pack(fill="x", padx=10, pady=5)
        
        # Speed
        ttk.Label(set_frame, text="Speed (mm/s):").pack(side="left")
        self.ent_speed = ttk.Entry(set_frame, width=5)
        self.ent_speed.insert(0, "5")
        self.ent_speed.pack(side="left", padx=5)
        
        # Accel
        ttk.Label(set_frame, text="Accel (mm/s²):").pack(side="left")
        self.ent_accel = ttk.Entry(set_frame, width=5)
        self.ent_accel.insert(0, "500")
        self.ent_accel.pack(side="left", padx=5)
        
        ttk.Button(set_frame, text="Set", command=self._cmd_set_params).pack(side="left")

        # 7. Credits (Packed bottom to ensure visibility)
        ttk.Label(self.root, text="Created by Changhyun Hwang (2026)", font=("Arial", 8), foreground="gray").pack(side="bottom", anchor="e", padx=10, pady=(5, 5))

        # 6. Terminal Log
        log_frame = ttk.LabelFrame(self.root, text="Terminal Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.txt_log = tk.Text(log_frame, height=10, state="disabled", font=("Consolas", 9))
        self.txt_log.pack(fill="both", expand=True)



        # Initial State
        self._update_settings_display() # Default display
        


    def log_message(self, message):
        """Append message to log widget."""
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def _refresh_ports(self, event=None):
        ports = self.serial.get_ports()
        self.port_combo['values'] = ports
        if ports and not self.port_combo.get():
             self.port_combo.current(0)
        if event is None: # Manual click
            self.log_message(f"Ports refreshed: {ports}")

    def _toggle_connection(self):
        if not self.serial.is_connected:
            port = self.port_combo.get()
            if not port:
                messagebox.showerror("Error", "Select a COM port first.")
                return
            if self.serial.connect(port):
                self.btn_connect.config(text="Disconnect")
                self._update_settings_display() # Update display on connect (though we don't read back yet, we assume defaults or what we send)
                # Ideally we send defaults on connect or rely on user to Set.
                # Let's send our defaults to sync
                self._cmd_set_params(silent=True)
            else:
                messagebox.showerror("Error", f"Failed to connect to {port}")
        else:
            self.serial.disconnect()
            self.btn_connect.config(text="Connect")
            self.is_homed = False



    def _update_settings_display(self):
        if self.serial.is_connected:
            self.lbl_settings.config(text=f"Speed: {self.current_speed_setting} mm/s | Accel: {self.current_accel_setting} mm/s²")
        else:
            self.lbl_settings.config(text="Speed: -- | Accel: --")

    def _emergency_stop(self):
        self.serial.send_command("S")
        self.lbl_status.config(text="EMERGENCY STOP SENT", foreground="red")
        self.is_homed = False # Assume lost position validity

    def _cmd_home(self):
        if not self.serial.is_connected: return
        response = messagebox.askyesno("Confirm Homing", "Ensure path is clear. Start Homing?")
        if response:
            self.serial.send_command("H")
            self.is_homed = False # Wait for STATUS:HOMED to set true

    def _cmd_move_abs(self):
        if not self._check_ready(): return
        try:
            val = float(self.ent_abs.get())
            if not (MIN_TRAVEL <= val <= MAX_TRAVEL):
                messagebox.showwarning("Range Error", f"Target {val} is out of bounds (0-40).")
                return
            self.serial.send_command(f"G{val}")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid number.")

    def _cmd_jog(self, direction):
        if not self._check_ready(): return
        try:
            step = float(self.ent_jog.get())
            val = step * direction
            
            # Predict target
            curr = self.serial.current_position
            target = curr + val
            
            if not (MIN_TRAVEL <= target <= MAX_TRAVEL):
                messagebox.showwarning("Range Error", f"Jog target {target:.2f} is out of bounds.")
                return
            
            self.serial.send_command(f"J{val}")
            
        except ValueError:
            messagebox.showerror("Input Error", "Invalid number.")

    def _cmd_set_params(self, silent=False):
        if not self.serial.is_connected: return
        try:
            spd = float(self.ent_speed.get())
            acc = float(self.ent_accel.get())
            
            # Validation
            if spd <= 0 or spd > MAX_SPEED_LIMIT:
                if not silent: messagebox.showwarning("Param Error", f"Speed must be 0 < speed <= {MAX_SPEED_LIMIT}")
                return
            if acc <= 0 or acc > MAX_ACCEL_LIMIT:
                 if not silent: messagebox.showwarning("Param Error", f"Accel must be 0 < accel <= {MAX_ACCEL_LIMIT}")
                 return

            self.serial.send_command(f"V{spd}")
            time.sleep(0.05) 
            self.serial.send_command(f"A{acc}")
            
            self.current_speed_setting = spd
            self.current_accel_setting = acc
            self._update_settings_display()
            
            if not silent:
                print(f"Params Set: V={spd}, A={acc}")
                
        except ValueError:
            if not silent: messagebox.showerror("Input Error", "Invalid number for parameters.")

    def _check_ready(self):
        if not self.serial.is_connected: return False
        if not self.is_homed:
            messagebox.showwarning("Not Homed", "Please Home the stage first.")
            return False
        return True

    def _start_update_loop(self):
        """Periodic UI update"""
        # Update Position
        self.lbl_pos.config(text=f"{self.serial.current_position:.3f} mm")
        
        # Update Status Message
        raw_status = self.serial.status_message
        self.lbl_status.config(text=raw_status)
        
        # Handle Logic based on status
        if "HOMED" in raw_status:
            self.is_homed = True
            self.lbl_status.config(foreground="green")
        elif "STOP" in raw_status or "ERROR" in raw_status or "DISCONNECTED" in raw_status:
           # self.is_homed = False # Keep homed unless forced? 
           # If emergency stop, we might have lost position steps or stalled. Safest to un-home.
           if "STOP" in raw_status: self.is_homed = False
           self.lbl_status.config(foreground="red")
        
        # Toggle buttons based on state
        if not self.serial.is_connected: 
            self.is_homed = False

        self.root.after(100, self._start_update_loop)

if __name__ == "__main__":
    # Set Taskbar Icon (Windows)
    try:
        appid = u'antigravity.bladerunner.linearstage.v3' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except Exception:
        pass

    root = tk.Tk()
    app = LinearStageApp(root)
    root.mainloop()
