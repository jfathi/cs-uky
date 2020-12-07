from master_pyraminx import *    # Pyraminx class developed in Project 1
from operator import attrgetter  # Used to sort the solver's list of open nodes
from time import time            # Used to determine the runtime of a solution
from math import ceil, sqrt      # Used to calculate heuristic values

def heuristic(p_state):
    '''
    Given state of the master pyraminx, 
    returns float guesstimate of steps toward a solution.\n
    Developed largely with Tony Chiu.
    '''
    # Declare temporary storage.
    bits = p_state.bits
    
    # If the given state is a solved state...
    if (bits == pyraminx().bits):
        return 0 # ...return a heuristic of 0.
    
    # For each face, define 4 smaller triangles of 4 bits each:
    tri1 = [2,0,1,3]    # "Top" Triangle, centered at bit 2(B).
    tri2 = [10,4,9,11]  # "Left" Triangle, centered at bit 10(K).
    tri3 = [6,5,7,12]   # "Center" Triangle, centered at bit 6(G)
    tri4 = [14,8,13,15] # "Right" Triangle, centered at bit 14(O)

    # Initialize two iterators for the hueristic counter.
    count1 = count2 = 0

    # For each face of the pyraminx...
    for face in bits:
        # and for each "triangle" on each face...
        for tri in [tri1, tri2, tri3, tri4]:
            # Consider the number of bits which are off-color...
            center_bit = tri[0] # ...in comparison to the "center" bit.
            for i in range(1,4):
                check_bit = tri[i]
                # If a bit is off-color from it's "center",
                if face[check_bit][0] != face[center_bit][0]: 
                    count1 += 0.5 # add a half-step to the 1st counter.
        # Consider the number of "center bits" which are off-color...
        center_bit = tri3[0] # ...in comparison to the face's "center" bit.
        for check_bit in [tri1[0], tri2[0], tri4[0]]:
            # If a center bit is off-color from the face's "center" bit,
            if face[check_bit][0] != face[center_bit][0]:
                count2 += .25 # add a fourth-step to the 2nd counter.
    
    # Return the sum of the roots of both counters.
    # Provides a signficantly faster solution for states of lower k.
    # Very reliable through k=6 moves of randomization.
    return sqrt(count1) + sqrt(count2)

class Node:
    def __init__(self, pyraminx, parent=None, next_move=None):
        '''
        Given a state of the Master Pyraminx, records bit-pattern,
        evaluates heuristic, and maintains list of moves from initial state.
        '''
        # Maintain pointer to parent Node, if it exists.
        self.parent = parent
        # Record the bit-pattern of the given state.
        self.bits = deepcopy(pyraminx.bits)
        # Initalize variables for...
        self.moves = [] # the list of moves from initial state
        self.g = 0      # number of steps taken from initial state.

        # If the parent Node exists
        if parent:
            # Iterate the number of steps from initial state by 1.
            self.g = parent.g + 1
            self.moves = deepcopy(parent.moves) # Copy parent's move-set...
            self.moves.append(next_move) # ...and append the next move given.
        
        # Calculate the heuristic of the given state/bit-pattern.
        self.h = heuristic(self)
        # Evaluate the heuristic and steps taken for the Node's current state.
        self.f = self.g + self.h

