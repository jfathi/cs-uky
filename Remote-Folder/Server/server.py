import os
import sys
import time
import socket
from functools import partial

DWNLD_DOC   = 'Download_Doc.txt'
SESSION_RPT = 'Session_Report.txt'
TEMP_FILE   = 'server.tmp'
FOLDER_NAME = 'Server_Folder'
SERVER_NAME = 'banana'

PERMITTED_USERS = {'jfathi':'password', 'silvestri':'password'}

MAX_PACKET = 1024
MAX_PAYLOAD = 1014
HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

NO_LOGIN      = 0
INVALID_LOGIN = 1

FILE_DNE     = 0
FILE_NO_DATA = 1

REPORT_FILESIZE = 'filesize'
REPORT_SPEED    = 'speed'

TOO_FAST = 'FAST'

BYTES_PER_KB    = 1000
BYTES_PER_MB    = 1000000
BYTES_PER_GB    = 1000000000

CMD_LOGIN     = 'LOGIN'
CMD_UPLOAD    = 'UPLOAD'
CMD_OVERWRITE = 'OVERWRITE'
CMD_DOWNLOAD  = 'DOWNLOAD'
CMD_DELETE    = 'DELETE'
CMD_DIR       = 'DIR'

SERVER_SUCCESS = 'SUCCESS'
SERVER_FAILURE = 'FAILURE'
REQUEST_FOR_INFO = 'REQUEST'

client_fd = ''
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
AUTHENTICATED = False

num_Dwnlds = {}
download_experiments = {}
upload_experiments = {}

def Folder_Documentation(updateDoc=False):
    # Confirm that relevant global vars are modifiable.
    global num_Dwnlds

    # Use the Download Doc to populate the numDownloads dictionary.
    if not updateDoc:
        # Open/create the Download Doc.
        fd = open(DWNLD_DOC,"r+")
        # Determine the names of all files on the server.
        file_names = os.listdir(f"{FOLDER_NAME}")
        
        # Initialize a list for files present on the server, but absent
        # from the Download Doc.
        undocumented_files = []

        for file in file_names:
            # Assume given file is absent from the Download Doc.
            # Assume respective number of downloads for file is 0.
            documented = False
            num_Dwnlds[file] = 0

            # Scan the Download Doc for filename. If found, set respective 
            # dictionary value to the number of downloads from the Doc.
            for cached_data in fd:
                file_cache = cached_data.split('?')
                if file_cache[0] == file:
                    documented = True
                    num_Dwnlds[file] = int(file_cache[1]) if (int(file_cache[1]) > 0) else 0
                    break
 
            # Filename was absent from the Download Doc. Add to list for 
            # later appension.
            if (documented == False):
                undocumented_files.append(file)
        # Close the Download Doc after usage.
        fd.close()
        
        # Open the Download Doc for appension of undocumented file information.
        fd = open(DWNLD_DOC, "a")
        for file in undocumented_files:
            fd.write(f'{file}?{num_Dwnlds[file]}\n')
        fd.close()
    
    # At end of communication, populate Download Doc with updated info.
    else:
        
        # Rebuild the Download Doc using updated info from the session.
        fd1 = open(DWNLD_DOC, "w")
        for file in num_Dwnlds:
            fd1.write(f'{file}?{num_Dwnlds[file]}\n')
        fd1.close()

        # Append data from significant upload/download sessions to the Session Report Doc
        if ((len(download_experiments) > 0) or len(upload_experiments) > 0):
            
            fd2 = open(SESSION_RPT, "a+")
            
            fd2.write(f'Session Report: {time.ctime(time.time())}\n')

            # Report download session data - if any exists.
            # Format: time,bytes_delivered (for each second of transmission)
            for experiment in download_experiments:
                fd2.write(f'Download Experiment #{experiment}\n')
                seconds_printed = 1
                for bytes_delivered in download_experiments[experiment]:
                    fd2.write(f'{seconds_printed},{bytes_delivered}\n')
                    seconds_printed += 1
                fd2.write('\n')

            # Report upload session data - if any exists.
            # Format: time,bytes_delivered (for each second of transmission)
            for experiment in upload_experiments:
                fd2.write(f'Upload Experiment #{experiment}\n')
                seconds_printed = 1
                for bytes_delivered in upload_experiments[experiment]:
                    fd2.write(f'{seconds_printed},{bytes_delivered}\n')
                    seconds_printed += 1
                fd2.write('\n')
             
            fd2.close()

