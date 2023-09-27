from anytree.exporter import UniqueDotExporter, DotExporter
from CustomErrorListener import CustomErrorListener
from antlr4 import InputStream, CommonTokenStream
from antlr4.tree.Tree import TerminalNode, ErrorNode
from anytree import Node, RenderTree
from YAPL3Parser import YAPL3Parser
from YAPL3Lexer import YAPL3Lexer
from typing import AnyStr
import os


class SyntaxTree:
    """
    Contains abstractions of input YAPL as Noted AST and the AST that generates antlr4 (through YAPL3Parser and YAPL3Lexer).
    """

    def __init__(self, input_data: AnyStr):
        """
        param input_data: The input YAPL code, usually uses the output from reading a file using file.read()
        """

        self.input_data = input_data

        # Fundamental objects
        self.lexer: YAPL3Lexer
        self.parser: YAPL3Parser
        self.stream: CommonTokenStream
        self.error_listener: CustomErrorListener
        self.__pre_run()  # Initializes attributes "lexer", "parser" and "stream"

        # Run syntax analysis
        self.tree: YAPL3Parser.ProgramContext
        self.syntax_errors: list = []
        self.__run_parser_lexer()

        # Runs anytree for output representation
        self.root_at: Node
        self.build_anytree()
        self.render_tree(output_name="visual_tree", show=False)

    def __pre_run(self):
        """
        Initializes fundamentals elements to analyze syntactically and lexically the input code through the objects
        generated using antlr4 (YAPL3Parser and YAPL3Lexer).
        - self.lexer
        - self.parser
        - self.stream
        - self.error_listener
        :return: void
        """

        input_stream = InputStream(self.input_data)

        error_listener = CustomErrorListener()

        lexer = YAPL3Lexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        stream = CommonTokenStream(lexer)

        parser = YAPL3Parser(stream)

        parser._errHandler.beginErrorCondition(parser)

        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        # Finally set as attributes
        self.lexer = lexer
        self.parser = parser
        self.stream = stream
        self.error_listener = error_listener

    def __run_parser_lexer(self):
        """
        Parses program and stores tree, saves syntax errors.

        Initializes:
        - self.tree
        - self.syntax_errors
        :return: void
        """
        tree = self.parser.program()
        syntax_errors = self.error_listener.get_errors()

        self.tree = tree
        self.syntax_errors = syntax_errors

    def __build_anytree(self, node, antlr_node):
        """
        Private build anytree with recursive calls construction tree.
        Called by build_anytree()

        :param node: Terminal or No Terminal Node that contains syntax tree
        :param antlr_node: Node but build by antlr
        :return: void
        """
        if isinstance(antlr_node, ErrorNode):
            return

        elif isinstance(antlr_node, TerminalNode):
            value = antlr_node.getText()
            # Replace double quotes with single quotes
            value = value.replace('"', "'")
            Node(value, node, start_line=antlr_node.symbol.line,
                 end_line=antlr_node.symbol.line)
        else:
            rule_name = self.parser.ruleNames[antlr_node.getRuleIndex()]

            child_node = Node(
                rule_name, node, start_line=antlr_node.start.line, end_line=antlr_node.stop.line)
            for child in antlr_node.getChildren():
                self.__build_anytree(child_node, child)

    def build_anytree(self):
        """
        Builds anytree used to build console tree.
        Currently also used to build the SymbolTable.
        :return: void
        """
        root_at = Node(name=self.parser.ruleNames[self.tree.getRuleIndex()], start_line=0, end_line=-1)
        self.__build_anytree(root_at, self.tree)
        self.root_at = root_at

    def explore_node_and_children(self, node, level=0):
        """
        Prints a node and its children in a readable format.

        :param node: The starting node.
        :param level: The level of indentation for printing.
        :return: void
        """
        indent = '    ' * level  # four spaces per level
        print(f"{indent}Node: {node.name}, Start Line: {node.start_line}, End Line: {node.end_line}")

        # Check if the node has children and recurse if needed.
        if node.children:
            for child in node.children:
                self.explore_node_and_children(child, level + 1)

    def containsEOF(self):

        queue = [self.root_at]

        empty_que = False
        found_eof = False
        explored_nodes = 0
        while not (empty_que or found_eof):
            if len(queue) < 1:
                empty_que = True
            else:
                current_node = queue.pop(0)
                explored_nodes += 1
                if current_node.name == "<EOF>":
                    found_eof = True
                else:
                    queue.extend(current_node.children)
        return found_eof


    """
    Auxiliar methods
    """
    def has_errors(self) -> bool:
        """
        Checks if syntax errors buffer contains something.

        :return: Boolean value indicating if there is any error.
        """
        return True if len(self.syntax_errors) else False

    """
     Output resources
    """

    def print_errors(self):
        """
        Print errors one by one
        :return: void
        """
        for error in self.syntax_errors:
            print(error)

    def render_tree(self, output_name: str, show: bool = False):
        """
        Creates an image (png) of the syntax tree
        :param output_name: filename to save the render of tree
        :param show: to either show a window with the rendered tree
        :return: void
        """
        dot_exporter = UniqueDotExporter(self.root_at)
        dot_exporter.to_picture(f"{output_name}.png")
        if show:
            os.system(f"start {output_name}.png")

    def print_tree(self):
        for pre, fill, node in RenderTree(self.root_at):
            print(f'{pre}{node.name}')