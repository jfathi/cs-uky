from master_pyraminx import *

# Get the needed piece of data from the user, number of bits (a whole number).
def user_request(): 
    num_turns = 0
    while (True):
        try:
            # Request number of turns to randomize the pyraminx.
            num_turns = int(input('Enter number of turns: '))
            # Deny Impossible Request (< 0 turns)
            if (num_turns < 0):
                print('Invalid input. Please enter a non-negative integer.', end='\n\n')
            # Confirm Excessive Request (10001+ turns)
            elif (num_turns > 20):
                print('It is not suggested that more than 20 turns be used.')
                request = False
                while (request is not True):
                    confirmation = input(f'Confirm request for {num_turns} turns (Y/N): ').upper().strip()                        
                    # Excessive Request withdrawn. Request integer input again.
                    if (confirmation[0] is NO):
                        print('Request withdrawn.', end='\n\n')
                        break
                    # Excessive request confirmed. Return request to caller.
                    elif (confirmation[0] is YES):
                        request = True
                        break
                    else:
                        print('Invalid input.', end=' ')   
                # Excessive request confirmed. Return request to caller.
                if (request):
                    break
            else:
                break
        # Deny Non-Integer Request
        except ValueError:
            print('Invalid input. Please enter a non-negative integer.', end='\n\n')
        # Program Termination
        except KeyboardInterrupt:
            print('Keyboard Interrupt.\nUnexpected quit.', end='\n\n')
            exit()
    # Deliver requested number of rotations to randomize method.
    return num_turns

def main():
    # Declare and initialize Master Pyraminx object.
    my_pyraminx = pyraminx()
    # Print initial GUI of the Pyraminx to the terminal.
    my_pyraminx.print()
    # Randomize the Pyraminx through standard rotations -
    # based on a requested number by the user.
    my_pyraminx.randomize(user_request())
    # Print the randomized/mixed Pyraminx to the terminal.
    my_pyraminx.print()
main()