def Data_String(literal, type):

    # Assume that the incoming value is not of float type and convert accordingly.
    literal = float(literal)

    # If requested, return a formatted string for the number of bytes in a certain file.
    if (type == REPORT_FILESIZE):
        if (literal < BYTES_PER_KB):
            return f'{literal}  b'
        elif (literal < BYTES_PER_MB):
            return f'{round(literal / BYTES_PER_KB, 2)} kb'
        elif (literal < BYTES_PER_GB):
            return f'{round(literal / BYTES_PER_MB, 2)} Mb'
        else:
            return f'{round(literal / BYTES_PER_GB, 2)} Gb'

    # If requested, return a formatted string for the historical transmission speed for a given event.
    elif (type == REPORT_SPEED):
        if (literal == TOO_FAST):
            return literal
        elif (literal < BYTES_PER_KB):
            return f'{literal}  bps'
        elif (literal < BYTES_PER_MB):
            return f'{round(literal / BYTES_PER_KB, 2)} kbps'
        elif (literal < BYTES_PER_GB):
            return f'{round(literal / BYTES_PER_MB, 2)} Mbps'
        else:
            return f'{round(literal / BYTES_PER_GB, 2)} Gbps'

def Recieve_Packet():

    # Wait to recieve an packet from the client.
    # Every packet will have a header of a fixed length (10 bytes)
    packet_header = client_fd.recv(HEADER_LENGTH)
    
    # If no bytes are recieved, connection has been closed by client.
    # Document collected data and shut down the server.
    if not len(packet_header):
        print("Connection closed by the client. Server shutting down...")
        Folder_Documentation(updateDoc=True)
        sys.exit()
    
    # The header will contain the number of incoming bytes in string form.
    # Decode the packet...
    packet_length = int(packet_header.decode('utf-8').strip())

    # ...and wait for the expected bytes accordingly.
    packet = client_fd.recv(packet_length)
    
    # Return recieved bytes for interpretation in the caller function.
    return packet

