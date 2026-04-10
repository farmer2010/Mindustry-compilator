import copy

text = """
num a = 0;

if (a == 0){
  a = 1;//comment
}
for (num i = 0; i < 10; i++){
a = 1 *2;
}
while(1){
num i = 2;
for (num h = 0;  h< 8; h++){
      i *=h;
    }

}
str f = "{aaa;;;}";
num c = 10;
num i = 0;
while (i < c){
print(i);
}
if (a+2*(3-  i) > 0){
print(1);
}else if (a<10){
print(2);
}else{
print(3);
}
num c;
"""

words = ["if", "else", "while", "num", "str", "bool", "obj", "id", "break", "continue", "null", "print"]
symb = ["{", "}", "(", ")", "=", "+=", "-=", "*=", "/=", "%=", "//=", "+", "-", "*", "**", "/", "%", "%%", "==", ">", "<", ">=", "<=", "!=", "'", '"', "++", "--", "===", "<<", ">>", ">>>", "!", "&&", "||", "&", "~", "^", ";"]
operations = ["+", "-", "*", "/", "//", "%", "%%", "**", ">", "<", ">=", "<=", "==", "===", "!=", "!", "&&", "||", "^", "&", "~", "<<", ">>", ">>>"]
operations_1_param = ["!", "~"]
spaces = [" ", "\t", "\n"]

commands = ["if", "else", "while", "for", "break", "continue", "print"]
types = ["num", "str", "bool", "obj", "id"]

prios = {
    "||" : 0,
    "&&" : 1,
    "^" : 2,
    "&" : 3,
    "==" : 4, "!=" : 4, "===" : 4,
    "<" : 5, ">" : 5, "<=" : 5, ">=" : 5,
    "<<" : 6, ">>" : 6, ">>>" : 6,
    "+" : 7, "-" : 7,
    "*" : 8, "/" : 8, "//" : 8,
    "%" : 9, "%%" : 9,
    "**" : 10,
    "!" : 11, "~" : 11,
}

class Token():
    def __init__(self, text):
        self.type = None
        if text in words:
            if text in commands:
                self.type = "command"
            elif text in types:
                self.type = "type"
            else:
                self.type = "word"
        elif '"' in text or "'" in text:
            self.type = "string"
        elif text in symb:
            self.type = "special symbol"
        else:
            self.type = "variable"
        self.text = text

    def __eq__(self, other):
        return(self.text == other)

    def __str__(self):
        return(self.text)

    def __repr__(self):
        return("'" + self.text + "'")

#+   первый уровень - разделение кода на блоки, удаление комментариев и пробелов перед строками
#+   второй уровень - токенайзер
#+   третий уровень - разделение цикла for
#+   четвертый уровень - небольшие преобразования команд + разделение конструкций else - if
#+   пятый уровень - преобразование токенов в команды
#+   шестой уровень - преобразование математических выражений
#-   седьмой уровень - индексация условий и циклов
#-   восьмой уровень - замена if и while на goto

