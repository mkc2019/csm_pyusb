import time
import usb.core
import usb.backend.libusb1
from datetime import datetime

def convert2BytesToDecimal(byte1, byte2):
    return int((byte1 << 8) + byte2)

def convertByteToDatetime(byteString):
    if len(byteString) != 7:
        raise ValueError('Date must be a 7 byte string.')
    y = convert2BytesToDecimal(byteString[0],byteString[1])
    m = int(byteString[2])
    d = int(byteString[3])
    hh = int(byteString[4])
    mm = int(byteString[5])
    ss = int(byteString[6])
    return datetime(y,m,d,hh,mm,ss)

if __name__ == "__main__":
    VENDOR_ID = 0x0770
    PRODUCT_ID = 0x0100

    device = usb.core.find(idVendor=VENDOR_ID,idProduct=PRODUCT_ID)
    if device is None:
        raise ValueError('ADU Device not found. Please ensure it is connected to the tablet.')
        sys.exit(1)
    print("Device obtained!")
    device.reset()

    device.clear_halt(0x83)
    device.clear_halt(0x02)


    byte = b"\x17\x01\x0c\x00\x00\x00\x1a\x01\x19\x00\x1d\x0f\x01\x00\x00\x00\x07\x00\x00\x00\x00\x00\x83\xb9\x92\x38"
    print(byte)
    device.write(0x02, byte)
    reply = device.read(0x83, 128, 3000)
    print(reply)
    print(len(reply))

    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x3b\x01\x19\x00\x1d\x01\x03\x00\x00\x00\x28\x00\x00\x00\x00" \
    b"\x21\x00\x1d\x00\x00\x00\x1b\x00\x65\x00\x00\x12\x7b\x57\x32\x3e" \
    b"\xd6\x1a\x4e\x3d\x8e\xbc\xc8\x65\x80\x07\xbb\xcb\x00\x01\x00\x00" \
    b"\x56\x0c\x26\xcf\x21\x39"
    device.write(0x02,byte)
    reply = device.read(0x83, 128, 3000)
    print(reply)
    print(len(reply))

    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x05\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\xee\xff\x50\x53"
    device.write(0x02,byte)
    reply = device.read(0x83, 128, 3000)
    print(reply)
    print(len(reply))
    if len(reply) == 63:
        print("NIBP Reading:")
        print("Systolic (Hg) : " + str(convert2BytesToDecimal(reply[43],reply[44])))
        print("Diastolic (Hg) : " + str(convert2BytesToDecimal(reply[45],reply[46])))
        print("MAP (Hg) : " + str(convert2BytesToDecimal(reply[47],reply[48])))
        print("HR (bpm) : " + str(convert2BytesToDecimal(reply[49],reply[50])))
        print("STime : " + convertByteToDatetime(reply[33:40]).strftime("%m/%d/%Y, %H:%M:%S"))
    time.sleep(0.3)
