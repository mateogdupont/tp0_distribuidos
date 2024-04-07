package common

import (
	"fmt"
	"net"
	"strconv"
)

// sendMessage takes the payload of a message sends it
// through a socket with its header. This function 
// prevents short-write errors.
func sendMessage (conn net.Conn, payload_msg string) error{
	msg := fmt.Sprintf("%d,%s", len(payload_msg),payload_msg)
	remainSize := len(msg)

	for remainSize > 0 {
		sendDataSize, err := conn.Write([]byte(msg))
		if err != nil {
			conn.Close()
			return err
		}
		if sendDataSize == 0 {
			break
		}
		remainSize -= sendDataSize
	}
	return nil
}

// receiveHeader reads from a socket and returns 
// the header of a message. It reads by one byte until it 
// finds the delimiter
func receiveHeader(conn net.Conn) (string, error) {
	completeHeader := ""
	for {
		byteBuffer := make([]byte, 1)
		_, err := conn.Read(byteBuffer)
		if err != nil {
			return "", err
		}
		completeHeader += string(byteBuffer)
		if string(byteBuffer) == "," {
			break
		}
	}
	return completeHeader, nil
}

// receiveMessage reads from a socket and returns 
// the message, it also prevents short-read errors.
func receiveMessage (conn net.Conn) (string, error){
	header, err := receiveHeader(conn)
    if err != nil{
		conn.Close()
		return "", err
	}
	expectedPayloadSize, err := strconv.Atoi(header[:len(header)-1])
	if err != nil{
		conn.Close()
		return "", err
	}
    payload := ""

	for {
		readBuffer := make([]byte, expectedPayloadSize - len(payload))
		readSize, err := conn.Read(readBuffer)
		if err != nil {
			conn.Close()
			return "", err
		}
		payload += string(readBuffer[:readSize])
		if len(payload) >= expectedPayloadSize || readSize == 0 {
			break
		}
	}
	return header + payload, nil
}
