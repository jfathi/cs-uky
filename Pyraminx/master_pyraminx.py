# Utilizing Colorama byte-codes to display/differentiate face/bit colors.
from colorama import Fore

# Used to implement movement randomization.
from random import randint, randrange

# Used to maintain copies of bit-patterns, relevant objects.
from copy import deepcopy

# Ordered byte-codes used to display/differentiate face/bit colors.
COLORS = [Fore.RED, Fore.YELLOW, Fore.BLUE, Fore.GREEN]
YES = 'Y'
NO  = 'N'
ODD  = 1
EVEN = 2

class pyraminx:
    def __init__(self, bits = None):
        '''
        Intialize a pyraminx object.\n
        If no bit-pattern given, generate a solved-state bit-pattern.\n
        bits=p.bits sets object's bit-pattern equal to p's bit-pattern.
        '''
        # If no bit-pattern is given...
        if not bits:
            # Initialize a solved-state bit-pattern...
            self.bits = []
            # ...using the Colorama byte-codes...
            for color in COLORS:
                new_side = []
                # ...and letter orderings from a to p...
                for x in range(ord('a'), ord('p')+1):
                    new_side.append((color, chr(x))) # ...for each bit...
                self.bits.append(new_side) # ...on each side.
        else:
            # Otherwise, maintain a copy of the given bit-pattern.
            self.bits = deepcopy(bits)

    def print(self):
        '''
        Print pyraminx bit-pattern to terminal using Colorama byte-codes.
        '''
        bits = self.bits
        print()
        # Sides One through Three
        for side in range(0,3):
            # Line One (Bit 0)
            print(end='      ')
            print(bits[side][0][0] + bits[side][0][1])
            # Line Two (Bits 1-3)
            print(end='    ')
            print(bits[side][1][0] + bits[side][1][1], bits[side][2][0] + bits[side][2][1], bits[side][3][0] + bits[side][3][1])
            # Line Three (Bits 4-8)
            print(end='  ')
            print(bits[side][4][0] + bits[side][4][1], bits[side][5][0] + bits[side][5][1], bits[side][6][0] + bits[side][6][1], end=' ')
            print(bits[side][7][0] + bits[side][7][1], bits[side][8][0] + bits[side][8][1])
            # Line Four (Bits 9-15)
            print(bits[side][9][0] + bits[side][9][1], bits[side][10][0] + bits[side][10][1], bits[side][11][0] + bits[side][11][1], end=' ')
            print(bits[side][12][0] + bits[side][12][1], bits[side][13][0] + bits[side][13][1], bits[side][14][0] + bits[side][14][1], end=' ')
            print(bits[side][15][0] + bits[side][15][1], end='\n\n')

        # Side Four
        # Line Four (Bits 15-9)
        print(bits[3][15][0] + bits[3][15][1], bits[3][14][0] + bits[3][14][1], bits[3][13][0] + bits[3][13][1], end=' ')
        print(bits[3][12][0] + bits[3][12][1], bits[3][11][0] + bits[3][11][1], bits[3][10][0] + bits[3][10][1], bits[3][9][0] + bits[3][9][1])
        # Line Three (Bits 8-4)
        print(end='  ')
        print(bits[3][8][0] + bits[3][8][1], bits[3][7][0] + bits[3][7][1], bits[3][6][0] + bits[3][6][1], end=' ')
        print(bits[3][5][0] + bits[3][5][1], bits[3][4][0] + bits[3][4][1])
        # Line Two (Bits 3-1)
        print(end='    ')
        print(bits[3][3][0] + bits[3][3][1], bits[3][2][0] + bits[3][2][1], bits[3][1][0] + bits[3][1][1])
        # Line One (Bit 0)
        print(end='      ')
        print(bits[3][0][0] + bits[3][0][1])
        print(Fore.WHITE)

    # Rotation Method 1 - Tip 1 Rotation, Clockwise
    def tip1_rCW(self): # Standard: RYB
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 -> 2 -> 1 -> 0 ...
        # Bits: Special Mapping Case!
        # All bits mapped to "same" positions on other faces.
        bits[0][0], bits[1][0], bits[2][0] = bits[1][0], bits[2][0], bits[0][0]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 2 - Tip 1 Rotation, Counter-Clockwise
    def tip1_rCCW(self):
        self.tip1_rCW()
        self.tip1_rCW()

    # Rotation Method 3 - Tip 2 Rotation, Clockwise
    def tip2_rCW(self): # Standard: RGY
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 ->  1 -> 3 -> 0 ...
        # Bits:  9 -> 15 -> 0 -> 9 ...
        bits[0][9], bits[3][0], bits[1][15] = bits[3][0], bits[1][15], bits[0][9]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 4 - Tip 2 Rotation, Counter-Clockwise
    def tip2_rCCW(self):
        self.tip2_rCW()
        self.tip2_rCW()

    # Rotation Method 5 - Tip 3 Rotation, Clockwise
    def tip3_rCW(self): # Standard: RBG
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 ->  3 -> 2 -> 0 ...
        # Bits: 15 -> 15 -> 9 -> 15 ...
        bits[0][15], bits[2][9], bits[3][15] = bits[2][9], bits[3][15], bits[0][15]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 6 - Tip 3 Rotation, Counter-Clockwise
    def tip3_rCCW(self):
        self.tip3_rCW()
        self.tip3_rCW()

    # Rotation Method 7 - Tip 4 Rotation, Clockwise
    def tip4_rCW(self): # Standard: GBY
        # Declare temporary storage.
        bits = self.bits
        # Faces: 1 -> 2 -> 3 -> 1 ...
        # Bits: 9 -> 15 -> 9 -> 9 ...
        bits[1][9], bits[3][9], bits[2][15] = bits[3][9], bits[2][15], bits[1][9]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 8 - Tip 4 Rotation, Counter-Clockwise
    def tip4_rCCW(self):
        self.tip4_rCW()
        self.tip4_rCW()
    
    # Rotation Method 9 - Pyramid 1 Rotation, Clockwise
    def pyr1_rCW(self):
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 -> 2 -> 1 -> 0 ...
        # Bits: Special Mapping Case!
        # All bits mapped to "same" positions on other faces.
        for i in range(0,4):
            bits[0][i], bits[1][i], bits[2][i] = bits[1][i], bits[2][i], bits[0][i]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 10 - Pyramid 1 Rotation, Counter-Clockwise
    def pyr1_rCCW(self):
        self.pyr1_rCW()
        self.pyr1_rCW()

    # Rotation Method 11 - Pyramid 2 Rotation, Clockwise
    def pyr2_rCW(self):
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 ->  1 -> 3 -> 0 ...
        # Bits:  4 -> 13 -> 3 -> 4 ...
        bits[0][4], bits[3][3], bits[1][13] = bits[3][3], bits[1][13], bits[0][4]
        # Faces: 0 ->  1 -> 3 -> 0 ...
        # Bits:  9 -> 15 -> 0 -> 9 ...
        self.tip2_rCW()
        # Faces: 0 ->  1 -> 3 ->  0 ...
        # Bits: 10 -> 14 -> 2 -> 10 ...
        bits[0][10], bits[3][2], bits[1][14] = bits[3][2], bits[1][14], bits[0][10]
        # Faces: 0 -> 1 -> 3 ->  0 ...
        # Bits: 11 -> 8 -> 1 -> 11 ...
        bits[0][11], bits[3][1], bits[1][8] = bits[3][1], bits[1][8], bits[0][11]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 12 - Pyramid 2 Rotation, Counter-Clockwise
    def pyr2_rCCW(self):
        self.pyr2_rCW()
        self.pyr2_rCW()

    # Rotation Method 13 - Pyramid 3 Rotation, Clockwise
    def pyr3_rCW(self):
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 -> 3 ->  2 -> 0 ...
        # Bits:  8 -> 8 -> 11 -> 8 ...
        bits[0][8], bits[2][11], bits[3][8] = bits[2][11], bits[3][8], bits[0][8]
        # Faces: 0 ->  3 -> 2 ->  0 ...
        # Bits: 13 -> 13 -> 4 -> 13 ...
        bits[0][13], bits[2][4], bits[3][13] = bits[2][4], bits[3][13], bits[0][13]
        # Faces: 0 ->  3 ->  2 ->  0 ...
        # Bits: 14 -> 14 -> 10 -> 14 ...
        bits[0][14], bits[2][10], bits[3][14] = bits[2][10], bits[3][14], bits[0][14]
        # Faces: 0 ->  3 -> 2 ->  0 ...
        # Bits: 15 -> 15 -> 9 -> 15 ...
        self.tip3_rCW()
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 14 - Pyramid 3 Rotation, Counter-Clockwise
    def pyr3_rCCW(self):
        self.pyr3_rCW()
        self.pyr3_rCW()
    
    # Rotation Method 15 - Pyramid 4 Rotation, Clockwise
    def pyr4_rCW(self): 
        bits = self.bits
        # Faces: 1 ->  2 -> 3 -> 1 ...
        # Bits:  4 -> 13 -> 4 -> 4 ...
        bits[1][4], bits[3][4], bits[2][13] = bits[3][4], bits[2][13], bits[1][4]
        # Faces: 1 ->  2 -> 3 -> 1 ...
        # Bits:  9 -> 15 -> 9 -> 9 ...
        self.tip4_rCW()
        # Faces: 1 ->  2 ->  3 ->  1 ...
        # Bits: 10 -> 14 -> 10 -> 10 ...
        bits[1][10], bits[3][10], bits[2][14] = bits[3][10], bits[2][14], bits[1][10]
        # Faces: 1 -> 2 ->  3 ->  1 ...
        # Bits: 11 -> 8 -> 11 -> 11 ...
        bits[1][11], bits[3][11], bits[2][8] = bits[3][11], bits[2][8], bits[1][11]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits
    
    # Rotation Method 16 - Pyramid 4 Rotation, Counter-Clockwise
    def pyr4_rCCW(self):
        self.pyr4_rCW()
        self.pyr4_rCW()
    
    # Rotation Method 17 - Big Pyramid 1 Rotation, Clockwise
    def big_pyr1_rCW(self):
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 -> 2 -> 1 -> 0 ...
        # Bits: Special Mapping Case!
        # All bits mapped to "same" positions on other faces.
        for i in range(0,9):
            bits[0][i], bits[1][i], bits[2][i] = bits[1][i], bits[2][i], bits[0][i]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 18 - Big Pyramid 1 Rotation, Counter-Clockwise
    def big_pyr1_rCCW(self):
        self.big_pyr1_rCW()
        self.big_pyr1_rCW()

    # Rotation Method 19 - Big Pyramid 2 Rotation, Clockwise
    def big_pyr2_rCW(self):
        # Complcete sub-rotation.
        self.pyr2_rCW()
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 ->  1 -> 3 -> 0 ...
        # Bits:  1 -> 11 -> 8 -> 1 ...
        bits[0][1], bits[3][8], bits[1][11] = bits[3][8], bits[1][11], bits[0][1]
        # Faces: 0 ->  1 -> 3 -> 0 ...
        # Bits:  5 -> 12 -> 7 -> 5 ...
        bits[0][5], bits[3][7], bits[1][12] = bits[3][7], bits[1][12], bits[0][5]
        # Faces: 0 -> 1 -> 3 -> 0 ...
        # Bits:  6 -> 6 -> 6 -> 6 ...
        bits[0][6], bits[3][6], bits[1][6] = bits[3][6], bits[1][6], bits[0][6]
        # Faces: 0 -> 1 -> 3 ->  0 ...
        # Bits: 12 -> 7 -> 5 -> 12 ...
        bits[0][12], bits[3][5], bits[1][7] = bits[3][5], bits[1][7], bits[0][12]
        # Faces: 0 -> 1 -> 3 ->  0 ...
        # Bits: 13 -> 3 -> 4 -> 13 ...
        bits[0][13], bits[3][4], bits[1][3] = bits[3][4], bits[1][3], bits[0][13]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 20 - Big Pyramid 2 Rotation, Counter-Clockwise
    def big_pyr2_rCCW(self):
        self.big_pyr2_rCW()
        self.big_pyr2_rCW()

    # Rotation Method 21 - Big Pyramid 3 Rotation, Clockwise
    def big_pyr3_rCW(self):
        # Complcete sub-rotation.
        self.pyr3_rCW()
        # Declare temporary storage.
        bits = self.bits
        # Faces: 0 -> 3 ->  2 -> 0 ...
        # Bits:  3 -> 3 -> 13 -> 3 ...
        bits[0][3], bits[2][13], bits[3][3] = bits[2][13], bits[3][3], bits[0][3]
        # Faces: 0 -> 3 -> 2 -> 0 ...
        # Bits:  6 -> 6 -> 6 -> 6 ...
        bits[0][6], bits[2][6], bits[3][6] = bits[2][6], bits[3][6], bits[0][6]
        # Faces: 0 -> 3 -> 2  -> 0 ...
        # Bits:  7 -> 7 -> 12 -> 7 ...
        bits[0][7], bits[2][12], bits[3][7] = bits[2][12], bits[3][7], bits[0][7]
        # Faces: 0 -> 3  -> 2 ->  0 ...
        # Bits: 11 -> 11 -> 1 -> 11 ...
        bits[0][11], bits[2][1], bits[3][11] = bits[2][1], bits[3][11], bits[0][11]
        # Faces: 0 -> 3  -> 2 ->  0 ...
        # Bits: 12 -> 12 -> 4 -> 12 ...
        bits[0][12], bits[2][5], bits[3][12] = bits[2][5], bits[3][12], bits[0][12]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits
   
    # Rotation Method 22 - Big Pyramid 3 Rotation, Counter-Clockwise
    def big_pyr3_rCCW(self):
        self.big_pyr3_rCW()
        self.big_pyr3_rCW()
    
    # Rotation Method 23 - Big Pyramid 4 Rotation, Clockwise
    def big_pyr4_rCW(self):
        # Complcete sub-rotation.
        self.pyr4_rCW()
        # Declare temporary storage.
        bits = self.bits
        # Faces: 1 ->  2 -> 3 -> 1 ...
        # Bits:  1 -> 11 -> 1 -> 1 ...
        bits[1][1], bits[3][1], bits[2][11] = bits[3][1], bits[2][11], bits[1][1]
        # Faces: 1 ->  2 -> 3 -> 1 ...
        # Bits:  5 -> 12 -> 5 -> 5 ...
        bits[1][5], bits[3][5], bits[2][12] = bits[3][5], bits[2][12], bits[1][5]
        # Faces: 1 -> 2 -> 3 -> 1 ...
        # Bits:  6 -> 6 -> 6 -> 6 ...
        bits[1][6], bits[3][6], bits[2][6] = bits[3][6], bits[2][6], bits[1][6]
        # Faces:  1 -> 2 ->  3 -> 1 ...
        # Bits:  12 -> 7 -> 12 -> 12 ...
        bits[1][12], bits[3][12], bits[2][7] = bits[3][12], bits[2][7], bits[1][12]
        # Faces:  1 -> 2 ->  3 ->  1 ...
        # Bits:  13 -> 3 -> 13 -> 13 ...
        bits[1][13], bits[3][13], bits[2][3] = bits[3][13], bits[2][3], bits[1][13]
        # Set pyraminx bits to newly assigned values. 
        self.bits = bits

    # Rotation Method 24 - Big Pyramid 4 Rotation, Counter-Clockwise
    def big_pyr4_rCCW(self):
        self.big_pyr4_rCW()
        self.big_pyr4_rCW()

    def move(self, numbers):
        '''
        Given an integer - or array of integers - rotate the pyraminx in the given
        order of steps.
        '''
        # Initalize an empty move-set list.
        move_list = []
        # If the given input is an integer...
        if type(numbers) == type(1):
            move_list.append(numbers) # append the input to the empty move-list.
        else:
            move_list = numbers # Otherwise, set the move-set equal to the input.
        # For each move number in the move-set, execute the numbered rotation.
        for number in move_list: # (Comparable to a switch function in C.)
            if (number == 1):
                self.tip1_rCW()
            elif (number == 2):
                self.tip1_rCCW()
            elif (number == 3):
                self.tip2_rCW()
            elif (number == 4):
                self.tip2_rCCW()
            elif (number == 5):
                self.tip3_rCW()
            elif (number == 6):
                self.tip3_rCCW()
            elif (number == 7):
                self.tip4_rCW()
            elif (number == 8):
                self.tip4_rCCW()
            elif (number == 9):
                self.pyr1_rCW()
            elif (number == 10):
                self.pyr1_rCCW()
            elif (number == 11):
                self.pyr2_rCW()
            elif (number == 12):
                self.pyr2_rCCW()
            elif (number == 13):
                self.pyr3_rCW()
            elif (number == 14):
                self.pyr3_rCCW()
            elif (number == 15):
                self.pyr4_rCW()
            elif (number == 16):
                self.pyr4_rCCW()
            elif (number == 17):
                self.big_pyr1_rCW()
            elif (number == 18):
                self.big_pyr1_rCCW()
            elif (number == 19):
                self.big_pyr2_rCW()
            elif (number == 20):
                self.big_pyr2_rCCW()
            elif (number == 21):
                self.big_pyr3_rCW()
            elif (number == 22):
                self.big_pyr3_rCCW()
            elif (number == 23):
                self.big_pyr4_rCW()
            elif (number == 24):
                self.big_pyr4_rCCW()

    def randomize(self, total_turns, last_move = 100, set=None):
        '''
        Given an integer n = total_turns, randomly rotate the pyraminx n times\n
        last_move=X can be used to restrict randomization to all numbered
        rotations but X when set=None.\n
        set=ODD and set=EVEN restrict randomization to even and odd numbered 
        rotations, respectively.
        '''
        # Confirm the number of random turns requested.
        print(f'{total_turns} turns requested!')

        # Initialize the next move number as an impossible value (-1)
        next_move = -1

        # For each turn requested...
        for turn in range(total_turns):
            while (True):
                if set: # If a set (ODD/EVEN) is given...
                    # Select next move number from appropriate set of ints.
                    next_move = randrange(set,25,step=2)
                    # Then execute numbered rotation and continue.
                    self.move(next_move)
                    break
                else: # If a set is not given...
                    # Select next potential move number...
                    next_move = randint(1, 24)
                    # ...and confirm that the move will not cancel last move
                    # (Error-prone logic. May only protects against one move,
                    # sometimes none.)
                    if ((next_move % 2 == 0) and (last_move - next_move != 1))\
                    or ((next_move % 2 == 1) and (next_move - last_move != 1)):
                        # If move is deemed acceptable,
                        # Execute numbered rotation and continue.
                        self.move(next_move)
                        break
            # Set last move number equal to the completed move number.
            last_move = next_move
        # Confirm the number of random turns completed.
        print(f'{total_turns} turns completed!')