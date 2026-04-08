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
#text = "else{print(1);}"

words = ["if", "else", "while", "num", "bool", "obj", "id", "break", "continue", "null", "print"]
symb = ["{", "}", "(", ")", "=", "+=", "-=", "*=", "/=", "%=", "//=", "+", "-", "*", "/", "==", ">", "<", ">=", "<=", "!=", "'", '"', "++", "--", "==="]
tokens = ["if", "elif", "while", "num", "str", "bool", "obj", "id", "}", "(", ")", "=", "+=", "-=", "*=", "/=", "+", "-", "*", "/"]
spaces = [" ", "\t", "\n"]

commands = ["if", "else", "while", "break", "continue", "print"]
types = ["num", "str", "bool", "obj", "id"]

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
#+   второй уровень - разделение цикла for
#+   третий уровень - токенайзер
#+   четвертый уровень - небольшие преобразования команд
#-   пятый уровень - создание команд из токенов
#-   шестой уровень -

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
            lines_level2.append(f"while ({cmds[1]})" + "{")
            lines_level2.append(cmds[2])
    #
    #третий уровень
    #токенайзер
    #
    lines_level3 = []
    for l in lines_level2:
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

        lines_level3.append(cmd)
    #
    #четвертый уровень
    #небольшие преобразования команд
    #
    for i in range(len(lines_level3)):
        line = lines_level3[i]
        if len(line) >= 2:
            if not line[0] in words:
                if line[1] == "++":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("+"), Token("1")]
                elif line[1] == "--":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("-"), Token("1")]
                elif line[1] == "+=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("+")] + line[2:]
                elif line[1] == "-=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("-")] + line[2:]
                elif line[1] == "*=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("*")] + line[2:]
                elif line[1] == "/=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("/")] + line[2:]
                elif line[1] == "%=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("%")] + line[2:]
                elif line[1] == "//=":
                    lines_level3[i] = [line[0], Token("="), line[0], Token("//")] + line[2:]
        if (line[0] == "num" or line[0] == "str" or line[0] == "bool" or line[0] == "obj" or line[0] == "id") and len(line) == 2:
            lines_level3[i] = [line[0], line[1], Token("="), Token("null")]
    #
    #пятый уровень
    #
    lines_level5 = []
    for l in lines_level3:
        line = []
        params = []
        param_ind = 0
        for i in range(len(l)):
            token = l[i]
            if token == "}" or token == "{" or token.type == "command":
                line.append(token)
            elif token.type == "type":
                line.append("set")
                line.append(token)
            #
            if token == ")":
                param_ind -= 1
                if param_ind == 0:
                    line.append(params)
                    params = []
            if param_ind > 0:
                params.append(token)
            if token == "(":
                param_ind += 1
            #
            if token.type == "variable":
                line.append("set")
                line.append("")
                
        lines_level5.append(line)
    #
    for line in lines_level3:
        print(line)
    print()
    return(lines_level5)

res = compile(text)
for st in res:
    print(st)