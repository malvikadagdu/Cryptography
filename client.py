import socket
import pickle
import sys
from matplotlib import pyplot as plt

HEADERSIZE = 10
localMessageDB = None
mySecret = 6
keys = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1243))
usrChoice = None

def recieveMsgs():
    while True:
        full_msg = b''
        new_msg = True
        while True:
            msg = s.recv(1024)

            if new_msg:
                #print("new msg len:", msg[:HEADERSIZE])
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            #print(f"full message length: {msglen}")

            full_msg += msg

            #print(len(full_msg))

            if len(full_msg) - HEADERSIZE == msglen:
                #print("full msg recvd",full_msg)
                full_msg_decoded = pickle.loads(full_msg[HEADERSIZE:])
            full_msg = b''
            new_msg = True
            return full_msg_decoded

def sendVariable(var):
    s.send(pickle.dumps(var))
    return

def sendCreds():
    uname = input("Enter UNAME\t")
    password = input("Enter Pass\t")
    creds = {"uname": uname, "password": password}
    sendVariable(creds)

def performTask(phase):
    print(localMessageDB[phase])
    if phase == 1:
        pass
    elif phase == 2:
        # get creds from user now
        sendCreds()
    elif phase == 3:
        # authentication successful
        global keys
        keys = recieveMsgs()
    elif phase == 6:
        #2 way authentication successful, now request data
        global usrChoice
        usrChoice = input()

    else:
        print(localMessageDB[phase])
        print("\nTERMINATING CONNECTION")
        sys.exit(1)

def runThis():
    #1st step, receive messages
    recievedMsg = recieveMsgs()
    print("Messages Received")
    global localMessageDB
    localMessageDB = recievedMsg
    phase = recieveMsgs()
    print("1st Phase Received")
    performTask(phase)
    phase = recieveMsgs()
    print("2nd Phase Received")
    performTask(phase)
    #if Authentication is Successful, receive keys, compute Shared Keys and transmit
    global keys
    myPubKey = keys["G"] ** mySecret % keys["N"]
    SharedSecretKey = keys["PubServKey"] ** mySecret % keys["N"]
    sendKeys = {"PubKey_Client": myPubKey, "SecKey_Client": SharedSecretKey}
    print("Transmitted PublicKey and Sec Shared Key to Server")
    sendVariable(sendKeys)
    phase = recieveMsgs()
    performTask(phase)
    #If authentication is successful, Curator is ready, enter choice
    query = {'requestData': 0, 'requestHist': 0}
    global usrChoice
    if (usrChoice == '1'):
        query['requestData'] = 1
    else:
        query['requestHist'] = 1
    sendVariable(query)
    print(query)
    #receive data now
    data = recieveMsgs()
    if type(data["Age"]) is list:
        print("Ploting Hist")

        plt.figure()
        plt.subplot(2,2,1)
        plt.hist(data["Age"])
        plt.title("AGE")
        
        plt.subplot(2, 2, 2)
        plt.hist(data["Height"])
        plt.title("HEIGHT")

        plt.subplot(2, 2, 3)
        plt.hist(data["Salary"])
        plt.title("SALARY")

        plt.show()
    else:
        print("Data is ",data)
runThis()
