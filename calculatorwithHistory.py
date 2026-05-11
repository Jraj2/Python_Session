HISTORY_FILE = "history.txt"

def show_history():
    file = open(HISTORY_FILE,'r')
    lines = file.readlines()
    if len(lines) == 0:
        print("No history found!")
    else:
        for line in reversed(lines):
            print(line.strip())
    file.close()

def clear_history():
    file = open(HISTORY_FILE,'w')
    file.close()
    print("History cleared")

def save_to_history(equation, result):
    file = open(HISTORY_FILE,'a')
    file.write(equation + "="+str(result)+ "\n")

def calculate(user_input):
    