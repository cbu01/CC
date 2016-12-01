from PowServer import PowServer

reflection_ip = "100.100.100.100"
reflection_port = 12345
local_listening_port = 23456
n = 20

server = PowServer(reflection_ip, reflection_port, local_listening_port)
server.run(n)