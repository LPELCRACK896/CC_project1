# Generated from YAPL.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .YAPLParser import YAPLParser
else:
    from YAPLParser import YAPLParser

# This class defines a complete listener for a parse tree produced by YAPLParser.
class YAPLListener(ParseTreeListener):

    # Enter a parse tree produced by YAPLParser#program.
    def enterProgram(self, ctx:YAPLParser.ProgramContext):
        pass

    # Exit a parse tree produced by YAPLParser#program.
    def exitProgram(self, ctx:YAPLParser.ProgramContext):
        pass


    # Enter a parse tree produced by YAPLParser#classDef.
    def enterClassDef(self, ctx:YAPLParser.ClassDefContext):
        pass

    # Exit a parse tree produced by YAPLParser#classDef.
    def exitClassDef(self, ctx:YAPLParser.ClassDefContext):
        pass


    # Enter a parse tree produced by YAPLParser#feature.
    def enterFeature(self, ctx:YAPLParser.FeatureContext):
        pass

    # Exit a parse tree produced by YAPLParser#feature.
    def exitFeature(self, ctx:YAPLParser.FeatureContext):
        pass


    # Enter a parse tree produced by YAPLParser#attr.
    def enterAttr(self, ctx:YAPLParser.AttrContext):
        pass

    # Exit a parse tree produced by YAPLParser#attr.
    def exitAttr(self, ctx:YAPLParser.AttrContext):
        pass


    # Enter a parse tree produced by YAPLParser#method.
    def enterMethod(self, ctx:YAPLParser.MethodContext):
        pass

    # Exit a parse tree produced by YAPLParser#method.
    def exitMethod(self, ctx:YAPLParser.MethodContext):
        pass


    # Enter a parse tree produced by YAPLParser#formals.
    def enterFormals(self, ctx:YAPLParser.FormalsContext):
        pass

    # Exit a parse tree produced by YAPLParser#formals.
    def exitFormals(self, ctx:YAPLParser.FormalsContext):
        pass


    # Enter a parse tree produced by YAPLParser#formal.
    def enterFormal(self, ctx:YAPLParser.FormalContext):
        pass

    # Exit a parse tree produced by YAPLParser#formal.
    def exitFormal(self, ctx:YAPLParser.FormalContext):
        pass


    # Enter a parse tree produced by YAPLParser#type.
    def enterType(self, ctx:YAPLParser.TypeContext):
        pass

    # Exit a parse tree produced by YAPLParser#type.
    def exitType(self, ctx:YAPLParser.TypeContext):
        pass


    # Enter a parse tree produced by YAPLParser#expr.
    def enterExpr(self, ctx:YAPLParser.ExprContext):
        pass

    # Exit a parse tree produced by YAPLParser#expr.
    def exitExpr(self, ctx:YAPLParser.ExprContext):
        pass


    # Enter a parse tree produced by YAPLParser#func_return.
    def enterFunc_return(self, ctx:YAPLParser.Func_returnContext):
        pass

    # Exit a parse tree produced by YAPLParser#func_return.
    def exitFunc_return(self, ctx:YAPLParser.Func_returnContext):
        pass


    # Enter a parse tree produced by YAPLParser#comparation_operators.
    def enterComparation_operators(self, ctx:YAPLParser.Comparation_operatorsContext):
        pass

    # Exit a parse tree produced by YAPLParser#comparation_operators.
    def exitComparation_operators(self, ctx:YAPLParser.Comparation_operatorsContext):
        pass


    # Enter a parse tree produced by YAPLParser#bool_value.
    def enterBool_value(self, ctx:YAPLParser.Bool_valueContext):
        pass

    # Exit a parse tree produced by YAPLParser#bool_value.
    def exitBool_value(self, ctx:YAPLParser.Bool_valueContext):
        pass


    # Enter a parse tree produced by YAPLParser#comparation.
    def enterComparation(self, ctx:YAPLParser.ComparationContext):
        pass

    # Exit a parse tree produced by YAPLParser#comparation.
    def exitComparation(self, ctx:YAPLParser.ComparationContext):
        pass



del YAPLParser