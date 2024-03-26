import sys

# Constants
INIT_LINES = ["version: '3.9'","name: tp0","services:"]
SERVER_LINES = ["\tserver:",
                    "\t\tcontainer_name: server",
                    "\t\timage: server:latest",
                    "\t\tentrypoint: python3 /main.py",
                    "\t\tenvironment:",
                    "\t\t\t- PYTHONUNBUFFERED=1",
                    "\t\t\t- LOGGING_LEVEL=DEBUG",
                    "\t\tnetworks:",
                    "\t\t\t- testing_net"]
NETWORK_LINES = ["\nnetworks:",
                    "\ttesting_net:",
                    "\t\tipam:",
                    "\t\t\tdriver: default",
                    "\t\t\tconfig:",
                    "\t\t\t\t- subnet: 172.25.125.0/24"]

def write_lines(file,lines):
    for line in lines:
        try:
            file.write(line.replace("\t","  ") + '\n')
        except Exception:
            return -1
    return 0

def write_n_clients(file,amount):
    for i in range(1, amount + 1):
        client_lines = ["\n\tclient{}:".format(str(i)),
                        "\t\tcontainer_name: client"+ str(i),
                        "\t\timage: client:latest",
                        "\t\tentrypoint: /client",
                        "\t\tenvironment:",
                        "\t\t\t- CLI_ID=" + str(i),
                        "\t\t\t- CLI_LOG_LEVEL=DEBUG",
                        "\t\tnetworks:",
                        "\t\t\t- testing_net",
                        "\t\tdepends_on:",
                        "\t\t\t- server"]
        if write_lines(file,client_lines) != 0:
            return -1
        
    return 0

def main(amount):
    if amount < 1:
        raise ValueError("Invalid amount of clients")
    new_file_name = "docker-compose-dev-with-{}-clients.yaml".format(str(amount))

    try:
        new_file = open(new_file_name,"w")
    except Exception:
        raise RuntimeError("Error opening file")
    
    if write_lines(new_file,INIT_LINES + SERVER_LINES) != 0:
        new_file.close()
        raise RuntimeError("Error writing in file")

    if write_n_clients(new_file,amount) != 0:
        new_file.close()
        raise RuntimeError("Error writing in file")

    if write_lines(new_file,NETWORK_LINES) != 0:
        new_file.close()
        raise RuntimeError("Error writing in file")

    new_file.close()
    print("File was created successfully")
    return 0

    
if __name__ == "__main__":
    main(int(sys.argv[1]))