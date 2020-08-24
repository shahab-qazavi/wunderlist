docker stop taskmanager
docker rm taskmanager
docker rmi taskmanager
docker build -t taskmanager .
docker run -d --restart always --name taskmanager -p 8011:8000 --network mongo taskmanager