def Download_File(filename, fileloc):
    # Confirm that relevant global vars are modifiable.
    global download_experiments

    # Determine the size of the requested file, in bytes.
    filesize = os.path.getsize(fileloc)

    # print(f'Filesize: {filesize}')
    # print(f'Expected bytes: {filesize + (10 * (int(filesize / MAX_PAYLOAD) + 1))}')

    # Transmit the size of the incoming file to the client.
    packet = f'{SERVER_SUCCESS:<{HEADER_LENGTH}}' + f'{filesize}'
    packet = f'{len(packet):<{HEADER_LENGTH}}' + packet
    client_fd.send(bytes(packet, 'utf-8'))

    # Open a file descriptor to read the file's binary data to the client.
    fd = open(fileloc, 'rb')

    # Record the start time of the download.
    download_start = time.time()

    # Initialize variables for documentation purposes.
    bytes_per_second = 0        # Number of chunks delivered over one-second.
    prev_time = download_start  # Variable for second-to-most recent time-check.
    curr_time = prev_time       # Variable for most recent time-check.
    transmission_data = []      # List of "num_chunks" delivered per second.
    
    # File Download - Main Transmission Loop
    # (While bytes in the file remain untransmitted...)
    for data_chunk in iter(partial(fd.read, MAX_PAYLOAD), b''):
        
        # Transmit a data chunk of 1014 or less bytes with a 10-byte header.
        # Maximum Packet Size = 1024 bytes
        packet = data_chunk
        packet_header = bytes(f"{len(packet):<{HEADER_LENGTH}}", 'utf-8')
        packet = packet_header + packet
        client_fd.send(packet)

        # Iterate the number of bytes delivered in the past second.
        # Update a current-time variable to the local time.
        bytes_per_second += len(data_chunk)
        curr_time = time.time()

        # If the time interval is approximately (>=) 1 second,
        # Document the number of chunks delivered during the period
        # and reset/update the variables for documentation.
        if (curr_time - prev_time >= 1):
            prev_time = curr_time
            transmission_data.append(bytes_per_second)
            bytes_per_second = 0

    # Record the total time for the file transmission.
    download_time = curr_time - download_start

    # Record the experiment data if and only if the data is significant.
    if (len(transmission_data) >= 2):
        download_experiments[len(download_experiments)] = transmission_data

    # Close the file descriptor used for the file transmission.
    fd.close()

    # Confirm that the client has successfuly recieved the file.
    packet = Recieve_Packet()

    # Error Case Protection:
    # An error has occurred on the client-side while processing the file.
    # The connection has been interrupted/closed - so shut down the server.
    if (packet.decode('utf-8') != SERVER_SUCCESS):
        print('A critical error has occurred on the client-side. Shutting down the server...')
        Folder_Documentation(updateDoc=True)
        sys.exit()

    # Return download time and size of the file downloaded to caller function.
    return (download_time, filesize)

def Login():
    # Confirm that relevant global vars are modifiable.
    global AUTHENTICATED

    # Assume that the user is authenticated and no failure is apparent.
    AUTHENTICATED = True
    failure_reason = ''

    # Recieve authentication package from the client.
    packet = Recieve_Packet().decode('utf-8')

    # Error Case: Client service does not support authentication
    # or packet is corrupted. User must try again.
    if (packet[:HEADER_LENGTH].strip() != CMD_LOGIN):
        print('Client is unauthenticated! Please try again...', end='\n\n')
        AUTHENTICATED = False
        failure_reason = f'{NO_LOGIN}'
    
    # Otherwise, process the packet for login details 
    # (requested username, requested password).
    else:
        login_details = packet[HEADER_LENGTH:]
        requested_user = login_details[:HEADER_LENGTH].strip()
        requested_pwd = login_details[HEADER_LENGTH:].strip()

        # Error Case: User with requested username is not on file.
        # Prepare to drop the connection.
        if (requested_user not in PERMITTED_USERS):
            print('Invalid user/password combination. Please try again...', end='\n\n')
            AUTHENTICATED = False
            failure_reason = f'{INVALID_LOGIN}'
        
        # Error Case: User on file does not have the requested password.
        # Prepare to drop the connection.
        elif (requested_pwd != PERMITTED_USERS[requested_user]):
            print('Invalid user/password combination. Please try again...', end='\n\n')
            AUTHENTICATED = False
            failure_reason = f'{INVALID_LOGIN}'

    # If the incoming connection has been marked as unauthenticated,
    # return an appropriate response to the client.
    if not AUTHENTICATED:
        server_response = f'{SERVER_FAILURE:<{HEADER_LENGTH}}' + failure_reason
        server_response = f'{len(server_response):<{HEADER_LENGTH}}' + server_response
        client_fd.send(bytes(server_response, 'utf-8'))
    
    # Otherwise, the user is logged in.
    # Report accordingly to the client and the server terminal.
    else:
        print(f'User {requested_user} is logged into the server!')
        server_response = f'{len(SERVER_SUCCESS):<{HEADER_LENGTH}}' + SERVER_SUCCESS
        client_fd.send(bytes(server_response, 'utf-8'))

