import os
import sys
import socket
from functools import partial

#MAX_PACKET   = 1024
MAX_PAYLOAD   = 1014
HEADER_LENGTH = 10

TEMP_FILE   = 'local.tmp'
FOLDER_NAME = 'Local_Folder'
SERVER_RPT  = 'Server_Report.txt'

IP = "127.0.0.1"
PORT = 1234
CONNECTED = False
AUTHENTICATED = False

INVALID_LOGIN = 1

FILE_DNE     = 0
FILE_NO_DATA = 1

CMD_CONNECT   = 'CONNECT'
CMD_LOGIN     = 'LOGIN'
CMD_UPLOAD    = 'UPLOAD'
CMD_OVERWRITE = 'OVERWRITE'
CMD_DOWNLOAD  = 'DOWNLOAD'
CMD_DELETE    = 'DELETE'
CMD_DIR       = 'DIR'
CMD_HELP      = 'HELP'
CMD_QUIT      = 'QUIT'
VALID_CMDS = [CMD_CONNECT, CMD_LOGIN, CMD_UPLOAD, CMD_DOWNLOAD, CMD_DELETE, CMD_DIR]

NUM_ARGS_CONNECT  = 3
NUM_ARGS_LOGIN    = 3
NUM_ARGS_UPLOAD   = 2
NUM_ARGS_DOWNLOAD = 2
NUM_ARGS_DELETE   = 2
NUM_ARGS_DIR      = 1

SERVER_SUCCESS = 'SUCCESS'
SERVER_FAILURE = 'FAILURE'
REQUEST_FOR_INFO = 'REQUEST'

LOGGED_IN_USER = ''
SERVER_NAME = ''
server_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
def Connect(Tokens):
    # Confirm that relevant global vars are modifiable.
    global CONNECTED
    global SERVER_NAME
    global server_fd

    # User Input Errors
    if (CONNECTED):
        print('Only one connection supported per session.', end='\n\n')
    elif (len(Tokens) != NUM_ARGS_CONNECT):
        print('Three arguments required to CONNECT. Enter HELP if necessary.', end='\n\n') 
    elif (Tokens[1] != IP):
        print('Illegal IP address. Try to CONNECT again.', end='\n\n')
    elif (int(Tokens[2]) != PORT):
        print('Illegal port number. Try to CONNECT again.', end='\n\n')
    
    # Main Connection Process
    else:
        server_fd.connect((IP,PORT))
        # Recieve Header Name
        SERVER_NAME = Recieve_Packet().decode('utf-8')
        # Report Connection Success
        print(f'Connected to the {SERVER_NAME} server! Please log in to continue.', end='\n\n')
        CONNECTED = True
        
def Recieve_Packet():
    # Recieve the first packet:
    # A header indicating the length of the next packet.
    packet_header = server_fd.recv(HEADER_LENGTH)

    # Error Case Protection
    # (No data recieved from the server. Connection is closed, end program.)
    if not len(packet_header):
        print("Connection closed by the server. Hard Quit.")
        Quit()
    
    # Determine length of the next packet.
    packet_length = int(packet_header.decode('utf-8').strip())
    
    # Recieve and return the desired packet, in bytes.
    packet = server_fd.recv(packet_length)
    return packet

def Download_File(filesize, fileloc_tmp=TEMP_FILE):
    # Initalize variable for total number of bytes downloaded.
    num_bytes_read = 0

    # Clear out the contents of the temporary file, create file if DNE
    open(fileloc_tmp,'w+').close()

    # Open the temporary file to write binary data.
    fd_tmp = open(fileloc_tmp, 'ab')

    # File Download - Main Transmission Loop
    while (num_bytes_read != filesize):
        # Recieve and write a packet of 1024 bytes or less to the temporary file.
        packet = Recieve_Packet()
        fd_tmp.write(packet)
        num_bytes_read += len(packet)
        # Loop until the number of bytes downloaded equals the indicated filesize.
    
    # Close the temporary file upon complete transmission.
    fd_tmp.close()

    # Report successful transmission to the server.
    packet = f"{len(SERVER_SUCCESS):<{HEADER_LENGTH}}" + SERVER_SUCCESS
    server_fd.send(bytes(packet, 'utf-8'))