def compile(code):
    #
    #первый уровень
    #
    lines_level1 = []
    line = ""
    string = 0
    start = 1
    comment = 0
    last_symbol = ""
    for_cycle = 0
    for symbol in code:
        if not comment:
            if symbol != " " and symbol != "\t" and symbol != "\n":
                start = 0
            if symbol == "'" or symbol == '"':
                string = not string
            if not string and not for_cycle:
                if symbol == ";":
                    lines_level1.append(line)
                    line = ""
                    start = 1
                elif symbol == "{":
                    lines_level1.append(line + "{")
                    line = ""
                    start = 1
            if for_cycle and symbol == "{":
                for_cycle = 0
                lines_level1.append(line + "{")
                line = ""
                start = 1
            if symbol == "}" and not string:
                lines_level1.append(line + "}")
                line = ""
                start = 1
            if (((symbol != ";" or for_cycle) and symbol != "}") or string) and not start:
                line += symbol
            if symbol == "/" and last_symbol == "/" and not string:
                comment = 1
            if line == "for":
                for_cycle = 1
        elif symbol == "\n":
            comment = 0
            line = ""
            start = 1
        last_symbol = symbol
    #
    #втррой уровень
    #токенайзер
    #
    lines_level2 = []
    for l in lines_level1:
        line = ""
        cmd = []
        txt = 0
        token_type = None
        for i in range(len(l)):
            symbol = l[i]
            if i < len(l) - 1:
                next_symbol = l[i+1]
            else:
                next_symbol = ""
            #
            if symbol == "'" or symbol == '"':
                txt = not txt
            #
            if token_type == None:
                if symbol == "'" or symbol == '"':
                    token_type = "string"
                elif symbol in symb and (symbol != "'" or symbol != '"'):
                    token_type = "special symbol"
                elif not symbol in spaces:
                    token_type = "word"
            if token_type == "string" or (not symbol in spaces and (
                    (token_type == "word" and not symbol in symb) or
                    (token_type == "special symbol" and symbol in symb)
            )):
                line += symbol
            #
            if (token_type == "word" and (next_symbol in spaces or next_symbol in symb)) or \
                    (token_type == "special symbol" and not line + next_symbol in symb) or \
                    (token_type == "string" and (symbol == "'" or symbol == '"') and not txt) or \
                    i == len(l) - 1:
                if line != "":
                    cmd.append(Token(line))
                    token_type = None
                    line = ""

        lines_level2.append(cmd)
    #
    #третий уровень
    #разделение цикла for
    #
    i = 0
    while i < len(lines_level2):
        l = lines_level2[i]
        if l[0] == "for":
            ops = []
            line = []
            start = 0
            for token in l:
                if start and token != ";":
                    line.append(token)
                if token == "(":
                    start = 1
                if token == ";":

            i += 1
        i += 1
    return(lines_level2)
    #
    #четвертый уровень
    #небольшие преобразования команд
    #
    for i in range(len(lines_level2)):
        line = lines_level2[i]
        if len(line) >= 2:
            if not line[0] in words:
                if line[1] == "++":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("+"), Token("1")]
                elif line[1] == "--":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("-"), Token("1")]
                elif line[1] == "+=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("+")] + line[2:]
                elif line[1] == "-=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("-")] + line[2:]
                elif line[1] == "*=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("*")] + line[2:]
                elif line[1] == "/=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("/")] + line[2:]
                elif line[1] == "%=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("%")] + line[2:]
                elif line[1] == "//=":
                    lines_level2[i] = [line[0], Token("="), line[0], Token("//")] + line[2:]
        if (line[0] == "num" or line[0] == "str" or line[0] == "bool" or line[0] == "obj" or line[0] == "id") and len(line) == 2:
            lines_level2[i] = [line[0], line[1], Token("="), Token("null")]
    #
    lines_level4 = []
    for l in lines_level2:
        if l[0] == "else" and l[1] == "if":
            lines_level4.append([Token("else")])
            lines_level4.append(l[1:])
        else:
            lines_level4.append(l)
    #
    #пятый уровень
    #преобразование токенов в команды
    #
    lines_level5 = []
    for l in lines_level4:
        line = []
        params = []
        bra_count = 0
        set_command_param = 0
        p = 0
        for i in range(len(l)):
            token = l[i]
            if token == "}" or token == "{" or token.type == "command":
                line.append(token)
            #
            if token == ")":
                bra_count -= 1
                if bra_count == 0:
                    line.append(params)
                    params = []
            if bra_count > 0:
                params.append(token)
            if token == "(":
                bra_count += 1
            #
            if set_command_param:
                if token != "=":
                    params.append(token)
                if i == len(l) - 1:
                    line.append(params)
                    params = []
            if token.type == "variable" and i == 0:
                line.append("set")
                line.append("")
                line.append(token)
                set_command_param = 1
            if token.type == "type":
                line.append("set")
                line.append(token)
                p = 1
            if token.type == "variable" and p:
                line.append(token)
                set_command_param = 1
                p = 0
        lines_level5.append(line)
    #
    #шестой уровень
    #преобразование математических выражений
    #
    lines_level6 = []
    for l in lines_level5:
        line = []
        for tk in l:
            if type(tk) == type(list()):
                mathline = copy.deepcopy(tk)
                var_ind = 0
                while len(mathline) > 3:
                    oper_tokens = []#нахождение всех операторов
                    bra_count = 0
                    for i in range(len(mathline)):
                        token = mathline[i]
                        if token == "(":
                            bra_count += 1
                        elif token == ")":
                            bra_count -= 1
                        elif token in operations:
                            p = prios[token.text] + bra_count * 20
                            oper_tokens.append([p, i])
                    #
                    ind = None#выбор оператора с максимальным приоритетом
                    max_prio = -1
                    for op in oper_tokens:
                        if op[0] > max_prio:
                            max_prio = op[0]
                            ind = op[1]
                    #
                    if mathline[ind] in operations_1_param:
                        operation = mathline[ind:ind + 2]#срез выражения с токенами(если один параметр)
                        for i in range(2):
                            mathline.pop(ind)
                    else:
                        operation = mathline[ind-1:ind+2]#срез выражения с токенами
                        for i in range(3):
                            mathline.pop(ind - 1)
                        mathline.insert(ind - 1, Token("__autogenerated" + str(var_ind) + "__"))
                    lines_level6.append(["set", Token("num"), Token("__autogenerated" + str(var_ind) + "__"), operation])
                    #
                    mathline2 = []
                    timer = 0
                    for i in range(len(mathline)):#удаление лишних скобок
                        token = mathline[i]
                        if i + 2 < len(mathline) and token == "(" and mathline[i + 2] == ")":
                            timer = 3
                            mathline2.append(mathline[i + 1])
                        if timer == 0:
                            mathline2.append(token)
                        if timer > 0:
                            timer -= 1
                    mathline = mathline2
                    #
                    var_ind += 1
                line.append(mathline)
            else:
                line.append(tk)
        lines_level6.append(line)
    #for line in lines_level5:
    #    print(line)
    print()
    return(lines_level2)

res = compile(text)
for st in res:
    print(st)