def solve(p_start, set=None, testing=False):
    '''
    Given an initial state of the Master Pyraminx, uses A* to return
    an solution set in approximately 10 minutes or less.\n
    Returns array of moves to solution, float runtime, 
    int number of nodes expanded\n.
    Use set=ODD or set=EVEN to restrict solver to clockwise, counter-clockwise moves.\n
    Use testing=True to ensure program will not end if solver fails.
    '''
    # Initialize the start, break time variables.
    start_time = time()
    break_time = time() - start_time # Program returns a failure after 10 minutes.

    # Create the first node using the given pyraminx state.
    start_node = Node(p_start, parent=None)

    # Initialize lists for open (to-be searched) nodes and closed (already-searched) nodes.
    open_list = []
    closed_list = []
    # Append the first node to the open list.
    open_list.append(start_node)

    # Allow for user to end solver using keyboard interrupt. (Ctl+C)
    try:
        # While a list of open nodes exists...
        while open_list: # If a possible solution exists, this logic block will always evaluate True.
            
            # Error Case - Solver has exceeded 10 minutes.
            # Failure is assumed and a non-solution is returned.
            if (break_time > 600):
                # Print message indicating failure to the terminal.
                print(f'Solution NOT found after {len(closed_list)} nodes expanded, {break_time:.10f} seconds.')
                # If testing is not flagged true (non-experiment case)...
                if (not testing): # ...exit the program with error code 01.
                    print('Program quit.\n')
                    exit(1)
                # Return non-solution, runtime and number of nodes expanded to the caller.
                return None, break_time, len(closed_list)
            
            # Evaluate the node at the top of the open list.
            current_node = open_list[0]
            
            # Initialize the current index as 0.
            current_idx = 0

            # (Used in most A* implementations.)
            # Confirm that current node has the lowest f-value of all other open nodes. 
            # If not, set the current node and index equal to those with the lowest f-value.
            # (Since open list is sorted at end of block, this step is unnecessary.)
            '''
            for idx, node in enumerate(open_list):
                if node.f < current_node.f:
                    current_idx, current_node = idx, node
            '''

            open_list.pop(current_idx) # Pop the node of the top of the open list...
            closed_list.append(current_node) # And append it to the closed list of evaluated nodes.

            # Check if the node currently being evaluated is the solve-state.
            if current_node.h == 0: # If so, print confirmation to the terminal...
                print(f'Solution found after {len(closed_list)} nodes expanded.')
                # ...and return move-set, runtime and number of nodes expanded to reach solution.
                return current_node.moves, time()-start_time, len(closed_list)

            # Since the current node is not the solve-state,
            # Initialize lists for the child moves and states of the current node. 
            move_nums = []
            children = []
            
            # If the solver is restricted to a set of moves (clockwise, counter-clockwise),
            if set: # initialize a list of corresponding numbered moves. (length = 12)
                for n in range(1, 13):
                    if set == EVEN:
                        move_nums.append(n * 2)
                    else:
                        move_nums.append(n)
            else: # Otherwise, generate a list of all possible moves,
                  # permitted that the next move does not reverse the previous one.
                  # (length = 24 for k = 1, 23 for k > 1)
                  # Clearly an error-prone implementation. Set method is favored.
                for n in range(1, 25):
                    move_nums.append(n)
                    if current_node.moves:
                        if ((n % 2 == 1) and (current_node.moves[-1] - n == 1))\
                        or ((n % 2 == 0) and (n - current_node.moves[-1] == 1)):
                            move_nums.pop()

            # While valid moves can be evaluated...
            while move_nums:
                # Randomly select a numbered move from the valid set.
                next_move = move_nums[randint(0, len(move_nums)-1)]
                # Generate a new pyraminx w/bit-pattern identical to current node's.
                new_p = pyraminx(bits = current_node.bits)
                # Rotate the pyraminx using the randomly selected move.
                new_p.move(next_move)
                # Generate node for new state and append to list of child nodes.
                children.append(Node(new_p, current_node, next_move))
                # Remove the selected move number from the unevaluated set.
                move_nums.remove(next_move)
            
            # For each child node...
            for child in children:
                # If the node has a bit-pattern that has already been evaluated...
                for node in closed_list:
                    if child.bits == node.bits:
                        continue # ...ignore it an move on.
                # If the node has a bit-pattern identical to an already open node...
                for node in open_list:
                    if child.bits == node.bits:
                        # ...and the new child takes less steps to reach the pattern...
                        if child.g < node.g:
                            node = child # ...set the open node equal to the child...
                        continue # ...and move on.
                # If a node has a new, unique bit-pattern, 
                # Append it to open list for evaluation.
                open_list.append(child)

            # Use the f-values of each node to sort the open list.
            open_list.sort(key=attrgetter('f'))

            # Record the amount of time that has passed since the solver started.
            break_time = time() - start_time
    
    # If the user requests the solver to quit...
    except KeyboardInterrupt:
        # Record the time and report failure to the terminal.
        fail_time = time()-start_time
        print(f'Solution NOT found after {len(closed_list)} nodes expanded, {fail_time:.10f} seconds.')
        # If testing is not flagged (non-experiment case)...
        if (not testing): # exit the program with error code 01.
            print('Program quit.\n')
            exit(1)
        # Return non-solution, runtime and number of nodes expanded to the caller.
        return None, fail_time, len(closed_list)     

# Main Driver Code 
if __name__ == '__main__':

    # Display Title
    print('Master Pyraminx Solver!')
    
    # Intialize a solved-state Master Pyraminx.
    p = pyraminx()
    
    # Until the user quits...
    while True:
        try:
            input('Press any key to continue... ') # Terminal break-line.

            # Verify that the pyraminx is solved.
            p.print()
            
            # Instruct the user on controls.
            print('Ctrl-C to Quit.')
            # Request input for the number of moves to randomize pyraminx.
            n = int(input('Input number of moves to be taken (0-20): '))
            
            # Ensure that the input is an integer between 0 and 20.
            if (n < 0 or n > 20):
                print('Input must be an integer between 0 and 20.')
            # Given acceptable input...
            else:
                # Randomize the pyraminx with the given number of steps.
                p.randomize(n, set=ODD) # Use ODD-numbered steps only.
                
                p.print() # Print the state of the randomized pyraminx.
                
                # Solve the pyraminx using EVEN-numbered steps only.
                sol, runtime, n_nodes = solve(p, set=EVEN)

                p.move(sol) # Use the returned solution to solve the pyraminx.

                # Print the number of random steps taken, and the returned
                # runtime and solution to the terminal.
                print(f'{n} moves, solved in {runtime:.10f} seconds: {sol}')
        
        # If an non-integer input is given,
        except ValueError or TypeError:
            # Display an error and request a new input.
            print('Input must be an integer between 0 and 20. Ctrl-C to Quit')

        # If the user inputs a keyboard interrupt, quit the program.
        except KeyboardInterrupt:
            print('\nProgram quit.\n')
            break