CS-463G-001: Program #1, Pyraminx Modeling
Prepared by Javid Fathi for Dr. Judy Goldsmith, September 2020
=========================================================================
INCLUDED FILES:
=========================================================================
    master_pyraminx.py
    randomizer.py
    README.txt
=========================================================================
HOW TO RUN:
=========================================================================

    Command line: py ./randomizer.py

    Note: Single-run program. Above command must be re-run for multiple tests.
    
    Sample Runs. '>' indicates terminal input.
    Sample Run 1:
        > py ./randomizer.py

        # GUI OF UNMIXED PYRAMINX #

        Enter number of tuns: > 20
        20 turns requested!
        20 turns completed!

        # GUI OF MIXED PYRAMINX #

    Sample Run 2:
        > py ./randomizer.py

        # GUI OF UNMIXED PYRAMINX #

        Enter number of turns: > 0
        0 turns requested!
        0 turns completed!
        
        # GUI OF UNMIXED PYRAMINX #

    Sample Run 3:
        > py ./randomizer.py

        # GUI OF UNMIXED PYRAMINX #

        Enter number of turns: > 10001
        It is not suggested that more than 10000 turns be used.
        Confirm request for 10001 turns (Y/N): > Yes
        10001 turns requested!
        10001 turns completed!

        # GUI OF MIXED PYRAMINX #

    Sample Run 4:
        > py ./randomizer.py

        # GUI OF UNMIXED PYRAMINX #

        Enter number of turns: 100000
        It is not suggested that more than 10000 turns be used.
        Confirm request for 100000 turns (Y/N): > sure
        Invalid input. Confirm request for 100000 turns (Y/N): > nah
        Request withdrawn.

        Enter number of turns: 10
        10 turns requested!
        10 turns completed!

        # GUI OF MIXED PYRAMINX #    
    
    Sample Run 5:
        > py ./randomizer.py

        # GUI OF UNMIXED PYRAMINX #

        Enter number of turns: > -1
        Invalid input. Please enter a non-negative integer.

        Enter number of turns: > what's a number?
        Invalid input. Please enter a non-negative integer.

        Enter number of turns: > Ctl+C KeyBoard Interrupt.
        Unexpected quit.

=========================================================================
PROGRAM WRITE-UP:
=========================================================================
Terminology: Bits == "Pyramidies" (Dr. Goldsmith's words, not mine.) :-)

Pyraminx Data Structure:

    - The Master Pyraminx was implemented through class methods:

        - __init__():
            Initializes a 2D array (bits), where bits[i][j] represents the
            bit in the jth position on the ith face. 
                It should be noted that side and position numbers are 
                selected arbitrarily, such that 3 faces have the same 
                "ordering" when rotated on a single axis - making 
                implementation much easier for some rotation methods.
                At initialization,
                    Side 1 is RED,
                    Side 2 is YELLOW,
                    Side 3 is BLUE, and
                    Side 4 is GREEN.
                    Bits 0 through 15 are denoted by an corresponding 
                    ASCII character (a through p).
            Each bit representation (bits[i][j]) is a tuple (color, position), 
            representing the color and original position of the selected bit.
                Color is represented by one of four Colorama byte codes,
                which are used to display an identifying color to the terminal.
                Original position is represented by a letter (a-p), which are
                displayed to the terminal to identify changes in position via
                rotation methods.

        - print():
            Provides a visual representaion of the pyraminx model to the terminal.
            Each side is represented by ASCII pyramids:
                Uses each bit's tuple values to display a letter and color to 
                represent those of the bit in each position. Relies on Python's 
                Colorama module to properly display colors to the terminal user.
            The first three sides are represented by descending (tip-top) pyramids, 
            and the fourth side is represented by an ansceding (bottoms-up) pyramid.
            For loops and print statements are heavily used to create a appealing,
            uniform graphic.

        - Rotation Methods:
            Rotation methods encode bit tuples to other bits as they
            would be expected to rotate on a real pyraminx. This means
            that the rotation of any one bit will always change two other bits.
            Most methods hard-code bit rotations, and for loops are used
            when reasonable. (See pyr1_rCW and big_pyr1_rCW). 
            Affected bits (i.e.: [side][position]) are indicated before 
            each encoding, denoting the "circular" pattern that these groupings 
            value. Other patterns - such as repeating bit values in rotation 
            groupings - are also observable.
            Rotation methods can be broken down into three categories:
            1) Tips (1 layer "pyramids" - edge pieces)
            2) Pyramids (2 layer pyramids - surrounding respective edge pieces)
            3) Big Pyramids (3 layer pyramids - surround respective 2 layer pyramids)
            Each category has four methods which rotate pyraminx bits
            clockwise - and four more methods which rotate the bits 
            counter-clockwise. Overall, there are 24 unique rotation methods.
                For ease of implementation, the counter-clockwise methods
                call their respective clockwise method twice. For the same
                reason, most pyramid and big pyramid methods invoke the 
                next smallest method - tips and pyramids, respectively - 
                thereby eliminating redundant code.

        - randomize(num_turns):
            The randomize function uses a given number of turns to mix the
            pyraminx bits onto different faces and positions. These rotations are
            implemented solely through the class' 24 rotation methods.
            Each rotation method is assigned an integer and has an opposite method
            which would reverse its rotation.
                i.e: Method 01 (tip1_rCW)     opposes Method 02 (tip1_rCCW),
                     Method 23 (big_pyr4_rCW) opposes Method 24 (big_pyr4_rCCW)
            For each requested turn,
                A variable (next_move) is assiged a random integer between 1 and 
                24, representing the random selection of a particular rotation 
                method. An additional variable (last_move) is used to track the 
                the most recent move taken. (Initially, last_move = next_move = -1)
                If the next move requested directly counters the move preceding it,
                another move is chosen in its place.
                    While this implementation does not guarantee against an opposite 
                    method undoing the changes of a preceding one - or a set of 
                    methods changing a preceding set - it makes such "reversal" 
                    signficantly less likely.
            After the specified number of rotations have been completed, the
            randomization is completed.
                Print functions are used to indicate the start and end of the
                process - to account for requests which may take longer for
                the randomizer to complete (10001+).
                    