def Login(Tokens):
    # Confirm that relevant global vars are modifiable.
    global AUTHENTICATED
    global LOGGED_IN_USER

    # User Input Errors
    if (AUTHENTICATED):
        print('Only one user may be logged in during a session.', end='\n\n')
    elif (len(Tokens) != NUM_ARGS_LOGIN):
        print('Three arguments required to LOGIN. Enter HELP if necessary.', end='\n\n')
    elif ((len(Tokens[1]) > HEADER_LENGTH) or (len(Tokens[2]) > HEADER_LENGTH)):
        print('Both the username and password must be 10 characters or less. Please try again.', end='\n\n')
    
    # Main Login Process
    else:
        print('Processing login request...')
        
        # Parse login info from the user input.
        # (username, password)
        requested_username = Tokens[1]
        requested_password = Tokens[2]
        print('---------------------\\')
        print(f'Username: {requested_username:<{HEADER_LENGTH}} |')
        print(f'Password: {requested_password:<{HEADER_LENGTH}} |')
        print('---------------------/')

        # Create and send a packet requesting a login to the server with the specific info.
        packet = f"{CMD_LOGIN:<{HEADER_LENGTH}}"
        packet += f"{requested_username:<{HEADER_LENGTH}}"
        packet += f"{requested_password:<{HEADER_LENGTH}}"
        packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
        server_fd.send(bytes(packet, 'utf-8'))

        # Await and process the server's response.
        server_response = Recieve_Packet().decode('utf-8')

        # Case 1 - Server Responds with Failure
        if (server_response[:HEADER_LENGTH].strip() == SERVER_FAILURE):
            # Case 1A - Invalid Login Info
            if (int(server_response[HEADER_LENGTH:]) == INVALID_LOGIN):
                print('Username/password combination not found. Please try again...', end='\n\n')
            # Case 1B - Server-Side Error
            else:
                print('A serious error has occurred server-side. Closing the program...', end='\n\n')
                Quit()
        # Case 2 - Server-Side Error
        elif (server_response[:HEADER_LENGTH].strip() != SERVER_SUCCESS):
            print('A serious error has occurred server-side. Closing the program...', end='\n\n')
            Quit()
        # Case 3 - Login Succesful
        # Report accordingly to the client terminal and document that the client is
        # logged into the account requested.
        else:
            AUTHENTICATED = True
            LOGGED_IN_USER = requested_username
            print(f'Login successful! Welcome to the server, {LOGGED_IN_USER}!', end='\n\n')

