"""
GUI Interface for AutoDraw AI Agent
Provides a user-friendly interface for natural language drawing requests
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
from datetime import datetime
import os
from typing import Dict, List
import pythoncom

from autodraw_ai_agent import AutoDrawAIAgent
import config

class AutoDrawAIGUI:
    """
    Graphical User Interface for AutoDraw AI Agent
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("AutoDraw AI Agent - AutoCAD Drawing Automation")
        self.root.geometry("1000x700")
        
        # Initialize AI Agent
        self.agent = None
        self.is_connected = False
        
        # Create GUI components
        self.create_widgets()
        self.setup_layout()
        
        # Status variables
        self.processing = False
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="AutoDraw AI Agent", 
            font=("Arial", 16, "bold")
        )
        
        # Connection frame
        self.connection_frame = ttk.LabelFrame(self.main_frame, text="AutoCAD Connection", padding="10")
        
        self.connect_btn = ttk.Button(
            self.connection_frame, 
            text="Connect to AutoCAD", 
            command=self.connect_to_autocad
        )
        
        self.status_label = ttk.Label(
            self.connection_frame, 
            text="Status: Not Connected", 
            foreground="red"
        )
        
        # Input frame
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Drawing Request", padding="10")
        
        # Natural language input
        ttk.Label(self.input_frame, text="Describe your drawing requirements:").pack(anchor="w")
        
        self.input_text = scrolledtext.ScrolledText(
            self.input_frame, 
            height=6, 
            width=80,
            wrap=tk.WORD
        )
        
        # Example requests
        self.example_frame = ttk.LabelFrame(self.input_frame, text="Example Requests", padding="5")
        
        examples = [
            "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature",
            "Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens",
            "Design a magneto track system 12 feet long with 75W fixtures every 2 feet"
        ]
        
        for example in examples:
            example_btn = ttk.Button(
                self.example_frame,
                text=example[:50] + "...",
                command=lambda ex=example: self.load_example(ex)
            )
            example_btn.pack(fill="x", pady=2)
        
        # Quick templates frame
        self.templates_frame = ttk.LabelFrame(self.input_frame, text="Quick Templates", padding="5")
        
        templates = [
            ("Linear Light", "linear_light"),
            ("Rush Light", "rush_light"),
            ("Magneto Track", "magneto_track"),
            ("PG Light", "pg_light")
        ]
        
        for name, template in templates:
            template_btn = ttk.Button(
                self.templates_frame,
                text=name,
                command=lambda t=template: self.load_template(t)
            )
            template_btn.pack(side="left", padx=5)
        
        # Execute button
        self.execute_btn = ttk.Button(
            self.input_frame,
            text="Create Drawing",
            command=self.execute_drawing,
            state="disabled"
        )
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.input_frame,
            mode='indeterminate'
        )
        
        # Output frame
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Results & Logs", padding="10")
        
        # Results text area
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame,
            height=15,
            width=80,
            wrap=tk.WORD
        )
        
        # Control buttons
        self.control_frame = ttk.Frame(self.output_frame)
        
        self.clear_btn = ttk.Button(
            self.control_frame,
            text="Clear Output",
            command=self.clear_output
        )
        
        self.save_btn = ttk.Button(
            self.control_frame,
            text="Save Results",
            command=self.save_results
        )
        
        # Batch processing frame
        self.batch_frame = ttk.LabelFrame(self.main_frame, text="Batch Processing", padding="10")
        
        ttk.Label(self.batch_frame, text="Load multiple requests from file:").pack(anchor="w")
        
        self.batch_btn = ttk.Button(
            self.batch_frame,
            text="Load Batch File",
            command=self.load_batch_file
        )
        
        self.batch_execute_btn = ttk.Button(
            self.batch_frame,
            text="Execute Batch",
            command=self.execute_batch,
            state="disabled"
        )
        
        self.batch_file_label = ttk.Label(
            self.batch_frame,
            text="No file loaded"
        )
        
        # Help frame
        self.help_frame = ttk.LabelFrame(self.main_frame, text="Help & Information", padding="10")
        
        help_text = """
Available Lighting Systems:
• Linear Light (LS) - Standard linear lighting
• Linear Light with Reflector (LSR) - Enhanced output
• Rush Light - High-output lighting system
• Rush Recessed - Recessed rush lighting
• PG Light - PG series lighting
• Magneto Track - Track-mounted system

Specify dimensions, power, color temperature, mounting type, and lens options.
        """
        
        self.help_text = scrolledtext.ScrolledText(
            self.help_frame,
            height=8,
            width=80,
            wrap=tk.WORD
        )
        self.help_text.insert("1.0", help_text)
        self.help_text.config(state="disabled")
    
    def setup_layout(self):
        """Setup the layout of all widgets"""
        
        self.main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="AutoDraw AI Agent", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Connection frame
        self.connection_frame.pack(fill="x", pady=(0, 10))
        self.connect_btn.pack(side="left", padx=(0, 10))
        self.status_label.pack(side="left")
        
        # Input frame
        self.input_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(self.input_frame, text="Describe your drawing requirements:").pack(anchor="w")
        self.input_text.pack(fill="x", pady=(0, 10))
        
        # Example and template frames side by side
        input_controls = ttk.Frame(self.input_frame)
        input_controls.pack(fill="x", pady=(0, 10))
        
        self.example_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.templates_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Execute button and progress
        execute_frame = ttk.Frame(self.input_frame)
        execute_frame.pack(fill="x")
        
        self.execute_btn.pack(side="left")
        self.progress.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Output frame
        self.output_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.output_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Control buttons
        self.control_frame.pack(fill="x")
        self.clear_btn.pack(side="left", padx=(0, 10))
        self.save_btn.pack(side="left")
        
        # Batch frame
        self.batch_frame.pack(fill="x", pady=(0, 10))
        
        batch_controls = ttk.Frame(self.batch_frame)
        batch_controls.pack(fill="x")
        
        self.batch_btn.pack(side="left", padx=(0, 10))
        self.batch_execute_btn.pack(side="left", padx=(0, 10))
        self.batch_file_label.pack(side="left")
        
        # Help frame
        self.help_frame.pack(fill="x")
        self.help_text.pack(fill="both", expand=True)
    
    def connect_to_autocad(self):
        """Connect to AutoCAD"""
        try:
            self.connect_btn.config(state="disabled")
            self.status_label.config(text="Status: Connecting...", foreground="orange")
            
            # Run connection in separate thread
            def connect_thread():
                try:
                    pythoncom.CoInitialize()  # <- Initialize COM in this thread
                    print("i am here p1")
                    self.agent = AutoDrawAIAgent()
                    print("i am here p3")
                    self.is_connected = True
                    
                    # Update GUI in main thread
                    print("i am here p2")
                    self.root.after(0, self.connection_success)
                    
                except Exception as e:
                    self.root.after(0, lambda e=e: self.connection_failed(str(e)))
                
                finally:
                    pythoncom.CoUninitialize()  # <- Clean up COM


            print("i am here P0")
            threading.Thread(target=connect_thread, daemon=True).start()
            
        except Exception as e:
            self.connection_failed(str(e))
    
    def connection_success(self):
        """Handle successful connection"""
        self.status_label.config(text="Status: Connected", foreground="green")
        self.connect_btn.config(text="Disconnect", command=self.disconnect_autocad)
        self.execute_btn.config(state="normal")
        self.batch_execute_btn.config(state="normal")
        self.log_message("Successfully connected to AutoCAD")
    
    def connection_failed(self, error):
        """Handle connection failure"""
        self.status_label.config(text="Status: Connection Failed", foreground="red")
        self.connect_btn.config(state="normal")
        messagebox.showerror("Connection Error", f"Failed to connect to AutoCAD:\n{error}")
    
    def disconnect_autocad(self):
        """Disconnect from AutoCAD"""
        if self.agent:
            self.agent.close_connection()
            self.agent = None
            self.is_connected = False
        
        self.status_label.config(text="Status: Not Connected", foreground="red")
        self.connect_btn.config(text="Connect to AutoCAD", command=self.connect_to_autocad)
        self.execute_btn.config(state="disabled")
        self.batch_execute_btn.config(state="disabled")
        self.log_message("Disconnected from AutoCAD")
    
    def load_example(self, example):
        """Load an example request"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", example)
    
    def load_template(self, template):
        """Load a template request"""
        templates = {
            "linear_light": "Create a linear light fixture with standard specifications",
            "rush_light": "Design a rush light system with high output",
            "magneto_track": "Build a magneto track lighting system",
            "pg_light": "Generate a PG series lighting fixture"
        }
        
        if template in templates:
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", templates[template])
    
    def execute_drawing(self):
        """Execute the drawing request"""
        if not self.is_connected:
            messagebox.showerror("Error", "Please connect to AutoCAD first")
            return
        
        request = self.input_text.get("1.0", tk.END).strip()
        if not request:
            messagebox.showerror("Error", "Please enter a drawing request")
            return
        
        self.processing = True
        self.execute_btn.config(state="disabled")
        self.progress.start()
        
        # Run in separate thread
        def execute_thread():
            try:
                result = self.agent.create_complete_drawing(request)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.handle_execution_result(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_execution_error(str(e)))
        
        threading.Thread(target=execute_thread, daemon=True).start()
    
    def handle_execution_result(self, result):
        """Handle execution result"""
        self.processing = False
        self.execute_btn.config(state="normal")
        self.progress.stop()
        
        if result.get("success"):
            self.log_message("✅ Drawing created successfully!")
            self.log_message(f"Specifications: {json.dumps(result.get('specifications', {}), indent=2)}")
            if result.get('summary'):
                self.log_message(f"Summary: {result['summary']}")
        else:
            self.log_message("❌ Drawing creation failed!")
            self.log_message(f"Error: {result.get('error', 'Unknown error')}")
    
    def handle_execution_error(self, error):
        """Handle execution error"""
        self.processing = False
        self.execute_btn.config(state="normal")
        self.progress.stop()
        
        self.log_message(f"❌ Error: {error}")
        messagebox.showerror("Execution Error", f"Error executing drawing:\n{error}")
    
    def load_batch_file(self):
        """Load a batch file with multiple requests"""
        file_path = filedialog.askopenfilename(
            title="Select Batch File",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Try to parse as JSON first, then as text
                try:
                    self.batch_requests = json.loads(content)
                    if isinstance(self.batch_requests, list):
                        self.batch_file_label.config(text=f"Loaded {len(self.batch_requests)} requests")
                    else:
                        raise ValueError("JSON must contain a list of requests")
                except json.JSONDecodeError:
                    # Parse as text file with one request per line
                    self.batch_requests = [line.strip() for line in content.split('\n') if line.strip()]
                    self.batch_file_label.config(text=f"Loaded {len(self.batch_requests)} requests")
                
                self.log_message(f"Loaded batch file: {file_path}")
                self.log_message(f"Number of requests: {len(self.batch_requests)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load batch file:\n{str(e)}")
    
    def execute_batch(self):
        """Execute batch processing"""
        if not hasattr(self, 'batch_requests') or not self.batch_requests:
            messagebox.showerror("Error", "Please load a batch file first")
            return
        
        if not self.is_connected:
            messagebox.showerror("Error", "Please connect to AutoCAD first")
            return
        
        self.batch_execute_btn.config(state="disabled")
        self.progress.start()
        
        # Run in separate thread
        def batch_thread():
            try:
                results = self.agent.batch_process_requests(self.batch_requests)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.handle_batch_result(results))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_execution_error(str(e)))
        
        threading.Thread(target=batch_thread, daemon=True).start()
    
    def handle_batch_result(self, results):
        """Handle batch execution results"""
        self.batch_execute_btn.config(state="normal")
        self.progress.stop()
        
        successful = sum(1 for r in results if r.get("success"))
        total = len(results)
        
        self.log_message(f"Batch processing completed: {successful}/{total} successful")
        
        for i, result in enumerate(results):
            status = "✅" if result.get("success") else "❌"
            self.log_message(f"Request {i+1}: {status} {result.get('error', 'Success')}")
    
    def log_message(self, message):
        """Add a message to the output log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """Clear the output log"""
        self.output_text.delete("1.0", tk.END)
    
    def save_results(self):
        """Save the output results to a file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.output_text.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Results saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results:\n{str(e)}")


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = AutoDrawAIGUI(root)
    
    # Handle window close
    def on_closing():
        if app.agent:
            app.agent.close_connection()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main() 