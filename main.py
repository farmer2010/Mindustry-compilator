import copy
import pyperclip

words = ["if", "else", "while", "for", "num", "str", "bool", "obj", "id", "break", "continue", "null", "print", "printflush", "stop", "end"]
symb = ["{", "}", "(", ")", "=", "+=", "-=", "*=", "/=", "%=", "~/=", "+", "-", "*", "**", "/", "~/", "%", "%%", "==", ">", "<", ">=", "<=", "!=", "'", '"', "++", "--", "===", "<<", ">>", ">>>", "!", "&&", "||", "&", "^", ";"]
operations = ["+", "-", "*", "/", "~/", "%", "%%", "**", ">", "<", ">=", "<=", "==", "===", "!=", "!", "&&", "||", "^", "&", "<<", ">>", ">>>"]
operations_1_param = ["!"]
spaces = [" ", "\t", "\n"]
numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
op_to_mlog = {
    "+" : "add",
    "-" : "sub",
    "*": "mul",
    "/": "div",
    "~/": "idiv",
    "%": "mod",
    "%%": "emod",
    "**": "pow",
    "==": "equal",
    "!=": "notEqual",
    "&&": "land",#булевое
    "<": "lessThan",
    "<=": "lessThanEq",
    ">": "greaterThan",
    ">=": "greaterThanEq",
    "===": "strictEqual",
    "<<": "shl",
    ">>": "shr",
    ">>>": "ushr",
    "||": "or",
    "&": "and",#побитовое
    "^": "xor",
    "!": "not"#побитовое
}

commands = ["if", "else", "while", "for", "break", "continue", "print", "printflush", "stop", "end"]
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
    "*" : 8, "/" : 8, "~/" : 8,
    "%" : 9, "%%" : 9,
    "**" : 10,
    "!" : 11
}

class Token():
    def __init__(self, text, line=0, pos=0):
        self.line = line
        self.pos = pos
        self.type = None
        number = 1
        try:
            float(text)
        except:
            number = 0
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
        elif number:
            self.type = "number"
        else:
            self.type = "variable"
        self.text = text

    def __eq__(self, other):
        return(self.text == other)

    def __str__(self):
        return(self.text)

    def __repr__(self):
        return("'" + self.text + "'")

def get_error(err_code, line_ind, pos, line):
    res = f"Syntax error (code {err_code}) on line {line_ind}:\n"
    res += line + "\n"
    res += " " * pos + "^\n"
    if err_code == 10:
        pass
    elif err_code == 11:
        pass
    elif err_code == 20:
        res += 'Unknown command ""'
    elif err_code == 30:
        res += "Invalid number format"
    return(res)

#+   1 уровень - разделение кода на блоки, удаление комментариев и пробелов перед строками
#+   2 уровень - токенайзер
#+   3 уровень - разделение цикла for
#+   4 уровень - небольшие преобразования команд + разделение конструкций else - if
#+   5 уровень - преобразование токенов в команды
#+   6 уровень - разделение цикла while
#+   7 уровень - добавление скобок в else
#+   8 уровень - преобразование if
#+   9 уровень - преобразование математических выражений
#+   10 уровень - замена set на op
#+   11 уровень - финальное преобразование команд в mlog

'''
Коды ошибок:
1x - неверное количество скобок
2x - неизвестная команда
3x - неправильный формат числа
4x - отсутствует ; в конце строки
5x - неверное количество кавычек

10 - неверное количество фигурных скобок
11 - неверное количество круглых скобок
12 - неверное количество квадратных скобок

20 - неизвестная команда

30 - неправильный формат числа

40 - отсутствует ;

50 - неверное количество '
51 - неверное количество "
'''

