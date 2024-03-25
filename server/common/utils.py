import csv
import datetime
import time


""" Bets storage location. """
STORAGE_FILEPATH = "./bets.csv"
""" Simulated winner number in the lottery contest. """
LOTTERY_WINNER_NUMBER = 7574

FIN_MSG = "FIN"
READY_MSG = "READY"
FIN_MSG_SIZE = "5"
READY_MSG_SIZE = "7"


""" A lottery bet registry. """
class Bet:
    def __init__(self, agency: str, first_name: str, last_name: str, document: str, birthdate: str, number: str):
        """
        agency must be passed with integer format.
        birthdate must be passed with format: 'YYYY-MM-DD'.
        number must be passed with integer format.
        """
        self.agency = int(agency)
        self.first_name = first_name
        self.last_name = last_name
        self.document = document
        self.birthdate = datetime.date.fromisoformat(birthdate)
        self.number = int(number)
    
    @staticmethod
    def from_message(bet_msg: str):
        payload = bet_msg.split(',',1)[1]
        agency, first_name, last_name, document, birthdate, number = payload.split(',')
        return Bet(agency, first_name, last_name, document, birthdate, number)

""" Checks whether a bet won the prize or not. """
def has_won(bet: Bet) -> bool:
    return bet.number == LOTTERY_WINNER_NUMBER

"""
Persist the information of each bet in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def store_bets(bets: list[Bet]) -> None:
    with open(STORAGE_FILEPATH, 'a+') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
        for bet in bets:
            writer.writerow([bet.agency, bet.first_name, bet.last_name,
                             bet.document, bet.birthdate, bet.number])

"""
Loads the information all the bets in the STORAGE_FILEPATH file.
Not thread-safe/process-safe.
"""
def load_bets() -> list[Bet]:
    with open(STORAGE_FILEPATH, 'r') as file:
        reader = csv.reader(file, quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            yield Bet(row[0], row[1], row[2], row[3], row[4], row[5])

def is_end_msg(msg: str) -> bool:
    split_msg = msg.split(',', 2)
    if split_msg[0] == FIN_MSG_SIZE and split_msg[2] == FIN_MSG:
        return True
    return False

def is_ready_msg(msg: str) -> bool:
    split_msg = msg.split(',', 2)
    if split_msg[0] == READY_MSG_SIZE and split_msg[2] == READY_MSG:
        return True
    return False