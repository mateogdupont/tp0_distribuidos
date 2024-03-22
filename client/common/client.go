package common

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	"strings"
	"strconv"
	"io"

	log "github.com/sirupsen/logrus"
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func sigterm_handler(sigs chan os.Signal, finish_channel chan bool, c *Client){
	<-sigs
	c.conn.Close()
	log.Infof("action: Handling SIGTERM | result: success | client_id: %v",c.config.ID,)
	finish_channel <- true
}

func (c *Client)sendMessage (payload_msg string) error{
	msgWithHeader := fmt.Sprintf("%d,%s", len(payload_msg) - 2,payload_msg)

	remainSize := len(msgWithHeader)
	for remainSize > 0 {
		sendDataSize, err := c.conn.Write([]byte(msgWithHeader))
		if err != nil {
			return err
		}
		if sendDataSize == 0 {
			break
		}
		remainSize -= sendDataSize
	}
	return nil
}

func (c *Client)receiveMessage () (string, error){
	reader := bufio.NewReader(c.conn)
	completeMsg := ""

	for {
		partialMsg, err := reader.ReadString('\n')
		if (err != nil) && (err != io.EOF){
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



// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	// autoincremental msgID to identify every message sent
	msgID := 1

	sigs := make (chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM);
	finish_channel := make(chan bool, 1)
	go sigterm_handler(sigs,finish_channel, c)

loop:
	// Send messages if the loopLapse threshold has not been surpassed
	for timeout := time.After(c.config.LoopLapse); ; {
		select {
		case <-timeout:
	        log.Infof("action: timeout_detected | result: success | client_id: %v",
                c.config.ID,
            )
			break loop
		case <- finish_channel:
			log.Infof("action: Exiting loop | result: success | client_id: %v",c.config.ID,)
			close(finish_channel)
			close(sigs)
			break loop

		default:
		}

		// Create the connection the server in every loop iteration.
		c.createClientSocket()
		msg_to_send := fmt.Sprintf("[CLIENT %v] Message N°%v\n", c.config.ID, msgID)
		c.sendMessage(msg_to_send)
		msg, err := c.receiveMessage()
		msgID++
		c.conn.Close()

		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
                c.config.ID,
				err,
			)
			return
		}
		log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
            c.config.ID,
            msg,
        )

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)
	}

	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}
