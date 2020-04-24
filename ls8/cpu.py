"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b001000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        # Dispatch table
        self.dispatch_table = {LDI: self.handle_ldi, PRN: self.handle_prn, HLT: self.handle_hlt, MUL: self.handle_mul,
                               ADD: self.handle_add, PUSH: self.handle_push, POP: self.handle_pop,
                               CALL: self.handle_call, RET: self.handle_ret, CMP: self.handle_cmp,
                               JMP: self.handle_jmp, JNE: self.handle_jne, JEQ: self.handle_jeq}

        self.ram = [0b0] * 0b100000000  # 256 in binary
        self.reg = [0b0] * 0b1000  # 8 in binary for the register
        self.pc = 0b0  # 0 in binary for the pc
        self.stack_pointer = 7  # R7 is reservered for the pointer to the stack
        # pointer to the correct index on RAM
        self.reg[self.stack_pointer] = 0xF4
        self.running = False
        self.FL = [0b0] * 0b1000 # 8 in binary for the flag

    def handle_ldi(self, *argv):
        self.reg[argv[0]] = argv[1]
        self.pc += 3

    def handle_prn(self, *argv):
        print(self.reg[argv[0]])
        self.pc += 2

    def handle_hlt(self, *argv):
        self.running = False
        self.pc += 1

    def handle_mul(self, *argv):
        self.alu('MUL', argv[0], argv[1])
        self.pc += 3

    def handle_add(self, *argv):
        self.alu("ADD", argv[0], argv[1])
        self.pc += 3

    def handle_push(self, *argv):
        self.reg[self.stack_pointer] -= 1
        self.ram[self.reg[self.stack_pointer]] = self.reg[argv[0]]
        self.pc += 2

    def handle_pop(self, *argv):
        copy_stack = self.ram[self.reg[self.stack_pointer]]
        self.reg[argv[0]] = copy_stack
        self.reg[self.stack_pointer] += 1
        self.pc += 2

    def handle_call(self, *argv):
        self.reg[self.stack_pointer] -= 1
        self.ram[self.reg[self.stack_pointer]] = self.pc + 2

        new_reg = self.ram[self.pc + 1]
        self.pc = self.reg[new_reg]

    def handle_ret(self, *argv):
        self.pc = self.ram[self.reg[self.stack_pointer]]
        self.reg[self.stack_pointer] += 1

    def handle_cmp(self, *argv):
        self.alu("CMP", argv[0], argv[1])
        self.pc += 3

    def handle_jmp(self, *argv):
        self.pc = self.reg[argv[0]]

    def handle_jne(self, *argv):
        if self.FL[-1] == 0:
            self.pc = self.reg[argv[0]]
        else:
            self.pc += 2

    def handle_jeq(self, *argv):
        if self.FL[-1] == 1:
            self.pc = self.reg[argv[0]]
        else:
            self.pc += 2

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    line = line.split('#')
                    line = line[0].strip()

                    if line == "":
                        continue

                    value = int(line, 2)
                    self.ram[address] = value

                    address += 1
        except FileNotFoundError:
            print("File not found...")
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL[-1] = 1
                self.FL[-2] = 0
                self.FL[-3] = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[-1] = 0
                self.FL[-2] = 1
                self.FL[-3] = 0
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL[-1] = 0
                self.FL[-2] = 0
                self.FL[-3] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if instruction in self.dispatch_table:
                self.dispatch_table[instruction](operand_a, operand_b)
            else:
                print('Invalid instruction...')
                sys.exit()