GUI implementation Notes: 
    See print() documentation above.

Randomizer:

    -  The randomizer was implmented through a combination of class methods
       and driver functions:

        - Class Methods:
            See randomize(num_turns) documentation above.

        - Driver Functions:
            
            In this implementation, the driver only serves a single use each 
            time that the program is run.

            - user_request():
                This function is a simple, error-protected input function from 
                the user. Outputs the requested non-negative integer number of 
                rotations used to randomize the pyraminx.
                Provides a warning if the user requests more than 10000 rotations
                to protect against memory overflow. User must confirm (Y/N) if 
                program is to use 10,001 rotations or more.

            - main():
                Declares, initializes and prints an unmixed Master Pyraminx.
                Invokes user_request() to determine the number of requested rotations.
                Uses pyraminx class method - .randomize() - to complete requested 
                number of rotations. Prints the mixed Master Pyraminx and closes the program.

Heuristic:

    A significant portion of this assignment was dedicated to developing a heuristic which
    could be used to solve the pyraminx - or identify a series of rotations which would
    place it in a goal state.

        For this problem, a goal state - or solved state - would be an unmixed pyraminx,
        where all four sides of the pyraminx have a single color, AND all sides
        of the pyraminx have bits of different colors.

    We will describe this problem is described by the admissible evaluation function:
        F(s) = G(s) + H(s), where
            G(s) is the number of turns taken to reach state s, starting from an initial 
            state (s=0).
                G(0) = 0
                G(c) = 1 if c is an immediate child of the initial state.
                    Thus, all child states increment a cost of one from the cost of 
                    their respective parent state.
            H(s) is the expected number of moves to reach the goal state (s=f) from a 
            state s.
                H(f) = 0
            F(s) is the expected number of moves to reach the goal state (s=f) from the 
            initial state (s=0).
                F(0) = H(0)
                F(f) = G(f)
        For F to be admissible, the expected number of moves cannot exceed the actual 
        number of moves that will be taken, thus
            H(s) must be less than or equal to the G(s) for all states s.
        

    For the purposes of this assignment, I have considered the solve-state (0-1) as a 
    heuristic evaluation function, where:
        H(s) = 0 iff the pyraminx is in a solved state, and
        H(s) = 1 under any other conditions.
    Practically, this means that if the pyraminx is in an unsolved state, it will take
    at least one more move to solve the puzzle. This is reasonable, and we can use
    a few examples to prove it.

    Evaluation One:
        Evaluate State 0:
            G(0) = 0
            Pyraminx is: solved
                Therefore, H(0) = 0
            F(0) = G(0) + H(0) = 0
        Therefore, zero moves are required to reach the goal state (0) from the
        initial state (0).
    
    Evaluation Two:
        Evaluate State 0:
            G(0) = 0
            Pyraminx is: not solved
                Therefore, H(0) = 1
            F(0) = G(0) + H(0) = 1
        Therefore, at least one moves is required to reach the goal state from 
        state 0.

        Identify Children of State 0:
            State 1
            State 2
            ...
            State 24

        Identify Child with Lowest Cost: State 1
        (Since all child states increment a cost of 1 from their parent, we choose
        this arbitrarily.)

        Evaluate State 1:
            G(1) = 1
            Pyraminx is: not solved
                Therefore, H(1) = 1
            F(1) = G(1) + H(1) = 2
        Therefore, at least two moves are required to reach the goal state from 
        state 0 through state 1.

        Evaluate Child with Next Lowest Cost: State 2
        ...
        The cycle continues...
        ...
        Evaluate Child with Next Lowest Cost: State 24
            G(24) = 1
            Pyraminx is: solved
                Therefore, H(24) = 0
            F(24) = G(24) + H(24) = 1
        Therefore, one moves is required to reach the goal state (24) from the
        initial state (0).

    The benefit to using this type of heuristic is that it is guaranteed to find
    the smallest cost (and the shortest path) to reach a solved state, since we
    are certain that the problem is solvable.
        The same rotations methods that were used to randomize the pyraminx
        are also being used to bring it back to a solved state!

    The detriment - and this is a huge detriment - is the memory requirement.
    Even from Evaluation Two, it is clear that the function must queue an 
    expontentially increasing number of states to solve the function.
        Suppose we determine that the initial state (s=0) is unsolved, and
        subsequently expand its child states:
            Rotation of Tip 1, Clockwise (s=1),
            Rotation of Tip 1, Counter-Clockwise (s=2),
            ...
            Rotation of Big Pyramid 4, Clockwise (s=23),
            Rotation of Big Pyramid 4, Counter-Clockwise (s=24)
        Now, suppose that none of the child states are solved.
        Even if the function were to eliminate a single, opposing method - to
        eliminate reversal - in each subsequent turn, the number of children to 
        queue at each "level" increases dramatically.
            1 -> 24 -> 552 -> 12696 -> 292008

    For this reasons, I cannot recommended that this heuristic be used to
    evaluate the master pyraminx. Unless we crack and commercialize quantum
    computing over the weekend, a better heurtistic will need to be identified
    for this problem to be realistically solved by a computer.

