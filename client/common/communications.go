package common

import (
	"bufio"
	"fmt"
	"net"
	"io"
	"strings"
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

func receiveMessage (conn net.Conn) (string, error){
	reader := bufio.NewReader(conn)
	completeMsg := ""

	for {
		partialMsg, err := reader.ReadString('\n')
		if (err != nil) && (err != io.EOF){
			conn.Close()
			return "", err
		}
		partialMsg = strings.TrimRight(partialMsg, "\r\n")
		if partialMsg == "" {
			break
		}

		completeMsg += partialMsg
		if strings.Contains(completeMsg, ",") {
			splitMsg := strings.SplitN(completeMsg, ",", 2)
			expectedByteSize, err := strconv.Atoi(splitMsg[0])
			if err != nil {
				conn.Close()
				return "", err
			}
			receivedPayloadSize := len(splitMsg[1])
			if receivedPayloadSize >= expectedByteSize {
				break
			}
		}
	}
	return completeMsg, nil
}