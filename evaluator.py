import operator

_binops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "==": operator.eq,
    "and": operator.and_,
    "or": operator.or_,
}
_unops = {
    "!": operator.not_,
    "-": operator.neg,
}

def evaluate(type_, payload, number, expressions, evaluated, environment):
    if number in evaluated:
        return True
    if type_ in ["int", "float", "bool", "string"]:
        # can immediately evaluate these
        evaluated[number] = payload
        return True
    elif type_ == "call":
        function = payload["function"]
        argument = payload["argument"]
        if function[2] in evaluated:
            if argument[2] in evaluated:
                # both are defined, we can actually call!
                evaluated[number] = evaluated[function[2]](
                    evaluated[argument[2]],
                )
                return True
            else:
                expressions.append(argument)
        else:
            expressions.append(function)
        return False
    elif type_ == "name":
        if payload in environment:
            # name is defined: assign its value to the expression
            evaluated[number] = environment[payload]
            return True
        return False
    elif type_ == "assignment":
        name = payload["name"]  # string
        value = payload["value"]  # expression
        if value[2] in evaluated:
            environment[name] = evaluated[value[2]]
            evaluated[number] = evaluated[value[2]]  # assignments return their value
            return True
        else:
            expressions.append(value)
        return False
    elif type_ == "binop":
        left = payload["left"]
        right = payload["right"]
        op = payload["operation"]
        if left[2] in evaluated:
            if right[2] in evaluated:
                evaluated[number] = _binops[op](
                    evaluated[left[2]],
                    evaluated[right[2]],
                )
                return True
            else:
                expressions.append(right)
        else:
            expressions.append(left)
        return False
    elif type_ == "unop":
        right = payload["right"]
        op = payload["operation"]
        if right[2] in evaluated:
            evaluated[number] = _unops[op](
                evaluated[right[2]],
            )
            return True
        else:
            expressions.append(right)
        return False
    elif type_ == "if":
        ...
    elif type_ == "while":
        ...
    elif type_ == "for":
        ...
    elif type_ == "list":
        ...
    else:
        raise NotImplementedError
