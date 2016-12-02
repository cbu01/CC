import PowUdp, PowHelper


class PowClient:
    def __init__(self, own_port, server_ip, server_port):
        self.own_port = own_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.data = None

    def run(self):
        print "Running PowClient"
        while True:
            print "Waiting for work from server ..."
            if self._check_for_work():
                self._do_work()

    def _check_for_work(self):
        command, data = PowUdp.udp_receive(self.server_ip, self.server_port)
        if command == PowHelper.CMD_SEND_TASK_TO_WORKER:
            print "Got work to do !"
            self.data = data
            return True
        return False

    def _check_for_success(self):
        print "Waiting for a success/fail response from the server"
        while True:
            command, data = PowUdp.udp_receive(self.server_ip, self.server_port)
            if command == PowHelper.CMD_TASK_SUCCESS_REPLY:
                work_successful = data
                if work_successful:
                    print "Awesome, the server agrees that I am great"
                else:
                    print "Boooo... the server thinks I made a mistake"
                break

    def _do_work(self):
        s, n = self.data
        x, x_int = PowHelper.find_x(s,n)
        print "Found my x !"
        print x
        PowUdp.udp_send(self.own_port, self.server_ip, self.server_port, PowHelper.CMD_TASK_SUCCESS_REQUEST, (s, x, n))
        self._check_for_success()