def Upload(filename):
    # Confirm that relevant global vars are modifiable.
    global num_Dwnlds
    global upload_experiments

    # Assume that the file can be uploaded to the server.
    # Prepare a successful response packet.
    response = SERVER_SUCCESS

    # Identify the location requested.
    fileloc = f'{FOLDER_NAME}\{filename}'

    # If a file on the server has the name of the file to be uploaded,
    # the client is requesting an overwrite process.
    # Indicate cient request to the terminal and prepare a Request for Info response packet.
    if filename in os.listdir(FOLDER_NAME):
        print('Request to overwrite ' + filename + '...')
        response = REQUEST_FOR_INFO
    # Otherwise, the filename is 'new' to the folder. Indicate the client request to the terminal.
    else:
        print('Request to upload ' + filename + '...')

    # Deliver the appropriate response to the client.
    packet = f"{len(response):<{HEADER_LENGTH}}" + response
    client_fd.send(bytes(packet, 'utf-8'))

    # Recieve the client response for processing.
    packet = Recieve_Packet()

    # If server requested info, proces the packet prefix (10 bytes) for info. 
    if (response == REQUEST_FOR_INFO):

        # Option A - Overwrite Request Confirmed. Size of incoming file appended.
        if ((packet[:HEADER_LENGTH].decode('utf-8')).strip() == CMD_OVERWRITE):
            print('Overwriting ' + filename + '...', sep='')
            packet = packet[HEADER_LENGTH:]
        
        # Option B - Overwrite Request Abandoned. Terminate download process.
        elif ((packet[:HEADER_LENGTH].decode('utf-8')).strip() == SERVER_FAILURE):
            print('File overwrite abandoned.')
            return

        # Option C - A serious error has occurred. Shut the server down.
        else:
            print('A serious error has occurred on the client-side. Shutting down the server...')
            Folder_Documentation(updateDoc=True)
            sys.exit()
    
    # Process the size of the incoming file.
    filesize = int(packet)

    # Identify and open a temporary file for the upload process.
    i = 0
    fileloc_tmp = f'{FOLDER_NAME}\{i}.tmp'
    while (fileloc_tmp in os.listdir(FOLDER_NAME)):
        i += 1
        fileloc = f'{FOLDER_NAME}\{i}.tmp'
    fd_tmp = open(fileloc_tmp, 'wb+')

    # Record the start time of the upload.
    upload_start = time.time()

    # Initialize variables for documentation purposes.
    total_bytes_read = 0          # Total number of bytes uploaded.
    bytes_per_second = 0        # Number of chunks delivered over one-second.
    prev_time = upload_start    # Variable for second-to-most recent time-check.
    curr_time = prev_time       # Variable for most recent time-check.
    transmission_data = []      # List of "num_chunks" delivered per second.
    
    # File Upload - Main Transmission Loop
    while (total_bytes_read != filesize):

        # Recieve a packet of 1024 bytes or less. 
        # Write to the temporary file designated.
        packet = Recieve_Packet() 
        fd_tmp.write(packet)

        # Increment the number of bytes delivered in the past second.
        # Update a current-time variable to the local time.
        bytes_per_second += len(packet)
        curr_time = time.time()

        # If the time interval is approximately (>=) 1 second,
        # Document the number of chunks delivered during the period
        # and reset/update the variables for documentation.
        if (curr_time - prev_time >= 1):
            prev_time = curr_time
            transmission_data.append(bytes_per_second)
            bytes_per_second = 0

        # Increment the total number of bytes delivered during the transmission.
        # Loop will continue until the number of bytes equals the expected file size.
        total_bytes_read += len(packet)
    
    # Record the total time for the file transmission.
    upload_time = curr_time - upload_start

    # Record the experiment data if and only if the data is significant.
    if (filesize >= BYTES_PER_KB):
        upload_experiments[len(upload_experiments)] = transmission_data

    # Close the file descriptor used for the file transmission.
    fd_tmp.close()

    # If the file exists, remove it from the server's folder.
    if (filename in os.listdir(FOLDER_NAME)):
        os.remove(fileloc)

    # Rename the file transmitted to the requested filename.
    os.rename(fileloc_tmp, fileloc)

    # Report the successful upload to the server terminal and the client.
    print(filename + ' successfully uploaded to server!')
    packet = f"{len(SERVER_SUCCESS):<{HEADER_LENGTH}}" + SERVER_SUCCESS
    client_fd.send(bytes(packet, 'utf-8'))

    # Create/update documentation for the incoming file's number of downloads (now 0).
    num_Dwnlds[filename] = 0

    # Set the historical transmission speed.
    if (upload_time > 0):
        upload_speed = filesize / upload_time
    else:
        upload_speed = TOO_FAST 
    
    # Report the size of the file uploaded and the average transmission speed of the upload
    # to the server terminal.
    print(f"File size: {Data_String(filesize, 'filesize')}")
    print(f"Upload speed: {Data_String(upload_speed, 'speed')}")

