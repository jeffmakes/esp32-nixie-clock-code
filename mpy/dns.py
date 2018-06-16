import socket
import uasyncio
import gc
import uselect


# see https://www.ietf.org/rfc/rfc1035.txt, section 4.1
class DNSQuery:
    def __init__(self, data):
        self.domain = ''
        self.data = data
        opcode = (data[2] >> 3) & 15  # opcode bits in header
        if opcode == 0:
            label_start = 12
            length = data[label_start]
            while length:        # Question section: extract labels and combine to form requested domain
                self.domain += data[label_start+1:label_start+1+length].decode('utf-8')+'.'
                label_start = label_start+1+length
                length = data[label_start]
            self.qend = label_start+1+4

    def answer(self, ip):     # reply, providing ip as answer
        packet = None
        if self.domain:
            packet = self.data[:2] + b'\x81\x80' # QR=1, AA=1, RA=1
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'   # Questions and Answers Counts
            packet += self.data[12:self.qend]                                         # Original Domain Name Question
            packet += b'\xc0\x0c'                                             # Pointer to domain name
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, ip.split('.')))                          # 4bytes of IP
        return packet


class DNSServer:
    def __init__(self,  ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, 53))
        self.socket.settimeout(0)
        self.ip = ip
        self.poller = uselect.poll()
        self.poller.register(self.socket, uselect.POLLIN)

    async def run(self):
        while True:
            gc.collect()
            r = self.poller.poll(100)
            if r:
                data, addr = r[0][0].recvfrom(512)
                if len(data):
                    q = DNSQuery(data)
                    self.socket.sendto(q.answer(self.ip), addr)
                    print("Answer: {} -> {}".format(q.domain, self.ip))
            await uasyncio.sleep(0)

