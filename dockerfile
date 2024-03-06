from python:latest
  LABEL maintainer "priyankayadav080399@gmail.com"
  Run apt update && apt install nginx -y
  WORKDIR /app
  COPY ../
 // ENTRYPOINT[","]
  EXPOSE 8080
  CMD["python", "main.py"]
