# sancy

yacns (a recursive backronym for New Asyncronous Computation YCNAS System) is a fully asynchronous* programming language.

## Principles:

- The program is (probably) not executed from top to bottom, but instead in a random order.
- At startup, all top-level expressions (those written directly in the file, seperated by semicolons) are scheduled to be executed at some point. When an expression is chosen, it first checks if it has unevaluated sub-expressions. If so, it schedules these, and asks the interpreter to come back later. If it has no unevaluated sub-expressions, it itself will be evaluated/executed.
- Expressions that depend on names (variables) will not run until the names that are used are defined. That means that your program will (currently) hang indefinitely if you misspell a name. On the other hand, you don't need to worry about execution order if the dependency is clear.

For example, the following program prints `23` regardless of the order of execution.

    print(x);
    x = 23;

- Due to the current implementation, all asncy programs have technically a worst-time complexity of O(Infinity).
- The only things that have order are lists and loops. There are two types of loops, `for` and `while`. A `while` loop guarantees that different executions of its body are not overlapping. For example, `x=5; while x != 0 {x = x - 1; print(x);}` will never print 5 zeroes or 5 ones. It might however print something like `5 3 3 2 0`, because sometimes the assignment is executed first, sometimes the print statement. `for` loops iterate over their argument in order, in a similar way.
- There are no statements (or at least no difference between a statement and an expression). All expressions have a value, including control structures like `if`, and assignments (like in C).
