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


    def _receive_header(self, client_sock):
        """
        Read the header of a message
        """
        complete_header = ""
        while True:
            partial_header = client_sock.recv(1).decode('utf-8')
            if not partial_header:
                logging.error("action: receive_header | result: fail")
                break
            complete_header += partial_header
            if partial_header == ',':
                break
        return complete_header

    def _receive_message(self, client_sock):
        header = self._receive_header(client_sock)
        if not header:
            return ""
        expected_payload_size = int(header[:-1])
        complete_msg = header
        while True:
            partial_msg = client_sock.recv(expected_payload_size).decode('utf-8')
            if not partial_msg:
                logging.error("action: receive_message | result: fail | error: {e}")
                break

            complete_msg += partial_msg
            if ',' in complete_msg:
                split_msg = complete_msg.split(',', 1)
                received_payload_size = len(split_msg[1].encode('utf-8'))
                if received_payload_size >= expected_payload_size:
                    break
        
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {complete_msg}')
        return complete_msg
    
    def _receive_chunk(self, client_sock) -> int:
        amount_of_bets = 0
        while True:
            msg = self._receive_message(client_sock)
            if not msg.strip() or is_end_msg(msg):
                return amount_of_bets
            
            self._procces_message(msg)
            amount_of_bets += 1
        
    def _send_message(self, client_sock, msg):
        remaind_size = len(msg)
        while remaind_size > 0:
            sent_data_size = client_sock.send(msg.encode('utf-8'))
            if sent_data_size == 0:
                logging.error("action: send_message | result: fail")
                break
            remaind_size -= sent_data_size
            msg = msg[sent_data_size:]

    def _send_ack_message(self, client_sock, msg):
        amount_to_ack = msg.split(',', 1)[0]
        payload_size = len("ACK:" + amount_to_ack)
        ack_message = "{}\n,".format(payload_size) + "ACK:" + amount_to_ack
        self._send_message(client_sock, ack_message)
 
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
            amount_receiced = self._receive_chunk(client_sock)
            msg = "{},\n,".format(amount_receiced)
            self._send_ack_message(client_sock,msg)

        except OSError as e:
            logging.error("action: receive_message | result: fail")
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
