"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b001000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b0] * 0b100000000  # 256 in binary
        self.reg = [0b0] * 0b1000  # 8 in binary
        self.pc = 0b0  # 0 in binary
        self.SP = 7 # R7 is reservered for the pointer to the stack
        self.reg[self.SP] = 0xF4 # pointer to the correct index on RAM

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
        running = True

        while running:

            instruction = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            # Check how much to add to PC depending on code
            if instruction == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif instruction == HLT:
                running = False
            elif instruction == MUL:
                self.alu('MUL', operand_a, operand_a)
                self.pc += 3
            elif instruction == POP:
                value = self.ram[self.reg[self.SP]]
                self.reg[operand_a] = value
                self.reg[self.SP] += 1
                self.pc += 2
            elif instruction == PUSH:
                self.reg[self.SP] -= 1
                self.ram[self.reg[self.SP]] = self.reg[operand_a]
                self.pc += 2
            else:
                print("Invalid instruction command...")
                running = False
                sys.exit()