def Download(filename):
    # Confirm that relevant global vars are modifiable.
    global num_Dwnlds

    # Identify the location of the file requested.
    fileloc = f'{FOLDER_NAME}\{filename}'

    # Report download request to the server terminal.
    print(f'Request to download {filename}...')
    
    # If the file requested does not exist on the server, report accordingly to the terminal and client.
    # The download process is terminated.
    if not (filename in os.listdir(FOLDER_NAME)):
        print(f'{filename} does not exist on the server.')    
        packet = f'{SERVER_FAILURE:<{HEADER_LENGTH}}' + f'{FILE_DNE}'
        packet = f'{len(packet):<{HEADER_LENGTH}}' + packet
        client_fd.send(bytes(packet, 'utf-8'))
        print('Download request terminated.')
        
    # If the file requested has no data to transmit, report accordingly to the terminal and client.
    # The download process is terminated.
    elif (os.path.getsize(fileloc) <= 0):
        print(f'{filename} has no data to transmit.')
        packet = f'{SERVER_FAILURE:<{HEADER_LENGTH}}' + f'{FILE_NO_DATA}'
        packet = f'{len(packet):<{HEADER_LENGTH}}' + packet
        client_fd.send(bytes(packet, 'utf-8'))
        print('Download request terminated.')        
    
    # Main Download Process
    else:      
        # Report initialized process to the server terminal.
        print('Initiating download...')

        # Download the file requested to the client's local directory.
        (download_time, filesize) = Download_File(filename, fileloc)

        # Report process success to the server terminal.
        print(f'{filename} was successfully downloaded!')
        
        # Increment the number of downloads for the requested file by 1.
        num_Dwnlds[filename] = num_Dwnlds[filename] + 1

        # Use the transmission time to determine the historical transmission rate.
        if (download_time > 0):
            download_speed = filesize / download_time
        else:
            download_speed = 'FAST' 

        # Report the size of the file downloaded and the average download speed to the server terminal.
        print(f"File size: {Data_String(filesize, 'filesize')}")
        print(f"Download speed: {Data_String(download_speed, 'speed')}")

def Delete(filename):
    # Confirm that relevant global vars are modifiable.
    global num_Dwnlds

    # Report deletion request to the server terminal.
    print(f'Request to delete {filename} from the server...')

    # Assume that the file does not exist - so the server will 
    # transmit a request failure.
    response = SERVER_FAILURE

    # Identify the file location of the requested file, if it exists.
    fileloc = f"{FOLDER_NAME}\{filename}"

    # If the file exists, remove it from the server's folder and internal 
    # download documentation. Prepare to transmit a request success.
    if (filename in os.listdir(FOLDER_NAME)):
        os.remove(fileloc)    
        num_Dwnlds.pop(filename)
        response = SERVER_SUCCESS
        
    # Report the result of the request to the server timal.
    if (response == SERVER_SUCCESS):
        print(f"{filename} successfully deleted from the server!")
    else:
        print(f"File {filename} does not exist on the server.")
    
    # Transmit the result of the request to the client.
    packet = f"{len(response):<{HEADER_LENGTH}}" + response
    client_fd.send(bytes(packet, 'utf-8'))

