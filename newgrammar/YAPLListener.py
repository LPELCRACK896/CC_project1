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


    # Enter a parse tree produced by YAPLParser#statement.
    def enterStatement(self, ctx:YAPLParser.StatementContext):
        pass

    # Exit a parse tree produced by YAPLParser#statement.
    def exitStatement(self, ctx:YAPLParser.StatementContext):
        pass


    # Enter a parse tree produced by YAPLParser#expressionStatement.
    def enterExpressionStatement(self, ctx:YAPLParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by YAPLParser#expressionStatement.
    def exitExpressionStatement(self, ctx:YAPLParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by YAPLParser#returnStatement.
    def enterReturnStatement(self, ctx:YAPLParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by YAPLParser#returnStatement.
    def exitReturnStatement(self, ctx:YAPLParser.ReturnStatementContext):
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


    # Enter a parse tree produced by YAPLParser#expression.
    def enterExpression(self, ctx:YAPLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by YAPLParser#expression.
    def exitExpression(self, ctx:YAPLParser.ExpressionContext):
        pass



del YAPLParser