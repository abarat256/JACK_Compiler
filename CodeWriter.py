import re
from SymbolTable import SymbolTable


class CodeWriter:
    CONVERT_KIND = {
        'ARG': 'ARG',
        'STATIC': 'STATIC',
        'VAR': 'LOCAL',
        'FIELD': 'THIS'
    }

    ARITHMETIC = {
        '+': 'ADD',
        '-': 'SUB',
        '=': 'EQ',
        '>': 'GT',
        '<': 'LT',
        '&': 'AND',
        '|': 'OR'
    }

    ARITHMETIC_UNARY = {
        '-': 'NEG',
        '~': 'NOT'
    }

    if_index = -1
    while_index = -1
    
    def __init__(self, tokenizer, output_file):
        self.output = output_file
        self.tokenizer = tokenizer
        self.symbol_table = SymbolTable()
        self.buffer = []
        
    def compile_class(self):
        self.get_token() 
        self.class_name = self.get_token()  
        self.get_token() 
        while self.is_class_var_dec():
            self.compile_classVarDec()  
        while self.is_subroutine_dec():
            self.compile_subroutineDec()  
        self.close()

    def compile_classVarDec(self):
        kind = self.get_token()  
        type = self.get_token()  
        name = self.get_token()  
        self.symbol_table.define(name, type, kind.upper())
        while self.peek() != ';': 
            self.get_token()  
            name = self.get_token()  
            self.symbol_table.define(name, type, kind.upper())
        self.get_token()  
        
    def compile_subroutineDec(self):
        subroutine_kind = self.get_token()  
        self.get_token()  
        subroutine_name = self.get_token()  
        self.symbol_table.start_subroutine()
        if subroutine_kind == 'method':
            self.symbol_table.define('instance', self.class_name, 'ARG')
        self.get_token()  
        self.compile_parameterList()  
        self.get_token() 
        self.get_token()  
        while self.peek() == 'var':
            self.compile_var_dec()  
        function_name = '{}.{}'.format(self.class_name, subroutine_name)
        num_locals = self.symbol_table.var_count('VAR')
        self.write_function(function_name, num_locals)
        if subroutine_kind == 'constructor':
            num_fields = self.symbol_table.var_count('FIELD')
            self.write_push('CONST', num_fields)
            self.write_call('Memory.alloc', 1)
            self.write_pop('POINTER', 0)
        elif subroutine_kind == 'method':
            self.write_push('ARG', 0)
            self.write_pop('POINTER', 0)
        self.compile_statements()  
        self.get_token() 

    
    def write_push(self, segment, index):
        if segment == 'CONST':
            segment = 'constant'
        elif segment == 'ARG':
            segment = 'argument'
        self.output.write('push {} {}\n'.format(segment.lower(), index))


    def write_pop(self, segment, index):
        if segment == 'CONST':
            segment = 'constant'
        elif segment == 'ARG':
            segment = 'argument'
        self.output.write('pop {} {}\n'.format(segment.lower(), index))


    def write_arithmetic(self, command):
        self.output.write(command.lower() + '\n')


    def write_label(self, label):
        self.output.write('label {}'.format(label))


    def write_goto(self, label):
        self.output.write('goto {}'.format(label))


    def write_if(self, label):
        self.output.write('if-goto {}'.format(label))


    def write_call(self, name, nArgs):
        self.output.write('call {} {}\n'.format(name, nArgs))


    def write_function(self, name, nLocals):
        self.output.write('function {} {}\n'.format(name, nLocals))


    def write_return(self):
        self.output.write('return\n')


    def close(self):
        self.output.close()


    def write(self, stuff):
        self.output.write(stuff)

   
    def compile_parameterList(self):
        if ')' != self.peek():
            type = self.get_token()  
            name = self.get_token()  
            self.symbol_table.define(name, type, 'ARG')
        while ')' != self.peek():
            self.get_token() 
            type = self.get_token() 
            name = self.get_token()  
            self.symbol_table.define(name, type, 'ARG')

    
    def compile_var_dec(self):
        self.get_token()  
        type = self.get_token()  
        name = self.get_token()  
        self.symbol_table.define(name, type, 'VAR')
        while self.peek() != ';':  
            self.get_token()  
            name = self.get_token()  
            self.symbol_table.define(name, type, 'VAR')
        self.get_token()  

    
    def compile_statements(self):
        while self.is_statement():
            token = self.get_token()
            if token == 'let':
                self.compile_letStatement()
            elif token == 'if':
                self.compile_ifStatement()
            elif token == 'while':
                self.compile_whileStatement()
            elif token == 'do':
                self.compile_doStatement()
            elif token == 'return':
                self.compile_returnStatement()

   
    def compile_doStatement(self):
        self.compile_subroutine_call()
        self.write_pop('TEMP', 0)
        self.get_token() 
        
    def compile_letStatement(self):
        var_name = self.get_token() 
        var_kind = self.CONVERT_KIND[self.symbol_table.kind_of(var_name)]
        var_index = self.symbol_table.index_of(var_name)
        if self.peek() == '[':  
            self.get_token()  
            self.compile_expression()  
            self.get_token()  
            self.write_push(var_kind, var_index)
            self.write_arithmetic('ADD')
            self.write_pop('TEMP', 0)
            self.get_token() 
            self.compile_expression()  
            self.get_token()  
            self.write_push('TEMP', 0)
            self.write_pop('POINTER', 1)
            self.write_pop('THAT', 0)
        else:  
            self.get_token()  
            self.compile_expression() 
            self.get_token() 
            self.write_pop(var_kind, var_index)

    
    def compile_whileStatement(self):
        self.while_index += 1
        while_index = self.while_index
        self.write_label('WHILE{}\n'.format(while_index))
        self.get_token()  
        self.compile_expression()  
        self.write_arithmetic('NOT')  
        self.get_token()  
        self.get_token()  
        self.write_if('WHILE_END{}\n'.format(while_index))
        self.compile_statements()  
        self.write_goto('WHILE{}\n'.format(while_index))
        self.write_label('WHILE_END{}\n'.format(while_index))
        self.get_token() 

    
    def compile_returnStatement(self):
        if self.peek() != ';':
            self.compile_expression()
        else:
            self.write_push('CONST', 0)
        self.write_return()
        self.get_token()  
        
    def compile_ifStatement(self):
        self.if_index += 1
        if_index = self.if_index
        self.get_token()  
        self.compile_expression()  
        self.get_token() 
        self.get_token() 
        self.write_if('IF_TRUE{}\n'.format(if_index))
        self.write_goto('IF_FALSE{}\n'.format(if_index))
        self.write_label('IF_TRUE{}\n'.format(if_index))
        self.compile_statements()  # statements
        self.write_goto('IF_END{}\n'.format(if_index))
        self.get_token()  # '}'
        self.write_label('IF_FALSE{}\n'.format(if_index))
        if self.peek() == 'else':  
            self.get_token()  
            self.get_token()  
            self.compile_statements() 
            self.get_token()  
        self.write_label('IF_END{}\n'.format(if_index))

    
    def compile_expression(self):
        self.compile_term()  
        while self.is_op():  
            op = self.get_token()
            self.compile_term()  
            if op in self.ARITHMETIC.keys():
                self.write_arithmetic(self.ARITHMETIC[op])
            elif op == '*':
                self.write_call('Math.multiply', 2)
            elif op == '/':
                self.write_call('Math.divide', 2)

    
    def compile_term(self):
        if self.is_unary_op_term():
            unary_op = self.get_token()  # unaryOp
            self.compile_term()  # term
            self.write_arithmetic(self.ARITHMETIC_UNARY[unary_op])
        elif self.peek() == '(':
            self.get_token()  # '('
            self.compile_expression()  # expression
            self.get_token()  # ')'
        elif self.peek_type() == 'INT_CONST':  # integerConstant
            self.write_push('CONST', self.get_token())
        elif self.peek_type() == 'STRING_CONST':  # stringConstant
            self.compile_string()
        elif self.peek_type() == 'KEYWORD':  # keywordConstant
            self.compile_keyword()
        else:  # first is a var or subroutine
            if self.is_array():
                array_var = self.get_token()  # varName
                self.get_token()  # '['
                self.compile_expression()  # expression
                self.get_token()  # ']'
                array_kind = self.symbol_table.kind_of(array_var)
                array_index = self.symbol_table.index_of(array_var)
                self.write_push(self.CONVERT_KIND[array_kind], array_index)
                self.write_arithmetic('ADD')
                self.write_pop('POINTER', 1)
                self.write_push('THAT', 0)
            elif self.is_subroutine_call():
                self.compile_subroutine_call()
            else:
                var = self.get_token()
                var_kind = self.CONVERT_KIND[self.symbol_table.kind_of(var)]
                var_index = self.symbol_table.index_of(var)
                self.write_push(var_kind, var_index)

    
    def compile_expression_list(self):
        number_args = 0
        if self.peek() != ')':
            number_args += 1
            self.compile_expression()
        while self.peek() != ')':
            number_args += 1
            self.get_token()  # ','
            self.compile_expression()
        return number_args

 
    def compile_keyword(self):
        keyword = self.get_token()  # keywordConstant
        if keyword == 'this':
            self.write_push('POINTER', 0)
        else:
            self.write_push('CONST', 0)
            if keyword == 'true':
                self.write_arithmetic('NOT')

   
    def compile_subroutine_call(self):
        identifier = self.get_token()  
        function_name = identifier
        number_args = 0
        if self.peek() == '.':
            self.get_token() 
            subroutine_name = self.get_token()  
            type = self.symbol_table.type_of(identifier)
            if type != 'NONE':  
                instance_kind = self.symbol_table.kind_of(identifier)
                instance_index = self.symbol_table.index_of(identifier)
                self.write_push(self.CONVERT_KIND[instance_kind], instance_index)
                function_name = '{}.{}'.format(type, subroutine_name)
                number_args += 1
            else:  # it's a class
                class_name = identifier
                function_name = '{}.{}'.format(class_name, subroutine_name)
        elif self.peek() == '(':
            subroutine_name = identifier
            function_name = '{}.{}'.format(self.class_name, subroutine_name)
            number_args += 1
            self.write_push('POINTER', 0)
        self.get_token()  # '('
        number_args += self.compile_expression_list()  
        self.get_token()  # ')'
        self.write_call(function_name, number_args)

    def compile_string(self):
        string = self.get_token()  
        self.write_push('CONST', len(string))
        self.write_call('String.new', 1)
        for char in string:
            self.write_push('CONST', ord(char))
            self.write_call('String.appendChar', 2)

    def is_subroutine_call(self):
        token = self.get_token()
        subroutine_call = self.peek() in ['.', '(']
        self.unget_token(token)
        return subroutine_call

    def is_array(self):
        token = self.get_token()
        array = self.peek() == '['
        self.unget_token(token)
        return array

    def is_class_var_dec(self):
        return self.peek() in ['static', 'field']

    def is_subroutine_dec(self):
        return self.peek() in ['constructor', 'function', 'method']

    def is_statement(self):
        return self.peek() in ['let', 'if', 'while', 'do', 'return']

    def is_op(self):
        return self.peek() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']

    def is_unary_op_term(self):
        return self.peek() in ['~', '-']

    def peek(self):
        return self.peek_info()[0]

    def peek_type(self):
        return self.peek_info()[1]

    def peek_info(self):
        token_info = self.get_token_info()
        self.unget_token_info(token_info)
        return token_info

    def get_token(self):
        return self.get_token_info()[0]

    def get_token_info(self):
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return self.get_next_token()

    def unget_token(self, token):
        self.unget_token_info((token, 'UNKNOWN'))

    def unget_token_info(self, token):
        self.buffer.insert(0, token)

    def get_next_token(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() is 'KEYWORD':
                return self.tokenizer.key_word().lower(), self.tokenizer.token_type()
            elif self.tokenizer.token_type() is 'SYMBOL':
                return self.tokenizer.symbol(), self.tokenizer.token_type()
            elif self.tokenizer.token_type() is 'IDENTIFIER':
                return self.tokenizer.identifier(), self.tokenizer.token_type()
            elif self.tokenizer.token_type() is 'INT_CONST':
                return self.tokenizer.int_val(), self.tokenizer.token_type()
            elif self.tokenizer.token_type() is 'STRING_CONST':
                return self.tokenizer.string_val(), self.tokenizer.token_type()