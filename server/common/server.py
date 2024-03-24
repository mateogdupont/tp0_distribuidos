import socket
import logging
import signal

from common.utils import *

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._exit = False
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signal,frame):
        logging.info(f'action: receive_kill_signal | result: success | SIGTERM')
        self._exit = True

    def graceful_finish(self):
        self._server_socket.close()
        logging.info(f'action: graceful_finish | result: success')

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while not self._exit:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)


    def _receive_message(self, client_sock):

        complete_msg = ""

        while True:
            partial_msg = client_sock.recv(1024).rstrip().decode('utf-8')
            if not partial_msg:
                logging.error("action: receive_message | result: fail | error: {e}")
                break

            complete_msg += partial_msg
            if ',' in complete_msg:
                split_msg = complete_msg.split(',', 1)
                expected_byte_size = int(split_msg[0])
                received_payload_size = len(split_msg[1])
                if received_payload_size >= expected_byte_size:
                    break
        
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {complete_msg}')
        return complete_msg
    
    def _send_ack_message(self, client_sock, msg):
        size_inside_msg = msg.split(',', 1)[0]
        payload_size = len("ACK:" + size_inside_msg)
        ack_message = "{}\n,".format(payload_size) + "ACK:" + size_inside_msg
        remaind_size = len(ack_message)

        while remaind_size > 0:
            sent_data_size = client_sock.send(ack_message)
            if sent_data_size == 0:
                logging.error("action: send_message | result: fail | error: {e}")
                break
            remaind_size -= sent_data_size
            ack_message = ack_message[sent_data_size:]
  
    def _procces_message(self, msg):
        bet = Bet.from_message(msg)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: ${bet.document} | numero: ${bet.number}')
         
    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg = self._receive_message(client_sock)
            if not msg.strip():
                return
            self.procces_message(msg)
            self._send_ack_message(client_sock,msg)

        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
