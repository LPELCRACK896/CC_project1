#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_radius: .word 0
	Main_attr_booleano: .byte 1
	Circle_attr_radio: .word 8
	Circle_getArea_formal_size: .word 0
	Main_attr_name: .asciiz "Hello world\n"
	temporal_var_1: .asciiz "Hola aaamigos"
.text
	li $t0, 7
	li $t1, 2
	mul $t2, $t0, $t1
	la $t1, Main_attr_radius
	sw $t2, 0($t1)

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
		jr $ra
	IO_inInt:
		li $v0, 5 
		syscall
		jr $ra
	Circle_getArea:
		lw $a0, 0($sp)
		sw $a0, Circle_getArea_formal_size
		li $t2, 3
		lw $t1, Circle_attr_radio
		mul $t0, $t2, $t1
		lw $t1, Circle_attr_radio
		mul $t2, $t0, $t1
		jr $ra
	Main_main:
		la $t2, temporal_var_1
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		li $t2, 1
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outInt
		addi $sp, $sp, 4
		li $v0, 10
		syscall
