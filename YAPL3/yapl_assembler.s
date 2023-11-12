.data


.text

main:
	li $t1, 4
	li $t0, 5
	add 	t19, $t1, $t0
	li $t0, t19
	li $t1, 1
	div $t0, $t1
	mflo 	t20
	lw $t0, <DIR>.Main.attr.t1
	li $t1, 1
	add 	t23, $t0, $t1


shape:
	lw $t0, <DIR>.Shape.isCool.declaration_assignation.b
	li $t1, 
	add 	<DIR>.Shape.isCool.declaration_assignation.a, $t0, $t1
	li $t1, 2
	lw $t0, <DIR>.Shape.getPerimeter.formal.height
	mul 	t26, $t1, $t0
	li $t0, 2
	lw $t1, <DIR>.Shape.getPerimeter.formal.width
	mul 	t27, $t0, $t1
	li $t1, t26
	li $t0, t27
	add 	t28, $t1, $t0


