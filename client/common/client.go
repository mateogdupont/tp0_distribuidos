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
	"encoding/csv"

	log "github.com/sirupsen/logrus"
)

const FIN = ",FIN"
const READY = ",READY"

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
	BetRegister   *BetRegister
	BetAmount	  string
	BetFilePath   string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	winners []int
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
	msg := fmt.Sprintf("%d,%s", len(payload_msg),payload_msg)
	remainSize := len(msg)

	for remainSize > 0 {
		sendDataSize, err := c.conn.Write([]byte(msg))
		if err != nil {
			c.conn.Close()
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
                c.config.ID,
				err,
			)
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
			c.conn.Close()
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",c.config.ID,err,)
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
				c.conn.Close()
				log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",c.config.ID,err,)
				return "", err
			}
			receivedPayloadSize := len(splitMsg[1])
			if receivedPayloadSize >= expectedByteSize {
				break
			}
		}
	}
	//log.Infof("action: receive_message | result: success | msg: %v",completeMsg,)
	return completeMsg, nil
}

func (c *Client)receiveWinners() error{
	for {
		winnerMsg, _ := c.receiveMessage()
		if winnerMsg == ""{
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d",len(c.winners),)
			break
		}
		splitMsg := strings.Split(winnerMsg, ",")
		winnersDocument, err := strconv.Atoi(splitMsg[1])
		if err != nil {
			log.Errorf("action: receive_winner | result: fail")
			return err
		}
		c.winners = append(c.winners, winnersDocument)
	}
	return nil
}

func (c *Client)sendBetMessage () error{
	betRegister := c.config.BetRegister
	payload_msg := c.config.ID + "," + betRegister.toBetMessage()
	return c.sendMessage(payload_msg);
}

// openFile opens the agency file in path: config.BetFilePath
// returns error in case that it couldnt open the file
func (c *Client) openFile() (*os.File, error) {
	filePath := c.config.BetFilePath
	file, err := os.Open(filePath)
	if err != nil {
		log.Errorf("action: open_bet_file | result: fail | client_id: %v | error: %v",c.config.ID,err,)
		return nil,err
	}
	return file,nil
}

// closeFile closes an open agency file
// returns error in case that it couldnt close the file
func (c *Client) closeFile(file *os.File) error{
	err := file.Close()
	if err != nil {
		log.Errorf("action: close_bet_file | result: fail | client_id: %v | error: %v",c.config.ID,err,)
		return err
	}
	return nil
}

// sendFinMessage sends a FIN messages to the server
func (c *Client) sendFinMessage() error{
	payload_msg := c.config.ID + FIN
	return c.sendMessage(payload_msg);
}

// sendReadyMessage sends a READY messages to the server
func (c *Client) sendReadyMessage() error{
	payload_msg := c.config.ID + READY
	return c.sendMessage(payload_msg);
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {
	sigs := make (chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM);
	finish_channel := make(chan bool, 1)
	go sigterm_handler(sigs,finish_channel, c)

	bet_file,_ := c.openFile()
	bet_reader := csv.NewReader(bet_file)
	// Create the connection the server.
	c.createClientSocket()
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
			break loop

		default:
		}

		amount, _ := strconv.Atoi(c.config.BetAmount)
		bets, read_chunk_err := readChunkFromFile(bet_reader, amount)

		if read_chunk_err != nil && read_chunk_err != io.EOF{
			c.sendFinMessage()
			break loop
		}
		for i, bet := range bets {
			c.config.BetRegister = bet
			send_error := c.sendBetMessage()
			if send_error !=nil{
				break loop
			}
			log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",c.config.BetRegister.Document,c.config.BetRegister.Number,)

			if i == len(bets)-1 {
				var send_error error
				if read_chunk_err == io.EOF{
					send_error = c.sendReadyMessage()
					if send_error != nil{
						break loop
					}
					_, err := c.receiveMessage()
					if err != nil {
						break loop
					}
					c.receiveWinners()
					break loop
				}else{
					send_error = c.sendFinMessage()
					if send_error != nil{
						break loop
					}
					_, err := c.receiveMessage()
					if err != nil {
						break loop
					}
				}
			}
		}

		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)
	}
	c.conn.Close()
	c.closeFile(bet_file)
	close(finish_channel)
	close(sigs)
	log.Infof("action: loop_finished_gracefuly | result: success | client_id: %v", c.config.ID)
}
