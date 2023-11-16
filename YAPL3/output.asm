#  Proyecto final Contruccion de compiladores
#  - Luis Pedro Gonzalez
#  - Mariano Reyes
.data
	buffer: .space 1024
	Main_attr_radius: .word 0
	Main_attr_booleano: .byte 1
	Main_attr_t1: .word 0
	Main_attr_name: .asciiz "Juan"
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

