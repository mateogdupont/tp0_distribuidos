import socket
import logging
import signal

from common.communications import *
from common.utils import *

TOTAL_AMOUNT_OF_CLIENTS = 5

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._exit = False
        self._ready_clients = {}
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signal,frame):
        logging.info(f'action: receive_kill_signal | result: success | SIGTERM')
        self._exit = True

    def graceful_finish(self):
        self._server_socket.close()
        logging.info(f'action: graceful_finish | result: success')

    def _send_winners(self):
        bets = load_bets()
        filtered_bets = list(filter(has_won, bets))
        for bet in filtered_bets:
            winners_document = bet.document
            agency_socket = self._ready_clients[bet.agency]
            send_message(agency_socket,winners_document)
            receive_message(agency_socket)
        return


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
            
            if len(self._ready_clients) == TOTAL_AMOUNT_OF_CLIENTS:
                logging.info(f'action: sorteo | result: success')
                self._send_winners()
                for client_sock in self._ready_clients.values():
                    client_sock.close()
    
    def _receive_chunk(self, client_sock) -> int:
        received_amount = 0
        while True:
            msg = receive_message(client_sock)      
            chunk_finish = self._procces_message(msg,client_sock)
            if chunk_finish:
                return received_amount
            received_amount += 1

    def _send_ack_message(self, client_sock, msg):
        amount_to_ack = msg.split(',', 1)[0]
        payload_msg = "ACK:" + amount_to_ack
        send_message(client_sock, payload_msg)
 
    def _procces_message(self, msg, client_sock) -> bool:
        """
        Procces message

        If massage type is bet, the server stores the bet.
        If messafe type is READY, the server add the client ID to the 
        list of ready clients
        """
        if not msg.strip() or is_end_msg(msg):
            return True
        if is_ready_msg(msg):
            split_msg = msg.split(',', 2)
            self._ready_clients[int(split_msg[1])] = client_sock
            return True
        bet = Bet.from_message(msg)
        store_bets([bet])
        logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
        return False
         
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
            if client_sock not in self._ready_clients.values():
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
