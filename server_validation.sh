echo "Starting containers"

#Run server service in docker-compose-dev
docker-compose -f docker-compose-dev.yaml up server -d > /dev/null 2>&1
#Run tester define in docker-compose-dev 
docker-compose -f docker-compose-dev.yaml up tester -d > /dev/null 2>&1


#Install netcat
echo "Installing netcat..."
docker exec tester bash -c "apt-get update; apt-get install -y netcat"  > /dev/null 2>&1

# Start test
echo "The result is:"
docker exec tester bash -c 'if [ "$(echo "Test01" | nc server 12345)" = "Test01" ]; then echo "OK"; else echo "Error"; fi '

echo "Closing containers"
#stop and remove all containers
make docker-compose-down > /dev/null 2>&1