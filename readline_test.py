import readline

print("heero der")


def main():
    print("we are in the main")

    history = '\n'.join([str(readline.get_history_item(i+1)) for i in range(readline.get_current_history_length())])

    print("end - showing history")

    print((history,))


main()
