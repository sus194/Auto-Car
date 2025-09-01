class EncoderReader:
    """Stub for quadrature encoder interface. Replace with pigpio/interrupts on Pi."""
    def __init__(self, pins):
        self.pins = pins

    def read_rps(self):
        # TODO: implement using pigpio callbacks for A/B channels
        return [0.0, 0.0, 0.0, 0.0]
