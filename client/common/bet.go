package common

import (
	"fmt"
	"strings"
	"strconv"
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

func FromMessage (message string) (*BetRegister, error){
	split_msg := strings.Split(message, ",")
	if len(split_msg) != 6 {
		return nil, fmt.Errorf("invalid format")
	}
	document, err := strconv.Atoi(split_msg[4])
	if err != nil {
		return nil, fmt.Errorf("invalid document format: %v", err)
	}
	number, err := strconv.Atoi(split_msg[6])
	if err != nil {
		return nil, fmt.Errorf("invalid number format: %v", err)
	}

	return &BetRegister{
		Name:      split_msg[2],
		Lastname: split_msg[3],
		Document: document,
		Birthdate: split_msg[5],
		Number:    number,
	}, nil
}

func (b *BetRegister)toBetMessage () string{
	return fmt.Sprintf("%s,%s,%d,%s,%d", b.Name, b.Lastname, b.Document, b.Birthdate, b.Number)
}