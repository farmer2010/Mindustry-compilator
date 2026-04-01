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
"""

#+   первый уровень - разделение кода на блоки, удаление комментариев и пробелов перед строками
#+   второй уровень - разделение цикла for
#-   третий уровень - токенайзер
#-   четвертый уровень - вычленение из блоков значимой части
#-   пятый уровень - удаление пробелов в математических выражениях
#-   шестой уровень - преобразование математических выражений и прочего

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
            if (symbol == ";" or symbol == "{") and not string and not for_cycle:
                lines_level1.append(line)
                line = ""
                start = 1
            if for_cycle and symbol == "{":
                for_cycle = 0
                lines_level1.append(line)
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
    #второй уровень
    #разделение for
    #
    lines_level2 = []
    for l in lines_level1:
        line = ""
        txt = 0
        start_cmd = 0
        start = 0
        cmd_ind = 0
        cmds = ["", "", ""]
        for_cycle = 0
        for symbol in l:
            line += symbol
            if line == "for":
                for_cycle = 1
            if for_cycle:
                if symbol == "'" or symbol == '"':
                    txt = not txt
                if txt:
                    cmds[cmd_ind] += symbol
                else:
                    if start_cmd and symbol != " " and symbol != "\t" and symbol != "\n":
                        start_cmd = 0
                    if start and start_cmd == 0 and symbol != ";" and symbol != ")":
                        cmds[cmd_ind] += symbol
                    if symbol == "(":
                        start = 1
                        start_cmd = 1
                    if symbol == ";":
                        start_cmd = 1
                        cmd_ind += 1
        if not for_cycle:
            lines_level2.append(line)
        else:
            lines_level2.append(cmds[0])
            lines_level2.append(f"while ({cmds[1]})")
            lines_level2.append(cmds[2])
    for line in lines_level2:
        print(line)
    print("")
    #
    #третий уровень
    #токенайзер
    #
    lines_level3 = []
    words = ["if", "elif", "else", "while"]
    symb = ["}", "(", ")", "=", "+=", "-=", "*=", "/=", "+", "-", "*", "/", "==", ">", "<", ">=", "<=", "!=", "'", '"']
    tokens = ["if", "elif", "while", "num", "str", "bool", "obj", "id", "}", "(", ")", "=", "+=", "-=", "*=", "/=", "+", "-", "*", "/"]
    spaces = [" ", "\t", "\n"]
    for l in lines_level2:
        line = ""
        cmd = []
        txt = 0
        last_symbol = ""
        i = 0
        for symbol in l:
            if symbol == "'" or symbol == '"':
                txt = not txt
            if (not txt and (symbol in spaces or symbol in symb or i == len(l) - 1)) or (txt and (symbol == "'" or symbol == '"')):
                if line != "":
                    cmd.append(line)
                    line = ""
            if txt or (not symbol in spaces):
                line += symbol
            last_symbol = symbol
            i += 1
        lines_level3.append(cmd)
    #
    #четвертый уровень
    #синтаксис: ["название команды", "параметр1", "параметр2"...]
    #
    return(lines_level3)

res = compile(text)
for st in res:
    print(st)