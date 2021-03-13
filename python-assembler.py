import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help='Provide the file path to the text file', type=str)
parser.add_argument("-o", "--output", help='Provide the output file name', type=str)
args = parser.parse_args()

OP_CODE_TABLE = {
 'add': {'op': '000000', 'type': 'R', 'Func': '100000'},
 'addi': {'op': '001000', 'type': 'I', 'Func': 'NA'},
 'addiu': {'op': '001001', 'type': 'I', 'Func': 'NA'},
 'addu': {'op': '000000', 'type': 'R', 'Func': '100001'},
 'and': {'op': '000000', 'type': 'R', 'Func': '100100'},
 'andi': {'op': '001100', 'type': 'I', 'Func': 'NA'},
 'beq': {'op': '000100', 'type': 'I', 'Func': 'NA'},
 'bne': {'op': '000101', 'type': 'I', 'Func': 'NA'},
 'j': {'op': '000010', 'type': 'J', 'Func': 'NA'},
 'jal': {'op': '000011', 'type': 'J', 'Func': 'NA'},
 'jr': {'op': '000000', 'type': 'R', 'Func': '001000'},
 'lw': {'op': '100011', 'type': 'I', 'Func': 'NA'},
 'nor': {'op': '000000', 'type': 'R', 'Func': '100111'},
 'or': {'op': '000000', 'type': 'R', 'Func': '100101'},
 'sll': {'op': '000000', 'type': 'R', 'Func': '000000'},
 'slt': {'op': '000000', 'type': 'R', 'Func': '101010'},
 'srl': {'op': '000000', 'type': 'R', 'Func': '000010'},
 'sub': {'op': '000000', 'type': 'R', 'Func': '100010'},
 'sw': {'op': '101011', 'type': 'I', 'Func': 'NA'},
}

REGISTERS = {
     '$zero': '00000',
     '$at': '00001',
     '$v0': '00010',
     '$v1': '00011',
     '$a0': '00100',
     '$a1': '00101',
     '$a2': '00110',
     '$a3': '00111',
     '$t0': '01000',
     '$t1': '01001',
     '$t2': '01010',
     '$t3': '01011',
     '$t4': '01100',
     '$t5': '01101',
     '$t6': '01110',
     '$t7': '01111',
     '$s0': '10000',
     '$s1': '10001',
     '$s2': '10010',
     '$s3': '10011',
     '$s4': '10100',
     '$s5': '10101',
     '$s6': '10110',
     '$s7': '10111',
     '$t8': '11000',
     '$t9': '11001',
     '$k0': '11010',
     '$k1': '11011',
     '$gp': '11100',
     '$sp': '11101',
     '$fp': '11110',
     '$ra': '11111'
}

def format_input(file_path):
    f = open(file_path, 'r')
    file_input = f.readlines()
    f.close()
    formatted_lines = []
    address_locations = {}
    counter = 0
    for line in file_input:
        line = line.strip()
        if len(line) == 0:
            # if blank line skip
            pass
        elif line.startswith('#'):
            # if a comment line skip
            pass
        else:
            line_space_split = line.split(' ')
            line_colon_split = line.split(':')
            if len(line_space_split) == 1:
                # e.g. LOOP: add branch name + address to a dict
                name = line.split(':')[0]
                address_locations.update({name: '{:04X}'.format(counter*4)})
            elif len(line_colon_split) > 1:
                # e.g LOOP: slt $t0, $t1, $t2 add branch name + address to dict
                name = line_colon_split[0]
                address_locations.update({name: '{:04X}'.format(counter*4)})
                formatted_lines.append(line_colon_split[1].strip().split('#')[0].strip('\t').strip())
                counter += 1
            else:
                formatted_lines.append(line.split('#')[0].strip('\t').strip())
                counter += 1
    return formatted_lines, address_locations

def calculate_branch_address(target_address, current_address):
    """
    target_address and current_address = 32-bit hex
    returns immediate address in two's complement binary
    """
    target_address_hex = int(target_address, 16)
    current_address_hex = int(current_address, 16)
    binary_immediate = int((target_address_hex - current_address_hex - 4) / 4)
    if binary_immediate < 0:
        binary_immediate = bin(binary_immediate & 0b1111111111111111)
        binary_immediate = binary_immediate.split('b')[1]
    else:
        binary_immediate = '{:016b}'.format(binary_immediate)
    return binary_immediate

