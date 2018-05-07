from class_server import Server

server = Server()
server.connect(input("Address? "), int(input("Port? ")))
print("Server started, listening...")
server.accepting_allow()