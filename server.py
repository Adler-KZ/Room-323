import threading, socket, random,pickle

# ------------------------------Global vaiables-------------------------------
rooms = 0
usernames_roomID={}
clients_RoomUser={}

# ------------------------------Classes-------------------------------
class Data:
    def __init__(self,method='',username='',color='',roomID='',message='',list=''):
        self.method = method
        self.username=username
        self.color=color
        self.roomID = roomID
        self.message = message
        self.list = list

class Server:
    def __init__(self,ip='127.0.0.1', port=4000):
        self.server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = ip
        self.server_port = port
        self.server_soc.bind((ip, port))

    def run(self):
        self.server_soc.listen(10)
        print('server is run')
        for i in range(10):
            client, addr = self.server_soc.accept()
            clients_RoomUser[(client,addr)]=''
            print(f'The new user ({addr[0]}) joined the server')
            threading.Thread(target=self.receive, args=(client, addr)).start()
        self.server_soc.close()

    def receive(self,CLIENT, ADDR):
        while True:
            try:
                data = CLIENT.recv(1024)
                self.analyze_data(data, CLIENT,ADDR)
            except:
                print(f'User {ADDR[0]} disconnected!')
                id, user = clients_RoomUser.pop((CLIENT,ADDR))
                usernames_roomID.pop(user)
                self.users_room()
                break

    def analyze_data(self,DATA, CLIENT,ADDR):
        data = pickle.loads(DATA)
        global rooms
        match data.method:
            case 'connect':
                # Unique Username
                username = data.username
                name = username
                while True:
                    if name not in usernames_roomID.keys():
                        break
                    name = f'{username}_{random.randint(0, 99)}'
                usernames_roomID[name]=''
                data = Data(username=name,roomID=rooms)
                CLIENT.sendall(pickle.dumps(data))
            case 'message':
                for c in clients_RoomUser.keys():
                    if clients_RoomUser[c][0]==data.roomID:
                        c[0].sendall(DATA)
            case 'create':
                rooms += 1
                clients_RoomUser[(CLIENT,ADDR)]=(str(rooms),data.username)
                usernames_roomID[data.username]=str(rooms)
                # roomID_users[str(rooms)]=data.username
                data = Data(method='create',roomID=str(rooms))
                CLIENT.sendall(pickle.dumps(data))
                self.users_room()
            case 'exist':
                clients_RoomUser[(CLIENT,ADDR)] = (data.roomID,data.username)
                usernames_roomID[data.username]=data.roomID
                self.users_room()
    
    def users_room(self):
        data = Data(method='refresh',list=usernames_roomID)
        for c in clients_RoomUser.keys():
            c[0].sendall(pickle.dumps(data))
            
# ------------------------------Main-------------------------------
if __name__ == '__main__':
    server = Server()
    server.run()
