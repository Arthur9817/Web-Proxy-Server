import os,sys,thread,socket

# Constant variables
MAX_CONN = 50            # how many pending connections queue will hold
BUFFER = 999999        # max number of bytes we receive at once

cache = {}
blocked = []

def main():

    print '\n------ Main Menu ------\nEnter "C" to start connection.\nEnter "B" to block URLs.\nEnter "E" to exit.'

    while True:
        input = raw_input('\nCommand: ')

        if(input == 'C' or input == 'c'):
            print '\n------ connection ------'
            connection()

        elif(input == 'B' or input == 'b'):
            print '\n------ URL Block ------\nEnter "1" to return to main menu.\nEnter "V" to view blocked URLs.\nEnter "U" to un-block URLs.\nEnter URL to block (www.example.com).'

            while True:
                block_url = raw_input('\nCommand: ')
                if(block_url == '1'):
                    break

                elif(block_url == 'V' or block_url == 'v'):
                    print '\n------ Blocked URLs ------'
                    for i in blocked:
                        print i

                elif(block_url == 'U' or block_url == 'u'):
                    while True:
                        unblock_url = raw_input('\nEnter URL to un-block: ')
                        if unblock_url in blocked:
                            blocked.remove(unblock_url)
                            print unblock_url, 'has been removed.'
                        else:
                            print 'This URL is not in the blocked list.'
                    break

                else:
                    blocked.append(block_url)
                    print block_url, 'is now blocked.'

        elif(input == 'E' or input == 'e'):
            print '\nExiting...'
            sys.exit()

        else:
            print '\nInvalid input'

def connection():

    host = 'localhost'

    try:
        port = raw_input('Enter port number: ')

        # Create a TCP/IP connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, int(port)))
        s.listen(MAX_CONN)

        print '\nProxy Server Running on',host,':',port
        print 'Enter Ctrl + C to shut down the server.\n'

    except ValueError:
        print "\nInvalid input.\n"
        connection()

    except socket.error, (value, message):
        if s:
            s.close()
            print "\nCould not open socket:", message,'\n'
            connection()

    # gets the connection from client
    while True:
        try:
            client_sock, client_addr = s.accept()

            thread.start_new_thread(proxy_thread, (client_sock, client_addr))

        # shuts down server on keyboard interrupt (Ctrl + C)
        except KeyboardInterrupt:
            s.close()
            print "\nProxy server shutting down...\n"
            sys.exit()

    s.close()


def proxy_thread(client_sock, client_addr):

    global webserver
    global port

    # gets the request from browser
    request = client_sock.recv(BUFFER)

    try:
        # parses the first line
        first_line = request.split('\n')[0]

        # gets url
        url = first_line.split(' ')[1]

        # find the webserver and port
        http_pos = url.find("://")          # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # get the rest of url

        port_pos = temp.find(":")           # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:
            # specific port
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        for i in range(0,len(blocked)):
            if blocked[i] in webserver:
                print webserver, " is blacklisted."
                client_sock.close()
                return

        while True:
            if cache[request]:
                client_sock.send(cache[request])
                client_sock.close()
                print 'sent from cache'
            else:
                break

            # except keyError:
            #     pass

    except Exception, e:
        pass

    except KeyboardInterrupt:
        s.close()
        print "\nProxy server shutting down...\n"
        sys.exit()

    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)         # send request to webserver

        while True:
            # receive data from web server
            data = s.recv(BUFFER)

            if (len(data) > 0):

                # add to cache
                cache[request] = data

                # send to browser
                client_sock.send(data)
                print 'Request processed from address: ', webserver, str(client_addr)
            else:
                break

        s.close()
        client_sock.close()

    except socket.error, (value, message):
        s.close()
        client_sock.close()
        sys.exit()

if __name__ == '__main__':
    main()
