import pyglet, random, sys, traceback

#constants for key mapping
KEY_MAP = {pyglet.window.key._1: 0x1,
                        pyglet.window.key._2: 0x2,
                        pyglet.window.key._3: 0x3,
                        pyglet.window.key._4: 0xc,
                        pyglet.window.key.Q: 0x4,
                        pyglet.window.key.W: 0x5,
                        pyglet.window.key.E: 0x6,
                        pyglet.window.key.R: 0xd,
                        pyglet.window.key.A: 0x7,
                        pyglet.window.key.S: 0x8,
                        pyglet.window.key.D: 0x9,
                        pyglet.window.key.F: 0xe,
                        pyglet.window.key.Z: 0xa,
                        pyglet.window.key.X: 0,
                        pyglet.window.key.C: 0xb,
                        pyglet.window.key.V: 0xf
                    }

class VM (pyglet.window.Window):
    '''Virtual machine that handles the emulation of the Chip 8 interpreter'''
    def __init__(self):
        super(VM, self).__init__()     
        self.funcMap = {0x000: self._0XXX, 0x00e0: self._0XX0, 0x00ee: self._0XXE,
                        0x1000: self._1XXX, 0x2000: self._2XXX, 0x3000: self._3XXX,
                        0x4000: self._4XXX, 0x5000: self._5XXX, 0x6000: self._6XXX,
                        0x7000: self._7XXX, 0x8000: self._8XXX, 0x8001: self._8XX1,
                        0x8002: self._8XX2, 0x8003: self._8XX3, 0x8004: self._8XX4,
                        0x8005: self._8XX5, 0x8006: self._8XX6, 0x8007: self._8XX7,
                        0x800E: self._8XXE, 0x9000: self._9XXX, 0xa000: self._AXXX,
                        0xb000: self._BXXX, 0xc000: self._CXXX, 0xd000: self._DXXX,
                        0xe000: self._EXXX, 0xe0a1: self._EXX1, 0xe09e: self._EXXE,
                        0xf000: self._FXXX, 0xf007: self._FXX7, 0xf00a: self._FXXA,
                        0xf015: self._FX15, 0xf018: self._FXX8, 0xf01e: self._FXXE,
                        0xf029: self._FX29, 0xf033: self._FX33, 0xf055: self._FX55,
                        0xf065: self._FX65
                        }
        self.fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
                    0x20, 0x60, 0x20, 0x20, 0x70, # 1
                    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
                    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
                    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
                    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
                    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
                    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
                    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
                    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
                    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
                    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
                    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
                    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
                    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
                    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
           ]
        self.beep = pyglet.resource.media('sound.wav', streaming=False)
        self.pixel = pyglet.resource.image('pixel.png')
        self.batch = pyglet.graphics.Batch()
        self.sprites = []
        for i in range(2048):
            self.sprites.append(pyglet.sprite.Sprite(self.pixel,batch=self.batch))
        
        self.reset()
        

    def reset(self):
        '''Resets the VM'''
        self.clear()
        self.keyInputs = [0] * 16
        self.displayBuffer = [0] * 32 * 64
        self.memory = [0] * 4096
        self.registers = [0] * 16
        self.pc = 0x200
        self.indexRegister = 0
        self.stack = []
        self.soundTimer = 0
        self.delayTimer = 0
        self.shouldDraw = False
        self.key_wait = False

        for i in range(80):
            self.memory[i] = self.fonts[i]

    def loadProgram(self, path):
        '''Loads the program at PATH into memory'''
        fileIn = open(path, "rb").read()
        for i in range(len(fileIn)):
            self.memory[0x200 + i] = fileIn[i]

    def cycle(self):
        '''Represents a CPU cycle'''
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        # process opcode
        self.vx = (self.opcode & 0x0f00) >> 8
        self.vy = (self.opcode & 0x00f0) >> 4
        self.pc += 2

        op = self.opcode & 0xf000
        try:            
            self.funcMap[op]()
        except Exception as e:
            print("Error:1 unknown instruction ({}) at pc: {}".format(op, self.pc))
            print(op in self.funcMap)
            print(traceback.format_exc())
            exit(0)

        if self.delayTimer > 0:
            self.delayTimer -= 1
        if self.soundTimer > 0:
            self.soundTimer -= 1
            if self.soundTimer == 0:
                self.beep.play()
                
                


    def _0XXX(self):
        '''Narrows down the opcode to either 0XX0 or 0XXE'''
        op = self.opcode & 0xf0ff
        try:
            self.funcMap[op]()
        except:
            print("Error:2 unknown instruction ({}) at pc: {}".format(self.opcode, self.pc))

    
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
        op = self.opcode & 0xf00f
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
        if self.registers[self.vx] > self.registers[self.vy]:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        self.registers[self.vx] -= self.registers[self.vy]
        self.registers[self.vx] &= 0xff


    def _8XX6(self):
        '''Shift right'''
        if (self.registers[self.vx] & 1) == 1:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        self.registers[self.vx] /= 2
        self.registers[self.vx] &= 0xff


    def _8XX7(self):
        '''Subtract N'''
        if self.registers[self.vy] > self.registers[self.vx]:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0
        self.registers[self.vx] = self.registers[self.vy] - self.registers[self.vx]
        self.registers[self.vx] &= 0xff


    def _8XXE(self):
        '''Shift left'''
        if (self.registers[self.vx] & 0x80) == 1:
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0

        self.registers[self.vx] *= 2
        self.registers[self.vx] &= 0xff

    
    def _9XXX(self):
        '''Skip next instruction if Vx != Vy'''
        if self.registers[self.vx] != self.registers[self.vy]:
            self.pc += 2


    def _AXXX(self):
        '''Set I register to nnn'''
        self.indexRegister = self.opcode & 0x0fff


    def _BXXX(self):
        self.pc = (self.opcode & 0x0fff) + self.registers[0]


    def _CXXX(self):
        '''Set Vx to random byte AND kk'''
        self.registers[self.vx] = random.randint(0, 255) & (self.opcode & 0xff)


    def _DXXX(self):
        '''Draws a frame'''
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
                self.displayBuffer[location] ^= pixel

                if self.displayBuffer[location] == 0:
                    self.registers[0xf] = 1
                else:
                    self.registers[0xf] = 0
            row += 1

        self.shouldDraw = True


    def _EXXX(self):
        op = self.opcode & 0xf0ff
        try:
            self.funcMap[op]()
        except:
            print("Error: unknown instruction ({})".format(self.opcode))


    def _EXX1(self):
        '''Skip next instruction if key is pressed'''
        key = self.registers[self.vx] & 0xf
        if self.keyInputs[key] == 0:
            self.pc += 2


    def _EXXE(self):
        '''Skip next instruction if key is not pressed'''
        key = self.registers[self.vx] & 0xf
        if self.keyInputs[key] == 0:
            self.pc += 2


    def _FXXX(self):
        op = self.opcode & 0xf0ff
        try:
            self.funcMap[op]()
        except:            
            print("Error:5 unknown instruction ({}) at pc: {}".format(op, self.pc))
            print(op in self.funcMap)
            print(traceback.format_exc())
            exit(0)


    def _FXXA(self):
        '''Get key input'''
        keyInput = self.getKey()
        if keyInput > -1:
            self.registers[self.vx] = keyInput
        else:
            self.pc -=2


    def _FXX7(self):
        '''Set Vx to delay timer'''
        self.registers[self.vx] = self.delayTimer


    def _FX15(self):
        '''Set delay timer to Vx'''
        self.delayTimer = self.registers[self.vx]


    def _FXX8(self):
        '''Set sound timer to Vx'''
        self.soundTimer = self.registers[self.vx]


    def _FXXE(self):
        '''Increment I register by Vx'''
        self.indexRegister += self.registers[self.vx]
        if self.indexRegister > 0xfff:
            self.registers[0xf] = 1
            self.indexRegister &= 0xfff
        else:
            self.registers[0xf] = 0


    def _FX29(self):
            '''Set location of sprite to I'''
            self.indexRegister = int(5 * self.registers[self.vx]) & 0xfff


    def _FX33(self):
        num = self.registers[self.vx]        
        self.memory[self.indexRegister + 2] = num % 10
        num /= 10
        self.memory[self.indexRegister + 1] = num % 10
        num /= 10
        self.memory[self.indexRegister] = num % 10


    def _FX55(self):
        for i in range(self.vx + 1):
            self.memory[self.indexRegister + i] = self.registers[i]
        self.indexRegister += self.vx + 1


    def _FX65(self):
        for i in range(self.vx + 1):
            self.registers[i] = self.memory[self.indexRegister + i]
        self.indexRegister += self.vx + 1


    def getKey(self):
        '''Checks to see if a key has been pressed.
        Returns the key number if pressed, or -1 if none found'''
        for i in range(16):
            if self.keyInputs[i] == 1:
                return i
        return -1


    def draw(self):
        '''Draws the new frame onto the window'''
        if self.shouldDraw:
            for i in range(2048):
                if self.displayBuffer[i] == 1:
                    self.sprites[i].x = (i % 64) * 10
                    self.sprites[i].y = 310 - ((i / 64) * 10)
                    self.sprites[i].batch = self.batch
                else:
                    self.sprites[i].batch = None
            
            self.clear()
            self.batch.draw()
            self.flip()
            self.shouldDraw = False


    def on_key_press(self, symbol, modifiers):
        '''Overridden method of Pyglet'''
        if symbol in KEY_MAP.keys():
            self.keyInputs[KEY_MAP[symbol]] = 1
            if self.key_wait:
                self.key_wait = False
        else:
            super(VM, self).on_key_press(symbol, modifiers)


    def on_key_release(self, symbol, modifiers):
        '''Overridden method of Pyglet'''
        if symbol in KEY_MAP.keys():
            self.keyInputs[KEY_MAP[symbol]] = 0


    def main(self):
        '''Main loop'''
        self.reset()
        self.loadProgram(sys.argv[1])

        while not self.has_exit:
            self.dispatch_events()
            self.cycle()
            self.draw()

if __name__ == '__main__':
    virtualMachine = VM()
    virtualMachine.main()