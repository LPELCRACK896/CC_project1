#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_radius: .word 0
	Main_attr_booleano: .byte 1
	Main_attr_t1: .word 0
	Main_attr_name: .asciiz "Juan"
	Main_attr_cadena: .asciiz "Pa"
	Arithmetic_sumaTres_formal_a: .word 0
	Arithmetic_sumaTres_formal_b: .word 0
	Arithmetic_sumaTres_formal_c: .word 0
	temporal_var_1: .asciiz "\n"
	temporal_var_2: .asciiz "\n"
	Main_suma_formal_a: .word 0
	Main_suma_formal_b: .word 0
	Main_setName_formal_newName: .asciiz ""
	temporal_var_3: .asciiz "Hola Carlos\n"
	temporal_var_4: .asciiz "hola"
.text
	li $t0, 7
	li $t1, 2
	mul $t2, $t0, $t1
	la $t1, Main_attr_radius
	sw $t2, 0($t1)
	li $t2, 90
	li $t1, 10
	add $t0, $t2, $t1
	la $t1, Main_attr_t1
	sw $t0, 0($t1)

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
	Arithmetic_sumaTres:
		lw $a0, 8($sp)
		sw $a0, Arithmetic_sumaTres_formal_a
		lw $a0, 4($sp)
		sw $a0, Arithmetic_sumaTres_formal_b
		lw $a0, 0($sp)
		sw $a0, Arithmetic_sumaTres_formal_c
		lw $t0, Arithmetic_sumaTres_formal_a
		lw $t1, Arithmetic_sumaTres_formal_b
		add $t2, $t0, $t1
		lw $t1, Arithmetic_sumaTres_formal_c
		add $t0, $t2, $t1
		move $v0, $t0
		jr $ra
	Main_main:
		la $t0, Main_attr_name
		li $t2, 67
		sb $t2, 0($t0)
		li $t2, 97
		sb $t2, 1($t0)
		li $t2, 114
		sb $t2, 2($t0)
		li $t2, 108
		sb $t2, 3($t0)
		li $t2, 105
		sb $t2, 4($t0)
		li $t2, 116
		sb $t2, 5($t0)
		li $t2, 111
		sb $t2, 6($t0)
		li $t2, 115
		sb $t2, 7($t0)
		li $t2, 0
		sb $t2, 9($t0)
		la $t0, Main_attr_name
		addi $sp, $sp -4
		sw $t0, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		li $t0, 1
		li $t2, 4
		addi $sp, $sp -4
		sw $t0, 0($sp)
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal Main_suma
		addi $sp, $sp, 8
		move $t2, $v0
		la $t0, Main_attr_radius
		sw $t2, 0($t0)
		li $t2, 6
		li $t0, 7
		slt $t1, $t0, $t2
		la $t0, Main_attr_booleano
		sb $t1, 0($t0)
		lb $t1, Main_attr_booleano
		beq $t1, $zero, L2
		la $t1, Main_attr_radius
		li $t0, 8
		sw $t0, 0($t1)
		j L5


		L2:
		la $t1, Main_attr_radius
		li $t0, 4
		sw $t0, 0($t1)


		L5:
		la $t1, temporal_var_1
		addi $sp, $sp -4
		sw $t1, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		lw $t1, Main_attr_radius
		addi $sp, $sp -4
		sw $t1, 0($sp)
		jal IO_outInt
		addi $sp, $sp, 4
		la $t1, temporal_var_2
		addi $sp, $sp -4
		sw $t1, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		li $t1, 0
		move $v0, $t1
		li $v0, 10
		syscall
	Main_suma:
		lw $a0, 4($sp)
		sw $a0, Main_suma_formal_a
		lw $a0, 0($sp)
		sw $a0, Main_suma_formal_b
		lw $t0, Main_suma_formal_a
		lw $t2, Main_suma_formal_b
		add $t3, $t0, $t2
		move $v0, $t3
		jr $ra
	Main_setName:
		lw $a0, 0($sp)
		sw $a0, Main_setName_formal_newName
		la $t3, Main_attr_name
		li $t2, 60
		sb $t2, -1($t3)
		li $t2, 68
		sb $t2, 0($t3)
		li $t2, 73
		sb $t2, 1($t3)
		li $t2, 82
		sb $t2, 2($t3)
		li $t2, 62
		sb $t2, 3($t3)
		li $t2, 46
		sb $t2, 4($t3)
		li $t2, 77
		sb $t2, 5($t3)
		li $t2, 97
		sb $t2, 6($t3)
		li $t2, 105
		sb $t2, 7($t3)
		li $t2, 110
		sb $t2, 8($t3)
		li $t2, 46
		sb $t2, 9($t3)
		li $t2, 115
		sb $t2, 10($t3)
		li $t2, 101
		sb $t2, 11($t3)
		li $t2, 116
		sb $t2, 12($t3)
		li $t2, 78
		sb $t2, 13($t3)
		li $t2, 97
		sb $t2, 14($t3)
		li $t2, 109
		sb $t2, 15($t3)
		li $t2, 101
		sb $t2, 16($t3)
		li $t2, 46
		sb $t2, 17($t3)
		li $t2, 102
		sb $t2, 18($t3)
		li $t2, 111
		sb $t2, 19($t3)
		li $t2, 114
		sb $t2, 20($t3)
		li $t2, 109
		sb $t2, 21($t3)
		li $t2, 97
		sb $t2, 22($t3)
		li $t2, 108
		sb $t2, 23($t3)
		li $t2, 46
		sb $t2, 24($t3)
		li $t2, 110
		sb $t2, 25($t3)
		li $t2, 101
		sb $t2, 26($t3)
		li $t2, 119
		sb $t2, 27($t3)
		li $t2, 78
		sb $t2, 28($t3)
		li $t2, 97
		sb $t2, 29($t3)
		li $t2, 109
		sb $t2, 30($t3)
		li $t2, 101
		sb $t2, 31($t3)
		li $t2, 0
		sb $t2, 32($t3)
		la $t3, Main_attr_name
		move $v0, $t3
		jr $ra
	Main_saludo:
		la $t2, temporal_var_3
		addi $sp, $sp -4
		sw $t2, 0($sp)
		jal IO_outString
		addi $sp, $sp, 4
		la $t2, temporal_var_4
		move $v0, $t2
		jr $ra
