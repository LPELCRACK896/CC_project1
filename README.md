# Construcción de compilador YAPL - Fase de análisis semántico

## Autores
- Luis Pedro González Aldana
- José Mariano Reyes Hernández

## Descripción del problema

### Análisis semántico

Esta fase de la construcción del compilador para YAPL se enfocará en la fase de análisis semántico. Esta fase se hará sobre un programa escrito en el lenguaje YAPL. El análisis semántico implementará principalmente un sistema de tipos y otras validaciones semánticas que tendrá que cumplir el programa para considerarse válido.

### Tareas principales:

- Agregar acciones semánticas al analizador sintáctico, de tal forma que se construya un árbol de análisis sintáctico. Durante la construcción de este árbol o en un recorrido posterior, se debe evaluar las reglas semánticas que considere necesarias.
  
- Construir la tabla de símbolos que interactuará con cada una de las fases del compilador. El diseño de dicha tabla deberá de contemplar el manejo de ámbitos, además de almacenar la información que usted considere necesaria. Dicha tabla deberá que ser utilizada en las fases restantes del compilador.

### Reglas semánticas para implementar:

Deberá implementar las reglas semánticas de YAPL que se explican en el documento “Aspectos semánticos YAPL”, el cual se encuentra cargado en Canvas.

### Entregable

- Interfaz de usuario que permita la escritura de programas en YAPL para pruebas de análisis léxico, sintáctico y semántico.
  

