import socket
import sqlite3
import os
from _thread import *
import googlemaps
import time
from twilio.rest import Client


# Create the emergencies table
def init_db():
    conn = sqlite3.connect('emergencies.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS dispatchers (id INTEGER PRIMARY KEY, name TEXT, type TEXT, location TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS emergency_logs (id INTEGER PRIMARY KEY, name TEXT, dispatcher_id INTEGER, type TEXT, address TEXT, status TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (dispatcher_id) REFERENCES dispatchers(id))''')
    conn.commit()

def populate_db():
    dispatchers =[
        (1, 'Udupi Town Police Station', 'police', '76, Lombard Memorial Hospital Rd, near Mission Compound, Chitpady, Udupi, Karnataka 576101'),
        (2,'Manipal Police Station', 'police', '8QXP+JCP, SH 25A, Madhav Nagar, Eshwar Nagar, Manipal, Karnataka 576104'),
        (3, 'Malpe Police Station','police', '9P63+69G, Kola, Malpe, Karnataka 576108'),
        (4, 'Katapady Police Station','police', '7PMX+Q5P, Katapadi Rd, Katpadi, Karnataka 576122'),
        (5, 'Kaup Police Station','police', '6PHX+G75, Kaup Main Rd, Uliyargoli, Kaup, Karnataka 574106'),

        (6, 'Kasturba Hospital, Manipal','medical', ' 9Q3Q+FVH, Udupi - Hebri Rd, Madhav Nagar, Manipal, Karnataka 576104'),
        (7, 'Adarsha Hospital','medical', 'Near KSRTC Bus stand, Udupi, Karnataka 576101'),
        (8, 'Gandhi Hospital','medical', '8PVX+HH3, SH 37, Thenkpete, Maruthi Veethika, Udupi, Karnataka 576101'),
        (9, 'District Hospital Udupi','medical', '8PMV+J77 Sarathi Bhavan, Ajjrakadu Road, Brahmagiri, Udupi, Karnataka 576101'),
        (10, 'New City Hospital','medical', 'Kadabettu, Vidyaranya Marg, opp. Shaneshwara Temple, Brahmagiri, Udupi, Karnataka 576101'),

        (11, 'Udupi Fire Station','fire', '8PHR+43P, Swami Vivekananda Rd, Brahmagiri, Udupi, Karnataka 576101'),
        (12, 'Cnara Fire Service','fire', ' D.No 5-50, Kampanbettu, Udyavara, Udupi, Karnataka 574118'),
    ]
    conn = sqlite3.connect('emergencies.db')
    c=conn.cursor()
    c.execute(''' SELECT count(id) FROM dispatchers ''')
    n=c.fetchone()[0]
    if n==0:
        conn.executemany('INSERT INTO dispatchers ( id, name, type, location) VALUES ( ?, ?, ?, ? )', dispatchers)
        conn.commit()
    conn.close()

init_db()
populate_db()

# Insert own values for account_sid, auth_token, dst_ph
account_sid = sid
auth_token = tok

dst_ph_fire = ph1
dst_ph_police = ph2
dst_ph_med = ph3
client = Client(account_sid, auth_token)


def get_location(address):
    # Geocode the address to get the latitude and longitude
    gmaps = googlemaps.Client(key='AIzaSyC9QD76UydJoopOIttI-Sg-WOLnuqlSvj4')
    geocode_result = gmaps.geocode(address)
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    return (lat, lng)

def find_nearest_dispatcher(emergency_type, address):
    # Query all dispatchers of required type
    conn = sqlite3.connect('emergencies.db')
    gmaps = googlemaps.Client(key='AIzaSyC9QD76UydJoopOIttI-Sg-WOLnuqlSvj4')
    c = conn.cursor()
    c.execute(''' SELECT id,name, location FROM dispatchers WHERE type = ? ''', (emergency_type,))
    dispatchers = c.fetchall()
    conn.close()

    distances = []
    for dispatcher in dispatchers:
        dispatcher_id, name, location = dispatcher
        loc=get_location(location)
        #print("Dispatcher Location:", loc)
        distance = gmaps.distance_matrix((address[0], address[1]), (loc[0], loc[1]))['rows'][0]['elements'][0]['distance']['value']
        distances.append((dispatcher_id,name, distance))

    # Sort the dispatchers by distance
    distances.sort(key=lambda x: x[2])
    # Return the nearest dispatcher
    nearest_dispatcher = distances[0]
    return nearest_dispatcher

def get_dispatcher_location(dispatcher):
    # Query the database for the location of the dispatcher
    conn = sqlite3.connect('emergencies.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT location FROM dispatchers WHERE id = ?''', (dispatcher[0],))
    location = cursor.fetchone()[0]
    conn.close()
    loc=get_location(location)   
    return loc

def calculate_eta(dispatcher, address):
    gmaps = googlemaps.Client(key='AIzaSyC9QD76UydJoopOIttI-Sg-WOLnuqlSvj4')
    dispatcher_location = get_dispatcher_location(dispatcher)
    # Calculate the directions between the dispatcher and the address
    directions_result = gmaps.directions(dispatcher_location, address, mode="driving", departure_time="now")
    # Extract the ETA from the directions result
    eta = (directions_result[0]['legs'][0]['duration_in_traffic']['value'])/100
    return eta

def handle_client(client_socket):
    # Receive the emergency request from the client
    
    emergency_type = int(client_socket.recv(1024).decode().strip())
    address = client_socket.recv(1024).decode().strip()

    if emergency_type==1:
        type='fire'
    elif emergency_type==2:
        type='police'
    elif emergency_type==3:
        type='medical'
    
    print(type+' emergency. Help requested from '+ address +'\n')

    # Query the database for the nearest emergency dispatcher    
    addr=get_location(address)
    dispatcher = find_nearest_dispatcher(type, addr)
    id, name=dispatcher[0],dispatcher[1]
    print(name +' dispatched for '+address+'\n')

    # Send emergence message to dispatcher    
    sms_body = f"Emergency {type.capitalize()} at {address}. Dispatch help immediately!!."
    if type=='fire':
        client.messages.create(to=dst_ph_fire, from_=ph_no, body=sms_body)
    if type=='police':
        client.messages.create(to=dst_ph_police, from_=ph_no, body=sms_body)
    if type=='medical':
        client.messages.create(to=dst_ph_med, from_=ph_no, body=sms_body)

    conn = sqlite3.connect('emergencies.db')
    c=conn.cursor()
    c.execute('INSERT INTO emergency_logs (dispatcher_id, name, type, address , status) VALUES (?,?, ?, ?, ?)', (id,name,emergency_type, address, 'ongoing' ))
    conn.commit()

    client_socket.send(name.encode())
    
    # Calculate the ETA using Google Maps API
    eta = calculate_eta(dispatcher, address)

    # Send the ETA back to the client
    client_socket.send(str(eta).encode())
    time.sleep(eta)
    while True:
        s=client_socket.recv(1024).decode()
        if not s:
            break
    
    c.execute("""UPDATE emergency_logs SET status = 'completed' WHERE dispatcher_id =? and address=?""",(id,address))
    conn.commit()
    conn.close()  
    

    print('Emergency handled at '+address+' Logged successfully\n')
    client_socket.close()


# The server socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind(('192.168.224.35', 12354))
except socket.error as e:
    print(str(e))
    
print('Waitiing for a Connection..')    
server_socket.listen(20)

while True:
    client_socket, addr = server_socket.accept()
    start_new_thread(handle_client, (client_socket, ))

server_socket.close()
