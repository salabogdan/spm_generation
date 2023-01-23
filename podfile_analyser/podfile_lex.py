import ply.lex as lex

# Keywords
reserved = {
    'require': 'REQUIRE',
    'platform': 'PLATFORM',
    'inhibit_all_warnings': 'INHIBIT_ALL_WARNINGS',
    'use_frameworks': 'USE_FRAMEWORKS',
    'workspace': 'WORKSPACE',
    'target': 'TARGET',
    'project': 'PROJECT',
    'pod': 'POD',
    'post_install': 'POST_INSTALL',
    'end': 'END',
    'do': 'DO'
}

tokens = [
             # Operators
             'EQUALS', 'COLON', 'COMMA', 'DOT', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE', 'QUOTE', 'EXCLAMATION',
             'LARGER',
             'SMALLER', 'PIPE', 'LPARANTESE', 'RPARANTESE',

             # Other
             'ID', 'STRING', 'NUMBER',
         ] + list(reserved.values())

# Operators
t_EQUALS = r'='
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPARANTESE = r'\('
t_RPARANTESE = r'\)'
t_QUOTE = r"'"
t_EXCLAMATION = r'!'
t_LARGER = r'>'
t_SMALLER = r'<'
t_PIPE = r'\|'


# Other
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_STRING(t):
    r'\'[^\']*\'|\"[^\"]*\"'
    t.value = t.value[1:-1]
    return t


def t_NUMBER(t):
    r'-?\d+\.?\d*(?![a-zA-Z_])'
    t.value = float(t.value)
    return t


# Ignored characters
t_ignore = ' \t\n'


def t_comment(t):
    r'\#.*'
    pass


def t_error(t):
    print(f'Illegal character "{t.value[0]}"')
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

if __name__ == '__main__':
    # Tokenize the input string
    with open("podfile") as file:
        lexer.input(file.read())
        # Tokenize the input string
        tokens = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok)

        # Print the tokens
        for token in tokens:
            print(token)
