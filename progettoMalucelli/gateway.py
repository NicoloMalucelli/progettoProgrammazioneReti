import socket as sk
import time

socket_lan = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
socket_cloud = ""

CLIENT_NUMBER = 4

gateway_lan_ip = '192.168.1.1'
gateway_cloudside_ip = '10.10.10.1'
cloud_ip = "10.10.10.2"

gateway_lanside_mac = "AB:53:5E:2A:AA:C5"
gateway_cloudside_mac = "EF:32:32:AB:A1:C9"
cloud_mac = "CF:4A:63:33:9B:44"

gateway_lanside_port = 8000
gateway_cloudside_port = ""
cloud_port = 8200

waiting_list = {}
arp_table = {}

socket_lan.bind(("localhost", gateway_lanside_port))

try:
    while True:
        print("Waiting for device connection... (128 bytes buffer)")
        received_message, address = socket_lan.recvfrom(128)
        received_message =  received_message.decode("utf-8")
        
        #reading headers
        header_Ethernet = received_message[0:34]
        header_Ip = received_message[34:56]
        header_Udp = received_message[56:66]
        device_ip = header_Ip[0:11]
        device_mac = header_Ethernet[0:17]
        device_port = header_Udp[0:5]
        
        #creating response headers
        header_Ethernet = gateway_lanside_mac + device_mac
        header_Ip = gateway_lan_ip + device_ip
        header_Udp = str(gateway_lanside_port).zfill(5) + str(device_port).zfill(5)
        
        print("received message from ", device_ip)
        print("sending response message to ", device_ip, "...\n")
        
        response = header_Ethernet + header_Ip + header_Udp + "received"
        socket_lan.sendto(bytes(response, "utf-8"), ("localhost", int(device_port)))
        
        #reading message 
        message = received_message[66:]
        arp_table[device_ip] = device_mac
        waiting_list[device_ip] = message
        
        #true if each device sends data
        if len(waiting_list.keys()) == CLIENT_NUMBER:
            
            #creating socket to connect with cloud
            socket_cloud = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            print("opening connection with cloud...")
            socket_cloud.connect(("localhost", cloud_port))
            gateway_cloudside_port = str(socket_cloud.getsockname()[1])
            
            #creating message headers
            header_Ethernet = gateway_cloudside_mac + cloud_mac       
            header_Ip = gateway_cloudside_ip + cloud_ip
            header_Tcp = str(gateway_cloudside_port).zfill(5) + str(cloud_port).zfill(5)
            cloud_message = header_Ethernet + header_Ip + header_Tcp
            
            #creating message
            for ip in waiting_list.keys():
                cloud_message = cloud_message + ip + ";" + waiting_list[ip] + " " 
            cloud_message = cloud_message[0:-1]
            
            start = time.time()
            print("sending data to cloud...")
            socket_cloud.send(cloud_message.encode()) #send data to cloud
            print("data sent to cloud, waiting for cloud response (128 bytes buffer)")
            
            received_message = socket_cloud.recv(128).decode()
            if received_message[64:] == "received":
                print("response message received from cloud")
            
            end = time.time()
            print("transmission time: ", end - start, " seconds")
            
            print("closing connection with cloud...\n\n\n")
            
            socket_cloud.close()
            waiting_list = {}
        
finally:
    socket_lan.close()
    socket_cloud.close()