def calculate_jump_address(target_address):
    """
    immediate = (target - 4 left most bits) / 4
    returns binary of immediate
    """
    binary_target = '{:032b}'.format(int(target_address, 16))
    binary_target_4 = binary_target[4:]
    decimal_target_4 = (int(binary_target_4, 2)) / 4
    jump_immediate = '{:026b}'.format(int(decimal_target_4))
    return jump_immediate

def assemble(mips_input, address_locations, file_output):
    """
    Takes in the mips instructions, the address locations 
    and the name of the file to save the binary instructions.
    """
    machine_code = []
    counter = 0
    for line in mips_input:
        op = line.split(',')
        command_name = op[0].split(' ')[0].strip()
        command = OP_CODE_TABLE[command_name]
        opcode = command['op']
        if command['type'] == 'I':
            if command_name == 'beq' or command_name == 'bne':
                # has the form OP rs, rt, IMM
                try:
                    # Constant jumps e.g. beq $t0, $t1, 3 # jump 3 instructions
                    immediate = int(op[2])
                    immediate = '{:016b}'.format(immediate)
                except:
                    # Not a constant jump e.g. beq $t0, $t1, Loop # jump to Loop
                    target_address = address_locations[op[2].strip()]
                    current_address = '{:08X}'.format(counter * 4)
                    immediate = calculate_branch_address(target_address, current_address)
                rt = op[0].split(' ')[1].strip()
                rs = op[1].strip()
                rt = REGISTERS[rt]
                rs = REGISTERS[rs]
                output = opcode + rt + rs + immediate
                machine_code.append(output)
                counter += 1
            elif command_name == 'lw' or command_name == 'sw':
                rt = op[0].split(' ')[1]
                rs = op[1].split('(')[1].strip(')')
                rt = REGISTERS[rt]
                rs = REGISTERS[rs]
                immediate = op[1].split('(')[0]
                immediate = '{:016b}'.format(int(immediate))
                output = opcode + rs + rt + immediate
                machine_code.append(output)
                counter += 1
            else:
                rs = op[1].strip()
                rt = op[0].split(' ')[1]
                immediate = op[2].strip()
                rt = REGISTERS[rt]
                rs = REGISTERS[rs]
                if int(immediate) < 0:
                    immediate = bin(int(immediate) & 0b1111111111111111).split('b')[1]
                else:
                    immediate = '{:016b}'.format(int(immediate))
                output = opcode + rs + rt + immediate
                machine_code.append(output)
                counter += 1
        elif command['type'] == 'R':
            function = command['Func']
            if command_name == 'jr':
                rs = op[0].split(' ')[1].strip()
                rs = REGISTERS[rs]
                shamt = '0'*15
                output = opcode + rs + shamt + function
                machine_code.append(output)
                counter += 1
            elif command_name == 'sll' or command_name == 'srl':
                shamt = '0' * 5
                rt = op[1].strip()
                rd = op[0].split(' ')[1].strip()
                sa = op[2].strip()
                rt = REGISTERS[rt]
                rd = REGISTERS[rd]
                sa = '{:05b}'.format(int(sa))
                output = opcode + shamt + rt + rd + sa + function
                machine_code.append(output)
                counter += 1
            else:
                if len(op) == 5:
                    shamt = op[3].strip()
                else:
                    shamt = '00000'
                rs = op[1].strip()
                rt = op[2].strip()
                rd = op[0].split(' ')[1].strip()
                rt = REGISTERS[rt]
                rs = REGISTERS[rs]
                rd = REGISTERS[rd]
                output = opcode + rs + rt + rd + shamt + function
                machine_code.append(output)
                counter += 1
        else:
            # J format
            immediate = op[0].split(' ')[1]
            target_address = address_locations[immediate]
            immediate = calculate_jump_address(target_address)
            output = opcode + immediate
            machine_code.append(output)
            counter += 1
    with open(file_output, 'w') as outfile:
        outfile.write("\n".join(machine_code))


if __name__ == '__main__':
    file_input = args.input
    file_output = args.output
    formatted_lines, address_locations = format_input(file_input)
    assemble(formatted_lines, address_locations, file_output)