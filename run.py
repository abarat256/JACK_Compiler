from Tokenizer import Tokenizer
from CodeWriter import CodeWriter
import os
import sys 

class run:

    def jack_compiler():
        path = run.get_command_line_argument(1)
        if os.path.isdir(path):
            fileList = run.check_file_dir(path, 'jack')
            while run.has_more_files(fileList):
                filename = run.next_file(fileList)
                run.compile_jack(filename)
        elif os.path.isfile(path):
            run.compile_jack(path)
        else:
            print('{} is not a file or dir'.format(path))
            sys.exit()

    
    def compile_jack(jack_file_name):
        token_file_name = jack_file_name.replace('.jack', 'T.xml')
        token_file = open(token_file_name, 'w')
        jack_file = open(jack_file_name, 'r')
        tokenizer = Tokenizer(jack_file, token_file)
        vm_file = open(jack_file_name.replace('.jack', '') + '.vm', 'w')
        code_writer = CodeWriter(tokenizer, vm_file)
        code_writer.compile_class()
        
    
    def get_command_line_argument(num):
        arg = None
        if num < len(sys.argv):
            arg = sys.argv[num]
        return arg
        
    def check_file_dir(filename, ext):
        target_ext = "." + ext
        (fname, ext) = ("test", "")  
        if filename:
            (fname, ext) = os.path.splitext(filename)

        type_file = False
        type_dir = False
        if ext:
            if ext == target_ext:
                type_file = True
        else:
            type_dir = True

        fileList = []
        dirList = []

        # File is provided
        if type_file:
            if os.path.isfile(filename):
                dirList = [filename]

        # Directory is provided
        if type_dir:
            if os.path.isdir(fname):
                dirList = os.listdir(fname)
                
        for filename in dirList:
            if os.path.splitext(filename)[1] == target_ext:
                if type_dir:
                    filename = os.path.join(fname, filename)
                fileList.append(filename)
        
        return fileList


    def has_more_files(fileList):
        if fileList:
            return True
        return False
    
    def next_file(fileList):
        filename = None
        if fileList:
            filename = fileList[0]
            fileList.remove(filename)
        return filename
   
run.jack_compiler()