def Upload(Tokens):
    # User Input Errors
    if (len(Tokens) != NUM_ARGS_UPLOAD):
        print('Two arguments required to UPLOAD. Enter HELP if necessary.', end='\n\n')
    elif not (Tokens[1] in os.listdir(FOLDER_NAME)):
        print(f"File {Tokens[1]} does not exist on the local directory.")
        print('Terminating upload request.', end='\n\n')
    
    # Main Upload Process
    else: 
        # Declare variables for file name, size and location on the local directory.
        filename = Tokens[1]
        fileloc = f'{FOLDER_NAME}\{filename}'
        filesize = os.path.getsize(fileloc)

        # If the requsted file has no data, terminate upload process.
        if (filesize <= 0):
            print(f'File {filename} found on the local directory, but has no data.')
            print('Terminating upload request.', end='\n\n')
            return

        # Indicate successful request format to the client terminal.
        print('Initiating upload request...')

        # Send packet requesting upload of file with given filename.
        packet = f"{CMD_UPLOAD:<{HEADER_LENGTH}}" + filename
        packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
        server_fd.send(bytes(packet, 'utf-8'))
        
        # Determine server response.
        packet = ''
        server_response = Recieve_Packet().decode('utf-8')

        # File with the same name already exists on the server.
        if (server_response == REQUEST_FOR_INFO):
            
            # Report the overwrite condition to the client terminal.
            print(f'A file with the name {filename} already exists on the server.')
            
            # Determine if overwrite is desired by user.
            overwrite = input('Overwrite this file? (Y/N) > ').strip()[0]
            
            # Overwrite is not confirmed by user. Suspend upload process.
            if (overwrite.upper() != 'Y'):
                if (overwrite.upper() != 'N'):
                    print('Unexpected input.',end=' ')
                print('Ceasing upload process.', end='\n\n')

                # Inform server of upload suspension.
                packet = f"{SERVER_FAILURE:<{HEADER_LENGTH}}"
                packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
                server_fd.send(bytes(packet, 'utf-8'))

                return
            
            # Overwrite is confirmed is confirmed by user.
            else:      
                print('Continuing upload process...')
                # Prepare a package header indicating overwrite request.
                packet = f"{CMD_OVERWRITE:<{HEADER_LENGTH}}"

        # Error Case Protection 
        # (Server should either allow upload or ask for overwrite.)
        elif (server_response != SERVER_SUCCESS):
            print('A critical error has occurred server-side.', end='\n\n')
            Quit()
        
        # Indicate upload initialization to the the client terminal.
        print(f'Initiating upload of {filename}...')

        # Inform the server of the size of the incoming file.
        packet += f"{filesize}"
        packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
        server_fd.send(bytes(packet, 'utf-8'))

        # Read and transmit file-data to the server in chunks.
        fd = open(fileloc, "rb")
        for data_chunk in iter(partial(fd.read, MAX_PAYLOAD), b''):
            packet = data_chunk
            packet_header = bytes(f"{len(packet):<{HEADER_LENGTH}}", 'utf-8')
            packet = packet_header + packet
            server_fd.send(packet)
        fd.close()

        # Determine and report if upload was successful.
        packet = Recieve_Packet().decode('utf-8')
        if (packet == SERVER_SUCCESS):
            print(filename + ' was successfully uploaded to the server!', end='\n\n')
        else:
            print('A critical error has occurred server-side.', end='\n\n')
            Quit()

def Download(Tokens):
    # User Input Errors
    if (len(Tokens) != NUM_ARGS_DOWNLOAD):
        print('Two arguments required to DOWNLOAD. Enter HELP if necessary.', end='\n\n')
    
    # Main Download Process
    else:
        # Create variables for the name, size and future location of the requested file.
        filename = Tokens[1]
        fileloc = f'{FOLDER_NAME}\{filename}'
        filesize = 0
        
        # An overwrite is required if a file of the same name already exists.
        if (filename in os.listdir(FOLDER_NAME)):
            print(f'A file with the name {filename} already exists on the local directory.')

            # Determine if overwrite is desired by user.
            overwrite = input('Overwrite this file? (Y/N) > ').strip()[0]
            
            # Overwrite is not confirmed by user. Terminate download request.
            if (overwrite.upper() != 'Y'):
                if (overwrite.upper() != 'N'):
                    print('Unexpected input.',end=' ')
                print('Download request terminated.', end='\n\n')
                return

        # Initialize download request.
        # Transmit name of requested file to the server.
        print('Initializing download request...')
        packet = f"{CMD_DOWNLOAD:<{HEADER_LENGTH}}" + filename
        packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
        server_fd.send(bytes(packet, 'utf-8'))

        # Recieve and process server response.
        server_response = Recieve_Packet().decode('utf-8')
        
        # If file requested cannot be downloaded, use packet to determine and display reason.
        # Then, terminate the download request.
        if (server_response[:HEADER_LENGTH].strip() == SERVER_FAILURE):
            failure_reason = int(server_response[HEADER_LENGTH:])
            
            # Reason 1A - Requested file does not exist.
            if (failure_reason == FILE_DNE):
                print(f'A file with the name {filename} does not exist on the server.')
            
            # Reason 1B - Requested file has no data.
            elif (failure_reason == FILE_NO_DATA):
                print(f'A file with the name {filename} exists on the server, but has no data.')
            
            # Error Case Protection
            # (Unexpected server response. End the program.)
            else:
                print('A critical error has occurred server-side', end='\n\n')
                Quit()

            # Report request termination to the client terminal.
            print('Download request terminated.', end='\n\n')
        
        # Error Case Protection
        # (Unexpected server response. End the program.)
        elif (server_response[:HEADER_LENGTH].strip() != SERVER_SUCCESS):
            print('A critical error has occurred server-side.', end='\n\n')
            Quit()
        
        # Succesful Download Request:
        else:
            # Report succcessful request and download initialization to the client terminal.
            print(f'A file with the name {filename} was found on the server.')
            print('Initiating download...')

            # Identify size of incoming file from suffix of server response.
            filesize = int(server_response[HEADER_LENGTH:])
            
            # Identify Location Temporary File
            i = 0
            fileloc_tmp = f'{FOLDER_NAME}\{i}.tmp'
            while (fileloc_tmp in os.listdir(FOLDER_NAME)):
                i += 1
                fileloc_tmp = f'{FOLDER_NAME}\{i}.tmp'

            # Download File to Temporary File Location
            Download_File(filesize, fileloc_tmp)

            # If a file of the same name exists on the local directory,
            # remove to permit overwrite.
            if (filename in os.listdir(FOLDER_NAME)):
                os.remove(fileloc)

            # Rename Temporary File to Requested Filename
            os.rename(fileloc_tmp, fileloc)

            # Report download success to the terminal.
            print(f'{filename} was successfully downloaded from the server!', end='\n\n')

