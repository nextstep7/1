import socket
import threading
import json
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5555, db_uri='mongodb://localhost:27017/'):
        # Initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        
        # Dictionary to store active client connections
        self.clients = {}
        
        # Initialize MongoDB connection
        self.mongo_client = AsyncIOMotorClient(db_uri)
        self.db = self.mongo_client.chat_db
        
        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Create indexes
        self.loop.run_until_complete(self.setup_indexes())
        
        print(f"Server started on {host}:{port}")
        print("Connected to MongoDB")

    async def setup_indexes(self):
        """Set up database indexes"""
        await self.db.users.create_index('username', unique=True)
        await self.db.messages.create_index('timestamp')

    async def register_user(self, username, password):
        """Register a new user in the database"""
        try:
            user_doc = {
                'username': username,
                'password': password,  # In a real app, hash this password!
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            await self.db.users.insert_one(user_doc)
            return True
        except Exception as e:
            print(f"Error registering user: {e}")
            return False

    async def authenticate_user(self, username, password):
        """Authenticate a user against the database"""
        user = await self.db.users.find_one({
            'username': username,
            'password': password
        })
        if user:
            await self.db.users.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return True
        return False

    async def store_message(self, sender, message):
        """Store a message in the database"""
        message_doc = {
            'sender': sender,
            'content': message,
            'timestamp': datetime.utcnow()
        }
        await self.db.messages.insert_one(message_doc)

    async def get_recent_messages(self, limit=50):
        """Retrieve recent messages from the database"""
        cursor = self.db.messages.find().sort('timestamp', -1).limit(limit)
        messages = await cursor.to_list(length=limit)
        return messages

    def broadcast(self, message, sender=None):
        """Send a message to all connected clients and store it"""
        message_data = {
            "sender": sender,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        encoded_message = json.dumps(message_data).encode('utf-8')
        
        # Store message in database using asyncio
        if sender and message:
            asyncio.run_coroutine_threadsafe(
                self.store_message(sender, message),
                self.loop
            )
        
        # Send to all connected clients
        for client in self.clients:
            if client != sender:
                try:
                    client.send(encoded_message)
                except:
                    self.remove_client(client)

    async def send_message_history(self, client_socket):
        """Send recent message history to newly connected client"""
        recent_messages = await self.get_recent_messages()
        for msg in reversed(recent_messages):
            message_data = {
                "sender": msg['sender'],
                "message": msg['content'],
                "timestamp": msg['timestamp'].isoformat()
            }
            try:
                client_socket.send(json.dumps(message_data).encode('utf-8'))
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming the client
            except:
                break

    def handle_client(self, client_socket, addr):
        """Handle individual client connections with authentication"""
        try:
            # Get authentication data from client
            auth_data = json.loads(client_socket.recv(1024).decode('utf-8'))
            username = auth_data.get('username')
            password = auth_data.get('password')
            is_registration = auth_data.get('register', False)
            
            # Handle authentication in the event loop
            if is_registration:
                success = asyncio.run_coroutine_threadsafe(
                    self.register_user(username, password),
                    self.loop
                ).result()
                if not success:
                    client_socket.send(json.dumps({
                        "error": "Registration failed"
                    }).encode('utf-8'))
                    return
            else:
                authenticated = asyncio.run_coroutine_threadsafe(
                    self.authenticate_user(username, password),
                    self.loop
                ).result()
                if not authenticated:
                    client_socket.send(json.dumps({
                        "error": "Authentication failed"
                    }).encode('utf-8'))
                    return
            
            # Authentication successful
            client_socket.send(json.dumps({
                "success": True
            }).encode('utf-8'))
            
            # Store client information
            self.clients[client_socket] = username
            
            # Send message history
            asyncio.run_coroutine_threadsafe(
                self.send_message_history(client_socket),
                self.loop
            ).result()
            
            # Announce new user
            self.broadcast(f"{username} joined the chat!", username)
            
            # Main message handling loop
            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if not message:
                        break
                    
                    message_data = json.loads(message)
                    self.broadcast(message_data['message'], username)
                except json.JSONDecodeError:
                    continue
                
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            self.remove_client(client_socket)

    def remove_client(self, client_socket):
        """Remove a client and clean up their connection"""
        if client_socket in self.clients:
            username = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            self.broadcast(f"{username} left the chat!", username)

    def start(self):
        """Start the server and accept client connections"""
        # Start the asyncio event loop in a separate thread
        loop_thread = threading.Thread(target=self._run_event_loop)
        loop_thread.daemon = True
        loop_thread.start()
        
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"New connection from {addr}")
            
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, addr)
            )
            client_thread.start()

    def _run_event_loop(self):
        """Run the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def cleanup(self):
        """Clean up MongoDB connection and server socket"""
        self.loop.stop()
        self.mongo_client.close()
        self.server_socket.close()

if __name__ == "__main__":
    server = ChatServer()
    print("Chat server is running... Press Ctrl+C to stop")
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.cleanup()
