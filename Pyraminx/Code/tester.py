from solver import *   # Use solver module and dependencies to test project code.
from sys import argv   # Used to take experiment inputs from the command line.
from os import listdir # Used to identify the contents of the pre-defined folder.

FOLDER_NAME = 'Experiments' # Pre-defined folder - used to store experiments.

def std_error():
    # Print error message relating to issues with standard input - then exit with error code 01.
    print('Three positive integer arguments required - tester.py [n_moves] [n_tests] [Document? y/n]')
    exit(1)

def experiment(n_moves, n_tests, documentation):
    '''
    Runs and documents randomized runs of the Master Pyraminx solver, 
    where requested variables k=n_moves and n=n_tests are given.\n
    Boolean flag (documentation) used to create and maintain record of each experiment.
    Flagged True/False on user request.
    '''
    # If documentation is flagged True...
    if (documentation):
        # Prepare a .CSV file to record the experiment.
        # Generate a filename specific to the given time.
        filename = f'Exp (k={n_moves}) - {time()}.csv'
        # If that filename already exists in the pre-defined directory...
        while (filename in listdir(FOLDER_NAME)):
            # Continue to define filenames until a unique one is found.
            filename = f'Exp (k={n_moves}) - {time()}.csv'
        # Open the determined CSV file for writing.
        fd = open(f'{FOLDER_NAME}\{filename}','w+')
        # Prepare column headers for each each variable.
        fd.write('Solution Length,Nodes Expanded,Runtime,Solution\n')
        # Note that Solution is usually a Comma-Separated List, and answers
        # can/will span multiple columns.
    
    # For each experiment requested...
    for i in range(0, n_tests):

        # Report the start of the experiment to the terminal.
        print(f'\nExperiment {i} - Start.')
        
        # Initialize a pyraminx with a solved state bit-pattern.
        p = pyraminx()
        
        # Randomly rotate the pyraminx (k=n_moves) times -- using ONLY
        # the odd-numbered (or clock-wise) moves.
        p.randomize(n_moves, set=ODD)

        # Attempt a solution (in under 10 minutes) using ONLY even-
        # numbered (or counter-clockwise) moves.
        sol, runtime, n_nodes = solve(p, set=EVEN, testing=True)

        # Report the end of the experiment to the terminal.
        print(f'Experiment {i} - Complete.')

        # If no solution was returned...
        if (type(sol) == type(None)):
            # The solver failed to find a solution in under 10 minutes.
            # (Failure has already been reported to terminal.)
            # If documentation is flagged True...
            if (documentation):
                # Write relevant results to the CSV file.
                fd.write(f'BAD,{n_nodes},{runtime},BAD\n')

            # Request user confirmation to continue the experiment.
            # Can and should be commented out for long-term unmanned tests.
            if(input('Quit? (y/n): ') == 'y'):
                if (documentation):
                    fd.close() # Close the CSV file if it exists.
                exit(0) # Exit without an error.

        # If a solution was returned...
        else:
            # Print the relevant data to the terminal.
            print(f'{len(sol)} moves, solved in {runtime:.10f} seconds: {sol}\n')
            # If documentation is flagged True...
            if (documentation):
                # Write relevant results to the CSV file.
                fd.write(f'{len(sol)},{n_nodes},{runtime},{sol}\n')

    # If documentation is flagged True...
    if (documentation):
        fd.close() # Close CSV file upon completion of experiment.

# Main Driver Code
if __name__ == '__main__':
    
    # Print indicative title to the terminal.
    print('Master Pyraminx Solver: Case-Testing')

    # Initialize variables for (k=n_moves) and (n=n_tests).
    n_moves = n_tests = 0

    # Check number of inputs to command line.
    if (len(argv) != 4): # If unexpected number...
        std_error()      # ...print standard error message and exit.
    try:
        # Attempt to convert standard inputs to...
        n_moves = int(argv[1]) # Integer for (k=n_moves)
        n_tests = int(argv[2]) # Integer for (n=n_tests)
        documentation = str(argv[3]).strip()[0].upper() # Character string for documentation flagging.

        # If any values are acceptable, but unexpected...
        if (n_moves < 0 or n_tests < 0 or (documentation != 'Y' and documentation != 'N')):
            std_error() # ...print standard error message and exit.
    
    # If any inputs are of unacceptable value or form...
    except ValueError or TypeError:
        std_error() # ...print standard error message and exit.
    
    # If documentation input is flagged as 'Y' for True...
    if documentation == 'Y':
        experiment(n_moves, n_tests, True) # ...document the experiment.
    else:
        experiment(n_moves, n_tests, False) # Otherwise, complete experiment w/o documentation.