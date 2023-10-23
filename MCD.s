.data
prompt0: .asciiz "Cálculo de MCD (-1 para salir) \n" # prompt instrucciones
prompt1: .asciiz "Ingrese el primer número: " # Segundo numero
prompt2: .asciiz "Ingrese el segundo número: " # Primer numero
resultado: .asciiz "MCD: " # res
enter: .asciiz "\n"  # Enter

.text
.globl main

# main del programa
main:
    # Imprimir nombre e ins
    li $v0, 4
    la $a0, prompt0
    syscall
    loop:
        # Imprimir primer prompt
        li $v0, 4
        la $a0, prompt1
        syscall

        # Tomar el primer número
        li $v0, 5
        syscall
        move $t0, $v0  # $t0 = primer número

        # Verificar si el usuario quiere salir
        li $t3, -1     # $t3 almacena la condición de salida
        beq $t0, $t3, exit  # Si es -1, salir del programa

        # Imprimir segundo prompt
        li $v0, 4 
        la $a0, prompt2
        syscall

        # Tomar el segundo número
        li $v0, 5
        syscall
        move $t1, $v0  # $t1 = segundo número

        # Llamada a función recursiva
        jal gcd
        move $a0, $v0

        # Imprimir resultado
        li $v0, 1
        syscall

        # Imprimir nueva línea
        li $v0, 4
        la $a0, enter
        syscall

        j loop  # Volver al inicio del bucle para más entradas

    exit:
        # Terminar programa
        li $v0, 10
        syscall

# gcd: cálcula recursivamente el MCD
gcd:
    beq $t0, $t1, iguales  # Si son iguales, ya tenemos el MCD
    blt $t1, $t0, cambiar  # Si n2 < n1, intercambiar
    sub $t1, $t1, $t0
    j gcd

cambiar:
    move $t2, $t0
    move $t0, $t1
    move $t1, $t2
    j gcd

iguales:
    move $v0, $t0
    jr $ra
