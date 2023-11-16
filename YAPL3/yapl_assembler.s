.data


.text

main:
	li $t1, 7
	li $t0, 2
	add 	t1, $t1, $t0
	li $t0, t1
	li $t1, 2
	div $t0, $t1
	mflo 	t2
	li $t1, 15
	li $t0, 2
	sub 	t3, $t1, $t0
	li $t0, 4
	li $t1, 5
	add 	t24, $t0, $t1
	li $t1, t24
	li $t0, 1
	div $t1, $t0
	mflo 	t25
	lw $t1, <DIR>.Main.attr.t1
	li $t0, 1
	add 	t28, $t1, $t0


shape:
	lw $t0, <DIR>.Shape.isCool.declaration_assignation.b
	li $t1, 
	add 	<DIR>.Shape.isCool.declaration_assignation.a, $t0, $t1
	li $t1, 2
	lw $t0, <DIR>.Shape.getPerimeter.formal.height
	mul 	t29, $t1, $t0
	li $t0, 2
	lw $t1, <DIR>.Shape.getPerimeter.formal.width
	mul 	t30, $t0, $t1
	li $t1, t29
	li $t0, t30
	add 	t31, $t1, $t0


