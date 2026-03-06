from functions.run_python_file import run_python_file

def test():
    result = run_python_file("calculator", "main.py")
    print("Result for calculator/main.py")
    print(result)
    print("")

    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print("Result for calculator , main.py, [3 + 5]")
    print(result)

    result = run_python_file("calculator", "tests.py")
    print("Result for running tests :")
    print(result)

    result = run_python_file("calculator", "../main.py")
    print("Result for running ../main.py :")
    print(result)

    result = run_python_file("calculator", "nonexistent.py")
    print("Result for running not existing py :")
    print(result)

    result = run_python_file("calculator", "lorem.txt")
    print("Result for running txt  :")
    print(result)

    
if __name__ == "__main__":
    test()