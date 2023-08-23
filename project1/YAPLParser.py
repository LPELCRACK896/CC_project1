# Generated from C:/Users/Jose/Documents/GitHub/Fork/Lab0_Compiladores/YAPL.g4 by ANTLR 4.13.0
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,45,251,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,1,0,5,0,
        28,8,0,10,0,12,0,31,9,0,1,0,1,0,1,1,1,1,1,1,1,1,3,1,39,8,1,1,1,1,
        1,5,1,43,8,1,10,1,12,1,46,9,1,1,1,1,1,1,2,1,2,3,2,52,8,2,1,3,1,3,
        1,3,1,3,1,3,3,3,59,8,3,1,3,1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,4,1,
        4,1,4,5,4,73,8,4,10,4,12,4,76,9,4,1,4,1,4,1,4,1,5,3,5,82,8,5,1,5,
        1,5,5,5,86,8,5,10,5,12,5,89,9,5,1,6,1,6,1,6,1,6,1,7,1,7,1,8,1,8,
        1,8,1,8,3,8,101,8,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,112,
        8,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,5,8,122,8,8,10,8,12,8,125,9,
        8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,135,8,8,1,8,1,8,1,8,1,8,1,
        8,1,8,3,8,143,8,8,5,8,145,8,8,10,8,12,8,148,9,8,1,8,1,8,1,8,1,8,
        1,8,1,8,1,8,1,8,1,8,1,8,1,8,5,8,161,8,8,10,8,12,8,164,9,8,1,8,1,
        8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,3,8,181,8,
        8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,5,8,193,8,8,10,8,12,8,
        196,9,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,1,8,5,8,209,8,8,
        10,8,12,8,212,9,8,1,8,1,8,5,8,216,8,8,10,8,12,8,219,9,8,1,9,1,9,
        1,9,1,9,1,10,1,10,1,10,1,10,1,10,1,10,1,10,3,10,232,8,10,1,11,1,
        11,1,11,1,11,3,11,238,8,11,1,12,1,12,1,12,1,12,1,12,1,12,1,12,1,
        12,1,12,3,12,249,8,12,1,12,0,1,16,13,0,2,4,6,8,10,12,14,16,18,20,
        22,24,0,2,2,0,11,16,39,39,1,0,40,41,281,0,29,1,0,0,0,2,34,1,0,0,
        0,4,51,1,0,0,0,6,53,1,0,0,0,8,62,1,0,0,0,10,81,1,0,0,0,12,90,1,0,
        0,0,14,94,1,0,0,0,16,180,1,0,0,0,18,220,1,0,0,0,20,231,1,0,0,0,22,
        237,1,0,0,0,24,248,1,0,0,0,26,28,3,2,1,0,27,26,1,0,0,0,28,31,1,0,
        0,0,29,27,1,0,0,0,29,30,1,0,0,0,30,32,1,0,0,0,31,29,1,0,0,0,32,33,
        5,0,0,1,33,1,1,0,0,0,34,35,5,1,0,0,35,38,5,45,0,0,36,37,5,2,0,0,
        37,39,5,45,0,0,38,36,1,0,0,0,38,39,1,0,0,0,39,40,1,0,0,0,40,44,5,
        3,0,0,41,43,3,4,2,0,42,41,1,0,0,0,43,46,1,0,0,0,44,42,1,0,0,0,44,
        45,1,0,0,0,45,47,1,0,0,0,46,44,1,0,0,0,47,48,5,4,0,0,48,3,1,0,0,
        0,49,52,3,6,3,0,50,52,3,8,4,0,51,49,1,0,0,0,51,50,1,0,0,0,52,5,1,
        0,0,0,53,54,5,39,0,0,54,55,5,5,0,0,55,58,3,14,7,0,56,57,5,6,0,0,
        57,59,3,16,8,0,58,56,1,0,0,0,58,59,1,0,0,0,59,60,1,0,0,0,60,61,5,
        7,0,0,61,7,1,0,0,0,62,63,5,39,0,0,63,64,5,8,0,0,64,65,3,10,5,0,65,
        66,5,9,0,0,66,67,5,5,0,0,67,68,3,14,7,0,68,74,5,3,0,0,69,70,3,16,
        8,0,70,71,5,7,0,0,71,73,1,0,0,0,72,69,1,0,0,0,73,76,1,0,0,0,74,72,
        1,0,0,0,74,75,1,0,0,0,75,77,1,0,0,0,76,74,1,0,0,0,77,78,3,18,9,0,
        78,79,5,4,0,0,79,9,1,0,0,0,80,82,3,12,6,0,81,80,1,0,0,0,81,82,1,
        0,0,0,82,87,1,0,0,0,83,84,5,10,0,0,84,86,3,12,6,0,85,83,1,0,0,0,
        86,89,1,0,0,0,87,85,1,0,0,0,87,88,1,0,0,0,88,11,1,0,0,0,89,87,1,
        0,0,0,90,91,5,39,0,0,91,92,5,5,0,0,92,93,3,14,7,0,93,13,1,0,0,0,
        94,95,7,0,0,0,95,15,1,0,0,0,96,97,6,8,-1,0,97,100,5,17,0,0,98,101,
        3,16,8,0,99,101,3,22,11,0,100,98,1,0,0,0,100,99,1,0,0,0,101,102,
        1,0,0,0,102,103,5,18,0,0,103,104,3,16,8,0,104,105,5,19,0,0,105,106,
        3,16,8,0,106,107,5,20,0,0,107,181,1,0,0,0,108,111,5,21,0,0,109,112,
        3,16,8,0,110,112,3,22,11,0,111,109,1,0,0,0,111,110,1,0,0,0,112,113,
        1,0,0,0,113,114,5,22,0,0,114,115,3,16,8,0,115,116,5,23,0,0,116,181,
        1,0,0,0,117,118,5,3,0,0,118,123,3,16,8,0,119,120,5,7,0,0,120,122,
        3,16,8,0,121,119,1,0,0,0,122,125,1,0,0,0,123,121,1,0,0,0,123,124,
        1,0,0,0,124,126,1,0,0,0,125,123,1,0,0,0,126,127,5,4,0,0,127,181,
        1,0,0,0,128,129,5,24,0,0,129,130,5,39,0,0,130,131,5,5,0,0,131,134,
        3,14,7,0,132,133,5,6,0,0,133,135,3,16,8,0,134,132,1,0,0,0,134,135,
        1,0,0,0,135,146,1,0,0,0,136,137,5,10,0,0,137,138,5,39,0,0,138,139,
        5,5,0,0,139,142,3,14,7,0,140,141,5,6,0,0,141,143,3,16,8,0,142,140,
        1,0,0,0,142,143,1,0,0,0,143,145,1,0,0,0,144,136,1,0,0,0,145,148,
        1,0,0,0,146,144,1,0,0,0,146,147,1,0,0,0,147,149,1,0,0,0,148,146,
        1,0,0,0,149,150,5,25,0,0,150,151,3,16,8,14,151,181,1,0,0,0,152,153,
        5,39,0,0,153,154,5,6,0,0,154,181,3,16,8,13,155,156,5,39,0,0,156,
        157,5,8,0,0,157,162,3,16,8,0,158,159,5,10,0,0,159,161,3,16,8,0,160,
        158,1,0,0,0,161,164,1,0,0,0,162,160,1,0,0,0,162,163,1,0,0,0,163,
        165,1,0,0,0,164,162,1,0,0,0,165,166,5,9,0,0,166,181,1,0,0,0,167,
        168,5,28,0,0,168,181,3,16,8,9,169,170,5,29,0,0,170,181,5,39,0,0,
        171,181,5,39,0,0,172,181,5,40,0,0,173,181,5,41,0,0,174,181,5,30,
        0,0,175,181,5,31,0,0,176,177,5,8,0,0,177,178,3,16,8,0,178,179,5,
        9,0,0,179,181,1,0,0,0,180,96,1,0,0,0,180,108,1,0,0,0,180,117,1,0,
        0,0,180,128,1,0,0,0,180,152,1,0,0,0,180,155,1,0,0,0,180,167,1,0,
        0,0,180,169,1,0,0,0,180,171,1,0,0,0,180,172,1,0,0,0,180,173,1,0,
        0,0,180,174,1,0,0,0,180,175,1,0,0,0,180,176,1,0,0,0,181,217,1,0,
        0,0,182,183,10,1,0,0,183,184,5,44,0,0,184,216,3,16,8,2,185,186,10,
        12,0,0,186,187,5,26,0,0,187,188,5,39,0,0,188,189,5,8,0,0,189,194,
        3,16,8,0,190,191,5,10,0,0,191,193,3,16,8,0,192,190,1,0,0,0,193,196,
        1,0,0,0,194,192,1,0,0,0,194,195,1,0,0,0,195,197,1,0,0,0,196,194,
        1,0,0,0,197,198,5,9,0,0,198,216,1,0,0,0,199,200,10,11,0,0,200,201,
        5,27,0,0,201,202,3,14,7,0,202,203,5,26,0,0,203,204,5,39,0,0,204,
        205,5,8,0,0,205,210,3,16,8,0,206,207,5,10,0,0,207,209,3,16,8,0,208,
        206,1,0,0,0,209,212,1,0,0,0,210,208,1,0,0,0,210,211,1,0,0,0,211,
        213,1,0,0,0,212,210,1,0,0,0,213,214,5,9,0,0,214,216,1,0,0,0,215,
        182,1,0,0,0,215,185,1,0,0,0,215,199,1,0,0,0,216,219,1,0,0,0,217,
        215,1,0,0,0,217,218,1,0,0,0,218,17,1,0,0,0,219,217,1,0,0,0,220,221,
        5,32,0,0,221,222,3,16,8,0,222,223,5,7,0,0,223,19,1,0,0,0,224,232,
        1,0,0,0,225,232,5,33,0,0,226,232,5,34,0,0,227,232,5,35,0,0,228,232,
        5,36,0,0,229,232,5,37,0,0,230,232,5,38,0,0,231,224,1,0,0,0,231,225,
        1,0,0,0,231,226,1,0,0,0,231,227,1,0,0,0,231,228,1,0,0,0,231,229,
        1,0,0,0,231,230,1,0,0,0,232,21,1,0,0,0,233,238,1,0,0,0,234,238,5,
        30,0,0,235,238,5,31,0,0,236,238,3,24,12,0,237,233,1,0,0,0,237,234,
        1,0,0,0,237,235,1,0,0,0,237,236,1,0,0,0,238,23,1,0,0,0,239,249,1,
        0,0,0,240,241,5,39,0,0,241,242,3,20,10,0,242,243,7,1,0,0,243,249,
        1,0,0,0,244,245,5,39,0,0,245,246,3,20,10,0,246,247,5,39,0,0,247,
        249,1,0,0,0,248,239,1,0,0,0,248,240,1,0,0,0,248,244,1,0,0,0,249,
        25,1,0,0,0,23,29,38,44,51,58,74,81,87,100,111,123,134,142,146,162,
        180,194,210,215,217,231,237,248
    ]

