
import zlib
import struct
import sys


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
        
    def decompress(self, data):
        self.data = data
        z = zlib.decompressobj()
        data = z.decompress(self.data)
        return data


def decompress_replay(data):
    first_header = FirstHeader(data[0x1c:0x30])
    sub_header = SubHeader(data[0x30:0x44])
    
    decompressed_data = b''
    block_i = 0x44
    n = 0

    while block_i < len(data):
        n+=1
        block = Block(data[block_i : block_i+8])
        decompressed_data += block.decompress(data[block_i+8 : block_i+8+block.size_compressed])
        block_i += 8 + block.size_compressed

    return decompressed_data

if __name__ == '__main__':
    name = sys.argv[1]
    f = open(name, "rb")
    data = f.read()
    f.close()
    
    data = data[:0x44] + decompress_replay(data)

    f = open(name[0:-3] + "txt", "wb")
    f.write(data)
    f.close()

   