def Delete(Tokens):
    # User Input Errors
    if (len(Tokens) != NUM_ARGS_DELETE):
        print('Two arguments required to DELETE. Enter HELP if necessary.', end='\n\n')

    # Main Deletion Process
    else:
        # Declare variable for the name of the file requested for deletion.
        filename = Tokens[1]

        # Send packet requesting deletion of file with given filename.
        packet = f"{CMD_DELETE:<{HEADER_LENGTH}}" + filename
        packet = f"{len(packet):<{HEADER_LENGTH}}" + packet
        server_fd.send(bytes(packet, 'utf-8'))
        
        # Determine server response.
        server_response = Recieve_Packet().decode('utf-8')
        
        # Report successful deletion of file.
        if (server_response == SERVER_SUCCESS):
            print(f"{filename} successfully deleted from the server!", end='\n\n')
        
        # Report unsuccessful deletion - (File does not exist on the server.)
        elif (server_response == SERVER_FAILURE):
            print(f"File {filename} does not exist on the server.", end='\n\n')
        
        # Error Case Protection
        # (Unexpected server response. End program.) 
        else:
            print("A serious server error has occurred.", end='\n\n')
            Quit()

def Dir(Tokens):
    # User Input Errors
    if (len(Tokens) != NUM_ARGS_DIR):
        print('One argument required for DIR. Enter HELP if necessary.', end='\n\n')
    
    # Main Directory Process
    else:
        
        print('Requesting server directory...')
        
        packet = f'{len(CMD_DIR):<{HEADER_LENGTH}}' + CMD_DIR
        server_fd.send(bytes(packet, 'utf-8'))

        server_response = Recieve_Packet().decode('utf-8')

        if (server_response[:HEADER_LENGTH].strip() != SERVER_SUCCESS):
            print('A serious server error has occurred.', end='\n\n')
            Quit()

        dirsize = int(server_response[HEADER_LENGTH:])

        Download_File(dirsize)

        print('Directory recieved!')   

        fd_tmp = open(TEMP_FILE, 'r')
        
        for dir_line in fd_tmp:
            print(dir_line, end='')
        print(end='\n\n')
        
        fd_tmp.close()

        open(TEMP_FILE, 'w').close()

