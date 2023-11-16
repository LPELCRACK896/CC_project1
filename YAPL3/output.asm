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
	temporal_var_1: .asciiz "palabraaa"
	temporal_var_2: .asciiz "hola"
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
	Shape_allType:
		jr $ra
	Shape_getPerimeter:
		li $t1, 2
		li $t2, None
		mul $t0, $t1, $t2
		li $t2, 2
		li $t1, None
		mul $t2, $t2, $t1
		add $t1, $t0, $t2
		jr $ra
	Main_main:
		li $t1, 1
		li $t2, 0
		la $t0, temporal_var_1
		la $t0, Main_attr_name
		li $t2, "M"
		sb $t2, 1($t0)
		li $t2, "a"
		sb $t2, 2($t0)
		li $t2, "r"
		sb $t2, 3($t0)
		li $t2, "i"
		sb $t2, 4($t0)
		li $t2, "o"
		sb $t2, 5($t0)
		li $t2, 0
		sb $t2, 6($t0)
		la $t0, temporal_var_2
		li $t0, 4
		li $t2, 5
		add $t1, $t0, $t2
		li $t2, 1
		div $t1, $t2
		mflo $t0
		la $t1, Main_attr_radius
		sw $t0, 0($t1)
		la $t0, Main_attr_booleano
		li $t1, None
		sb $t1, 0($t0)
		li $t0, 1
		li $t1, 4
		la $t1, Main_attr_radius
		li $t0, None
		sw $t0, 0($t1)
		li $t1, None
		li $t0, 1
		add $t2, $t1, $t0
		la $t0, Main_attr_t1
		sw $t2, 0($t0)
		la $t2, Main_attr_radius
		li $t0, 8
		sw $t0, 0($t2)
		la $t2, Main_attr_radius
		li $t0, 4
		sw $t0, 0($t2)
		li $v0, 10
		syscall
	Main_suma:
		li $t2, None
		li $t0, None
		add $t1, $t2, $t0
		jr $ra
	Main_saludo:
		jr $ra
