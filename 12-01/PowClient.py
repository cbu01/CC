import PowUdp, PowHelper
import time
import sys


class PowClient:
    def __init__(self, reflection_ip, reflection_port, listening_port):
        self.reflection_ip = reflection_ip
        self.reflection_port = reflection_port
        self.data = None

    def run(self):
        print "Running PowClient"
        try:
            udp_connection_successful = self._register_client()
            while udp_connection_successful is None:
                print "Unable to connect to reflection server. Retrying ..."
                time.sleep(5)
                udp_connection_successful = self._register_client()
        except Exception as ex:
            print "Failed to connect with reflection server. Reason is " + ex.message
            sys.exit()
        while True:
            print "Waiting for work from server ..."
            if self._check_for_work():
                self._do_work()

    def _register_client(self):
        """ Registers the server as a udp client. Returns the udp connection """
        return PowUdp.udp_send(self.reflection_ip , self.reflection_port, PowHelper.CMD_REGISTER_SERVER, self.listening_port)


    def _check_for_work(self):
        command, data = PowUdp.udp_receive(self.reflection_ip, self.reflection_port)
        if command == PowHelper.CMD_SEND_TASK_TO_WORKER:
            print "Got work to do !"
            self.data = data
            return True
        return False

    def _check_for_success(self):
        print "Waiting for a success/fail response from the server"
        while True:
            command, data = PowUdp.udp_receive(self.reflection_ip, self.reflection_port)
            if command == PowHelper.CMD_TASK_SUCCESS_REPLY:
                work_successful = data
                if work_successful:
                    print "Awesome, the server agrees that I am great"
                else:
                    print "Boooo... the server thinks I made a mistake"
                break

    def _do_work(self):
        s, n = self.data
        x = PowHelper.find_x(s,n)
        print "Found my x !"
        print x
        PowUdp.udp_send(self.reflection_ip, self.reflection_port, PowHelper.CMD_TASK_SUCCESS_REQUEST, (s, x, n))
        self._check_for_success()