from machine import Pin, I2C, SPI, PWM, ADC, UART
import framebuf
import time

I2C_SDA = 6
I2C_SDL = 7

DC = 8
CS = 9
SCK = 10
MOSI = 11
RST = 12
BL = 25
V_bat_Pin = 29


class Lcd1inch28(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240

        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)

        self.cs(1)
        self.spi = SPI(1, 100_000_000, polarity=0, phase=0, sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        self.red = 0x07E0
        self.green = 0x001f
        self.blue = 0xf800
        self.white = 0xffff

        self.fill(self.white)
        self.show()

        self.pwm = PWM(Pin(BL))
        self.pwm.freq(5000)
        self.font = {
            ' ': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '!': [0x0, 0x0, 0x0, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300,
                  0x0, 0x0, 0x300, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '"': [0x0, 0x0, 0xcc0, 0xcc0, 0xcc0, 0xcc0, 0xcc0, 0xcc0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '#': [0x0, 0x0, 0x0, 0x210, 0x230, 0x630, 0x630, 0x620, 0x3ffc, 0x3ffc, 0xc60, 0xc60, 0xc40, 0x7ff8, 0x7ff8,
                  0x18c0, 0x18c0, 0x18c0, 0x18c0, 0x1080, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '$': [0x180, 0x180, 0x380, 0xfe0, 0x1c70, 0x1830, 0x1838, 0x1838, 0x1800, 0x1e00, 0xf80, 0x3e0, 0xf0, 0x38,
                  0x18, 0x3018, 0x3838, 0x1870, 0x1fe0, 0x7c0, 0x180, 0x180, 0x0, 0x0, 0x0, 0x0],
            '%': [0x0, 0x0, 0x0, 0x3c00, 0x7c00, 0x4620, 0x4660, 0x4640, 0x7cc0, 0x3c80, 0x180, 0x300, 0x270, 0x6f8,
                  0x4cc, 0xc8c, 0x188c, 0x8c, 0xf8, 0x70, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '&': [0x0, 0x0, 0x0, 0x780, 0x1fc0, 0x18e0, 0x1860, 0x18c0, 0x1980, 0xf00, 0xf00, 0xf00, 0x3b0c, 0x3198,
                  0x71d8, 0x60f8, 0x7070, 0x3070, 0x3ff8, 0xf9c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '\'': [0x0, 0x0, 0x300, 0x300, 0x300, 0x300, 0x200, 0x200, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                   0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '(': [0x0, 0x40, 0xc0, 0x180, 0x300, 0x300, 0x600, 0x600, 0x600, 0x600, 0xc00, 0xc00, 0xc00, 0xc00, 0xc00,
                  0xc00, 0xe00, 0x600, 0x600, 0x600, 0x300, 0x300, 0x180, 0xc0, 0x40, 0x40],
            ')': [0x0, 0x800, 0xc00, 0x600, 0x300, 0x300, 0x180, 0x180, 0x180, 0x1c0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0,
                  0xc0, 0xc0, 0x180, 0x180, 0x180, 0x300, 0x300, 0x600, 0x600, 0xc00, 0x800],
            '*': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x380, 0x180, 0x100, 0x2108, 0x3d38, 0x1ff8, 0x380, 0x680, 0x6c0, 0xc60,
                  0x1c70, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '+': [0x0, 0x0, 0x0, 0x0, 0x0, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x7ff8, 0x7ff8, 0x300, 0x300,
                  0x300, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            ',': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x700, 0x700,
                  0x700, 0x600, 0x600, 0xc00, 0x400, 0x0, 0x0],
            '-': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1ff0, 0x1ff0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '.': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x380, 0x380,
                  0x380, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '/': [0x0, 0x0, 0x0, 0x30, 0x60, 0x60, 0x60, 0xc0, 0xc0, 0xc0, 0x180, 0x180, 0x300, 0x300, 0x300, 0x600,
                  0x600, 0xc00, 0xc00, 0xc00, 0x1800, 0x0, 0x0, 0x0, 0x0, 0x0],
            '0': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1870, 0x3030, 0x3038, 0x3038, 0x3078, 0x31d8, 0x3398, 0x3618, 0x3c18,
                  0x3818, 0x3038, 0x3030, 0x1870, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '1': [0x0, 0x0, 0x0, 0x180, 0x780, 0x3f80, 0x3980, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180,
                  0x180, 0x180, 0x180, 0x180, 0x180, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '2': [0x0, 0x0, 0x0, 0xf80, 0x1fe0, 0x3060, 0x6070, 0x6030, 0x30, 0x60, 0xe0, 0xc0, 0x180, 0x300, 0x600,
                  0xe00, 0x1c00, 0x3800, 0x7ff8, 0x7ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '3': [0x0, 0x0, 0x0, 0xf80, 0x3fe0, 0x3060, 0x7070, 0x70, 0x70, 0x60, 0x7c0, 0x7c0, 0xe0, 0x70, 0x30,
                  0x6030, 0x7030, 0x3060, 0x3fe0, 0xf80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '4': [0x0, 0x0, 0x0, 0xe0, 0xe0, 0x1e0, 0x360, 0x360, 0x660, 0xc60, 0xc60, 0x1860, 0x3060, 0x3060, 0x7ff8,
                  0x7ff8, 0x60, 0x60, 0x60, 0x60, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '5': [0x0, 0x0, 0x0, 0x1ff0, 0x1ff0, 0x1800, 0x1800, 0x1800, 0x1800, 0x1fc0, 0x1ff0, 0x1830, 0x38, 0x18,
                  0x18, 0x3018, 0x3838, 0x1830, 0xff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '6': [0x0, 0x0, 0x0, 0x1c0, 0x7c0, 0xc00, 0x1800, 0x1800, 0x3380, 0x3fe0, 0x3870, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x3830, 0x1870, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '7': [0x0, 0x0, 0x0, 0x7ff8, 0x7ff8, 0x30, 0x30, 0x60, 0x60, 0xc0, 0xc0, 0x1c0, 0x180, 0x180, 0x300, 0x300,
                  0x600, 0x600, 0xc00, 0x1c00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '8': [0x0, 0x0, 0x0, 0x7c0, 0xfe0, 0x1830, 0x1830, 0x1830, 0x1830, 0x1c70, 0xfe0, 0xfe0, 0x1830, 0x3838,
                  0x3018, 0x3018, 0x3838, 0x1830, 0x1ff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '9': [0x0, 0x0, 0x0, 0x780, 0x1fe0, 0x3860, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3870, 0x1ff0, 0xfb0,
                  0x30, 0x30, 0x60, 0xe0, 0xfc0, 0xf00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            ':': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1c0, 0x1c0, 0x1c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1c0,
                  0x1c0, 0x1c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            ';': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x380, 0x380, 0x380, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1c0,
                  0x1c0, 0x1c0, 0x180, 0x180, 0x300, 0x0, 0x0, 0x0],
            '<': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x70, 0x3e0, 0xf00, 0x3c00, 0x3000, 0x1e00, 0x780, 0x1e0,
                  0x70, 0x10, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '=': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x3ff8, 0x3ff8, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '>': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2000, 0x3800, 0x1f00, 0x7c0, 0xf0, 0x30, 0x1e0, 0x780, 0x1e00,
                  0x3800, 0x2000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '?': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1830, 0x3030, 0x30, 0x30, 0x70, 0xe0, 0x1c0, 0x380, 0x300, 0x300, 0x0,
                  0x0, 0x300, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '@': [0x0, 0x0, 0x0, 0x7c0, 0xff0, 0x1830, 0x3198, 0x23c8, 0x6648, 0x644c, 0x4c4c, 0x4c4c, 0x4cc8, 0x4cc8,
                  0x4f78, 0x6770, 0x2000, 0x3000, 0x1fc0, 0xf80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'A': [0x0, 0x0, 0x0, 0x300, 0x380, 0x380, 0x780, 0x6c0, 0x6c0, 0xcc0, 0xc60, 0xc60, 0x1c60, 0x1870, 0x1ff0,
                  0x3ff0, 0x3038, 0x3018, 0x7018, 0x601c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'B': [0x0, 0x0, 0x0, 0x3fc0, 0x3fe0, 0x3030, 0x3038, 0x3038, 0x3038, 0x3070, 0x3fe0, 0x3fe0, 0x3030, 0x3018,
                  0x3018, 0x3018, 0x3018, 0x3030, 0x3ff0, 0x3fc0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'C': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1830, 0x3038, 0x3018, 0x7000, 0x6000, 0x6000, 0x6000, 0x6000, 0x6000,
                  0x7000, 0x3018, 0x3038, 0x1830, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'D': [0x0, 0x0, 0x0, 0x3f80, 0x3fe0, 0x3070, 0x3030, 0x3038, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018,
                  0x3018, 0x3038, 0x3030, 0x3070, 0x3fe0, 0x3f80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'E': [0x0, 0x0, 0x0, 0x3ff8, 0x3ff8, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3fe0, 0x3fe0, 0x3000, 0x3000,
                  0x3000, 0x3000, 0x3000, 0x3000, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'F': [0x0, 0x0, 0x0, 0x3ff8, 0x3ff8, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3ff0, 0x3ff0, 0x3000,
                  0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'G': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1830, 0x3038, 0x3018, 0x7000, 0x6000, 0x6000, 0x60f8, 0x60f8, 0x6018,
                  0x7018, 0x3018, 0x3018, 0x1838, 0xff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'H': [0x0, 0x0, 0x0, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3ff8, 0x3ff8, 0x3018, 0x3018,
                  0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'I': [0x0, 0x0, 0x0, 0x3ff0, 0x3ff0, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300,
                  0x300, 0x300, 0x300, 0x3ff0, 0x3ff0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'J': [0x0, 0x0, 0x0, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x6030, 0x7030,
                  0x3860, 0x1fe0, 0xf80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'K': [0x0, 0x0, 0x0, 0x3018, 0x3038, 0x3070, 0x30e0, 0x31c0, 0x3180, 0x3300, 0x3700, 0x3f00, 0x3f80, 0x39c0,
                  0x30c0, 0x30e0, 0x3070, 0x3030, 0x3038, 0x301c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'L': [0x0, 0x0, 0x0, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000,
                  0x3000, 0x3000, 0x3000, 0x3000, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'M': [0x0, 0x0, 0x0, 0x3838, 0x3838, 0x3878, 0x3c78, 0x3c58, 0x3cd8, 0x36d8, 0x3698, 0x3798, 0x3398, 0x3318,
                  0x3318, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'N': [0x0, 0x0, 0x0, 0x3018, 0x3818, 0x3818, 0x3c18, 0x3c18, 0x3e18, 0x3618, 0x3318, 0x3318, 0x3198, 0x3198,
                  0x30d8, 0x30d8, 0x3078, 0x3078, 0x3038, 0x3038, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'O': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1870, 0x3030, 0x3018, 0x7018, 0x6018, 0x6018, 0x6018, 0x6018, 0x6018,
                  0x7018, 0x3018, 0x3030, 0x1870, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'P': [0x0, 0x0, 0x0, 0x3fc0, 0x3ff0, 0x3038, 0x3018, 0x3018, 0x3018, 0x3018, 0x3038, 0x3ff0, 0x3fc0, 0x3000,
                  0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'Q': [0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1870, 0x3030, 0x3018, 0x6018, 0x6018, 0x6018, 0x6018, 0x6018, 0x6018,
                  0x6018, 0x3018, 0x3030, 0x1870, 0x1fe0, 0x7e0, 0x38, 0x1c, 0x0, 0x0, 0x0, 0x0],
            'R': [0x0, 0x0, 0x0, 0x3fc0, 0x3ff0, 0x3030, 0x3018, 0x3018, 0x3018, 0x3038, 0x3030, 0x3fe0, 0x3fc0, 0x30c0,
                  0x30e0, 0x3060, 0x3070, 0x3030, 0x3038, 0x3018, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'S': [0x0, 0x0, 0x0, 0x7c0, 0x1ff0, 0x3830, 0x3018, 0x3018, 0x3000, 0x3800, 0x1f00, 0x7c0, 0x1f0, 0x38,
                  0x18, 0x7018, 0x3018, 0x3838, 0x1ff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'T': [0x0, 0x0, 0x0, 0x7ffc, 0x7ffc, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300,
                  0x300, 0x300, 0x300, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'U': [0x0, 0x0, 0x0, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018, 0x3018,
                  0x3018, 0x3038, 0x3030, 0x1870, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'V': [0x0, 0x0, 0x0, 0x6018, 0x7018, 0x3038, 0x3030, 0x3030, 0x1830, 0x1860, 0x1860, 0xc60, 0xcc0, 0xcc0,
                  0xec0, 0x7c0, 0x780, 0x780, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'W': [0x0, 0x0, 0x0, 0x630c, 0x638c, 0x638c, 0x6398, 0x6398, 0x2698, 0x3698, 0x36d8, 0x36d8, 0x34d8, 0x34d8,
                  0x3c50, 0x3c70, 0x1c70, 0x1c70, 0x1870, 0x1870, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'X': [0x0, 0x0, 0x0, 0x701c, 0x3838, 0x1830, 0x1c70, 0xc60, 0xec0, 0x7c0, 0x380, 0x380, 0x380, 0x6c0, 0xec0,
                  0xc60, 0x1c70, 0x1830, 0x3038, 0x701c, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'Y': [0x0, 0x0, 0x0, 0x6018, 0x7038, 0x3030, 0x3870, 0x1860, 0x1ce0, 0xcc0, 0xec0, 0x780, 0x780, 0x300,
                  0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'Z': [0x0, 0x0, 0x0, 0x7ff0, 0x7ff0, 0x70, 0x60, 0xe0, 0xc0, 0x180, 0x380, 0x300, 0x600, 0xe00, 0xc00,
                  0x1c00, 0x1800, 0x3000, 0x7ff8, 0x7ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '[': [0x0, 0x7c0, 0x7c0, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600,
                  0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x7c0, 0x7c0, 0x0, 0x0],
            '\\': [0x0, 0x0, 0x0, 0x1800, 0x1800, 0xc00, 0xc00, 0xc00, 0x600, 0x600, 0x300, 0x300, 0x300, 0x180, 0x180,
                   0x80, 0xc0, 0xc0, 0x60, 0x60, 0x30, 0x0, 0x0, 0x0, 0x0, 0x0],
            ']': [0x0, 0x780, 0x780, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180,
                  0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x780, 0x780, 0x0, 0x0],
            '^': [0x0, 0x0, 0x0, 0x300, 0x300, 0x780, 0x780, 0x6c0, 0xcc0, 0xc60, 0x1860, 0x1830, 0x0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '_': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                  0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0],
            '`': [0x0, 0x0, 0x700, 0x380, 0x1c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'a': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x3870, 0x3030, 0x30, 0xff0, 0x1ff0, 0x3030, 0x3030,
                  0x3030, 0x3870, 0x1ff0, 0xfb8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'b': [0x0, 0x0, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x37c0, 0x3fe0, 0x3870, 0x3030, 0x3038, 0x3018,
                  0x3018, 0x3018, 0x3038, 0x3030, 0x3870, 0x3fe0, 0x37c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'c': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x1830, 0x3030, 0x3010, 0x3000, 0x3000, 0x3000,
                  0x3000, 0x3030, 0x1830, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'd': [0x0, 0x0, 0x30, 0x30, 0x30, 0x30, 0x30, 0x7b0, 0x1ff0, 0x1870, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x1870, 0x1ff0, 0x7b0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'e': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c0, 0xfe0, 0x1870, 0x3030, 0x3018, 0x3ff8, 0x3ff8, 0x3000,
                  0x3000, 0x1810, 0x1830, 0x1ff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'f': [0x0, 0xf0, 0x1f0, 0x380, 0x700, 0x600, 0x600, 0x3ff0, 0x3ff0, 0x600, 0x600, 0x600, 0x600, 0x600,
                  0x600, 0x600, 0x600, 0x600, 0x600, 0x600, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'g': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7b0, 0x1ff0, 0x1870, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x1870, 0x1ff0, 0x7b0, 0x30, 0x1030, 0x3870, 0x1fe0, 0x7c0, 0x0],
            'h': [0x0, 0x0, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x33c0, 0x37f0, 0x3830, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'i': [0x0, 0x0, 0x0, 0x180, 0x380, 0x180, 0x0, 0x3f80, 0x3f80, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180,
                  0x180, 0x180, 0x180, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'j': [0x0, 0x0, 0x0, 0x180, 0x380, 0x180, 0x0, 0x1fc0, 0x1fc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0,
                  0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0xc0, 0x180, 0x1f80, 0x3e00, 0x0],
            'k': [0x0, 0x0, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x3070, 0x30e0, 0x31c0, 0x3380, 0x3700, 0x3600,
                  0x3f00, 0x3b80, 0x31c0, 0x30c0, 0x3060, 0x3070, 0x3038, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'l': [0x0, 0x0, 0x3f80, 0x3f80, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180,
                  0x180, 0x180, 0x180, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'm': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6e70, 0x7ff8, 0x6318, 0x6318, 0x6318, 0x6318, 0x6318, 0x6318,
                  0x6318, 0x6318, 0x6318, 0x6318, 0x6318, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'n': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x33c0, 0x37e0, 0x3830, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'o': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c0, 0x1fe0, 0x3870, 0x3030, 0x3018, 0x7018, 0x7018, 0x7018,
                  0x3018, 0x3030, 0x3870, 0x1fe0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'p': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x37c0, 0x3fe0, 0x3870, 0x3030, 0x3038, 0x3018, 0x3018, 0x3018,
                  0x3038, 0x3030, 0x3870, 0x3fe0, 0x37c0, 0x3000, 0x3000, 0x3000, 0x3000, 0x3000, 0x0],
            'q': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7b0, 0x1ff0, 0x1870, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x1870, 0x1ff0, 0x7b0, 0x30, 0x30, 0x30, 0x30, 0x30, 0x0],
            'r': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0xcf8, 0xff0, 0xe00, 0xe00, 0xc00, 0xc00, 0xc00, 0xc00, 0xc00,
                  0xc00, 0xc00, 0xc00, 0xc00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            's': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7c0, 0x1ff0, 0x1830, 0x3838, 0x1800, 0x1e00, 0x7e0, 0xf0, 0x38,
                  0x3038, 0x3830, 0x1ff0, 0x7c0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            't': [0x0, 0x0, 0x0, 0x0, 0x600, 0x600, 0x600, 0x3ff0, 0x3ff0, 0x600, 0x600, 0x600, 0x600, 0x600, 0x600,
                  0x600, 0x600, 0x700, 0x3f0, 0x1f0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'u': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030, 0x3030,
                  0x3030, 0x3030, 0x1870, 0x1ff0, 0xfb0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'v': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7018, 0x3038, 0x3030, 0x1830, 0x1860, 0x1860, 0xc60, 0xcc0,
                  0x6c0, 0x680, 0x780, 0x380, 0x300, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'w': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x630c, 0x630c, 0x638c, 0x6398, 0x6798, 0x6698, 0x36d8, 0x3cd0,
                  0x3cd0, 0x1c70, 0x1c70, 0x1870, 0x1860, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'x': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x7038, 0x3830, 0x1c60, 0xce0, 0x7c0, 0x780, 0x380, 0x780, 0x6c0,
                  0xce0, 0x1c60, 0x3830, 0x7038, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'y': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6018, 0x7018, 0x3030, 0x3830, 0x1870, 0x1c60, 0xc60, 0xcc0,
                  0x6c0, 0x780, 0x780, 0x380, 0x300, 0x300, 0x600, 0xe00, 0x3c00, 0x3800, 0x0],
            'z': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x3ff0, 0x3ff0, 0x70, 0xe0, 0x1c0, 0x180, 0x300, 0x700, 0xe00,
                  0x1c00, 0x1800, 0x3ff8, 0x3ff8, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            '{': [0x0, 0x70, 0xf0, 0xc0, 0x180, 0x180, 0x180, 0x180, 0x180, 0x180, 0x380, 0xf00, 0xe00, 0x300, 0x180,
                  0x180, 0x180, 0x180, 0x180, 0x180, 0x1c0, 0xc0, 0xf0, 0x30, 0x0, 0x0],
            '|': [0x0, 0x0, 0x0, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300,
                  0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x0],
            '}': [0x0, 0xc00, 0xe00, 0x300, 0x300, 0x300, 0x300, 0x300, 0x300, 0x380, 0x180, 0xf0, 0xf0, 0x1c0, 0x180,
                  0x380, 0x300, 0x300, 0x300, 0x300, 0x300, 0x700, 0xe00, 0xc00, 0x0, 0x0],
            '~': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1c00, 0x7e0c, 0x630c, 0x41f8, 0xf0, 0x0, 0x0, 0x0,
                  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'invalid': [0x0, 0x7c00, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400,
                        0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x4400, 0x7c00, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
        }

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def set_bl_pwm(self, duty):
        self.pwm.duty_u16(duty)  # max 65535

    def init_display(self):
        """Initialize display"""
        self.rst(1)
        time.sleep(0.01)
        self.rst(0)
        time.sleep(0.01)
        self.rst(1)
        time.sleep(0.05)

        self.write_cmd(0xEF)
        self.write_cmd(0xEB)
        self.write_data(0x14)

        self.write_cmd(0xFE)
        self.write_cmd(0xEF)

        self.write_cmd(0xEB)
        self.write_data(0x14)

        self.write_cmd(0x84)
        self.write_data(0x40)

        self.write_cmd(0x85)
        self.write_data(0xFF)

        self.write_cmd(0x86)
        self.write_data(0xFF)

        self.write_cmd(0x87)
        self.write_data(0xFF)

        self.write_cmd(0x88)
        self.write_data(0x0A)

        self.write_cmd(0x89)
        self.write_data(0x21)

        self.write_cmd(0x8A)
        self.write_data(0x00)

        self.write_cmd(0x8B)
        self.write_data(0x80)

        self.write_cmd(0x8C)
        self.write_data(0x01)

        self.write_cmd(0x8D)
        self.write_data(0x01)

        self.write_cmd(0x8E)
        self.write_data(0xFF)

        self.write_cmd(0x8F)
        self.write_data(0xFF)

        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x20)

        self.write_cmd(0x36)
        self.write_data(0x98)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0x90)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x08)

        self.write_cmd(0xBD)
        self.write_data(0x06)

        self.write_cmd(0xBC)
        self.write_data(0x00)

        self.write_cmd(0xFF)
        self.write_data(0x60)
        self.write_data(0x01)
        self.write_data(0x04)

        self.write_cmd(0xC3)
        self.write_data(0x13)
        self.write_cmd(0xC4)
        self.write_data(0x13)

        self.write_cmd(0xC9)
        self.write_data(0x22)

        self.write_cmd(0xBE)
        self.write_data(0x11)

        self.write_cmd(0xE1)
        self.write_data(0x10)
        self.write_data(0x0E)

        self.write_cmd(0xDF)
        self.write_data(0x21)
        self.write_data(0x0c)
        self.write_data(0x02)

        self.write_cmd(0xF0)
        self.write_data(0x45)
        self.write_data(0x09)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x26)
        self.write_data(0x2A)

        self.write_cmd(0xF1)
        self.write_data(0x43)
        self.write_data(0x70)
        self.write_data(0x72)
        self.write_data(0x36)
        self.write_data(0x37)
        self.write_data(0x6F)

        self.write_cmd(0xF2)
        self.write_data(0x45)
        self.write_data(0x09)
        self.write_data(0x08)
        self.write_data(0x08)
        self.write_data(0x26)
        self.write_data(0x2A)

        self.write_cmd(0xF3)
        self.write_data(0x43)
        self.write_data(0x70)
        self.write_data(0x72)
        self.write_data(0x36)
        self.write_data(0x37)
        self.write_data(0x6F)

        self.write_cmd(0xED)
        self.write_data(0x1B)
        self.write_data(0x0B)

        self.write_cmd(0xAE)
        self.write_data(0x77)

        self.write_cmd(0xCD)
        self.write_data(0x63)

        self.write_cmd(0x70)
        self.write_data(0x07)
        self.write_data(0x07)
        self.write_data(0x04)
        self.write_data(0x0E)
        self.write_data(0x0F)
        self.write_data(0x09)
        self.write_data(0x07)
        self.write_data(0x08)
        self.write_data(0x03)

        self.write_cmd(0xE8)
        self.write_data(0x34)

        self.write_cmd(0x62)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x71)
        self.write_data(0xED)
        self.write_data(0x70)
        self.write_data(0x70)
        self.write_data(0x18)
        self.write_data(0x0F)
        self.write_data(0x71)
        self.write_data(0xEF)
        self.write_data(0x70)
        self.write_data(0x70)

        self.write_cmd(0x63)
        self.write_data(0x18)
        self.write_data(0x11)
        self.write_data(0x71)
        self.write_data(0xF1)
        self.write_data(0x70)
        self.write_data(0x70)
        self.write_data(0x18)
        self.write_data(0x13)
        self.write_data(0x71)
        self.write_data(0xF3)
        self.write_data(0x70)
        self.write_data(0x70)

        self.write_cmd(0x64)
        self.write_data(0x28)
        self.write_data(0x29)
        self.write_data(0xF1)
        self.write_data(0x01)
        self.write_data(0xF1)
        self.write_data(0x00)
        self.write_data(0x07)

        self.write_cmd(0x66)
        self.write_data(0x3C)
        self.write_data(0x00)
        self.write_data(0xCD)
        self.write_data(0x67)
        self.write_data(0x45)
        self.write_data(0x45)
        self.write_data(0x10)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)

        self.write_cmd(0x67)
        self.write_data(0x00)
        self.write_data(0x3C)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x54)
        self.write_data(0x10)
        self.write_data(0x32)
        self.write_data(0x98)

        self.write_cmd(0x74)
        self.write_data(0x10)
        self.write_data(0x85)
        self.write_data(0x80)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x4E)
        self.write_data(0x00)

        self.write_cmd(0x98)
        self.write_data(0x3e)
        self.write_data(0x07)

        self.write_cmd(0x35)
        self.write_cmd(0x21)

        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x29)
        time.sleep(0.02)

        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)

        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

    def draw_char(self, c, top, left, scale=1, color=0xffff):
        code_width = 16
        if c not in self.font:
            c = 'invalid'
        arr = self.font[c]
        for row in range(26):
            code = arr[row]
            for col in range(code_width, -1, -1):
                if code & (1 << col):
                    x, y = left + scale * (code_width - col), top + scale * row
                    for a in range(scale):
                        for b in range(scale):
                            self.pixel(x + a, y + b, color)

    def text_plus(self, s: str, x: int, y: int, c: int, scale=1):
        letter_width = 14 * scale
        for char in s:
            self.draw_char(char, y, x, scale, c)
            x += letter_width


class QMI8658(object):
    def __init__(self, address=0X6B):
        self._address = address
        self._bus = I2C(id=1, scl=Pin(I2C_SDL), sda=Pin(I2C_SDA), freq=100_000)
        b_ret = self.who_am_i()
        if b_ret:
            self.read_revision()
        else:
            return NULL
        self.config_apply()

    def _read_byte(self, cmd):
        rec = self._bus.readfrom_mem(int(self._address), int(cmd), 1)
        return rec[0]

    def _read_block(self, reg, length=1):
        rec = self._bus.readfrom_mem(int(self._address), int(reg), length)
        return rec

    def _read_u16(self, cmd):
        lsb = self._bus.readfrom_mem(int(self._address), int(cmd), 1)
        msb = self._bus.readfrom_mem(int(self._address), int(cmd) + 1, 1)
        return (msb[0] << 8) + lsb[0]

    def _write_byte(self, cmd, val):
        self._bus.writeto_mem(int(self._address), int(cmd), bytes([int(val)]))

    def who_am_i(self):
        b_ret = False
        if 0x05 == self._read_byte(0x00):
            b_ret = True
        return b_ret

    def read_revision(self):
        return self._read_byte(0x01)

    def config_apply(self):
        # REG CTRL1
        self._write_byte(0x02, 0x60)
        # REG CTRL2 : QMI8658AccRange_8g  and QMI8658AccOdr_1000Hz
        self._write_byte(0x03, 0x23)
        # REG CTRL3 : QMI8658GyrRange_512dps and QMI8658GyrOdr_1000Hz
        self._write_byte(0x04, 0x53)
        # REG CTRL4 : No
        self._write_byte(0x05, 0x00)
        # REG CTRL5 : Enable Gyroscope And Accelerometer Low-Pass Filter
        self._write_byte(0x06, 0x11)
        # REG CTRL6 : Disables Motion on Demand.
        self._write_byte(0x07, 0x00)
        # REG CTRL7 : Enable Gyroscope And Accelerometer
        self._write_byte(0x08, 0x03)

    def read_raw_xyz(self):
        xyz = [0, 0, 0, 0, 0, 0]
        # raw_timestamp = self._read_block(0x30, 3)
        # raw_acc_xyz = self._read_block(0x35, 6)
        # raw_gyro_xyz = self._read_block(0x3b, 6)
        raw_xyz = self._read_block(0x35, 12)
        # timestamp = (raw_timestamp[2] << 16) | (raw_timestamp[1] << 8) | (raw_timestamp[0])
        for i in range(6):
            # xyz[i]=(raw_acc_xyz[(i*2)+1]<<8)|(raw_acc_xyz[i*2])
            # xyz[i+3]=(raw_gyro_xyz[((i+3)*2)+1]<<8)|(raw_gyro_xyz[(i+3)*2])
            xyz[i] = (raw_xyz[(i * 2) + 1] << 8) | (raw_xyz[i * 2])
            if xyz[i] >= 32767:
                xyz[i] = xyz[i] - 65535
        return xyz

    def read_xyz(self):
        xyz = [0, 0, 0, 0, 0, 0]
        raw_xyz = self.read_raw_xyz()
        # QMI8658AccRange_8g
        acc_lsb_div = (1 << 12)
        # QMI8658GyrRange_512dps
        gyro_lsb_div = 64
        for i in range(3):
            xyz[i] = raw_xyz[i] / acc_lsb_div  # (acc_lsb_div/1000.0)
            xyz[i + 3] = raw_xyz[i + 3] * 1.0 / gyro_lsb_div
        return xyz


if __name__ == '__main__':

    LCD = Lcd1inch28()
    LCD.set_bl_pwm(65535)
    qmi8658 = QMI8658()
    V_bat = ADC(Pin(V_bat_Pin))
    uart1 = UART(1, baudrate=9600, tx=Pin(4))

    while True:
        # read QMI8658
        xyz = qmi8658.read_xyz()

        LCD.fill(LCD.white)

        LCD.fill_rect(0, 0, 240, 80, LCD.blue)
        LCD.text_plus("!!RDKS!!", 120 - (4 * 14 * 2), 30, LCD.red, 2)

        LCD.fill_rect(0, 80, 60, 40, 0x000F)
        LCD.fill_rect(60, 80, 60, 40, 0x00F0)
        LCD.fill_rect(120, 80, 60, 40, 0x0F00)
        LCD.fill_rect(180, 80, 60, 40, 0xF000)
        for i in range(0, 16):
            LCD.fill_rect(i*15, 120, 15, 40, 1 << i)

        LCD.fill_rect(0, 160, 120, 40, 0x0007)
        LCD.fill_rect(120, 160, 120, 40, 0xE007)

        LCD.set_bl_pwm(65535)

        # LCD.fill_rect(0, 80, 120, 120, 0x1805)
        # LCD.text("ACC_X={:+.2f}".format(xyz[0]), 20, 100 - 3, LCD.white)
        # LCD.text("ACC_Y={:+.2f}".format(xyz[1]), 20, 140 - 3, LCD.white)
        # LCD.text("ACC_Z={:+.2f}".format(xyz[2]), 20, 180 - 3, LCD.white)
        #
        # LCD.fill_rect(120, 80, 120, 120, 0xF073)
        # LCD.text("GYR_X={:+3.2f}".format(xyz[3]), 125, 100 - 3, LCD.white)
        # LCD.text("GYR_Y={:+3.2f}".format(xyz[4]), 125, 140 - 3, LCD.white)
        # LCD.text("GYR_Z={:+3.2f}".format(xyz[5]), 125, 180 - 3, LCD.white)
        #
        # LCD.fill_rect(0, 200, 240, 40, 0x180f)
        # reading = V_bat.read_u16() * 3.3 / 65535 * 2
        # LCD.text("V-bat={:.2f}".format(reading), 80, 215, LCD.white)

        LCD.show()
        time.sleep(0.1)
