
import zlib
import struct
import sys

class CouldNotDecompress(Exception):
    pass

class FirstHeader:
    def __init__(self, data):
        (
            self.fileoffset,
            self.compressed_size,
            self.replay_header_version,
            self.decompressed_size,
            self.nr_of_compressed_blocks
        ) = struct.unpack('<5i', data)

    def get_hm(self):
        return {'fileoffset': self.fileoffset,
                'compressed_size': self.compressed_size,
                'replay_header_version': self.replay_header_version,
                'decompressed_size': self.decompressed_size,
                'nr_of_compressed_blocks': self.nr_of_compressed_blocks}
    
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

    def get_hm(self):
        return {'game_str': self.game_str,
                'version_number': self.version_number,
                'build_number': self.build_number,
                'flags': self.flags,
                'replay_length_ms': self.replay_length_ms,
                'header_checksum': self.header_checksum
                }

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


# testing time
def decompress_block_function(data):
    (
        size_compressed,
        size_decompressed,
        unknown_checksum,
    ) = struct.unpack('hhi', data[0:8])

    z = zlib.decompressobj()
    data = z.decompress(data)
    return data


def decompress(data, status = None):
    try:
        first_header = FirstHeader(data[0x1c:0x30])
        sub_header = SubHeader(data[0x30:0x44])
        #print(sub_header.get_hm())
        decompressed_data = bytearray(first_header.decompressed_size)
        block_i = 0x44
        n = 0

        decom_i = 0 # decompressed data index

        if sub_header.version_number > 10031 or sub_header.version_number == 0:  # temp replay
            header_len = 12
            unpacking = 'iii'
        else:
            header_len = 8
            unpacking = 'hhi'
        #print(hex(block_i))
        #print('header_len', header_len)
        while block_i < len(data):
            #print(n, ':', block_i,'/', len(data))
            if status:
                status.progress = (block_i, len(data))

            n+=1

            (
                size_compressed,
                size_decompressed,
                unknown_checksum,
            ) = struct.unpack(unpacking, data[block_i:block_i+header_len])
            #print(hex(block_i), size_compressed, size_decompressed)
            z = zlib.decompressobj()

            data_block = data[block_i+header_len : block_i+header_len+size_compressed]
            data_block = z.decompress(data_block)

            decompressed_data[decom_i: decom_i+len(data_block)] = data_block
            decom_i += len(data_block)

            block_i += header_len + size_compressed

        if status:
            status.progress = (block_i, len(data))
        return decompressed_data
    except Exception as e:
        raise CouldNotDecompress


# Arguments used for threading
def decompress_replay(data, status = None):
    decompressed_data = data[:0x44] + decompress(data, status)
    return decompressed_data


if __name__ == '__main__':
    try:
        name = sys.argv[1]
    except IndexError:
        name = 'tr1.w3g'

    f = open(name, "rb")
    data = f.read()
    f.close()
    import time

    first_header = FirstHeader(data[0x1c:0x30])
    sub_header = SubHeader(data[0x30:0x44])

    #print(first_header.get_hm())
    #print(sub_header.get_hm())

    t0 = time.time()
    """
    thread1 = threading.Thread(target=decompress_replay, args=(data, q1, qrv))
    thread1.start()

    progress = 0
    while progress < 100:
        done, total = q1.get(True)
        progress = 100*done / total
        #print(done,'/', total)
  
    data = qrv.get_nowait()
    """
    data = decompress_replay(data)
    print('first header info:')
    print('compressed size', first_header.compressed_size)
    print('decompressed size', first_header.decompressed_size)


    t1 = time.time()

    print(t1-t0)

    f = open(name[0:-3] + "txt", "wb")
    f.write(data)
    f.close()

   
