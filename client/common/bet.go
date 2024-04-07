package common

import (
	"fmt"
	"strings"
	"strconv"
	"encoding/csv"
)

type BetRegister struct {
	Name      string
	Lastname  string
	Document  int
	Birthdate string
	Number    int
}

// NewBetRegister is a constructor function for BetRegister
func NewBetRegister(name string, lastname string, document int, birthdate string, number int) *BetRegister {
	return &BetRegister{
		Name:      name,
		Lastname: lastname,
		Document: document,
		Birthdate: birthdate,
		Number:    number,
	}
}

func FromCSV(readLine []string) (*BetRegister, error) {
    document, docErr := strconv.Atoi(readLine[2])
    if docErr != nil {
        return nil, docErr
    }

    number, err := strconv.Atoi(readLine[4])
    if err != nil {
        return nil, err
    }

    return &BetRegister{
        Name:      readLine[0],
        Lastname: readLine[1],
        Document: document,
        Birthdate: readLine[3],
        Number:    number,
    }, nil
}



func FromMessage (message string) (*BetRegister, error){
	splitMsg := strings.Split(message, ",")
	if len(splitMsg) != 6 {
		return nil, fmt.Errorf("invalid format")
	}
	document, docErr := strconv.Atoi(splitMsg[4])
	if docErr != nil {
		return nil, docErr
	}
	number, err := strconv.Atoi(splitMsg[6])
	if err != nil {
		return nil, err
	}

	return &BetRegister{
		Name:      splitMsg[2],
		Lastname: splitMsg[3],
		Document: document,
		Birthdate: splitMsg[5],
		Number:    number,
	}, nil
}

func (b *BetRegister)toBetMessage () string{
	return fmt.Sprintf("%s,%s,%d,%s,%d", b.Name, b.Lastname, b.Document, b.Birthdate, b.Number)
}

// getChunkMessage creates the payload with the format of 
// a chunk message:
// client_id,bet_message,bet_message,...,fin_message
func getChunkMessage(bets []*BetRegister, client_id string) string{
	chunk_message := client_id
	fin_payload := client_id + ",FIN"

	for _, bet := range bets {
		payload := fmt.Sprintf("%s,%s",client_id,bet.toBetMessage())
		chunk_message += fmt.Sprintf(",%d,%s", len(payload),payload)
	}

	complete_msg := fmt.Sprintf("%s,%d,%s", chunk_message,len(fin_payload),fin_payload)
	return complete_msg
}

func readChunkFromFile(reader *csv.Reader, chunksize int) ([]*BetRegister, error){
	var bets []*BetRegister
    for i := 0; i < chunksize; i++ {
        readLine, read_err := reader.Read()
        if read_err != nil{
            return bets, read_err
        }
		readBet, err := FromCSV(readLine)
		if err != nil{
			return nil, err
		}
		bets = append(bets, readBet) 
    }

    return bets, nil
}