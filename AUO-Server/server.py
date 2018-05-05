from class_server import Server

server = Server(input("Address? "), int(input("Port? ")))
server.run()