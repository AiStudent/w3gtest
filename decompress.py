
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


def decompress(data, status_queue = None):
    try:
        first_header = FirstHeader(data[0x1c:0x30])

        decompressed_data = bytearray(first_header.decompressed_size)
        block_i = 0x44
        n = 0

        decom_i = 0 # decompressed data index

        while block_i < len(data):
            #print(n, ':', block_i,'/', len(data))
            if status_queue:
                status_queue.put((block_i, len(data)))

            n+=1
            (
                size_compressed,
                size_decompressed,
                unknown_checksum,
            ) = struct.unpack('hhi', data[block_i:block_i+8])

            z = zlib.decompressobj()

            data_block = data[block_i+8 : block_i+8+size_compressed]
            data_block = z.decompress(data_block)

            decompressed_data[decom_i: decom_i+len(data_block)] = data_block
            decom_i += len(data_block)

            block_i += 8 + size_compressed

        if status_queue:
            status_queue.put((block_i, len(data)))
        return decompressed_data
    except:
        raise CouldNotDecompress


# Arguments used for threading
def decompress_replay(data, status_queue = None, returnvalue_queue = None):
    decompressed_data = data[:0x44] + decompress(data, status_queue)
    if returnvalue_queue:
        returnvalue_queue.put(decompressed_data)
    return decompressed_data


if __name__ == '__main__':
    name = sys.argv[1]
    f = open(name, "rb")
    data = f.read()
    f.close()
    import time
    import queue
    import threading

    first_header = FirstHeader(data[0x1c:0x30])
    sub_header = SubHeader(data[0x30:0x44])

    q1 = queue.Queue()
    qrv = queue.Queue()

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
    print(first_header.compressed_size)
    print(first_header.decompressed_size)


    t1 = time.time()

    print(t1-t0)

    f = open(name[0:-3] + "txt", "wb")
    f.write(data)
    f.close()

   
