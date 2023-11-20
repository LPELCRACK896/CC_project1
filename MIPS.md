# Instrucciones MIPS

## Resumen de llamadas al sistema

- print_int $v0=1 $a0= entero a imprimir Imprime $a0 en la salida estándar
- print_float $v0=2 $f12= float a imprimir Imprime $f12 en la salida estándar
- print_double $v0=3 $f12= double a imprimir Imprime $f12 en la salida estándar
- print_string $v0=4 $a0= dirección del primer carácter Imprime la cadena de caracterer en la salida estándar
- read_int $v0=5 Lee en $v0 un entero de la entrada estándar
- read_float $v0=6 Lee en $v0 un float de la entrada estándar
- read_double $v0=7 Lee en $v0 un double de la entrada estándar
- read_string $v0=8 $a0 = dirección del buffer, $a1= longitud del buffer Lee en el buffer de la entrada estándar
- sbrk $v0=9 $a0= número necesario de bytes Deja en $v0 la dirección de memoria reservada Reserva memoria del montón o heap
- exit $v0=10 Finaliza la ejecución

## Resumen del juego de instrucciones

- $zero $0 constante entera 0 sí
- $at $1 temporal del ensamblador no
- $v0–$v1 $2–$3 Valores de retorno de funciones y evaluación de expresiones no
- $a0–$a3 $4–$7 Paso argumentos a subrutinas no
- $t0–$t7 $8–$15 Temporales no
- $s0–$s7 $16–$23 Temporales salvados sí
- $t8–$t9 $24–$25 Temporales no
- $k0–$k1 $26–$27 Reservados para el núcleo del S.O. no
- $gp $28 puntero global sí
- $sp $29 puntero de pila sí
- $fp $30 puntero de marco de pila sí
- $ra $31 dirección de retorno no

## Instrucciones reales

### Instrucciones Aritméticas

- Suma: add $1,$2,$3
- Suma sin signo: addu $1,$2,$3
- Resta: sub $1,$2,$3
- Suma inmediata: addi $1,$2,CONST
- Suma inmediata sin signo addiu $1,$2,CONST
- Multiplicación: mult $1,$2
- División: div $1, $2

### Instrucciones de Transferencia de Datos

- Carga de dirección: la $1, Etiqueta
- Carga de palabra: lw $1,CONST($2)
- Carga de media palabra: lh $1,CONST($2)
- Carga de byte: lb $1,CONST($2)
- Almacenamiento de palabra: sw $1,CONST($2)
- Almacenamiento de media palabra: sh $1,CONST($2)
- Almacenamiento de byte: sb $1,CONST($2)
- Carga del inmediato superior: lui $1,CONST
- Mover desde "high": mfhi $1
- Mover desde "low": mflo $1

### Instrucciones Lógicas

- And: and $1,$2,$3
- And con inmediato: andi $1,$2,CONST
- Or: or $1,$2,$3
- Or con inmediato: ori $1,$2,CONST
- Or exclusivo: xor $1,$2,$3
- Nor: nor $1,$2,$3
- Inicializar si menor que: slt $1,$2,$3
- Inicializar si menor que con inmediato: slti $1,$2,CONST

### Instrucciones de Desplazamiento de bits

- Desplazamiento lógico a la izquierda: sll $1,$2,CONST
- Desplazamiento lógico a la derecha: srl $1,$2,CONST
- Desplazamiento aritmético a la derecha: sra $1,$2,CONST

### Instrucciones de Saltos condicionales

- Salto si igual: beq $1,$2,CONST
- Salto si no igual: bne $1,$2,CONST

### Instrucciones de Salto incondicional

- Salto: j CONST
- Salto a registro: jr $1
- Salto y enlace: jal CONST

### Pseudoinstrucciones

- Saltar si mayor que: bgt $rs,$rt,Label
- Saltar si menor que: blt $rs,$rt,Label
- Saltar si mayor o igual que: bge $rs,$rt,Label
- Saltar si menor o igual que: ble $rs,$rt,Label
- Saltar si igual que: beq $rs, $rt,Label
- Saltar si igual a cero: beqz $rs,Label
- Saltar si mayor que (sin signo): bgtu $rs,$rt,Label
- Saltar si mayor que cero: bgtz $rs,Label
