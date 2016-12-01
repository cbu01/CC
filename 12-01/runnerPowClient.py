from PowClient import PowClient

reflection_ip = "100.100.100.100"
reflection_port = 12345
local_listening_port = 23456

server = PowClient(reflection_ip, reflection_port, local_listening_port)
server.run()