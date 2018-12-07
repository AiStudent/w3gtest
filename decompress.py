
import zlib
import struct
import sys


name = sys.argv[1]
f = open(name, "rb")
data = f.read()
print(len(data))

class FirstHeader:
    def __init__(self, data):
        (
            self.fileoffset,
            self.compressed_size,
            self.replay_header_version,
            self.decompressed_size,
            self.nr_of_compressed_blocks
        ) = struct.unpack('<5i', data)

    
class SubHeader:
    def __init__(self, data):
        self.game_str = b''.join(struct.unpack('cccc', data[3::-1])).decode("utf-8")
        (
            self.version_number,
            self.build_number,
            self.flags,
            self.replay_length_ms,
            self.header_checksum
            ) = struct.unpack('ihhii', data[4:])

class Block:
    def __init__(self, data):
        (
            self.size_compressed,
            self.size_decompressed,
            self.unknown_checksum,
        ) = struct.unpack('hhi', data[0:8])

        #self.compressed_data = data[3:]

    def __str__(self):
        return "" + str(self.size_compressed) + "\n" + str(self.size_decompressed) + "\n"

first_header = FirstHeader(data[0x1c:0x30])
sub_header = SubHeader(data[0x30:0x44])

block_i = 0x44
n = 0
while True:
    n+=1
    b1 = Block(data[block_i : block_i+8])
    data_i = block_i + 8
    d1 = data[data_i : data_i+b1.size_compressed]
    block_i = data_i + b1.size_compressed

    z = zlib.decompressobj()
    du1 = z.decompress(d1)

    f = open(name[0:-3] + "txt", "ab")
    f.write(du1)
    f.close()

    print(n, "blocks parsed..")
    print(block_i, '/', len(data))
    
    if block_i >= len(data):
        print("reached end of data. Saved to ", str(name[0:-3]) + "txt")
        break