Learning Outcome:

    I sat down to write this program with little initial planning beforehand, but
    felt pretty good about my work. After 4 hours of work over two days, I figured
    that I was finished my rotation methods! ...Until I realized that I had spent
    that time encoding a 3x3x4 model instead of a 4x4x4 one.

    I (gave myself a day to sulk, and then) took three more days to re-write the
    program, now in the form of a class implementation rather than a pure
    driver format. Again, this was with little planning as to how the GUI or
    randomizer would work. The problem was simple, but still worthy of a detailed
    design.

    In short, I've learned three lessons from this project:
        1) Start early if you can,
        2) start on by designing your program on paper, and
        3) always, always, ALWAYS read the specifications carefully.

    (I also learned a little about heuristics. Although I had a hard time
    identifying an admissible one for this project, I understand the concept 
    much better now.)
    
    Hopefully I take these lessons to heart. Happy grading!
    [NAME REDACTED]
=========================================================================
REFERENCES:
=========================================================================
    - Viewed classmate's (Will Berry) terminal output of as reference for GUI.
      We did NOT compare or develop code together. (His solution is probably 
      way more efficient, anyway.)

    - Borrowed error handling in the randomizer's user_request() function from
      a personal implementation for a CS-115 project. (Available on request.)

    - Mistakenly developed a 3x3x4 Pyraminx for this assignment, originally.
      Coding methods referenced, but not copied. (Available on request.)

    - This 3D Master Myraminx model was heavily referenced during modeling,
      bit "encoding"/rotation.
      Source: https://www.grubiks.com/puzzles/master-pyraminx-4x4x4/

    - Referenced 2D 3x3x4 Pyraminx model when developing original solution.
      Used to develop "bit encoding" method.
      Source: https://rubiks-cube-solver.com/pyraminx/    

    - Referenced Geeks for Geeks on how to use the colorama module.
      (Recommended by Will Berry)
      Source: https://www.geeksforgeeks.org/print-colors-python-terminal/

    - Referenced Stack Overflow code to assert characters
      [i.e.: ord('a'), ord('z')+ 1] to pyraminx bits via a for loop.
      Source: https://stackoverflow.com/questions/32799607/how-to-create-a-loop-from-1-9-and-from-a-z/32799657
