import socket
import threading
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime

class ChatClient:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python Chat Client")
        self.window.geometry("800x600")
        
        # Create main container
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the main chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.main_container, 
            wrap=tk.WORD, 
            width=70, 
            height=30
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create input container
        self.input_container = ttk.Frame(self.main_container)
        self.input_container.pack(fill=tk.X, pady=5)
        
        # Create the message input field
        self.message_entry = ttk.Entry(self.input_container)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Create the send button
        self.send_button = ttk.Button(
            self.input_container, 
            text="Send", 
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        
        self.connected = False
        self.username = None
        
    def connect_to_server(self, host, port, username, password, register=False):
        """Connect to the chat server with authentication"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            
            # Send authentication data
            auth_data = {
                "username": username,
                "password": password,
                "register": register
            }
            self.client_socket.send(json.dumps(auth_data).encode('utf-8'))
            
            # Wait for authentication response
            response = json.loads(self.client_socket.recv(1024).decode('utf-8'))
            
            if response.get('error'):
                messagebox.showerror("Authentication Error", response['error'])
                self.client_socket.close()
                return False
                
            self.connected = True
            self.username = username
            
            # Start receiving messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.display_system_message("Connected to server!")
            return True
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            return False
            
    def receive_messages(self):
        """Receive and display messages from the server"""
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    try:
                        message_data = json.loads(message)
                        sender = message_data.get('sender', 'Server')
                        content = message_data.get('message', '')
                        timestamp = message_data.get('timestamp')
                        
                        if timestamp:
                            # Convert ISO format to datetime
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M:%S")
                            self.display_message(f"[{time_str}] {sender}: {content}")
                        else:
                            self.display_message(f"{sender}: {content}")
                            
                    except json.JSONDecodeError:
                        self.display_system_message(message)
            except:
                self.connected = False
                self.display_system_message("Disconnected from server")
                break
                
    def send_message(self):
        """Send a message to the server"""
        message = self.message_entry.get().strip()
        if message and self.connected:
            message_data = {
                "message": message
            }
            try:
                self.client_socket.send(json.dumps(message_data).encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except:
                self.display_system_message("Error sending message")
                self.connected = False
                
    def display_message(self, message):
        """Display a chat message in the chat window"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, message + '\n')
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
        
    def display_system_message(self, message):
        """Display a system message in the chat window"""
        self.chat_display.configure(state='normal')
        self.chat_display.insert(tk.END, f"System: {message}\n")
        self.chat_display.configure(state='disabled')
        self.chat_display.see(tk.END)
        
    def start(self):
        """Start the chat client"""
        self.window.mainloop()
        
    def cleanup(self):
        """Clean up resources when closing"""
        if self.connected:
            self.connected = False
            self.client_socket.close()

def create_login_window():
    """Create and return a login window"""
    login_window = tk.Tk()
    login_window.title("Chat Login")
    login_window.geometry("300x400")
    
    style = ttk.Style()
    style.configure('TFrame', padding=5)
    style.configure('TLabel', padding=5)
    style.configure('TEntry', padding=5)
    style.configure('TButton', padding=5)
    
    main_frame = ttk.Frame(login_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Create input fields
    ttk.Label(main_frame, text="Server IP:").pack(fill=tk.X)
    host_entry = ttk.Entry(main_frame)
    host_entry.insert(0, "localhost")
    host_entry.pack(fill=tk.X)
    
    ttk.Label(main_frame, text="Port:").pack(fill=tk.X)
    port_entry = ttk.Entry(main_frame)
    port_entry.insert(0, "5555")
    port_entry.pack(fill=tk.X)
    
    ttk.Label(main_frame, text="Username:").pack(fill=tk.X)
    username_entry = ttk.Entry(main_frame)
    username_entry.pack(fill=tk.X)
    
    ttk.Label(main_frame, text="Password:").pack(fill=tk.X)
    password_entry = ttk.Entry(main_frame, show="*")
    password_entry.pack(fill=tk.X)
    
    # Create variable for registration checkbox
    register_var = tk.BooleanVar()
    ttk.Checkbutton(
        main_frame, 
        text="Register new account", 
        variable=register_var
    ).pack(pady=10)
    
    def start_chat():
        """Handle the login/registration process"""
        host = host_entry.get()
        port = int(port_entry.get())
        username = username_entry.get()
        password = password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        login_window.destroy()
        
        # Create and start chat client
        client = ChatClient()
        if client.connect_to_server(host, port, username, password, register=register_var.get()):
            client.start()
            client.cleanup()
    
    # Create login button
    ttk.Button(main_frame, text="Join Chat", command=start_chat).pack(pady=20)
    
    login_window.mainloop()

if __name__ == "__main__":
    create_login_window()
