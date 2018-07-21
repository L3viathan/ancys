import operator

_binops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "==": operator.eq,
    "!=": operator.ne,
    "and": operator.and_,
    "or": operator.or_,
}
_unops = {
    "!": operator.not_,
    "-": operator.neg,
}

def unevaluate(something, evaluated):
    if isinstance(something, tuple) and len(something) == 3:
        evaluated.pop(something[2], None)
        unevaluate(something[1], evaluated)
    elif isinstance(something, dict):
        for key in something:
            unevaluate(something[key], evaluated)
    elif isinstance(something, list):
        for element in something:
            unevaluate(element, evaluated)
    elif isinstance(something, tuple):
        for element in something:
            unevaluate(element, evaluated)

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
        condition = payload["condition"]
        body = payload["body"]
        if condition[2] in evaluated:
            if evaluated[condition[2]]:  # actual boolean test
                expressions.extend(body)
                evaluated[number] = True
            else:
                evaluated[number] = False
            return True
        else:
            expressions.append(condition)
        return False
    elif type_ == "while":
        condition = payload["condition"]
        body = payload["body"]
        if condition[2] in evaluated:
            if evaluated[condition[2]]:  # actual boolean test
                expressions.extend(body)
                evaluated[number] = True
                # retry after we are finished:
                # This works (hopefully) by putting a check on the queue. When
                # it runs, it first checks whether the while loop has
                # terminated (whether all inner expressions are evaluated). If
                # not, it reschedules itself. If yes, it invalidates
                # (unevaluates) all inner expressions recursively and then puts
                # the while loop back on the queue.
                expressions.append((
                    "while!",
                    payload,
                    ~number,
                ))
            else:
                # this will (hopefully) eventually be reached. When it is, we
                # don't schedule a while! check
                evaluated[number] = False
            return True
        else:
            expressions.append(condition)
        return False
    elif type_ == "while!":
        condition = payload["condition"]
        body = payload["body"]
        # First check if the while loop is done: In that case we reschedule
        if any(expr[2] not in evaluated for expr in body):
            return False
        # Next, we unevaluate all inner expressions
        unevaluate(body, evaluated)
        unevaluate(condition, evaluated)
        evaluated.pop(~number)

        # Finally, we reschedule the while loop:
        expressions.append(("while", payload, ~number))
        return True
    elif type_ in ["for", "for!"]:
        name = payload["name"]
        argument = payload["argument"]
        body = payload["body"]
        if argument[2] in evaluated:
            if type_ == "for!" and any(expr[2] not in evaluated for expr in body):
                # previous run isn't finished
                return False
            # unevaluate inner expressions
            unevaluate(body, evaluated)

            values = iter(evaluated[argument[2]])
            evaluated[argument[2]] = values
            try:
                value = next(values)
                environment[name] = value  # has to be evaluated already
                expressions.extend(body)
                expressions.append(("for!", payload, number))
            except StopIteration:
                evaluated[number] = True
            return True
        else:
            expressions.append(argument)
            return False
    elif type_ == "list":
        not_evaluated = [item for item in payload if item[2] not in evaluated]
        if not_evaluated:
            expressions.extend(not_evaluated)
            return False
        else:
            evaluated[number] = [evaluated[item[2]] for item in payload]
            return True
    else:
        raise NotImplementedError
