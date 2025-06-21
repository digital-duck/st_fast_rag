import asyncio

def outer_function():
    outer_var = "Hello" # Variable in the enclosing scope

    async def inner_function():
        nonlocal outer_var # Declare intent to modify outer_var
        outer_var += ", World!" # Modifies outer_var

    # Before calling inner_function, outer_var is "Hello"
    asyncio.run(inner_function())
    # After calling inner_function, outer_var is "Hello, World!"
    return outer_var

if __name__ == "__main__":
    print(outer_function())