def Dir():
    # Report directory request to the server terminal.
    print('Server directory requested...')

    # Open and overwrite a temporary file for directory documentation.
    fd = open(TEMP_FILE, 'w')
    
    # Write a directory to the temporary file.
    fd.write('/------------------------------------------------------------------------------------\\\n')
    fd.write('| Directory Contents                                                                 |\n')
    fd.write('|------------------------------------------------------------------------------------|\n')
    fd.write('| FILENAME                       |  FILESIZE  |     UPLOAD DATE/TIME     | DOWNLOADS |\n')
    fd.write('|--------------------------------|------------|--------------------------|-----------|\n')
    for file in num_Dwnlds:
        fileloc = f'{FOLDER_NAME}\{file}'
        file_info = os.stat(fileloc)
        print_line = f"| {file:<30} | "
        print_line += f"{Data_String(file_info.st_size, REPORT_FILESIZE):>10} | "
        print_line += f"{time.ctime(file_info.st_mtime):>24} | "
        print_line += f"{num_Dwnlds[file]:>9} |" + '\n'
        fd.write(print_line)
    fd.write('\\------------------------------------------------------------------------------------/')

    fd.close()

    # Transmit the temporary file to the client.
    Download_File(TEMP_FILE, TEMP_FILE)

    # Report success to the server terminal.
    print('Directory delivered to the client.')

    # Clear the contents of the server's temporary file.
    open(TEMP_FILE, 'w').close()

def Process(packet):
    # Process the recieved packet as a request with arguments.
    packet_cmd = ((packet[:HEADER_LENGTH]).decode('utf-8')).strip()

    # Requests can come in one of four different forms:
    # 1. UPLOAD filename - Attempt upload of a local file to the folder.
    if (packet_cmd == CMD_UPLOAD):
        Upload(packet[HEADER_LENGTH:].decode('utf-8'))
        return
    
    # 2. DOWNLOAD filename - Attempt download of a file on the server folder to the 
    # local folder.
    elif (packet_cmd == CMD_DOWNLOAD):
        Download(packet[HEADER_LENGTH:].decode('utf-8'))

    # 3. DELETE filename - Attempt deletion of a file on the server folder.
    elif (packet_cmd == CMD_DELETE):
        Delete(packet[HEADER_LENGTH:].decode('utf-8'))

    # 4. DIR - Transmit a directory of the server folder with info relevant to the client.
    elif (packet_cmd == CMD_DIR):
        Dir()

    # Error Case Protection:
    # Client Transmission Corrupted - Requested Command Does Not Exist
    # Ignore request and continue.
    else:
        print('Illegal command recognized. No action taken.')

def main():
    # Confirm that relevant global vars are modifiable.
    global client_fd
    global server_socket

    # Run initial documentation on contents of the server folder.
    Folder_Documentation()

    # Set up a reusable socket for the server.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the permitted port and IP number.
    # (127.0.0.1, 1234)
    server_socket.bind((IP, PORT))

    # Listen for connection requests.
    server_socket.listen()

    while True:
        # Accept all valid connection requests.
        (client_fd, address) = server_socket.accept()

        # Report connection establishment to server terminal.
        print("Connection from", address, "has been established!", end='\n\n')

        # Transmit name of the server to the incoming client. (banana)
        First_Packet = f"{len(SERVER_NAME):<{HEADER_LENGTH}}" + SERVER_NAME
        client_fd.send(bytes(First_Packet, 'utf-8'))

        while not AUTHENTICATED:
            Login()

        # Initiate service loop for duration of the communication.
        while True:
            print()
            packet = Recieve_Packet()
            Process(packet)
main()