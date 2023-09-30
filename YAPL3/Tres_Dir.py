from antlr4 import ParseTreeVisitor
from YAPL3Parser import YAPL3Parser
from YAPL3Listener import YAPL3Listener


class Cuadrupla:
    def __init__(self, operador, arg1=None, arg2=None, destino=None):
        self.operador = operador
        self.arg1 = arg1
        self.arg2 = arg2
        self.destino = destino

    def __str__(self):
        return f"{self.operador} {self.arg1} {self.arg2} -> {self.destino}"


class IntermediateCode(YAPL3Listener):
    def __init__(self):
        self.temp_counter = 0
        self.label_counter = 0
        self.cuadruplos = []
        self.current_scope = "global"
        self.scopes = {"global": {}}

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def enter_scope(self, scope_name):
        self.current_scope = scope_name
        self.scopes[scope_name] = {}

    def exit_scope(self):
        self.current_scope = "global"

    def enterProgram(self, ctx: YAPL3Parser.ProgramContext):
        # Puedes iniciar la generación de código intermedio aquí si es necesario
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterClassDef(self, ctx: YAPL3Parser.ClassDefContext):
        # Procesa la definición de una clase si es necesario
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterFeature(self, ctx: YAPL3Parser.FeatureContext):
        # Procesa una característica (atributo o método) de una clase
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterAttr(self, ctx: YAPL3Parser.AttrContext):
        # Procesa una declaración de atributo
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterMethod(self, ctx: YAPL3Parser.MethodContext):
        # Procesa una definición de método
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    # Implementa las reglas de generación de código intermedio para las expresiones
    def enterExpr(self, ctx: YAPL3Parser.ExprContext):
        if ctx.ID():
            # Procesa una expresión que es una variable
            variable_name = ctx.ID().getText()
            # Genera una cuádrupla para cargar el valor de la variable en un temporal
            temp = self.new_temp()
            self.cuadruplos.append(
                Cuadrupla("load", variable_name, None, temp))
        elif ctx.INT():
            # Procesa una expresión que es un entero
            value = int(ctx.INT().getText())
            # Genera una cuádrupla para cargar el valor del entero en un temporal
            temp = self.new_temp()
            self.cuadruplos.append(Cuadrupla("load", value, None, temp))
        elif ctx.STRING():
            # Procesa una expresión que es una cadena
            value = ctx.STRING().getText()
            # Genera una cuádrupla para cargar el valor de la cadena en un temporal
            temp = self.new_temp()
            self.cuadruplos.append(Cuadrupla("load", value, None, temp))
        elif ctx.op:
            # Procesa una expresión que involucra un operador (por ejemplo, +, -, *, /)
            left_temp = self.visit(ctx.expr(0))
            right_temp = self.visit(ctx.expr(1))
            # Genera una cuádrupla para la operación binaria
            temp = self.new_temp()
            self.cuadruplos.append(
                Cuadrupla(ctx.op.text, left_temp, right_temp, temp))
        elif ctx.bool_value:
            # Procesa una expresión booleana
            if ctx.bool_value.RW_TRUE():
                value = True
            else:
                value = False
            # Genera una cuádrupla para cargar el valor booleano en un temporal
            temp = self.new_temp()
            self.cuadruplos.append(Cuadrupla("load", value, None, temp))
        elif ctx.RW_NOT():
            # Procesa una expresión con el operador 'not'
            operand_temp = self.visit(ctx.expr(0))
            # Genera una cuádrupla para la operación 'not'
            temp = self.new_temp()
            self.cuadruplos.append(Cuadrupla("not", operand_temp, None, temp))
        elif ctx.RW_ISVOID():
            # Procesa una expresión con el operador 'isvoid'
            operand_temp = self.visit(ctx.expr(0))
            # Genera una cuádrupla para la operación 'isvoid'
            temp = self.new_temp()
            self.cuadruplos.append(
                Cuadrupla("isvoid", operand_temp, None, temp))
        elif ctx.RW_NEW():
            # Procesa una expresión con el operador 'new'
            class_name = ctx.type().getText()  # Puede ser CLASS_ID o 'SELF_TYPE'
            # Genera una cuádrupla para la operación 'new'
            temp = self.new_temp()
            self.cuadruplos.append(Cuadrupla("new", class_name, None, temp))
        elif ctx.expr(0).ID() and ctx.RW_ASSIGN():
            # Procesa una asignación (por ejemplo, x <- expr)
            variable_name = ctx.expr(0).ID().getText()
            expr_temp = self.visit(ctx.expr(1))
            # Genera una cuádrupla para la asignación
            self.cuadruplos.append(
                Cuadrupla("assign", expr_temp, None, variable_name))
        elif ctx.expr(0).RW_IF():
            # Procesa una expresión condicional (if-then-else-fi)
            bool_temp = self.visit(ctx.expr(0).bool_value())
            then_expr_temp = self.visit(ctx.expr(1))
            else_expr_temp = self.visit(ctx.expr(2))
            # Genera cuádruplas para la expresión condicional
            label_if = self.new_label()
            label_else = self.new_label()
            label_end = self.new_label()
            self.cuadruplos.append(
                Cuadrupla("brfalse", bool_temp, None, label_else))
            # Asigna el valor de 'then' a la variable
            self.cuadruplos.append(
                Cuadrupla("assign", then_expr_temp, None, variable_name))
            self.cuadruplos.append(Cuadrupla("jump", None, None, label_end))
            self.cuadruplos.append(Cuadrupla("label", None, None, label_else))
            # Asigna el valor de 'else' a la variable
            self.cuadruplos.append(
                Cuadrupla("assign", else_expr_temp, None, variable_name))
            self.cuadruplos.append(Cuadrupla("label", None, None, label_end))

    def enterFunc_return(self, ctx: YAPL3Parser.Func_returnContext):
        # Procesa un valor de retorno de una función
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterComparation_operators(self, ctx: YAPL3Parser.Comparation_operatorsContext):
        # Procesa operadores de comparación si es necesario
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterBool_value(self, ctx: YAPL3Parser.Bool_valueContext):
        # Procesa valores booleanos si es necesario
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def enterComparation(self, ctx: YAPL3Parser.ComparationContext):
        # Procesa comparaciones si es necesario
        self.cuadruplos.append(
            Cuadrupla("", "", "", ctx.OBJECT_ID().getText()))

    def get_codigo_intermedio(self):
        return "\n".join(str(cuad) for cuad in self.cuadruplos)
