#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_radius: .word 0
	Main_attr_booleano: .byte 1
	Main_attr_t1: .word 0
	Main_attr_name: .asciiz "Juan"
	Shape_attr_radius: .word 0
	Shape_attr_color: .asciiz ""
	Shape_attr_ancho: .word 0
	Shape_attr_hasCorners: .byte 1
.text
	li $t0, 7
	li $t1, 2
	mul $t2, $t0, $t1
	la $t1, Main_attr_radius
	sw $t2, 0($t1)
	li $t2, 90
	li $t1, 10
	add $t0, $t2, $t1
	li $t1, 6
	sub $t2, $t0, $t1
	li $t0, 5
	div $t2, $t0
	mflo $t1
	la $t2, Main_attr_t1
	sw $t1, 0($t2)

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
	Shape_isCool:
		jr $ra
	Shape_getArea:
		jr $ra
	Shape_getPerimeter:
		jr $ra
	Main_main:
		li $v0, 10
		syscall
	Main_suma:
		jr $ra
	Main_saludo:
		jr $ra
