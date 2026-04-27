def lexer(code):
    """Разбивает код на токены."""
    tokens = []
    current_token = ""
    in_quotes = False
    in_parentheses = 0
    
    for char in code:
        if char == "'":
            in_quotes = not in_quotes
            current_token += char
        elif char == "(" and not in_quotes:
            in_parentheses += 1
            current_token += char
        elif char == ")" and not in_quotes:
            in_parentheses -= 1
            current_token += char
        elif char == " " and not in_quotes and in_parentheses == 0:
            if current_token:
                tokens.append(current_token)
                current_token = ""
        else:
            current_token += char
    
    if current_token:
        tokens.append(current_token)
    
    return tokens


def parser(tokens, line):
    """Преобразует токены в команды."""
    if tokens[0] == "печать":
        # Собираем все аргументы после "печать"
        arguments = []
        i = 1
        while i < len(tokens):
            arg = tokens[i]
            # Если аргумент в кавычках - это строка
            if arg.startswith("'") and arg.endswith("'"):
                arguments.append({"type": "string", "value": arg.strip("'")})
            # Если аргумент - это переменная
            elif arg in ["и", "а", "но", "тогда", "конец"]:  # Игнорируем служебные слова
                pass
            else:
                arguments.append({"type": "variable", "value": arg})
            i += 1
        
        return {"command": "print", "arguments": arguments}
    
    elif tokens[0] == "сумма":
        num1 = int(tokens[1])
        num2 = int(tokens[3])
        return {"command": "add", "num1": num1, "num2": num2}
    
    elif tokens[0] == "прм":
        name = tokens[1]
        
        if len(tokens) >= 4 and tokens[2] == "=":
            value_part = " ".join(tokens[3:])
            
            if value_part.startswith("ввод(") and value_part.endswith(")"):
                inner = value_part[5:-1]
                return {"command": "input", "name": name, "type": inner}
            
            value_str = value_part
            
            if value_str.startswith("'") and value_str.endswith("'"):
                value = value_str.strip("'")
            elif value_str.isdigit():
                value = int(value_str)
            elif value_str.replace('.', '', 1).isdigit() and value_str.count('.') == 1:
                value = float(value_str)
            elif value_str in ["правда", "истина", "да"]:
                value = True
            elif value_str in ["ложь", "ложно", "нет"]:
                value = False
            else:
                value = value_str
            
            return {"command": "variable", "name": name, "value": value}
        else:
            raise ValueError(f"Неправильный формат присваивания. Ожидается: прм x = значение. Получено: {line}")
    
    elif tokens[0] == "если":
        left = tokens[1]
        operator = tokens[2]
        right_tokens = tokens[3:-1]
        
        if len(right_tokens) == 1:
            right = right_tokens[0]
            if right.isdigit():
                right = int(right)
            elif right.replace('.', '', 1).isdigit():
                right = float(right)
            elif right in ["правда", "истина", "да"]:
                right = True
            elif right in ["ложь", "ложно", "нет"]:
                right = False
        else:
            right = " ".join(right_tokens).strip("'")
        
        return {"command": "if", "left": left, "operator": operator, "right": right, "type": "start"}
    
    elif tokens[0] == "инсли":
        left = tokens[1]
        operator = tokens[2]
        right_tokens = tokens[3:-1]
        
        if len(right_tokens) == 1:
            right = right_tokens[0]
            if right.isdigit():
                right = int(right)
            elif right.replace('.', '', 1).isdigit():
                right = float(right)
            elif right in ["правда", "истина", "да"]:
                right = True
            elif right in ["ложь", "ложно", "нет"]:
                right = False
        else:
            right = " ".join(right_tokens).strip("'")
        
        return {"command": "elif", "left": left, "operator": operator, "right": right, "type": "middle"}
    
    elif tokens[0] == "иначе":
        return {"command": "else", "type": "middle"}
    
    elif tokens[0] == "конец":
        return {"command": "endif", "type": "end"}
    
    else:
        raise ValueError(f"Неизвестная команда: {tokens[0]}")


def evaluate_condition(left, operator, right, variables):
    """Вычисляет условие."""
    if isinstance(left, str):
        if left in variables:
            left_value = variables[left]
        elif left.isdigit():
            left_value = int(left)
        elif left.replace('.', '', 1).isdigit():
            left_value = float(left)
        elif left in ["правда", "истина", "да"]:
            left_value = True
        elif left in ["ложь", "ложно", "нет"]:
            left_value = False
        else:
            left_value = left
    else:
        left_value = left
    
    if isinstance(right, str):
        if right in variables:
            right_value = variables[right]
        elif right.isdigit():
            right_value = int(right)
        elif right.replace('.', '', 1).isdigit():
            right_value = float(right)
        elif right in ["правда", "истина", "да"]:
            right_value = True
        elif right in ["ложь", "ложно", "нет"]:
            right_value = False
        else:
            right_value = right
    else:
        right_value = right
    
    if operator == "равно":
        return left_value == right_value
    elif operator == "неравно":
        return left_value != right_value
    elif operator == "больше":
        return left_value > right_value
    elif operator == "меньше":
        return left_value < right_value
    elif operator == "больше_или_равно":
        return left_value >= right_value
    elif operator == "меньше_или_равно":
        return left_value <= right_value
    else:
        raise ValueError(f"Неизвестный оператор: {operator}")


