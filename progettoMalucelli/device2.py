import socket as sk
import time 
import dataCollector as dc

client_ip = "192.168.1.3"
gateway_ip = "192.168.1.1"

client_mac = "CF:18:56:92:13:CF"
gateway_mac = "AB:53:5E:2A:AA:C5"

client_port = ""
gateway_port = 8000

gateway = ("localhost", gateway_port)

data = []

try:
    while True:
        #data meameasurement
        print("measuring data")
        data.append((dc.getTime(),dc.getTemperature(),dc.getHumidity()))
        
        print("data measured, opening the connection with the gateway")
        #creating socket and connecting to the gateway
        socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        socket.connect(gateway)
        client_port = str(socket.getsockname()[1])
        print("connection opened, sending data to gateway")
        
        #creating headers
        header_Ethernet = client_mac + gateway_mac
        header_Ip = client_ip + gateway_ip
        header_udp = str(client_port).zfill(5) + str(gateway_port).zfill(5)
        message = header_Ethernet + header_Ip + header_udp
        
        for measurement in data:
            message = message + measurement[0] + ";" + str(measurement[1])  + ";" + str(measurement[2]) + ";"
        message = message[0:-1]
        
        start = time.time()
        socket.sendto(bytes(message, "utf-8"), gateway) #send data to gateway
        print("data sent, waiting for response message (128 bytes buffer)")
        
        received_message, address = socket.recvfrom(128) #waiting for gateway response
        received_message.decode()
        if received_message[66:] == "received":
            print("response message received from gateway")
        
        end = time.time()
        print("transmission time: ", end - start, " seconds") #calculating transmission time
        
        socket.close() #closing connection
        
        print("connection closed. Wait a day to send data again\n\n\n")
        time.sleep(60)
        data.clear()
        
finally:
    socket.close()