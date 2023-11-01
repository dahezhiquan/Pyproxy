# encoding: utf-8

import socket
import sys
import threading

# In all printable character positions, keep the original characters unchanged; in all non-printable character
# positions, put a period
# To Enhance visualization
HEX_FILTER = ''.join(
    chr(i) if 32 <= i < 127 else '.'
    for i in range(256)
)


def hexdump(src, length=16, show=True):
    """
    Receive input of bytes or string type, convert it into hexadecimal format and output it to the screen
    Provide real-time observation of data flow within the agent
    :param src:Input data to convert, which can be of type byte or string
    :param length:Number of bytes displayed per line, default is 16
    :param show:Whether to output the results to the screen, the default is True
    :return:Hexadecimal format
    """

    # Check whether the input src is of byte type
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        # Convert the extracted characters into printable character format
        printable = word.translate(HEX_FILTER)
        # Convert to hexadecimal
        hexa = ''.join([f'{ord(c):02X} ' for c in word])
        hexwidth = length * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results


def receive_from(connection):
    """
    Receive data from both ends of the broker
    :param connection:socket
    :return:Data received on the given connection
    """
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except socket.timeout:
        pass
    except socket.error:
        pass
    return buffer


def request_handler(buffer):
    """
    Modify the reply packet or request packet before the proxy forwards the packet
    :param buffer:data pack
    :return:bad hacker data pack
    """
    return buffer


def response_handler(buffer):
    """
    Modify the reply packet or request packet before the proxy forwards the packet
    :param buffer:data pack
    :return:bad hacker data pack
    """
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """
    Continuously read data from the client and remote host and forward it to the other party
    :param client_socket:Socket to communicate with remote host
    :param remote_host:remote host address
    :param remote_port:remote host port
    :param receive_first:Used to control whether the proxy server first receives data from the remote host after establishing a connection.
    :return:No
    """
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    remote_buffer = bytes()
    # For example, the FTP server will first send you a welcome message
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    # Modify the reply packet or request packet before the proxy forwards the packet
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)

    # Enter an infinite loop that handles data forwarding between the local client and the remote host
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.Bye Bye Hacker")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """
    Implement proxy function
    :param local_host:The name or IP address of the local host
    :param local_port:Port number on localhost
    :param remote_host:The name or IP address of the remote host
    :param remote_port:Port number on the remote host
    :param receive_first:Whether to receive the response from the remote host before forwarding the client request
    :return:No
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on shit bind: %r' % e)
        print("[!!] Failed to listen on %s:%d,Fuck!" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    # Most 5 client
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # Give the new connection to the proxy_handler function, which will send and receive data to both ends of the
        # data flow.
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] ", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit()

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()
