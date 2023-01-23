import ply.yacc as yacc

# Get the tokens from the lexer
from podspec_analyser.podspec_lex import tokens


def p_entry(p):
    '''entry : body
             | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = {}


def p_body(p):
    '''body : declare_new_pod
            | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = []


def p_declare_new_pod(p):
    '''declare_new_pod : POD COLON COLON ID DOT NEW DO PIPE ID PIPE podspec_attributes END'''
    pod_json = {'variable_name': p[9]}
    dependencies = []
    subspecs = []
    for pod_attribute in p[11]:
        membercalls_list = pod_attribute.get('podspec_attribute')
        if membercalls_list[0] != p[9]:
            # need to treat the subspec case
            raise ValueError('the pod name is not correct')
        membercalls_list.pop(0)
        if membercalls_list[0] == 'dependency':
            dependencies.append(pod_attribute['value'])
            inner_dict = {'dependencies': dependencies}
        elif membercalls_list[0] == 'subspec':
            subspecs.append(pod_attribute['value'])
            inner_dict = {'subspecs': subspecs}
        else:
            inner_dict = {membercalls_list.pop(): pod_attribute['value']}
        members_queue = membercalls_list.copy()
        while len(members_queue) > 1:
            inner_dict = {members_queue.pop(): inner_dict}
        pod_json.update(inner_dict)
    p[0] = {'new pod':
                pod_json
            }


def p_subspec(p):
    '''subspec : ID DOT SUBSPEC STRING DO PIPE ID PIPE podspec_attributes END
                '''

    spec_json = {'name': p[4],
                 'variable_name': p[7]
                 }

    subspec_json = {'podspec_attribute': [p[1], p[3]],
                    'value': spec_json
                    }

    dependencies = []
    for pod_attribute in p[9]:
        membercalls_list = pod_attribute.get('podspec_attribute')
        if membercalls_list[0] != p[7]:
            # need to treat the subspec case
            raise ValueError('the pod name is not correct')
        membercalls_list.pop(0)
        if membercalls_list[0] == 'dependency':
            dependencies.append(pod_attribute['value'])
            inner_dict = {'dependencies': dependencies}
        else:
            inner_dict = {membercalls_list.pop(): pod_attribute['value']}
        members_queue = membercalls_list.copy()
        while len(members_queue) > 1:
            inner_dict = {members_queue.pop(): inner_dict}
        spec_json.update(inner_dict)
    p[0] = subspec_json


def p_dependency(p):
    '''dependency : ID DOT DEPENDENCY list_elements'''
    p[0] = {'podspec_attribute': [p[1], p[3]],
            'value': p[4]
            }


def p_podspec_attributes(p):
    '''podspec_attributes :  podspec_attribute
                            | dependency
                            | subspec
                            | dependency podspec_attributes
                            | podspec_attribute podspec_attributes
                            | subspec podspec_attributes'''
    if len(p) == 2:
        # print('p = 2', p[1])
        p[0] = [p[1]]
    else:
        # print('p = 3', 'p[1] = ', p[1], 'p[2] = ', p[2])
        p[0] = [p[1]] + p[2]


def p_podspec_attribute(p):
    '''podspec_attribute : membercall EQUALS STRING
                            | membercall EQUALS COLON ID COMMA STRING
                            | membercall EQUALS SMALLER SMALLER MINUS DESC description DESC
                            | membercall EQUALS LBRACE dictionary RBRACE
                            | membercall EQUALS list_elements
                            | membercall EQUALS ID'''
    if len(p) == 4:
        p[0] = {'podspec_attribute': p[1],
                'value': p[3]}
    elif len(p) == 7:
        p[0] = {'podspec_attribute': p[1],
                'value': {p[4]: p[6]}
                }
    elif len(p) == 9:
        p[0] = {'podspec_attribute': p[1],
                'value': p[7]}
    else:
        p[0] = {'podspec_attribute': p[1],
                'value': p[4]}


def p_list_elements(p):
    '''list_elements : STRING list_elements
                        | COMMA STRING list_elements
                        | COMMA STRING
                        | STRING'''
    if p[1] == ',':
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = [p[2]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]


def p_membercall(p):
    '''membercall :  ID membercall
                    | STRING membercall
                    | TARGET membercall
                    | DOT ID membercall
                    | DOT STRING membercall
                    | DOT ID
                    | DOT STRING'''
    if p[1] == '.':
        if len(p) == 4:
            p[0] = [p[2]] + p[3]
        else:
            p[0] = [p[2]]
    else:
        p[0] = [p[1]] + p[2]


def p_dictionary(p):
    '''dictionary : COMMA dictionary_value
                    | dictionary_value
                    | dictionary_value dictionary
                    | COMMA dictionary_value dictionary'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[1] == ',':
            p[0] = p[2]
        else:
            p[1].update(p[2])
            p[0] = p[1]


def p_dictinary_equals(p):
    '''dictinary_equals : EQUALS LARGER
                        | COLON '''
    p[0] = "="


def p_dictionary_value(p):
    '''dictionary_value : COLON ID dictinary_equals STRING
                        | STRING dictinary_equals STRING
                        | COLON ID dictinary_equals membercall
                        | STRING dictinary_equals membercall
                        | COLON ID dictinary_equals LBRACKET list_elements RBRACKET
                        | STRING dictinary_equals LBRACKET list_elements RBRACKET
                        '''
    if len(p) == 4:
        p[0] = {p[1]: p[3]}
    elif len(p) == 5:
        p[0] = {p[2]: p[4]}
    elif len(p) == 6:
        p[0] = {p[1]: p[4]}
    else:
        p[0] = {p[2]: p[5]}


def p_description(p):
    '''description : ID
                    | DOT
                    | ID description'''
    if len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1]


def p_empty(p):
    '''empty :'''
    pass


def p_error(t):
    print(f'Error: illegal character "{t.value[0]}" at line {t.lineno}, position {t.lexpos}')
    t.lexer.skip(1)


# Build the parser
parser = yacc.yacc(start="entry"
                   # , debug=True
                   )

if __name__ == '__main__':
    print("valid tokens count", len(tokens))
    # Parse the input string
    with open("podspec") as file:
        result = parser.parse(file.read(),
                              # debug=True
                              )
        print(result)


def parse_podspec(path: str) -> dict:
    with open(path) as podspec_file:
        result_dict = parser.parse(podspec_file.read())
        return result_dict
