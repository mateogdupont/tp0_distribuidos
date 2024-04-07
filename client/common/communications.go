package common

import (
	"fmt"
	"net"
	"strconv"
)

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