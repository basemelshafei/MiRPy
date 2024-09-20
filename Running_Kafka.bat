@echo off
REM Set Kafka directory
set KAFKA_DIR=c:\kafka_2.13-3.8.0

REM Start Zookeeper in a new Command Prompt window
start "" cmd /k "%KAFKA_DIR%\bin\windows\zookeeper-server-start.bat %KAFKA_DIR%\config\zookeeper.properties"

REM Wait for Zookeeper to start (increase timeout to ensure it's up and running)
timeout /t 10

REM Start Kafka in a new Command Prompt window
start "" cmd /k "%KAFKA_DIR%\bin\windows\kafka-server-start.bat %KAFKA_DIR%\config\server.properties"

REM Wait for Kafka to start (increase timeout as Kafka startup can be slow)
timeout /t 10

REM Check if the topic already exists
echo Checking if topic 'my_mir_data' exists...
"%KAFKA_DIR%\bin\windows\kafka-topics.bat" --list --bootstrap-server localhost:9092 | findstr /r "\<my_mir_data\>"

REM If the topic does not exist, create it
if errorlevel 1 (
    echo Topic 'my_mir_data' does not exist, creating it...
    "%KAFKA_DIR%\bin\windows\kafka-topics.bat" --create --topic my_mir_data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
) else (
    echo Topic 'my_mir_data' already exists, skipping creation.
)

echo Kafka setup complete.


