import time
import struct
import usb.core
import usb.backend.libusb1
from datetime import datetime

def convert2BytesToDecimal(byte1, byte2):
    return int((byte1 << 8) + byte2)

def convertByteToDatetime(byteString):
    if len(byteString) != 7:
        raise ValueError('Date must be a 7 byte string.')
    try:
        y = convert2BytesToDecimal(byteString[0],byteString[1])
        m = int(byteString[2])
        d = int(byteString[3])
        hh = int(byteString[4])
        mm = int(byteString[5])
        ss = int(byteString[6])
        return datetime(y,m,d,hh,mm,ss)
    except:
        return datetime.now()


if __name__ == "__main__":
    VENDOR_ID = 0x0770
    PRODUCT_ID = 0x0100

    device = usb.core.find(idVendor=VENDOR_ID,idProduct=PRODUCT_ID)
    if device is None:
        raise ValueError('ADU Device not found. Please ensure it is connected to the tablet.')
        sys.exit(1)
    print("Device obtained!")
    device.reset()

    """These 2 lines are necessary to set up the communication."""
    byte = b"\x17\x01\x0c\x00\x00\x00\x1a\x01\x19\x00\x1d\x0f\x01\x00\x00\x00\x07\x00\x00\x00\x00\x00\x83\xb9\x92\x38"
    device.write(0x02, byte)
    reply = device.read(0x83, 128, 3000)

    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x3b\x01\x19\x00\x1d\x01\x03\x00\x00\x00\x28\x00\x00\x00\x00" \
    b"\x21\x00\x1d\x00\x00\x00\x1b\x00\x65\x00\x00\x12\x7b\x57\x32\x3e" \
    b"\xd6\x1a\x4e\x3d\x8e\xbc\xc8\x65\x80\x07\xbb\xcb\x00\x01\x00\x00" \
    b"\x56\x0c\x26\xcf\x21\x39"
    device.write(0x02,byte)
    reply = device.read(0x83, 128, 3000)


    """Obtain NIBP Data"""
    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x05\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\xee\xff\x50\x53"
    device.write(0x02,byte)
    reply = device.read(0x83, 128, 3000)
    print(reply)
    print(len(reply))
    if len(reply) == 63:
        print("NIBP Reading:")
        print("Systolic(Hg) : " + str(convert2BytesToDecimal(reply[43],reply[44])))
        print("Diastolic(Hg) : " + str(convert2BytesToDecimal(reply[45],reply[46])))
        print("MAP(Hg) : " + str(convert2BytesToDecimal(reply[47],reply[48])))
        print("HR(bpm) : " + str(convert2BytesToDecimal(reply[49],reply[50])))
        print("STime : " + convertByteToDatetime(reply[33:40]).strftime("%m/%d/%Y, %H:%M:%S"))
    time.sleep(0.3)

    """Obtain SpO2 Data"""
    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x04\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\x6b\xaa\xd9\xe5"
    device.write(0x02, byte)
    reply = device.read(0x83,128,3000)
    print(reply)
    print(len(reply))
    if len(reply) == 59:
        print("SpO2 Reading:")
        print("Saturation(%) : " + str(convert2BytesToDecimal(reply[43],reply[44])))
        print("Heart Rate(bpm) : " + str(convert2BytesToDecimal(reply[45],reply[46])))
        print("STime : " + convertByteToDatetime(reply[33:40]).strftime("%m/%d/%Y, %H:%M:%S"))

    """Obtain Temperature Data"""
    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x03\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\xe9\x32\x0e\xdf"
    device.write(0x02, byte)
    reply = device.read(0x83,128,3000)
    print(reply)
    print(len(reply))
    if len(reply) == 59:
        print("Temperature Reading:")
        temperature = struct.unpack('>f', reply[49:53])[0] - 273.15
        print("Temperature(C) : " + str(temperature))

    """Device Data"""
    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x18\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\x71\xe8\x1a\x1f"
    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    print(reply)
    print(len(reply))
    if len(reply) == 147:
        serial_number_byte = reply[77:89]
        serial_number = bytes(serial_number_byte).decode("utf-8")
        print("Device Data")
        print("Serial Number : " + serial_number)

    """Get current session data (necessary for capturing manually input HR)"""
    byte = b"\x17\x01\x0c\x00\x00" \
    b"\x00\x2f\x01\x1a\x00\x17\x0b\x00\x00\x00\x00\x1c\x00\x00\x00\x00" \
    b"\x15\x00\x17\x10\x00\x00\x0f\x00\x64\x40\x00\x08\x00\x00\x00\x03" \
    b"\x00\x00\x00\x00\xcb\x75\xb9\xcc\x1e\xeb"
    device.write(0x02, byte)
    reply = device.read(0x83,1024,3000)
    print(reply)
    print(len(reply))
    if len(reply) == 720:
        print(reply[707])
        print("Session HR : " + str(convert2BytesToDecimal(reply[706],reply[707])))

    """Get Height Data"""
    byte = b"\x1b\x00\xa0\xa8\xfb\x4f\x82\x91\xff\xff\x70\x61\x8d\x51\x09\x00" \
    b"\x00\x01\x00\x0b\x00\x02\x03\x1a\x00\x00\x00\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x1a\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\x73\x53\xdf\x23"
    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    if len(reply) == 59:
        height = convert2BytesToDecimal(reply[45],reply[46]) / 10
        print(height)
        print("Height: " + str(height) + " cm")

    """Get Weight Data"""
    byte = b"\x1b\x00\x60\xf4\x1d\x4e\x82\x91\xff\xff\x00\x00\x00\x00\x09\x00" \
    b"\x00\x01\x00\x0b\x00\x02\x03\x1a\x00\x00\x00\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x13\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\xfc\xea\x69\xe4"

    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    if len(reply) == 60:
        weight = convert2BytesToDecimal(reply[45],reply[46]) / 1000
        print("Weight: " + str(weight) + " kg")

    """Get General Info"""
    byte = b"\x1b\x00\x90\xe0\x62\x4e\x82\x91\xff\xff\x00\x00\x00\x00\x09\x00" \
    b"\x00\x01\x00\x0f\x00\x02\x03\x2b\x00\x00\x00\x17\x01\x0c\x00\x00" \
    b"\x00\x2b\x01\x1a\x00\x6b\x0b\x00\x00\x00\x00\x18\x00\x00\x00\x00" \
    b"\x11\x00\x6b\x10\x00\x00\x0b\x00\x64\x00\x00\x04\x00\x00\x00\x01" \
    b"\xf7\x29\x53\x4b\x7b\xd6"
    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    print(reply)
    ptr = 35
    try:
        location_id_len = convert2BytesToDecimal(reply[33],reply[34])
        location_id_byte = reply[ptr:ptr+location_id_len]
        location_id = bytes(location_id_byte).decode("utf-8")
        print(location_id)

        ptr = ptr + location_id_len
        asset_id_len = convert2BytesToDecimal(reply[ptr],reply[ptr+1])
        ptr = ptr + 2
        asset_id_byte = reply[ptr:ptr+asset_id_len]
        print(asset_id_byte)
        asset_id = bytes(asset_id_byte).decode("utf-8")
        print(asset_id)

    except Exception as E:
        print(E)

    """Get Respiration Rate"""
    byte = b"\x1b\x00\x20\xd3\xa8\x50\x82\x91\xff\xff\x00\x00\x00\x00\x09\x00" \
    b"\x00\x01\x00\x16\x00\x02\x03\x1a\x00\x00\x00\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x12\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\x79\xbf\xe0\x52"
    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    print(reply)
    try:
        respirationRate = reply[49]
        print("Respiration Rate: " + str(respirationRate))
    except Exception as E:
        print(E)

    """Get BMI"""
    byte = b"\x1b\x00\xa0\x79\x1d\x4b\x82\x91\xff\xff\x00\xd0\xc5\x37\x09\x00" \
    b"\x00\x01\x00\x1a\x00\x02\x03\x1a\x00\x00\x00\x17\x01\x0c\x00\x00" \
    b"\x00\x1a\x01\x1a\x00\x11\x0b\x00\x00\x00\x00\x07\x00\x00\x00\x00" \
    b"\x00\xfe\x51\xac\xd8"
    device.write(0x02, byte)
    reply = device.read(0x83,256,3000)
    print(reply)
    if len(reply) == 67:
        height = convert2BytesToDecimal(reply[49],reply[50]) / 10
        print("Height: " + str(height))

        weight = convert2BytesToDecimal(reply[51],reply[52])
        print(weight)

        BMI = convert2BytesToDecimal(reply[53],reply[54])
        print("BMI Index is: " + str(BMI))

    #53-54
