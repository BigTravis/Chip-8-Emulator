import pyglet
class VM (pyglet.window.Window):
    def __init__(self):
        self.reset()
        self.funcMap = { 0x000: self._0XXX,
                        0x00e0: self._0XX0,
                        0x00ee: self._0XXE,
                        0x1000: self._1XXX,
                        0x2000: self._2XXX,
                        0x3000: self._3XXX,
                        0x4000: self._4XXX,
                        0x5000: self._5XXX,
                        0x6000: self._6XXX,
                        0x7000: self._7XXX,
                        0x8000: self._8XXX,
                        0x8001: self._8XX1,
                        0x8002: self._8XX2,
                        0x8003: self._8XX3,
                        0x8004: self._8XX4,
                        0x8005: self._8XX5,
                        0x8006: self._8XX6,
                        0x8007: self._8XX7,
                        0x800E: self._8XXE,
                        0x9000: self._9XXX,
                        0xa000: self._AXXX,
                        0xb000: self._BXXX,
                        0xc000: self._CXXX,
                        0xd000: self._DXXX,
                        0xe000: self._EXXX,
                        0xe001: self._EXX1,
                        0xe00e: self._EXXE,
                        0xf000: self._FXXX,
                        0xf007: self._FXX7,
                        0xf00a: self._FXXA,
                        0xf015: self._FX15,
                        0xf018: self._FXX8,
                        0xf01e: self._FXXE,
                        0xf029: self._FX29,
                        0xf033: self._FX33,
                        0xf055: self._FX55,
                        0xf065: self._FX65
                        }

    def reset(self):
        self.clear()
        self.keyInputs = [0] * 16
        self.displayBuffer = [0] * 32 * 64
        self.memory = [0] * 0xfff
        self.registers = [0] * 16
        self.pc = 0x200
        self.indexRegister = 0
        self.stack = []
        self.soundTimer = 0
        self.delayTimer = 0
        self.shouldDraw = False

        for i in range(80):
            self.memory[i] = self.fonts[i]

    def loadProgram(self, path):
        log('Loading {}...'.format(path))
        fileIn = open(path, "rb").read()
        
        for i in range(len(fileIn)):
            self.memory[0x200 + i] = ord(fileIn[i])

    def cycle(self):
        self.opcode = self.memory[self.pc]
        # process opcode
        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4
        self.pc += 2

        op = self.opcode & 0xf000
        try:
            self.funcMap[op]()
        except:
            print("Error: unknown instruction ({})".format(self.opcode))

        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                return # play sound
                
                


    def _0XXX(self):
        op = self.opcode & 0xf0ff
        try:
            self.funcMap[op]()
        except:
            print("Error: unknown instruction ({})".format(self.opcode))

    
    def _0XX0(self):
        '''Clears the display'''
        self.displayBuffer = [0] * 64 * 32
        self.shouldDraw = True

    
    def _0XXE(self):
        '''Returns from subroutine'''
        self.pc = self.stack.pop()


    def _1XXX(self):
        '''Jump instruction'''
        self.pc = self.opcode & 0x0fff


    def _2XXX(self):
        '''Call subroutine'''
        self.stack.append(self.pc)
        self.pc = self.opcode & 0x0fff


    def _3XXX(self):
        '''Skip next instruction if equal'''
        if self.registers[self.vx] == (self.opcode & 0xff):
            self.pc += 2


    def _4XXX(self):
        '''Skip next instruction if not equal'''
        if self.registers[self.vx] != (self.opcode & 0xff):
            self.pc += 2


    def _5XXX(self):
        '''Compare'''
        if self.registers[self.vx] == self.registers[self.vy]:
            self.pc += 2


    def _6XXX(self):
        '''Set register'''
        self.registers[self.vx] = self.opcode & 0xff


    def _7XXX(self):
        '''Add constant to register'''
        self.registers[self.vx] += self.opcode & 0xff
        if self.registers[self.vx] > 0xff:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        
        self.registers[self.vx] &= 0xff


    def _8XXX(self):
        '''Checks if opcode is 0x8000, else calls correction function'''
        op = self.opcode & 0xf0ff
        if op != 0x8000:
            try:
                self.funcMap[op]()
            except:
                print("Error: unknown instruction ({})".format(self.opcode))

        else:
            self.registers[self.vx] = self.registers[self.vy]


    def _8XX1(self):
        '''Bitwise OR'''
        self.registers[self.vx] = self.registers[self.vx] | self.registers[self.vy]


    def _8XX2(self):
        '''Bitwise AND'''
        self.registers[self.vx] = self.registers[self.vx] & self.registers[self.vy]


    def _8XX3(self):
        '''Bitwise XOR'''
        self.registers[self.vx] = self.registers[self.vx] ^ self.registers[self.vy]


    def _8XX4(self):
        '''Add'''
        self.registers[self.vx] += self.registers[self.vy]
        if self.registers[self.vx] > 0xff:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        
        self.registers[self.vx] &= 0xff

    def _8XX5(self):
        '''Subtract'''
        if self.registers[self.vy] > self.registers[self.vx]:
            self.registers[0xf] = 0
        else:
            self.registers[0xf] = 1
        self.registers[self.vx] -= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8XX6(self):
        '''Shift right'''
        if (self.registers[self.vx] & 1) == 1:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        self.registers[self.vx] /= 2


    def _DXXX(self):
        self.registers[0xf] = 0
        x = self.registers[self.vx] & 0xff
        y = self.registers[self.vy] & 0xff
        height = self.opcode & 0x000f
        row = 0

        while row < height:
            currentRow = self.memory[row + self.indexRegister]
            offset = 0

            while offset < 8:
                location = x + offset + ((y + row) * 64)
                offset += 1

                if (row + y) > 31 or (offset - 1 + x) > 63:
                    # off screen
                    continue

                mask = 1 << 8 - offset
                pixel = (currentRow & mask) >> (8 - offset)
                self.displayBuffer ^= pixel

                if self.displayBuffer[location] == 0:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0
            row += 1

        self.shouldDraw = True


    def _EXX1(self):
        '''Skip next instruction if key is pressed'''
        key = self.registers[self.vx] & 0xf
        if self.keyInputs[key] == 0:
            self.pc += 2


    def _EZZE(self):
        '''Skip next instruction if key is not pressed'''
        key = self.registers[self.vx] & 0xf
        if self.keyInputs[key] == 0:
            self.pc += 2


    def _FX29(self):
            '''Set location of sprite to I'''
            self.indexRegister = (5 * self.registers[self.vx]) & 0xfff


    def _FX33(self):
        num = self.registers[self.vx]        
        #TOOD
        print(num)


    def draw(self):
        if self.shouldDraw:
            self.clear()
            line = 0

            for i in range(2048):
                if self.displayBuffer[i] == 1:
                    self.pixel.blit((i % 64) * 10, 310 - ((i / 64) * 10))
            
            self.flip()
            self.shouldDraw = False


    def on_key_press(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.keyInputs[KEY_MAP[symbol]] = 1
            if self.key_wait:
                self.key_wait = False
        else:
            super(VM, self).on_key_press(symbol, modifiers)


    def on_key_release(self, symbol, modifiers):
        if symbol in KEY_MAP.keys():
            self.key_inputs[KEY_MAP[symbol]] = 0


    def main(self):
        self.reset()
        self.loadProgram(sys.argv[1])

        while not self.hasExit:
            self.dispatch_events()
            self.cycle()
            self.draw()
