import pyglet
class VM (pyglet.window.Window):
    def __init__(self):
        self.reset()
        self.funcMap = { 0x000: self._0XXX,
                        0x00e0: self._0XX0,
                        0x00ee: self._0XXE,
                        0x1000: self._1XXX,

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
                # play sound
                


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


    def _4XXX(self):
        '''Skip next instruction if not equal'''
        if self.registers[self.vx] != (self.opcode & 0x00ff):
            self.pc += 2


    def _5XXX(self):
        '''Compare'''
        if self.registers[self.vx] == self.registers[self.vy]:
            self.pc += 2


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


    def _FX29(self):
        '''Set location of sprite to I'''
        self.indexRegister = (5 * self.registers[self.vx]) & 0xfff


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

        

    def on_key_press(self, symbol, modifiers):
        continue

    def on_key_release(self, symbol, modifiers):
        continue

    def main(self):
        self.reset()
        self.loadProgram(sys.argv[1])

        while not self.hasExit:
            self.dispatch_events()
            self.cycle()
            self.draw()
