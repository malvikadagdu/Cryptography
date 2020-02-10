import socket
import pickle
import sys

N = 23
G = 5
SecretKeyServer = 15
PublicKeyServer = (G ** SecretKeyServer) % N
HEADERSIZE = 10
data = {"Age":21, "Height": 108, "Salary":21000}
hist = {"Age":[21,22,33,21,12,45,56,6,72,23], "Height":[100,110,120,23,123,123,45345,345,123,120], "Salary":[1000,2000,12000,23000,50000,78500,43000,21000,61000,52000]}

usersSecDB = {"Malvika":"Mal123", "Laukik":"Lauk123"}
messages = { 2:"Enter Credentials", 3: "Authentication Successful", 4:"Username not registered", 5: "Authentication Failed", 6: "Curator is Ready,\nRequest Data:1 Request Histogram:2"}
phase = 1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1243))
s.listen(5)
d = {"G":G, "N": N, "PubServKey": PublicKeyServer}
authUser = False

def sendClientPickle(data):
    msg = pickle.dumps(data)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    clientsocket.send(msg)
    return


while True:    
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")
    sendClientPickle(messages)
    phase = 2
    sendClientPickle(phase)
    print("sent recv creds")
    recvCreds = pickle.loads(clientsocket.recv(1024))
    print("received")
    print(recvCreds)
    
    if (recvCreds["uname"] in usersSecDB.keys()) and (recvCreds["password"] == usersSecDB[recvCreds["uname"]]):
        print("Authentic User")
        phase = 3
        sendClientPickle(phase)
        authUser = True
    else:
        print("Failed Authentication")
        phase = 5
        sendClientPickle(phase)
        authUser = False
        
    if (authUser == True):
            
        #send Keys
        sendClientPickle(d)
        clientKeys = pickle.loads(clientsocket.recv(1024))
        print("Received Public Key is ",clientKeys)
        SecKey_Server = clientKeys["PubKey_Client"] ** SecretKeyServer % N
        if (SecKey_Server == clientKeys["SecKey_Client"]):
            print("Authentication Successful")
            phase = 6
            sendClientPickle(phase)

            #wait for request
            print("Waiting for request")
            client_query = pickle.loads(clientsocket.recv(1024))
            if client_query['requestData'] == 1:
                #transmit data here
                sendClientPickle(data)
                print('transmit data')
                continue
            elif client_query['requestHist'] == 1:
                #transmit Histo here
                sendClientPickle(hist)
                print('transmit histo')
                continue
        
        
    else:
        print("GOING TO TRANSMIT PHASE 3")
        phase = 5
        sendClientPickle(phase)
        clientsocket.close()
        print("CLOSED SESSION")
        sys.exit(1)
