from PowClient import PowClient

reflection_ip = "100.100.100.100"
reflection_port = 12345

server = PowClient(reflection_ip, reflection_port)
server.run()