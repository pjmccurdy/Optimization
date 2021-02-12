import socket






# setting up client
HOST = "172.16.119.10"
PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


data=client_socket.recv(1024)
dataList = data.split(',')
dataFloats = map(float, dataList)
#print(dataList)
#print(dataFloats)
indoorTemp = dataFloats[0]
outdoorTemp = dataFloats[1]
print("Indoor Temp received as:", indoorTemp)
print("Outdoor Temp received as:", outdoorTemp)

optE = indoorTemp*2-6;

result = str(optE)
rresult = result + "\n"

client_socket.sendall((rresult).encode())
