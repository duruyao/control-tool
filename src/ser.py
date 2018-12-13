import sys, os, signal
import getopt, socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 8080
size = 4096 * 10
msize = 0
fsize = 0
lisnum = 1  # how many ears to listen to client
cmdinput = False  # if input command lines
up = False
down = False
filename = ''


def usage():
    """
    ------------------------------------------------------------------------------------------------------
    ## Syntax

    python ser.py [-h <host>] [-p <port>] [-l <lisnum>] [-s <size>] [-c] [{-u <updest> | -d <downdest>}]
    ------------------------------------------------------------------------------------------------------
    ## Parameters

    Parameters:     Descriptions:
    -h --host       IPV4 for binding, default is [ 127.0.0.1 ]
    -p --port       Port for binding, default is [ 8080 ]
    -l --lisnum     Number of listening, default is  [ 1 ]
    -s --size       Size of data for one TCP connection, default is  [ 4096 * 10 ]
    -c --cmdinput   If input command lines, default is [ False ]
    -u --updest     The destiantion of file to upload
    -d --downdest   The destination of file to download
    ------------------------------------------------------------------------------------------------------
    ## Examples

    > python ser.py -t 122.233.78.211 -p 8090 -l 5 -c

    > python ser.py -t 127.0.0.1 -u E:/imgs/1024.png

    > python ser.py -p 8070 -d /home/user/imgs/512.jpg
    ------------------------------------------------------------------------------------------------------
    """


def quit(signum, frame):
    print '[*] Caught Ctrl C, Interrupt Program'
    sys.exit()


def check_filename():
    global filename
    filepath = os.path.abspath(os.path.dirname(filename))
    if down and not up:
        if os.path.isfile(filename):
            while os.path.isfile(filename):
                newfile = ''
                onetime = False
                for sign in filename[::-1]:
                    if sign == '.' and not onetime:
                        sign = '.wen-'
                        onetime = True
                    newfile = newfile + sign
                filename = newfile[::-1]
            print '[*] Exist the file of same name, and change new filename as [ %s ]' % (filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    elif up and not down:
        if not os.path.isfile(filename):
            print '[*] NO Such File!'
            exit()


def handle_client(client_socket, reinfo):
    client_socket.send(reinfo)
    client_socket.close()


def send_command():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(lisnum)
    print '[*] Set %d Listening on [ %s:%d ]' % (lisnum, host, port)

    while True:
        client, addr = server.accept()
        print '\n' + '-' * 102
        print '[*] Accepted connection from [ %s:%d ]' % (addr[0], addr[1])
        request = client.recv(size)
        print request
        print '[*] Input command lines, and type "Ctrl + Z" as end of input: '
        command = sys.stdin.read()
        try:
            handle_client(client, command)
        except:
            print '[*] Failed to send command to [ %s:%d ]' % (addr[0], addr[1])


def upload_file():
    global filename
    global fsize
    global msize
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(lisnum)
    print '[*] Set %d Listening on [ %s:%d ]' % (lisnum, host, port)
    # be connected by client
    client, addr = server.accept()
    print '\n' + '-' * 102
    print '[*] Accepted connection from [ %s:%d ]' % (addr[0], addr[1])
    # send the maxsize of file that will be uploaded
    msize = os.path.getsize(filename)
    while True:
        try:
            client.send(str(msize))
            break
        except:
            pass
    print '[*] Plan to upload %ld bytes file named [ %s ] to it' % (msize, filename)
    # start to upload
    with open(filename, 'rb') as f:
        for data in f:
            client.send(data)
            # fsize = sys.getsizeof(data) + fsize
            # if fsize >= msize:  fsize = msize
            # str = '[' + '>' * int(80 * fsize / msize) + ' ' * int(80 - (80 * fsize / msize)) + ']'
            # sys.stdout.write('\r' + str + ('[%3s%%]' % (100 * fsize / msize)))
            # sys.stdout.flush()
    print '\n[*] Success to upload file'


def download_file():
    global filename
    global msize
    global fsize
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(lisnum)
    print '[*] Set %d Listening on [ %s:%d ]' % (lisnum, host, port)
    # be connected by client
    client, addr = server.accept()
    print '\n' + '-' * 102
    print '[*] Accepted connection from [ %s:%d ]' % (addr[0], addr[1])
    # get the maxsize of file that will be downloaded
    msize = long(client.recv(size))
    print '[*] Plan to download %ld bytes file as [ %s ] from it' % (msize, filename)
    while True:
        data = client.recv(size)
        if not data:
            break
        else:
            with open(filename, 'ab') as f:
                f.write(data)
                f.close()
            fsize = os.path.getsize(filename)
            str = '[' + '>' * int(80 * fsize / msize) + ' ' * int(80 - (80 * fsize / msize)) + ']'
            sys.stdout.write('\r' + str + ('[%3s%%]' % (100 * fsize / msize)))
            sys.stdout.flush()
    print '\n[*] Success to download file as [ %s ]' % (filename)


def main():
    # the Keyword 'global' will be used when modifying values of Global Variables in function
    global host
    global port
    global size
    global lisnum
    global cmdinput
    global up
    global down
    global filename

    opts, args = ['', '']
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:p:s:l:cu:d:',
                                   ['host', 'port', 'size', 'lisnum', 'cmdinput', 'updest', 'downdest'])
    except getopt.GetoptError as e:
        print e
        exit()

    for o, a in opts:
        if o in ('-h', '--host'):
            host = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-s', '--size'):
            size = int(a)
        elif o in ('-l', '--lisnum'):
            lisnum = int(a)
        elif o in ('-c', '--cmdinput'):
            cmdinput = True
        elif o in ('-u', '--updest'):
            up = True
            filename = a
        elif o in ('-d', '--downdest'):
            down = True
            filename = a
        else:
            assert False, 'Unhandled Option'

    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    if cmdinput and not up and not down:
        cmdthread = threading.Thread(target=send_command(), args=())
        cmdthread.setDaemon(True)
        cmdthread.start()
        # cmdthread.join()
    elif up and len(filename) and not down and not cmdinput:
        check_filename()
        upload_file()
    elif down and len(filename) and not up and not cmdinput:
        check_filename()
        download_file()
    else:
        print usage.__doc__
        exit()


if __name__ == '__main__':
    main()