def process_input(input_type):
    """Обрабатывает пользовательский ввод в зависимости от типа."""
    if input_type == "целчисл()" or input_type == "целоечисло()" or input_type == "число()":
        while True:
            try:
                user_input = input("Введите целое число: ")
                return int(user_input)
            except ValueError:
                print("Ошибка! Пожалуйста, введите целое число.")
    
    elif input_type == "дробчисл()" or input_type == "дробноечисло()" or input_type == "вещчисло()":
        while True:
            try:
                user_input = input("Введите дробное число: ")
                return float(user_input)
            except ValueError:
                print("Ошибка! Пожалуйста, введите число (целое или дробное).")
    
    elif input_type == "строка()" or input_type == "текст()":
        return input("Введите текст: ")
    
    elif input_type == "бул()" or input_type == "булево()" or input_type == "логич()":
        while True:
            user_input = input("Введите 'правда' или 'ложь': ").lower()
            if user_input in ["правда", "истина", "да", "true", "yes"]:
                return True
            elif user_input in ["ложь", "ложно", "нет", "false", "no"]:
                return False
            else:
                print("Ошибка! Пожалуйста, введите 'правда' или 'ложь'.")
    
    else:
        prompt = input_type.strip("'").strip('"')
        if prompt.endswith("()"):
            prompt = prompt[:-2]
        return input(f"Введите {prompt}: ")


def interpreter(command, variables, condition_stack):
    """Выполняет команду."""
    cmd_type = command.get("type", "simple")
    
    if cmd_type == "start":
        result = evaluate_condition(command["left"], command["operator"], command["right"], variables)
        condition_stack.append({
            "active": result,
            "executed": result
        })
        return None
    
    elif cmd_type == "middle":
        if not condition_stack:
            raise ValueError("Нет открытого условия для elif/else")
        
        current_condition = condition_stack[-1]
        
        if command["command"] == "elif":
            should_execute = not current_condition["executed"] and evaluate_condition(
                command["left"], command["operator"], command["right"], variables
            )
            if should_execute:
                current_condition["executed"] = True
            condition_stack[-1]["active"] = should_execute
            
        elif command["command"] == "else":
            should_execute = not current_condition["executed"]
            condition_stack[-1]["active"] = should_execute
            if should_execute:
                current_condition["executed"] = True
        
        return None
    
    elif cmd_type == "end":
        if condition_stack:
            condition_stack.pop()
        return None
    
    else:
        if condition_stack and not condition_stack[-1]["active"]:
            return None
        
        if command["command"] == "print":
            # Собираем все части для вывода
            output_parts = []
            for arg in command["arguments"]:
                if arg["type"] == "string":
                    output_parts.append(arg["value"])
                elif arg["type"] == "variable":
                    var_name = arg["value"]
                    if var_name in variables:
                        output_parts.append(str(variables[var_name]))
                    else:
                        output_parts.append(f"[Ошибка: переменная '{var_name}' не определена]")
            
            # Выводим все части через пробел
            print(" ".join(output_parts))
        
        elif command["command"] == "add":
            result = command["num1"] + command["num2"]
            print(f"Результат: {result}")
        
        elif command["command"] == "variable":
            variables[command["name"]] = command["value"]
        
        elif command["command"] == "input":
            value = process_input(command["type"])
            variables[command["name"]] = value
            # Убрал автоматический вывод для чистоты
            # print(f"Значение '{command['name']}' сохранено: {value}")


def execute_file(file_path):
    """Читает и выполняет код из файла."""
    variables = {}
    condition_stack = []
    
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    cleaned_lines = []
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    
    i = 0
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        
        try:
            tokens = lexer(line)
            parsed_command = parser(tokens, line)
            
            if parsed_command["command"] == "if":
                block_lines = [line]
                i += 1
                
                while i < len(cleaned_lines):
                    current_line = cleaned_lines[i]
                    current_tokens = lexer(current_line)
                    current_command = parser(current_tokens, current_line)
                    
                    block_lines.append(current_line)
                    
                    if current_command["command"] == "endif":
                        break
                    
                    i += 1
                
                execute_condition_block(block_lines, variables)
                
            else:
                interpreter(parsed_command, variables, condition_stack)
            
            i += 1
            
        except Exception as e:
            print(f"Ошибка при выполнении строки '{line}': {e}")
            i += 1


def execute_condition_block(block_lines, variables):
    """Выполняет блок условий (if-elif-else)."""
    condition_stack = []
    
    for line in block_lines:
        tokens = lexer(line)
        command = parser(tokens, line)
        
        if command["command"] == "if":
            result = evaluate_condition(command["left"], command["operator"], command["right"], variables)
            condition_stack.append({
                "active": result,
                "executed": result
            })
        
        elif command["command"] == "elif":
            if condition_stack:
                current = condition_stack[-1]
                should_execute = not current["executed"] and evaluate_condition(
                    command["left"], command["operator"], command["right"], variables
                )
                if should_execute:
                    current["executed"] = True
                condition_stack[-1]["active"] = should_execute
        
        elif command["command"] == "else":
            if condition_stack:
                current = condition_stack[-1]
                should_execute = not current["executed"]
                condition_stack[-1]["active"] = should_execute
                if should_execute:
                    current["executed"] = True
        
        elif command["command"] == "endif":
            if condition_stack:
                condition_stack.pop()
        
        else:
            if not condition_stack or condition_stack[-1]["active"]:
                temp_stack = condition_stack.copy() if condition_stack else []
                interpreter(command, variables, temp_stack)


if __name__ == "__main__":
    file_path = "sum.tcm"
    execute_file(file_path)
