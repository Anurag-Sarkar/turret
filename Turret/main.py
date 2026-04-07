# ble_simple_peripheral.py

import bluetooth
from micropython import const
import struct

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

_UART_SERVICE = (
    _UART_UUID,
    (
        (_UART_TX, bluetooth.FLAG_NOTIFY,),
        (_UART_RX, bluetooth.FLAG_WRITE,),
    ),
)

class BLESimplePeripheral:
    def __init__(self, ble, name="ESP32-RGB"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        ((self._tx_handle, self._rx_handle,),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None

        self._payload = self._advertising_payload(name=name)
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)

            time.sleep_ms(200)   # 👈 FIX (important)
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle:
                if self._write_callback:
                    self._write_callback(self._ble.gatts_read(self._rx_handle))

    def send(self, data):
        for conn in self._connections:
            self._ble.gatts_notify(conn, self._tx_handle, data)

    def is_connected(self):
        return len(self._connections) > 0

    def on_write(self, callback):
        self._write_callback = callback

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _advertising_payload(self, name=None):
        payload = bytearray()

        def _append(adv_type, value):
            payload.extend(struct.pack("BB", len(value) + 1, adv_type) + value)

        _append(0x01, b'\x06')  # flags

        if name:
            _append(0x09, name.encode())

        return payload



The Contractor agrees to design and deliver a complete robotics product design (“Product”) as per the specifications, requirements, and standards communicated by the Company from time to time.
The scope shall include, but not be limited to:
• Product design (3D Modeling, CAD drawings, etc.)
• Functional implementation
• Complete documentation (if required by the Company)
All deliverables must strictly comply with the quality standards and expectations of the Company.