#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_booleano: .byte 1
	Main_attr_age: .word 0
	temporal_var_1: .asciiz "Hola Carlos ingrese su edad: "
	temporal_var_2: .asciiz "\n"
	temporal_var_3: .asciiz "\nEs mayor de edad"
	temporal_var_4: .asciiz "\nEs menor de edad"
.text

	j Main_main

	IO_outString:
		li $v0, 4
		lw $a0, 0($sp)
		syscall
		jr $ra
	IO_outInt:
		li $v0, 1
		lw $a0, 0($sp)
		syscall
		jr $ra
	IO_inString:
		li $v0, 8
		la $a0, buffer
		li $a1, 1024
		syscall
		la $t0, buffer
		move $v0, $t0
		jr $ra
	IO_inInt:
		li $v0, 5 
		syscall
		jr $ra
	Main_main:
		la $t0, temporal_var_1
		addi $sp, $sp -4
		sw $t0, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		jal IO_inInt
		addi $sp, $sp, 0
		move $t0, $v0
		la $t1, Main_attr_age
		sw $t0, 0($t1)
		la $t0, temporal_var_2
		addi $sp, $sp -4
		sw $t0, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		lw $t0, Main_attr_age
		addi $sp, $sp -4
		sw $t0, 0($sp)
		jal IO_outInt
		addi $sp, $sp, 4
		lw $t0, Main_attr_age
		li $t1, 17
		slt $t2, $t1, $t0
		beq $t2, $zero, L2
		la $t2, temporal_var_3
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		j L5


		L2:
		la $t2, temporal_var_4
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4


		L5:
		li $t2, 1
		move $v0, $t2
		li $v0, 10
		syscall