class YAPLParser ( Parser ):

    grammarFileName = "YAPL.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'class'", "'inherits'", "'{'", "'}'", 
                     "':'", "'<-'", "';'", "'('", "')'", "','", "'SELF_TYPE'", 
                     "'Int'", "'String'", "'Bool'", "'IO'", "'Object'", 
                     "'if'", "'then'", "'else'", "'fi'", "'while'", "'loop'", 
                     "'pool'", "'let'", "'in'", "'.'", "'@'", "'isvoid'", 
                     "'new'", "'true'", "'false'", "'return'", "'<'", "'>'", 
                     "'<='", "'>='", "'=='", "'!='" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "ID", "INT", 
                      "STRING", "WS", "COMMENT", "OP", "CLASS_ID" ]

    RULE_program = 0
    RULE_classDef = 1
    RULE_feature = 2
    RULE_attr = 3
    RULE_method = 4
    RULE_formals = 5
    RULE_formal = 6
    RULE_type = 7
    RULE_expr = 8
    RULE_func_return = 9
    RULE_comparation_operators = 10
    RULE_bool_value = 11
    RULE_comparation = 12

    ruleNames =  [ "program", "classDef", "feature", "attr", "method", "formals", 
                   "formal", "type", "expr", "func_return", "comparation_operators", 
                   "bool_value", "comparation" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    ID=39
    INT=40
    STRING=41
    WS=42
    COMMENT=43
    OP=44
    CLASS_ID=45

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.0")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(YAPLParser.EOF, 0)

        def classDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.ClassDefContext)
            else:
                return self.getTypedRuleContext(YAPLParser.ClassDefContext,i)


        def getRuleIndex(self):
            return YAPLParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = YAPLParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 26
                self.classDef()
                self.state = 31
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 32
            self.match(YAPLParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassDefContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def CLASS_ID(self, i:int=None):
            if i is None:
                return self.getTokens(YAPLParser.CLASS_ID)
            else:
                return self.getToken(YAPLParser.CLASS_ID, i)

        def feature(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.FeatureContext)
            else:
                return self.getTypedRuleContext(YAPLParser.FeatureContext,i)


        def getRuleIndex(self):
            return YAPLParser.RULE_classDef

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassDef" ):
                listener.enterClassDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassDef" ):
                listener.exitClassDef(self)




    def classDef(self):

        localctx = YAPLParser.ClassDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_classDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 34
            self.match(YAPLParser.T__0)
            self.state = 35
            self.match(YAPLParser.CLASS_ID)
            self.state = 38
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==2:
                self.state = 36
                self.match(YAPLParser.T__1)
                self.state = 37
                self.match(YAPLParser.CLASS_ID)


            self.state = 40
            self.match(YAPLParser.T__2)
            self.state = 44
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==39:
                self.state = 41
                self.feature()
                self.state = 46
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 47
            self.match(YAPLParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FeatureContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def attr(self):
            return self.getTypedRuleContext(YAPLParser.AttrContext,0)


        def method(self):
            return self.getTypedRuleContext(YAPLParser.MethodContext,0)


        def getRuleIndex(self):
            return YAPLParser.RULE_feature

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFeature" ):
                listener.enterFeature(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFeature" ):
                listener.exitFeature(self)




    def feature(self):

        localctx = YAPLParser.FeatureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_feature)
        try:
            self.state = 51
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 49
                self.attr()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 50
                self.method()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AttrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(YAPLParser.ID, 0)

        def type_(self):
            return self.getTypedRuleContext(YAPLParser.TypeContext,0)


        def expr(self):
            return self.getTypedRuleContext(YAPLParser.ExprContext,0)


        def getRuleIndex(self):
            return YAPLParser.RULE_attr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAttr" ):
                listener.enterAttr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAttr" ):
                listener.exitAttr(self)




    def attr(self):

        localctx = YAPLParser.AttrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_attr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 53
            self.match(YAPLParser.ID)
            self.state = 54
            self.match(YAPLParser.T__4)
            self.state = 55
            self.type_()
            self.state = 58
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==6:
                self.state = 56
                self.match(YAPLParser.T__5)
                self.state = 57
                self.expr(0)


            self.state = 60
            self.match(YAPLParser.T__6)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MethodContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(YAPLParser.ID, 0)

        def formals(self):
            return self.getTypedRuleContext(YAPLParser.FormalsContext,0)


        def type_(self):
            return self.getTypedRuleContext(YAPLParser.TypeContext,0)


        def func_return(self):
            return self.getTypedRuleContext(YAPLParser.Func_returnContext,0)


        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.ExprContext)
            else:
                return self.getTypedRuleContext(YAPLParser.ExprContext,i)


        def getRuleIndex(self):
            return YAPLParser.RULE_method

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMethod" ):
                listener.enterMethod(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMethod" ):
                listener.exitMethod(self)




    def method(self):

        localctx = YAPLParser.MethodContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_method)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self.match(YAPLParser.ID)
            self.state = 63
            self.match(YAPLParser.T__7)
            self.state = 64
            self.formals()
            self.state = 65
            self.match(YAPLParser.T__8)
            self.state = 66
            self.match(YAPLParser.T__4)
            self.state = 67
            self.type_()
            self.state = 68
            self.match(YAPLParser.T__2)
            self.state = 74
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 3852336234760) != 0):
                self.state = 69
                self.expr(0)
                self.state = 70
                self.match(YAPLParser.T__6)
                self.state = 76
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 77
            self.func_return()
            self.state = 78
            self.match(YAPLParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FormalsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def formal(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.FormalContext)
            else:
                return self.getTypedRuleContext(YAPLParser.FormalContext,i)


        def getRuleIndex(self):
            return YAPLParser.RULE_formals

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFormals" ):
                listener.enterFormals(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFormals" ):
                listener.exitFormals(self)




    def formals(self):

        localctx = YAPLParser.FormalsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_formals)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==39:
                self.state = 80
                self.formal()


            self.state = 87
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==10:
                self.state = 83
                self.match(YAPLParser.T__9)
                self.state = 84
                self.formal()
                self.state = 89
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FormalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(YAPLParser.ID, 0)

        def type_(self):
            return self.getTypedRuleContext(YAPLParser.TypeContext,0)


        def getRuleIndex(self):
            return YAPLParser.RULE_formal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFormal" ):
                listener.enterFormal(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFormal" ):
                listener.exitFormal(self)




    def formal(self):

        localctx = YAPLParser.FormalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_formal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 90
            self.match(YAPLParser.ID)
            self.state = 91
            self.match(YAPLParser.T__4)
            self.state = 92
            self.type_()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(YAPLParser.ID, 0)

        def getRuleIndex(self):
            return YAPLParser.RULE_type

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterType" ):
                listener.enterType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitType" ):
                listener.exitType(self)




    def type_(self):

        localctx = YAPLParser.TypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 549755942912) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.op = None # Token

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.ExprContext)
            else:
                return self.getTypedRuleContext(YAPLParser.ExprContext,i)


        def bool_value(self):
            return self.getTypedRuleContext(YAPLParser.Bool_valueContext,0)


        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(YAPLParser.ID)
            else:
                return self.getToken(YAPLParser.ID, i)

        def type_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(YAPLParser.TypeContext)
            else:
                return self.getTypedRuleContext(YAPLParser.TypeContext,i)


        def INT(self):
            return self.getToken(YAPLParser.INT, 0)

        def STRING(self):
            return self.getToken(YAPLParser.STRING, 0)

        def OP(self):
            return self.getToken(YAPLParser.OP, 0)

        def getRuleIndex(self):
            return YAPLParser.RULE_expr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr" ):
                listener.enterExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr" ):
                listener.exitExpr(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = YAPLParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 16
        self.enterRecursionRule(localctx, 16, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
            if la_ == 1:
                self.state = 97
                self.match(YAPLParser.T__16)
                self.state = 100
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,8,self._ctx)
                if la_ == 1:
                    self.state = 98
                    self.expr(0)
                    pass

                elif la_ == 2:
                    self.state = 99
                    self.bool_value()
                    pass


                self.state = 102
                self.match(YAPLParser.T__17)
                self.state = 103
                self.expr(0)
                self.state = 104
                self.match(YAPLParser.T__18)
                self.state = 105
                self.expr(0)
                self.state = 106
                self.match(YAPLParser.T__19)
                pass

            elif la_ == 2:
                self.state = 108
                self.match(YAPLParser.T__20)
                self.state = 111
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
                if la_ == 1:
                    self.state = 109
                    self.expr(0)
                    pass

                elif la_ == 2:
                    self.state = 110
                    self.bool_value()
                    pass


                self.state = 113
                self.match(YAPLParser.T__21)
                self.state = 114
                self.expr(0)
                self.state = 115
                self.match(YAPLParser.T__22)
                pass

            elif la_ == 3:
                self.state = 117
                self.match(YAPLParser.T__2)
                self.state = 118
                self.expr(0)
                self.state = 123
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==7:
                    self.state = 119
                    self.match(YAPLParser.T__6)
                    self.state = 120
                    self.expr(0)
                    self.state = 125
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 126
                self.match(YAPLParser.T__3)
                pass

            elif la_ == 4:
                self.state = 128
                self.match(YAPLParser.T__23)
                self.state = 129
                self.match(YAPLParser.ID)
                self.state = 130
                self.match(YAPLParser.T__4)
                self.state = 131
                self.type_()
                self.state = 134
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==6:
                    self.state = 132
                    self.match(YAPLParser.T__5)
                    self.state = 133
                    self.expr(0)


                self.state = 146
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==10:
                    self.state = 136
                    self.match(YAPLParser.T__9)
                    self.state = 137
                    self.match(YAPLParser.ID)
                    self.state = 138
                    self.match(YAPLParser.T__4)
                    self.state = 139
                    self.type_()
                    self.state = 142
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if _la==6:
                        self.state = 140
                        self.match(YAPLParser.T__5)
                        self.state = 141
                        self.expr(0)


                    self.state = 148
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 149
                self.match(YAPLParser.T__24)
                self.state = 150
                self.expr(14)
                pass

            elif la_ == 5:
                self.state = 152
                self.match(YAPLParser.ID)
                self.state = 153
                self.match(YAPLParser.T__5)
                self.state = 154
                self.expr(13)
                pass

            elif la_ == 6:
                self.state = 155
                self.match(YAPLParser.ID)
                self.state = 156
                self.match(YAPLParser.T__7)
                self.state = 157
                self.expr(0)
                self.state = 162
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==10:
                    self.state = 158
                    self.match(YAPLParser.T__9)
                    self.state = 159
                    self.expr(0)
                    self.state = 164
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 165
                self.match(YAPLParser.T__8)
                pass

            elif la_ == 7:
                self.state = 167
                self.match(YAPLParser.T__27)
                self.state = 168
                self.expr(9)
                pass

            elif la_ == 8:
                self.state = 169
                self.match(YAPLParser.T__28)
                self.state = 170
                self.match(YAPLParser.ID)
                pass

            elif la_ == 9:
                self.state = 171
                self.match(YAPLParser.ID)
                pass

            elif la_ == 10:
                self.state = 172
                self.match(YAPLParser.INT)
                pass

            elif la_ == 11:
                self.state = 173
                self.match(YAPLParser.STRING)
                pass

            elif la_ == 12:
                self.state = 174
                self.match(YAPLParser.T__29)
                pass

            elif la_ == 13:
                self.state = 175
                self.match(YAPLParser.T__30)
                pass

            elif la_ == 14:
                self.state = 176
                self.match(YAPLParser.T__7)
                self.state = 177
                self.expr(0)
                self.state = 178
                self.match(YAPLParser.T__8)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 217
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,19,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 215
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,18,self._ctx)
                    if la_ == 1:
                        localctx = YAPLParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 182
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 183
                        localctx.op = self.match(YAPLParser.OP)
                        self.state = 184
                        self.expr(2)
                        pass

                    elif la_ == 2:
                        localctx = YAPLParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 185
                        if not self.precpred(self._ctx, 12):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 12)")
                        self.state = 186
                        self.match(YAPLParser.T__25)
                        self.state = 187
                        self.match(YAPLParser.ID)
                        self.state = 188
                        self.match(YAPLParser.T__7)
                        self.state = 189
                        self.expr(0)
                        self.state = 194
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        while _la==10:
                            self.state = 190
                            self.match(YAPLParser.T__9)
                            self.state = 191
                            self.expr(0)
                            self.state = 196
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)

                        self.state = 197
                        self.match(YAPLParser.T__8)
                        pass

                    elif la_ == 3:
                        localctx = YAPLParser.ExprContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 199
                        if not self.precpred(self._ctx, 11):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 11)")
                        self.state = 200
                        self.match(YAPLParser.T__26)
                        self.state = 201
                        self.type_()
                        self.state = 202
                        self.match(YAPLParser.T__25)
                        self.state = 203
                        self.match(YAPLParser.ID)
                        self.state = 204
                        self.match(YAPLParser.T__7)
                        self.state = 205
                        self.expr(0)
                        self.state = 210
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        while _la==10:
                            self.state = 206
                            self.match(YAPLParser.T__9)
                            self.state = 207
                            self.expr(0)
                            self.state = 212
                            self._errHandler.sync(self)
                            _la = self._input.LA(1)

                        self.state = 213
                        self.match(YAPLParser.T__8)
                        pass

             
                self.state = 219
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,19,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class Func_returnContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self):
            return self.getTypedRuleContext(YAPLParser.ExprContext,0)


        def getRuleIndex(self):
            return YAPLParser.RULE_func_return

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunc_return" ):
                listener.enterFunc_return(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunc_return" ):
                listener.exitFunc_return(self)




    def func_return(self):

        localctx = YAPLParser.Func_returnContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_func_return)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self.match(YAPLParser.T__31)
            self.state = 221
            self.expr(0)
            self.state = 222
            self.match(YAPLParser.T__6)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Comparation_operatorsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return YAPLParser.RULE_comparation_operators

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparation_operators" ):
                listener.enterComparation_operators(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparation_operators" ):
                listener.exitComparation_operators(self)




    def comparation_operators(self):

        localctx = YAPLParser.Comparation_operatorsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_comparation_operators)
        try:
            self.state = 231
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [39, 40, 41]:
                self.enterOuterAlt(localctx, 1)

                pass
            elif token in [33]:
                self.enterOuterAlt(localctx, 2)
                self.state = 225
                self.match(YAPLParser.T__32)
                pass
            elif token in [34]:
                self.enterOuterAlt(localctx, 3)
                self.state = 226
                self.match(YAPLParser.T__33)
                pass
            elif token in [35]:
                self.enterOuterAlt(localctx, 4)
                self.state = 227
                self.match(YAPLParser.T__34)
                pass
            elif token in [36]:
                self.enterOuterAlt(localctx, 5)
                self.state = 228
                self.match(YAPLParser.T__35)
                pass
            elif token in [37]:
                self.enterOuterAlt(localctx, 6)
                self.state = 229
                self.match(YAPLParser.T__36)
                pass
            elif token in [38]:
                self.enterOuterAlt(localctx, 7)
                self.state = 230
                self.match(YAPLParser.T__37)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Bool_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def comparation(self):
            return self.getTypedRuleContext(YAPLParser.ComparationContext,0)


        def getRuleIndex(self):
            return YAPLParser.RULE_bool_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBool_value" ):
                listener.enterBool_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBool_value" ):
                listener.exitBool_value(self)




    def bool_value(self):

        localctx = YAPLParser.Bool_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_bool_value)
        try:
            self.state = 237
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,21,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 234
                self.match(YAPLParser.T__29)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 235
                self.match(YAPLParser.T__30)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 236
                self.comparation()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ComparationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self, i:int=None):
            if i is None:
                return self.getTokens(YAPLParser.ID)
            else:
                return self.getToken(YAPLParser.ID, i)

        def comparation_operators(self):
            return self.getTypedRuleContext(YAPLParser.Comparation_operatorsContext,0)


        def INT(self):
            return self.getToken(YAPLParser.INT, 0)

        def STRING(self):
            return self.getToken(YAPLParser.STRING, 0)

        def getRuleIndex(self):
            return YAPLParser.RULE_comparation

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparation" ):
                listener.enterComparation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparation" ):
                listener.exitComparation(self)




    def comparation(self):

        localctx = YAPLParser.ComparationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_comparation)
        self._la = 0 # Token type
        try:
            self.state = 248
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 240
                self.match(YAPLParser.ID)
                self.state = 241
                self.comparation_operators()
                self.state = 242
                _la = self._input.LA(1)
                if not(_la==40 or _la==41):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 244
                self.match(YAPLParser.ID)
                self.state = 245
                self.comparation_operators()
                self.state = 246
                self.match(YAPLParser.ID)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[8] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 1)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 12)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 11)
         




