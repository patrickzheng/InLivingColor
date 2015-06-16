import sys
import time


if __name__ == '__main__':
    # Unbuffered reading of the stream
    k = 0

    try:
        buff = ''

        while True:
            buff += sys.stdin.read(1)
            if buff.endswith('\n'):

                print buff[:-1]
                buff = ''
                k = k + 1

    except KeyboardInterrupt:
       sys.stdout.flush()
       pass
    print k