def compile(code):
    console = ""
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
    line_ind = 0
    lines_indexes = []
    for symbol in code:
        if symbol == "\n":
            line_ind += 1
        if not comment:
            if symbol != " " and symbol != "\t" and symbol != "\n":
                start = 0
            if symbol == "'" or symbol == '"':
                string = not string
            if string == 0 and not for_cycle:
                if symbol == ";":
                    lines_indexes.append(line_ind)
                    lines_level1.append(line)
                    line = ""
                    start = 1
                elif symbol == "{":
                    lines_indexes.append(line_ind)
                    lines_level1.append(line + "{")
                    line = ""
                    start = 1
            if for_cycle and symbol == "{":
                for_cycle = 0
                lines_indexes.append(line_ind)
                lines_level1.append(line + "{")
                line = ""
                start = 1
            if symbol == "}" and string == 0:
                lines_indexes.append(line_ind)
                lines_level1.append(line + "}")
                line = ""
                start = 1
            if (((symbol != ";" or for_cycle) and symbol != "}") or string) and not start:
                line += symbol
            if symbol == "/" and last_symbol == "/" and string == 0:
                comment = 1
            if line == "for":
                for_cycle = 1
        elif symbol == "\n":
            comment = 0
            line = ""
            start = 1
        last_symbol = symbol
    #
    #второй уровень
    #токенайзер
    #
    lines_level2 = []
    for li in range(len(lines_level1)):
        l = lines_level1[li]
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
                elif symbol in numbers:
                    token_type = "number"
                elif symbol in symb and (symbol != "'" or symbol != '"'):
                    if symbol == "-" and next_symbol in numbers:
                        token_type = "number"
                    else:
                        token_type = "special symbol"
                elif not symbol in spaces:
                    token_type = "word"
            #
            if token_type == "string" or (not symbol in spaces and (
                    (token_type == "word" and not symbol in symb) or
                    (token_type == "special symbol" and symbol in symb) or
                    (token_type == "number")
            )):
                line += symbol
            #
            if (token_type == "word" and (next_symbol in spaces or next_symbol in symb)) or \
                    (token_type == "special symbol" and not line + next_symbol in symb) or \
                    (token_type == "string" and (symbol == "'" or symbol == '"') and txt == 0) or \
                    (token_type == "number" and (next_symbol in spaces or next_symbol in symb)) or \
                    i == len(l) - 1:
                if line != "":
                    if token_type == "number":
                        try:
                            float(line)
                        except:
                            console += get_error(30, lines_indexes[li], 0, code.split("\n")[lines_indexes[li]])
                            return([], console)
                    elif token_type == "string":
                        if line[0] != line[-1]:
                            if line[0] == "'":
                                console += get_error(50, lines_indexes[li], 0, code.split("\n")[lines_indexes[li]])
                            elif line[0] == '"':
                                console += get_error(51, lines_indexes[li], 0, code.split("\n")[lines_indexes[li]])
                            return([], console)
                    cmd.append(Token(line, lines_indexes[li]))
                    token_type = None
                    line = ""
        lines_level2.append(cmd)
    #
    #уровень 2.5
    #проверка синтаксиса
    #
    fig_bra_count = 0
    for li in range(len(lines_level2)):
        l = lines_level2[li]
        circ_bra_count = 0
        for j in range(len(l)):
            token = l[j]
            if j < len(l) - 1:
                next_token = l[j + 1]
            else:
                next_token = ""
            #
            if token == "{":
                fig_bra_count += 1
            elif token == "}":
                fig_bra_count -= 1
            #
            if token == "(":
                circ_bra_count += 1
            elif token == ")":
                circ_bra_count -= 1
            #
            if token.type == "variable" and next_token != "=" and j == 0:
                console += get_error(20, lines_indexes[li], 0, code.split("\n")[lines_indexes[li]])
                return([], console)
        if circ_bra_count != 0:
            console += get_error(11, lines_indexes[li], 0, code.split("\n")[lines_indexes[li]])
            return([], console)
    if fig_bra_count != 0:
        console += get_error(10, -1, 0, code.split("\n")[lines_indexes[li]])
        return([], console)
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
            bra_count = 0
            for token in l:
                if token == ")":
                    bra_count -= 1
                if start and token != ";" and bra_count != 0:
                    line.append(token)
                if token == "(":
                    bra_count += 1
                    start = 1
                if token == ";" or (token == ")" and bra_count == 0):
                    ops.append(line)
                    line = []
            #
            lines_level2[i] = [Token("while"), Token("("), *ops[1], Token(")"), Token("{")]
            lines_level2.insert(i, ops[0])
            #
            bra_count = 0
            for j in range(i, len(lines_level2)):
                l2 = lines_level2[j]
                if "{" in l2:
                    bra_count += 1
                if "}" in l2:
                    bra_count -= 1
                    if bra_count == 0:
                        lines_level2.insert(j, ops[2])
                        break
            #
            i += 1
        i += 1
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
        st = 0
        for i in range(len(l)):
            token = l[i]
            if token == "}" or token == "{" or token.type == "command":
                line.append(token)
            #
            if token == ")" and not set_command_param:
                bra_count -= 1
                if bra_count == 0:
                    line.append(params)
                    params = []
            if bra_count > 0 and not set_command_param:
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
                st = 1
            if token.type == "variable" and st:
                line.append(token)
                set_command_param = 1
                st = 0
        lines_level5.append(line)
    #
    #шестой уровень
    #разделение цикла while
    #
    i = 0
    ind = 0
    while i < len(lines_level5):
        l = lines_level5[i]
        if l[0] == "while":
            op = copy.deepcopy(l[1])
            #
            j = i
            bra_count = 0
            while j < len(lines_level5):
                if lines_level5[j][-1] == "{":
                    bra_count += 1
                if lines_level5[j][0] == "}":
                    bra_count -= 1
                #
                if bra_count == 0 and lines_level5[j][0] == "}":
                    lines_level5.insert(j, [Token("set"), Token("bool"), Token("__cycle_condition__"), op])
                    lines_level5[j + 1] = [Token("goto"), Token("cycle_label" + str(ind)), Token("__cycle_condition__"), Token("true")]
                    break
                j += 1
            #
            lines_level5[i] = [Token("label"), Token("cycle_label" + str(ind))]
            #
            ind += 1
        i += 1
    #
    #седьмой уровень
    #добавление скобок в else
    #
    i = 0
    while i < len(lines_level5):
        act = 0
        if i > 0:
            if lines_level5[i - 1][0] != "else":
                act = 1
            else:#if else
                if len(lines_level5[i - 1]) == 2:
                    act = 1
        else:
            act = 1
        #
        if lines_level5[i][0] == "if" and act:
            j = i
            elseif_count = 0
            bra_count = 0
            end_flag = 0
            while j < len(lines_level5):
                if lines_level5[j][-1] == "{":
                    bra_count += 1
                if lines_level5[j][0] == "}":
                    bra_count -= 1
                #
                if lines_level5[j][0] == "else" and len(lines_level5[j]) == 1 and bra_count == 0:
                    elseif_count += 1
                    lines_level5[j].append(Token("{"))
                elif lines_level5[j][0] == "else" and len(lines_level5[j]) == 2 and bra_count == 1:
                    end_flag = 1
                #
                if lines_level5[j][0] == "}" and end_flag and bra_count == 0:
                    break
                #
                j += 1
            #
            for k in range(elseif_count):
                lines_level5.insert(j, [Token("}")])
        i += 1
    #
    #восьмой уровень
    #преобразование if
    #
    i = 0
    ind = 0
    while i < len(lines_level5):
        if lines_level5[i][0] == "if":
            endif_pos = i
            bra_count = 0
            while endif_pos < len(lines_level5):#определение позиции конца if
                if lines_level5[endif_pos][-1] == "{":
                    bra_count += 1
                if lines_level5[endif_pos][0] == "}":
                    bra_count -= 1
                if bra_count == 0:
                    break
                #
                endif_pos += 1
            #
            if endif_pos + 1 < len(lines_level5) and lines_level5[endif_pos + 1][0] == "else":#if-else
                endelse_pos = endif_pos + 1
                bra_count = 0
                while endelse_pos < len(lines_level5):#определение позиции конца else
                    if lines_level5[endelse_pos][-1] == "{":
                        bra_count += 1
                    if lines_level5[endelse_pos][0] == "}":
                        bra_count -= 1
                    if bra_count == 0:
                        break
                    #
                    endelse_pos += 1
                #
                lines_level5[endelse_pos] = [Token("label"), Token("if_label" + str(ind))]
                #
                lines_level5[endif_pos] = [Token("goto"), Token("if_label" + str(ind)), Token(""), Token("always")]
                ind += 1
                lines_level5[endif_pos + 1] = [Token("label"), Token("if_label" + str(ind))]
                #
                lines_level5.insert(i, [Token("set"), Token("bool"), Token("__if_condition__"), copy.deepcopy(lines_level5[i][1])])
                lines_level5[i + 1] = [Token("goto"), Token("if_label" + str(ind)), Token("__if_condition__"), Token("false")]
                ind += 1
            else:#if
                lines_level5[endif_pos] = [Token("label"), Token("if_label" + str(ind))]
                lines_level5.insert(i, [Token("set"), Token("bool"), Token("__if_condition__"), copy.deepcopy(lines_level5[i][1])])
                lines_level5[i + 1] = [Token("goto"), Token("if_label" + str(ind)), Token("__if_condition__"), Token("false")]
                ind += 1
        i += 1
    #
    #девятый уровень
    #преобразование математических выражений
    #
    lines_level9 = []
    for l in lines_level5:
        line = []
        command = l[0]
        count = 1
        if command == "set":
            count = 3
        for tk in l:
            if type(tk) == type(list()):
                mathline = copy.deepcopy(tk)
                var_ind = 0
                if command == "set" and mathline[0] == "-" and len(mathline) == 2:
                    mathline = [mathline[1], Token("*"), Token("-1")]
                while len(mathline) > count:
                    oper_tokens = []#нахождение всех операторов
                    bra_count = 0
                    for i in range(len(mathline)):
                        token = mathline[i]
                        if token == "(":
                            bra_count += 1
                        elif token == ")":
                            bra_count -= 1
                        elif token == "-":
                            if i == 0 or mathline[i - 1] in operations:#унарный минус
                                st = 11 + bra_count * 20
                                oper_tokens.append([st, i])
                            else:#обычный минус
                                st = prios[token.text] + bra_count * 20
                                oper_tokens.append([st, i])
                        elif token in operations:
                            st = prios[token.text] + bra_count * 20
                            oper_tokens.append([st, i])
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
                        mathline.insert(ind, Token("__autogenerated" + str(var_ind) + "__"))
                    elif mathline[ind] == "-" and (ind == 0 or mathline[ind - 1] in operations):
                        operation = [mathline[ind + 1], Token("*"), Token("-1")]#срез выражения с токенами(если один параметр)(для унарного минуса)
                        for i in range(2):
                            mathline.pop(ind)
                        mathline.insert(ind, Token("__autogenerated" + str(var_ind) + "__"))
                    else:
                        operation = mathline[ind-1:ind + 2]#срез выражения с токенами
                        for i in range(3):
                            mathline.pop(ind - 1)
                        mathline.insert(ind - 1, Token("__autogenerated" + str(var_ind) + "__"))
                    lines_level9.append(["set", Token("num"), Token("__autogenerated" + str(var_ind) + "__"), operation])
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
        lines_level9.append(line)
    #
    #десятый уровень
    #замена set на op
    #
    for i in range(len(lines_level9)):
        l = lines_level9[i]
        if l[0] == "set" and len(l[3]) == 3:
            lines_level9[i] = [Token("op"), l[2], Token(op_to_mlog[l[3][1].text]), l[3][0], l[3][2]]#'op' result operator op1 op2
        elif l[0] == "set" and len(l[3]) == 2:
            lines_level9[i] = [Token("op"), l[2], Token(op_to_mlog[l[3][0].text]), l[3][1], Token("x")]
    #
    #одиннадцатый уровень
    #финальное преобразование команд в mlog
    #
    lines_level11 = []
    for l in lines_level9:
        if l[0] == "set":
            lines_level11.append(f"set {l[2]} {l[3][0]}")
        elif l[0] == "op":
            lines_level11.append(f"op {l[2]} {l[1]} {l[3]} {l[4]}")
        elif l[0] == "goto":
            if l[3] != "always":
                lines_level11.append(f"jump {l[1]} equal {l[2]} {l[3]}")
            else:
                lines_level11.append(f"jump {l[1]} always x false")
        elif l[0] == "label":
            lines_level11.append(f"{l[1]}:")
        elif l[0] == "print":
            lines_level11.append(f"print {l[1][0]}")
        elif l[0] == "printflush":
            lines_level11.append(f"printflush {l[1][0]}")
        elif l[0] == "stop":
            lines_level11.append(f"stop")
        elif l[0] == "end":
            lines_level11.append(f"end")
    lines_level11.append("end")
    #
    console += "File succesfully compilated"
    #
    return(lines_level11, console)


text = """
for (num i = 0; i < 10; i++){
print(i + 2*2);
}
stop();
num a = 0;
a = 22333 + 1;
"""

res = compile(text)
for st in res[0]:
    print(st)
print()
print(res[1])
#
txt = ""
for st in res[0]:
    txt += st + "\n"
pyperclip.copy(txt)
