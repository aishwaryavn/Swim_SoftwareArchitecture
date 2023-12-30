_Author_ = "Karthik Vaidhyanathan"

import socket
import traceback

def test_adaptation(host,port,check_type="server"):

    if check_type == "server":
        # To add server in swim
        print(" Adding Server ")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = s.connect((host, port))
            s.sendall(b'remove_server')
            data = s.recv(1024)
            s.sendall(b'get_arrival_rate')
            data = s.recv(1024)
            print (" arrival rate ")
            s.close()
            print(str(data.decode("utf-8")))
            server_add_flag = True
        except Exception as e:
            traceback.print_exc()
    elif check_type == "dimmer":
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = s.connect((host, port))
            #s.sendall(b'set_dimmer ' + b'0.50')

            value = "0.25"

            value = str.encode(value)


            s.sendall(b'set_dimmer ' + value)


            data = s.recv(1024)
            print(str(data.decode("utf-8")))
            s.close()
        except Exception as e:
            traceback.print_exc()





if __name__ == '__main__':
    test_adaptation("35.180.116.52",4242,"server")