from functions.write_file import write_file

def test():
    result = write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum")
    print("Result for calculator/lorem.txt")
    print(result)
    print("")

    result = write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")
    print("Result for pkg/morelorem.txt")
    print(result)

    result = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    print("Result for tmp/temp.txt :")
    print(result)

if __name__ == "__main__":
    test()