import ply.yacc as yacc

# Get the tokens from the lexer
from podfile_analyser.podfile_lex import tokens


def p_entry(p):
    '''entry : body
             | empty'''
    if p[1]:
        p[0] = ('entry', p[1])
    else:
        p[0] = ('entry',)


def p_body(p):
    '''body : require body
            | platform body
            | workspace body
            | targets body
            | post_install body
            | inhibit_all_warnings body
            | use_frameworks body
            | empty'''
    if p[1]:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_empty(p):
    '''empty :'''
    pass


def p_require(p):
    '''require : REQUIRE STRING'''
    p[0] = ('require', p[2])


def p_inhibit_all_warnings(p):
    '''inhibit_all_warnings : INHIBIT_ALL_WARNINGS EXCLAMATION'''
    p[0] = ('inhibit_all_warnings', p[2])


def p_use_frameworks(p):
    '''use_frameworks : USE_FRAMEWORKS EXCLAMATION'''
    p[0] = ('use_frameworks', p[2])


def p_platform(p):
    '''platform : PLATFORM COLON ID COMMA STRING'''
    p[0] = ('platform', p[3], p[5])


def p_workspace(p):
    '''workspace : WORKSPACE STRING'''
    p[0] = ('workspace', p[2])


def p_target(p):
    '''target : TARGET STRING DO target_elements END'''
    p[0] = ('target', p[2], p[4])


def p_targets(p):
    '''targets : target
               | targets target'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[1], [p[2]])


def p_target_elements(p):
    '''target_elements : target_element
                       | target_elements target_element'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ([p[1]], p[2])


def p_target_element(p):
    '''target_element : pod
                      | project'''
    p[0] = p[1]


def p_pod(p):
    '''pod : POD STRING COMMA pod_options
            | POD STRING'''
    p[0] = ('pod', p[2], p[4])


def p_pod_options(p):
    '''pod_options : pod_option
                   | pod_options pod_option'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = (p[1], [p[2]])


def p_pod_option(p):
    '''pod_option : STRING EQUALS STRING COMMA
                  | STRING EQUALS NUMBER COMMA
                  | COLON ID EQUALS LARGER STRING COMMA
                  | COLON ID EQUALS LARGER subscript COMMA
                  | STRING EQUALS STRING
                  | STRING EQUALS NUMBER
                  | COLON ID EQUALS LARGER STRING
                  | COLON ID EQUALS LARGER subscript'''
    if p[1] == ':':
        p[0] = (p[2], p[5])
    else:
        p[0] = (p[1], p[3])


def p_project(p):
    '''project : PROJECT STRING'''
    p[0] = ('project', p[2])


def p_error(t):
    print(f'Error: illegal character "{t.value[0]}" at line {t.lineno}, position {t.lexpos}')
    t.lexer.skip(1)


def p_post_install(p):
    '''post_install : POST_INSTALL DO PIPE ID PIPE scripts END'''
    p[0] = ('post_install', p[4], [p[6]])


def p_subscript(p):
    '''subscript : LBRACKET STRING RBRACKET
                | LBRACKET NUMBER RBRACKET'''
    p[0] = ('subscript', p[2])


def p_scripts(p):
    '''scripts :  script
                | script scripts
                | DO PIPE ID PIPE scripts END
                | DO PIPE TARGET PIPE scripts END
                '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = (p[1], p[3], p[5])


def p_script(p):
    '''script : function
                | ID
                | STRING
                | subscript
                | EQUALS
                | membercall
                '''
    p[0] = p[1]


def p_membercall(p):
    '''membercall : DOT ID
                    | DOT STRING
                    | ID membercall
                    | STRING membercall
                    | TARGET membercall'''
    if p[1] == '.':
        p[0] = ['membercall', p[2]]
    else:
        p[0] = ['root membercall', p[1]]


def p_function(p):
    '''function : ID LPARANTESE RPARANTESE'''
    p[0] = ('function call', p[1])


# Build the parser
parser = yacc.yacc(start="entry")

if __name__ == '__main__':
    # Parse the input string
    with open("podfile") as file:
        result = parser.parse(file.read())
        print(result)
