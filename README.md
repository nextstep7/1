# Python Chat Application with MongoDB

A real-time chat application built with Python, featuring user authentication, message persistence, and a graphical user interface. The application uses MongoDB for storing user data and chat history.

## Features

- Real-time messaging between multiple users
- User authentication (login/registration)
- Message persistence using MongoDB
- Graphical user interface built with tkinter
- Message history retrieval
- Timestamps for all messages
- System notifications for user join/leave events

## Prerequisites

- Python 3.x
- MongoDB installed and running
- Required Python packages:
  ```bash
  pip install motor
  pip install pymongo
  ```

## Project Structure

```
python-chat/
├── chat_server.py      # Server implementation
├── chat_client.py      # Client implementation with GUI
└── README.md          # This file
```

## Installation

1. Clone the repository or download the source files
2. Install the required dependencies:
   ```bash
   pip install motor pymongo
   ```
3. Ensure MongoDB is installed and running on your system
   - For Windows: Make sure the MongoDB service is running
   - For Linux: `sudo systemctl start mongod`
   - For macOS: `brew services start mongodb-community`

## Usage

### Starting the Server

1. Open a terminal and navigate to the project directory
2. Run the server:
   ```bash
   python chat_server.py
   ```
3. The server will start on port 5555 by default

### Running the Client

1. Open a new terminal window
2. Run the client:
   ```bash
   python chat_client.py
   ```
3. In the login window:
   - Enter the server IP (localhost if running locally)
   - Enter the port number (default: 5555)
   - Enter your username and password
   - Check "Register new account" if you're a new user

## Configuration

### Server Configuration
You can modify these parameters in `chat_server.py`:
- `host`: Server IP address (default: '0.0.0.0')
- `port`: Server port (default: 5555)
- `db_uri`: MongoDB connection URI (default: 'mongodb://localhost:27017/')

### Client Configuration
Default connection settings in the login window:
- Server IP: localhost
- Port: 5555

## Security Notes

- Passwords are currently stored in plaintext. In a production environment, implement proper password hashing.
- The connection is not encrypted. For production use, implement SSL/TLS.
- The server accepts connections from any IP by default.

## Troubleshooting

Common issues and solutions:

1. **Connection Refused Error**
   - Ensure the server is running
   - Check if the port is available
   - Verify firewall settings

2. **MongoDB Connection Error**
   - Verify MongoDB is running
   - Check MongoDB connection string
   - Ensure MongoDB port (27017) is accessible

3. **Import Errors**
   - Verify all required packages are installed
   - Check Python version compatibility
   - Try reinstalling dependencies

## Future Improvements

- Implement password hashing
- Add SSL/TLS encryption
- Private messaging functionality
- File sharing capabilities
- User profile pictures
- Message editing and deletion
- Read receipts
- User typing indicators
- Room/Channel support
- Message search functionality

## Contributing

Feel free to fork the project and submit pull requests. You can also open issues for bugs or feature requests.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with Python's socket programming
- GUI implemented using tkinter
- Database functionality powered by MongoDB and Motor
