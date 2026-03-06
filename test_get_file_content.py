from functions.get_file_content import get_file_content

def test():
    result = get_file_content("calculator", "lorem.txt")
    print("Result for calculator/lorem.txt")
    print(result)
    print("")

    result = get_file_content("calculator", "main.py")
    print("Result for calculator/main.py")
    print(result)

    result = get_file_content("calculator", "pkg/calculator.py")
    print("Result for pkg/calculator.py")
    print(result)

    result = get_file_content("calculator", "/bin/cat")
    print("Result for bin/cat :")
    print(result)

    result = get_file_content("calculator", "pkg/does_not_exist.py")
    print("Result for pkg/doesnotexist:")
    print(result)

if __name__ == "__main__":
    test()