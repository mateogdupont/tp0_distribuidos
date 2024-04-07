import socket
import logging

def send_message(client_sock, payload):
    payload_size = len(payload)
    msg = "{},".format(payload_size) + payload
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