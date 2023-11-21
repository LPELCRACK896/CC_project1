#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_booleano: .byte 1
	Main_attr_age: .word 0
	Main_attr_name: .asciiz " "
	temporal_var_1: .asciiz " ingrese su edad: "
	temporal_var_2: .asciiz "\nEs mayor de edad"
	temporal_var_3: .asciiz "\nEs menor de edad"
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
		la $t0, Main_attr_name
		li $t1, 76
		sb $t1, 0($t0)
		li $t1, 117
		sb $t1, 1($t0)
		li $t1, 105
		sb $t1, 2($t0)
		li $t1, 115
		sb $t1, 3($t0)
		li $t1, 0
		sb $t1, 5($t0)
		la $t0, Main_attr_name
		addi $sp, $sp -4
		sw $t0, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
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
		lw $t0, Main_attr_age
		li $t1, 17
		slt $t2, $t1, $t0
		beq $t2, $zero, L2
		la $t2, temporal_var_2
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		j L5


		L2:
		la $t2, temporal_var_3
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4


		L5:
		li $t2, 1
		move $v0, $t2
		li $v0, 10
		syscall
