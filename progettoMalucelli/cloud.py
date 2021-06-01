import socket

cloud_ip = "10.10.10.2"
cloud_mac = "CF:4A:63:33:9B:44"
cloud_port = 8200

socket_cloud = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cloud.bind(("localhost", cloud_port))
socket_cloud.listen(1)
print("Cloud online\n\n")

try:

    while True:
        print("Waiting for gateway connection...")
        conn, addr = socket_cloud.accept()
        print("Gateway connected, ready to receive data (256 bytes buffer)")
        message = conn.recv(256)
        message = message.decode()
        
        #reading headers
        header_Ethernet = message[0:34]
        header_Ip = message[34:54]
        header_Tcp = message[54:64]
        #reading message
        message = message[64:]
        #reading gateway info
        gateway_ip = header_Ip[0:10]
        gateway_mac = header_Ethernet[0:17]
        gateway_port = header_Tcp[0:5]
        
        print("Received message from ", gateway_ip)
        
        #creating response header
        header_Ethernet = cloud_mac + gateway_mac
        header_Ip = cloud_ip + gateway_ip
        header_Tcp = str(cloud_port).zfill(5) + str(gateway_port).zfill(5)
        
        #creating response message
        response = header_Ethernet + header_Ip + header_Tcp + "received"
        
        print("Sending response message to ", gateway_ip, "...")
        conn.send(bytes(response, "utf-8"))

        print("Closing connection...\n")        
        conn.close()
        
        print("received data: ")
        
        for message_from_device in message.split(" "):
            data = message_from_device.split(";")
            ip = data[0]
            data = data[1:]
            for i in range(0,int(len(data)/3)):
                print(ip + " - " + data[3*i] + " - " + data[3*i+1] + "°C - " + data[3*i+2] + "%")
        print("\n\n\n\n")
        
finally:
    socket_cloud.close()