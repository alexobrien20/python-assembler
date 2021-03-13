# python-assembler
| Instruction | Format | Syntax |
|-------------|--------|--------|
|add |R | add $rd, $rs, $rt |
| addi | I | addi $rd, $rs, imm |
| addiu | I | addi $rd, $rs, imm |
| addu | R | addu $rd, $rs, $rt |
| and | R | and $rd, $rs, $rt |
| andi | I | $rt, $rs, imm |
| beq |I | $rs, $rt, imm |
| bne | I | $rs, $rt, imm |
| j | J | j address |
| jal | J | jal address |
| jr | R | jr $ra |
| lw | I | lw $rt, imm($rs) |
| nor | R | nor $rd, $rs, $rt |
| or | R | or $rd, $rs, $rt |
| sll | R | sll $rd, $rt, shamt |
| slt | R | $rd, $rs, $rt |
| srl | R | srl $rd, $rt, shamt |
| sub | R | $rd, $rs, $rt |
| sw  | I | sw $rt, imm($rs) |
