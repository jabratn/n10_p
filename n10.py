from serial import Serial
from typing import Callable

class N10:
    PKG_HEADER_0 = 0xA5
    PKG_HEADER_1 = 0x5A
    MIN_PAYLOAD = 108
    POINT_PER_PACK = 16

    def __init__(self, port, baud=460800):
        self.serial = Serial(port, baud)
        self._shutdown = False
    
    def get_raw(self):
        while self.serial.in_waiting < N10.MIN_PAYLOAD:
            pass
        return self.serial.read(self.serial.in_waiting)
    
    def scan(self, update: Callable):
        data = []
        while not self._shutdown:
            for i in self.get_raw():
                data.append(i)

            if len(data) < N10.MIN_PAYLOAD:
                continue

            if len(data) > N10.MIN_PAYLOAD * 100:
                data = []

            start = 0
            while start + N10.MIN_PAYLOAD <= len(data):
                if data[start] == N10.PKG_HEADER_0 and data[start+1] == N10.PKG_HEADER_1:
                    break
                start += 1

            if start + N10.MIN_PAYLOAD > len(data):
                data = data[start:]
                continue

            _data = data[start:start + N10.MIN_PAYLOAD]
            data = data[start + N10.MIN_PAYLOAD:]

            if _data[0] != N10.PKG_HEADER_0 or _data[1] != N10.PKG_HEADER_1:
                print("assertion failed")
                break

            start_angle = (_data[5] * 256 + _data[6]) / 100.0
            end_angle = (_data[105] * 256 + _data[106]) / 100.0

            if end_angle > 360:
                end_angle -= 360

            final_data = []

            if (start_angle > end_angle):
                diff = end_angle + 360 - start_angle
            else:
                diff = end_angle - start_angle

            diff /= N10.POINT_PER_PACK

            # print(start_angle, end_angle, diff)

            for i in range(N10.POINT_PER_PACK):
                s = _data[i * 6 + 7]
                z = _data[i * 6 + 8]
                y = _data[i * 6 + 9]
                final_data.append((round(start_angle + i * diff) % 360, (s * 256 + z), y))

            update(final_data)

    def stop(self):
        self.serial.write(
            b'\xa5\x5a\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x01\x00\xfa\xfb')
        
    def start(self):
        self.serial.write(
            b'\xa5\x5a\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x01\x01\xfa\xfb')

    def shutdown(self):
        self._shutdown = True

if __name__ == '__main__':
    n10 = N10('/dev/ttyUSB0')
    n10.scan(lambda x:[print(i[0], i[1], i[2]) for i in x])
