import socket
import logging
import signal

from common.utils import *
from multiprocessing import Process, Pipe, Lock

TOTAL_AMOUNT_OF_CLIENTS = 5

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._exit = False
        self._processes = []
        self._winners_per_agency = {}
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signal,frame):
        logging.info(f'action: receive_kill_signal | result: success | SIGTERM')
        self._exit = True

    def graceful_finish(self):
        self._server_socket.close()
        self._finish_processes()
        logging.info(f'action: graceful_finish | result: success')

    def _get_winners(self, file_lock):
        with file_lock:
            bets = load_bets()
        filtered_bets = list(filter(has_won, bets))
        for bet in filtered_bets:
            if bet.agency not in self._winners_per_agency.keys():
                self._winners_per_agency[bet.agency] = []
            self._winners_per_agency[bet.agency].append(bet.document)

    def _send_winners_to_childs(self, file_lock):
        self._get_winners(file_lock)
        for processManager in self._processes:
            if processManager.client_id in self._winners_per_agency.keys():
                process_winners = self._winners_per_agency[processManager.client_id]
                for winner in process_winners:
                    processManager.pipe.send(winner)
            processManager.pipe.send(None)
        
    def _set_childs_id(self):
        """
        Loads the ID of the client in each process to its processManager.
        """
        if not self._processes:
            return False
        for processManager in self._processes:
            try:
                processManager.set_own_id()
            except EOFError as e:
                return False
        return True

    def _finish_processes(self):
        for processManager in self._processes:
            processManager.finish()


    def run(self):
        file_lock = Lock()
        while not self._exit:
            client_sock = self.__accept_new_connection()
            process_manager = ProcessManager(handle_client_connection, file_lock,client_sock)
            self._processes.append(process_manager)
            if len(self._processes) == TOTAL_AMOUNT_OF_CLIENTS:
                if self._set_childs_id():
                    self._send_winners_to_childs(file_lock)
                    logging.info(f'action: sorteo | result: success')
                self._finish_processes()
                self._processes = []
        
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

def send_message(client_sock, payload):
    payload_size = len(payload)
    msg = "{},".format(payload_size) + payload + "\n"
    remaind_size = len(msg)
    while remaind_size > 0:
        try:
            sent_data_size = client_sock.send(msg.encode('utf-8'))
        except (OSError, BrokenPipeError):
            logging.error("action: send_message | result: fail")
            break
        if sent_data_size == 0:
            logging.error("action: send_message | result: fail")
            break
        remaind_size -= sent_data_size
        msg = msg[sent_data_size:]

def send_ack_message(client_sock, msg):
    amount_to_ack = msg.split(',', 1)[0]
    payload_msg = "ACK:" + amount_to_ack
    send_message(client_sock, payload_msg)

def procces_message(msg, file_lock):
    """
    Procces message

    If massage type is bet, the server stores the bet.
    """
    bet = Bet.from_message(msg)
    with file_lock:
        store_bets([bet])
    logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
   
def receive_header(client_sock):
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


def receive_message(client_sock):
    header = receive_header(client_sock)
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
    return complete_msg


def receive_chunk(client_sock,file_lock) -> tuple[int, str]:
    """
    Read a complete chunk. It reads until a FIN or a READY message.

    It returns the amount of messages read in the chunk and the last
    message of the chunk.
    """
    received_amount = 0
    while True:
        msg = receive_message(client_sock)
        if not msg.strip() or is_end_msg(msg):
            return (received_amount , msg)

        procces_message(msg,file_lock)
        received_amount += 1

def receive_and_send_winners(client_sock, pipe_with_manager):
    winners = []
    try:
        while True:
            winner = pipe_with_manager.recv()
            if winner is None:
                break
            winners.append(winner)
    finally:
        pipe_with_manager.close()
        for winners_document in winners:
            send_message(client_sock,winners_document)
        client_sock.close()
        

def handle_client_connection(client_sock,file_lock, pipe_with_manager):
    finish = False
    while not finish:
        (amount_receiced, last_message) = receive_chunk(client_sock,file_lock)
        #handle client_disconection
        if not last_message.strip():
            client_sock.close()
            pipe_with_manager.close()
            break
        msg = "{},\n,".format(amount_receiced)
        send_ack_message(client_sock,msg)
        if is_ready_msg(last_message):
            #Notify main process and wait for winners
            client_id = get_client_id(last_message)
            pipe_with_manager.send(f"{client_id}")
            receive_and_send_winners(client_sock, pipe_with_manager)
            finish = True