def Help():
    # Give the user a helpful guide on command formats.
    print('/-------------------------------------------------\\')
    print('| Valid Commands:                                 |')
    print('|-------------------------------------------------|')
    print('| example > CONNECT server_IP_address server_port |')
    print('| example > LOGIN username password               |')
    print('| example > UPLOAD filename                       |')
    print('| example > DOWNLOAD filename                     |')
    print('| example > DELETE filename                       |')
    print('| example > DIR                                   |')
    print('| example > HELP                                  |')
    print('| example > QUIT                                  |')
    print('\\-------------------------------------------------/\n')

def Quit():
    # Terminate the client using a system exit.
    Footer()
    sys.exit()

def Header():
    # Program Banner
    print('/-------------------------------------------------\\')
    print('| Welcome to the Bluegrass Remote Folder Service! |')
    print('\\-------------------------------------------------/\n')
    # Initial command to the user.
    print('Please connect to your service provider.')

def Footer():
    # Program Footer
    print('/----------------------------------------------------------\\')
    print('| Thank You for Using the Bluegrass Remote Folder Service! |')
    print('\\----------------------------------------------------------/')

def Process(user_in):
    # Determine and execute user command.
    Command = user_in.split()[0].upper()

    # Connect to the server. (First permitted command.)
    if Command == CMD_CONNECT:
        Connect(user_in.split())

    # Log into a specific account in the server. (Second permitted command.)
    elif Command == CMD_LOGIN:
        Login(user_in.split())
    
    # If the user is not logged in, no other valid command can be used.
    # Return False, so that the invalid command counter can increment by 1.
    elif not AUTHENTICATED:
        print('Please LOGIN first. Enter HELP if necessary.', end='\n\n')
        return False

    # Upload a file on the local directory to server.
    elif Command == CMD_UPLOAD:
        Upload(user_in.split())
    
    # Download a file from the server to the local directory.
    elif Command == CMD_DOWNLOAD:
        Download(user_in.split())
    
    # Delete a file on the server.
    elif Command == CMD_DELETE:
        Delete(user_in.split())
    
    # Display information about the contents of the server.
    elif Command == CMD_DIR:
        Dir(user_in.split())
    
    # Error Case Protection
    # (Unexpected command and entry to the Process. End program.)
    else:
        print('A serious error has occurred. Hard Quit.')
        Quit()
    
    # Return True, so that the invalid command counter can be set to 0.
    return True

def Input():
    # Initialize variables for user input, help "safe-guard"
    user_in = ''
    num_invalid_in = 0  # Number of consecutive input errors, loops from 0 to 3.

    while True:

        # Grab user input - allow for CTL+C input to end the program.
        try:
            user_in = input(f'{SERVER_NAME} > ')
        except KeyboardInterrupt:
            print()
            break

        # Continue if the user inputs nothing.
        if not user_in:
            continue

        # Quit normally if the user requests.
        elif (user_in.split()[0].upper() == CMD_QUIT):
            break

        # Display valid command options if the user requests help.
        elif (user_in.split()[0].upper() == CMD_HELP):
            Help()
            # Set the help "safe-guard" back to 0.
            num_invalid_in = 0
        
        # Display error message if the user inputs an invalid command.
        elif (user_in.split()[0].upper() not in VALID_CMDS):
            print('Invalid command. Enter HELP if necessary.', end='\n\n')
            num_invalid_in += 1

        # Display error message if the user inputs a valid command, but has NOT 
        # connected to the server.
        elif ((not CONNECTED) and (user_in.split()[0].upper() != CMD_CONNECT)):
            print('Please CONNECT first. Enter HELP if necessary.', end='\n\n')
            num_invalid_in += 1
        
        # Great, we have a valid command! Pass input to the program Process.
        else:
            if Process(user_in):
                num_invalid_in = 0
            else:
                num_invalid_in += 1
        
        # The Help Safeguard!
        # Force user to review valid command formats after 3 erroneous attempts.
        if num_invalid_in == 3:
            Help()
            num_invalid_in = 0

def main():
    Header()
    Input()
    Footer()
main()