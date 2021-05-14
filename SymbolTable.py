class SymbolTable:
    static_scope = {}

    counts = \
        {
            'STATIC': 0,
            'FIELD': 0,
            'ARG': 0,
            'VAR': 0
        }

    def __init__(self):
        self.counts['FIELD'] = 0
        self.subroutine_scope = {}
        self.field_scope = {}

    def start_subroutine(self):
        self.subroutine_scope = {}
        self.counts['ARG'] = 0
        self.counts['VAR'] = 0

    def define(self, name, type, kind):
        id = self.var_count(kind)
        self.counts[kind] += 1
        if kind in ['ARG', 'VAR']:
            self.subroutine_scope[name] = (type, kind, id)
        elif kind == 'STATIC':
            self.static_scope[name] = (type, kind, id)
        elif kind == 'FIELD':
            self.field_scope[name] = (type, kind, id)

    def var_count(self, kind):
        return self.counts[kind]

    def kind_of(self, name):
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][1]
        elif name in self.field_scope.keys():
            return self.field_scope[name][1]
        elif name in self.static_scope.keys():
            return self.static_scope[name][1]
        else:
            return 'NONE'

    def type_of(self, name):
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][0]
        elif name in self.field_scope.keys():
            return self.field_scope[name][0]
        elif name in self.static_scope.keys():
            return self.static_scope[name][0]
        else:
            return 'NONE'

    def index_of(self, name):
        if name in self.subroutine_scope.keys():
            return self.subroutine_scope[name][2]
        elif name in self.field_scope.keys():
            return self.field_scope[name][2]
        elif name in self.static_scope.keys():
            return self.static_scope[name][2]
        else:
            return 'NONE'