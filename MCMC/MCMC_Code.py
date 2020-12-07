
#----------------------------------------------------
# Monte Carlo Markov Chain, Gibbs Sampling Project
# Authored by Javid Fathi
# ---------------------------------------------------
# Submitted with the MCMC Project for CS-463G
# Fish Group Members: Lauren Bassett, Will Berry, 
#                     Adam Brewer, Javid Fathi, 
#                     Tian Qiu
#----------------------------------------------------
# Prepared for Dr. Judy Goldsmith, Computer Science,
# University of Kentucky, Fall 2020
#----------------------------------------------------

from random import random, randint

Probabilties = {}
StatesVisited = {}
TransitTable = {}
COVID_Graph = {}

COVID_BIT = 64
FEVER_BIT = 32
COUGH_BIT = 16
NAUSEA_BIT = 8
FEV_COU_BIT = 4
FEV_NAU_BIT = 2
COU_NAU_BIT = 1

TOTAL_VARS = 127
EVIDENCE_VARS = NAUSEA_BIT + FEV_NAU_BIT

COVID_Counter = 0                                    # t = 0
Fever_Counter = Cough_Counter = Nausea_Counter = 0   # t = 1
FevNau_Counter = FevCou_Counter = CouNau_Counter = 0 # t = 2

NUM_RUNS = 1
EXPERIMENTS_PER_RUN = 10000
VAL_CHECK =  1000 # <- Edit this value to see how (COVID) counters changes during experiment.
                  #    Set it to a negative value if you'd like to not report any values.


def state_gen():
    '''
    Generates a random state (bit-string/integer) s.t. respective bits 
    for evidence variables are set to True.
    '''
    state = randint(EVIDENCE_VARS,TOTAL_VARS)
    while (state & EVIDENCE_VARS != EVIDENCE_VARS):
        state = randint(EVIDENCE_VARS,TOTAL_VARS)
    return state

def flip_var(state,req_var):
    '''
    Given a state (bit-string/integer) a relevant bit is flipped 
    either or True or False (0/1)
    '''
    if (state & req_var != req_var):
        state += req_var
    else:
        state -= req_var
    return state

def iterate_counters(state):
    '''
    Given a state (bit-string/integer), iterate a set of global counter 
    for each variable where its respective bit is set True.
    '''
    if (state & COVID_BIT == COVID_BIT):
        global COVID_Counter
        COVID_Counter += 1

    if (state & FEVER_BIT == FEVER_BIT):
        global Fever_Counter
        Fever_Counter += 1
    
    if (state & COUGH_BIT == COUGH_BIT):
        global Cough_Counter
        Cough_Counter += 1
    
    if (state & NAUSEA_BIT == NAUSEA_BIT):
        global Nausea_Counter
        Nausea_Counter += 1
    
    if (state & FEV_NAU_BIT == FEV_NAU_BIT):
        global FevNau_Counter
        FevNau_Counter += 1
    
    if (state & FEV_COU_BIT == FEV_COU_BIT):
        global FevCou_Counter
        FevCou_Counter += 1
    
    if (state & COU_NAU_BIT == COU_NAU_BIT):
        global CouNau_Counter
        CouNau_Counter += 1


def determine_probability(Probs):
    '''
    Generates and fills a global dictionary of Probabilities, where
    Probabilities[i] = P(i), where i is an integer representing a discrete state.
    '''
    for state in range(TOTAL_VARS + 1):
        #if (state & EVIDENCE_VARS == EVIDENCE_VARS) # <- Replace subsequent if statement w/this to limit
        if (True):                                   #    Probs to sub-set where evidence vars are True.
            if (state & COVID_BIT == COVID_BIT):
                p_covid  = 0.01
                p_fever  = 0.78 if (state & FEVER_BIT == FEVER_BIT) else 0.22
                p_cough  = 0.98 if (state & COUGH_BIT == COUGH_BIT) else 0.02
                p_nausea = 0.59 if (state & NAUSEA_BIT == NAUSEA_BIT) else 0.41
            else:
                p_covid  = 0.99
                p_fever  = 0.10 if (state & FEVER_BIT == FEVER_BIT) else 0.90
                p_cough  = 0.10 if (state & COUGH_BIT == COUGH_BIT) else 0.90
                p_nausea = 0.20 if (state & NAUSEA_BIT == NAUSEA_BIT) else 0.80
            
            if (state & (FEVER_BIT + COUGH_BIT) == (FEVER_BIT + COUGH_BIT)):
                p_fev_cou = 0.80 if (state & FEV_COU_BIT == FEV_COU_BIT) else 0.20
            elif (state & FEVER_BIT == FEVER_BIT):
                p_fev_cou = 0.95 if (state & FEV_COU_BIT == FEV_COU_BIT) else 0.05
            elif (state & COUGH_BIT == COUGH_BIT):
                p_fev_cou = 0.30 if (state & FEV_COU_BIT == FEV_COU_BIT) else 0.70
            else:
                p_fev_cou = 0.20 if (state & FEV_COU_BIT == FEV_COU_BIT) else 0.80

            if (state & (FEVER_BIT + NAUSEA_BIT) == (FEVER_BIT + NAUSEA_BIT)):
                p_fev_nau = 0.85 if (state & FEV_NAU_BIT == FEV_NAU_BIT) else 0.15
            elif (state & FEVER_BIT == FEVER_BIT):
                p_fev_nau = 0.63 if (state & FEV_NAU_BIT == FEV_NAU_BIT) else 0.37
            elif (state & NAUSEA_BIT == NAUSEA_BIT):
                p_fev_nau = 0.58 if (state & FEV_NAU_BIT == FEV_NAU_BIT) else 0.42
            else:
                p_fev_nau = 0.08 if (state & FEV_NAU_BIT == FEV_NAU_BIT) else 0.92

            if (state & (COUGH_BIT + NAUSEA_BIT) == (COUGH_BIT + NAUSEA_BIT)):
                p_cou_nau = 0.76 if (state & COU_NAU_BIT == COU_NAU_BIT) else 0.24
            elif (state & COUGH_BIT == COUGH_BIT):
                p_cou_nau = 0.42 if (state & COU_NAU_BIT == COU_NAU_BIT) else 0.58
            elif (state & NAUSEA_BIT == NAUSEA_BIT):
                p_cou_nau = 0.29 if (state & COU_NAU_BIT == COU_NAU_BIT) else 0.71
            else:
                p_cou_nau = 0.05 if (state & COU_NAU_BIT == COU_NAU_BIT) else 0.95

            Probs[state] = p_covid * p_fever * p_nausea * p_cough * p_fev_cou * p_fev_nau * p_cou_nau

    return Probs

def probability_flip(state, variable_val):
    '''
    Given a state and a bit-value representing a variable, determine the probability
    that the variable will be true, conditioned on the other conditions of the state.
    Then, randomly assign a the state's variable to be True or False based on that probability.
    '''
    if (state & variable_val == variable_val):
        true_var_prob = Probabilties[state] / (Probabilties[state] + Probabilties[state - variable_val])
    else:
        true_var_prob = Probabilties[state + variable_val] / (Probabilties[state + variable_val] + Probabilties[state])
    
    toss = random()
    
    if ((toss <= true_var_prob) and (state & variable_val != variable_val))\
        or ((toss > true_var_prob) and (state & variable_val == variable_val)):
        state = flip_var(state, variable_val)
    
    return state

def bit_print(val):
    '''
    Given a bit-value related to a variable, return an identifying string.
    Otherwise, return "nothing" (--).
    '''
    string = '--'
    if val == COVID_BIT:
        string = 'C19'
    elif val == FEVER_BIT:
        string = 'Fever'
    elif val == COUGH_BIT:
        string = 'Cough'
    elif val == NAUSEA_BIT:
        string = 'Nausea'
    elif val == FEV_COU_BIT:
        string = 'FevCou'
    elif val == FEV_NAU_BIT:
        string = 'FevNau'
    elif val == COU_NAU_BIT:
        string = 'CouNau'
    return string

def p_A_given_B(variable, TRUE_VARS=[0], FALSE_VARS=[128]):
    '''
    Given 3 sets of bit-values related to variables,
    evaluate the probability that the first variable is True
    given the probability that the other variables are set to 
    True and/or False, as requested.
    '''
    prob = 0
    given = 0

    for state in Probabilties:

        if state & sum(TRUE_VARS) == sum(TRUE_VARS) and state & sum(FALSE_VARS) != sum(FALSE_VARS):
            
            given += Probabilties[state]

            if state & variable == variable:

                prob += Probabilties[state]

    TRUE_STRS = [bit_print(i) for i in TRUE_VARS]
    FALSE_STRS = [bit_print(i) for i in FALSE_VARS]
    
    print(f'P({bit_print(variable)}=T | T=', *TRUE_STRS, '; F=', *FALSE_STRS, f') = {prob/given}')

def probability_charts():
    '''
    Prints the conditional probabilities tables of all requested variables.
    '''
    print()
    try:
        if input('COVID Tables? (Y/N) ').strip().upper()[0] == 'Y':
            p_A_given_B(COVID_BIT, [COUGH_BIT, FEVER_BIT, NAUSEA_BIT])      # 111
            p_A_given_B(COVID_BIT, [COUGH_BIT, FEVER_BIT], [NAUSEA_BIT])    # 110
            p_A_given_B(COVID_BIT, [COUGH_BIT, NAUSEA_BIT], [FEVER_BIT])    # 101
            p_A_given_B(COVID_BIT, [COUGH_BIT], [FEVER_BIT, NAUSEA_BIT])    # 100
            p_A_given_B(COVID_BIT, [FEVER_BIT, NAUSEA_BIT], [COUGH_BIT])    # 011
            p_A_given_B(COVID_BIT, [FEVER_BIT], [COUGH_BIT, NAUSEA_BIT])    # 010
            p_A_given_B(COVID_BIT, [NAUSEA_BIT], [COUGH_BIT, FEVER_BIT])    # 001
            p_A_given_B(COVID_BIT, [0], [COUGH_BIT, FEVER_BIT, NAUSEA_BIT]) # 000
    except IndexError:
        pass

    print()
    try:
        if input('Fever Tables? (Y/N) ').strip().upper()[0] == 'Y':
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT])      # 11111
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT], [FEV_NAU_BIT])    # 11110
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_NAU_BIT], [FEV_COU_BIT])    # 11101
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, NAUSEA_BIT], [FEV_COU_BIT, FEV_NAU_BIT])    # 11100
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, FEV_COU_BIT, FEV_NAU_BIT], [NAUSEA_BIT])    # 11011
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, FEV_COU_BIT], [NAUSEA_BIT, FEV_NAU_BIT])    # 11010
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT, FEV_NAU_BIT], [NAUSEA_BIT, FEV_COU_BIT])    # 11001
            p_A_given_B(FEVER_BIT, [COVID_BIT, COUGH_BIT], [NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 11000
            p_A_given_B(FEVER_BIT, [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT], [COUGH_BIT])    # 10111
            p_A_given_B(FEVER_BIT, [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT], [COUGH_BIT, FEV_NAU_BIT])    # 10110
            p_A_given_B(FEVER_BIT, [COVID_BIT, NAUSEA_BIT, FEV_NAU_BIT], [COUGH_BIT, FEV_COU_BIT])    # 10101
            p_A_given_B(FEVER_BIT, [COVID_BIT, NAUSEA_BIT], [COUGH_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 10100
            p_A_given_B(FEVER_BIT, [COVID_BIT, FEV_COU_BIT, FEV_NAU_BIT], [COUGH_BIT, NAUSEA_BIT])    # 10011
            p_A_given_B(FEVER_BIT, [COVID_BIT, FEV_COU_BIT], [COUGH_BIT, NAUSEA_BIT, FEV_NAU_BIT])    # 10010
            p_A_given_B(FEVER_BIT, [COVID_BIT, FEV_NAU_BIT], [COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 10001
            p_A_given_B(FEVER_BIT, [COVID_BIT], [COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 10000
            p_A_given_B(FEVER_BIT, [COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT], [COVID_BIT])    # 01111
            p_A_given_B(FEVER_BIT, [COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT], [COVID_BIT, FEV_NAU_BIT])    # 01110
            p_A_given_B(FEVER_BIT, [COUGH_BIT, NAUSEA_BIT, FEV_NAU_BIT], [COVID_BIT, FEV_COU_BIT])    # 01101
            p_A_given_B(FEVER_BIT, [COUGH_BIT, NAUSEA_BIT], [COVID_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 01100
            p_A_given_B(FEVER_BIT, [COUGH_BIT, FEV_COU_BIT, FEV_NAU_BIT], [COVID_BIT, NAUSEA_BIT])    # 01011
            p_A_given_B(FEVER_BIT, [COUGH_BIT, FEV_COU_BIT], [COVID_BIT, NAUSEA_BIT, FEV_NAU_BIT])    # 01010
            p_A_given_B(FEVER_BIT, [COUGH_BIT, FEV_NAU_BIT], [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 01001
            p_A_given_B(FEVER_BIT, [COUGH_BIT], [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 01000
            p_A_given_B(FEVER_BIT, [NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT], [COVID_BIT, COUGH_BIT])    # 00111
            p_A_given_B(FEVER_BIT, [NAUSEA_BIT, FEV_COU_BIT], [COVID_BIT, COUGH_BIT, FEV_NAU_BIT])    # 00110
            p_A_given_B(FEVER_BIT, [NAUSEA_BIT, FEV_NAU_BIT], [COVID_BIT, COUGH_BIT, FEV_COU_BIT])    # 00101
            p_A_given_B(FEVER_BIT, [NAUSEA_BIT], [COVID_BIT, COUGH_BIT, FEV_COU_BIT, FEV_NAU_BIT])    # 00100
            p_A_given_B(FEVER_BIT, [FEV_COU_BIT, FEV_NAU_BIT], [COVID_BIT, COUGH_BIT, NAUSEA_BIT])    # 00011
            p_A_given_B(FEVER_BIT, [FEV_COU_BIT], [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_NAU_BIT])    # 00010
            p_A_given_B(FEVER_BIT, [FEV_NAU_BIT], [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 00001
            p_A_given_B(FEVER_BIT, [0], [COVID_BIT, COUGH_BIT, NAUSEA_BIT, FEV_COU_BIT, FEV_NAU_BIT]) # 00000
    except IndexError:
        pass

    print()
    try:
        if input('Cough Tables? (Y/N) ').strip().upper()[0] == 'Y':
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT])      # 11111
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT], [COU_NAU_BIT])    # 11110
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, NAUSEA_BIT, COU_NAU_BIT], [FEV_COU_BIT])    # 11101
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, NAUSEA_BIT], [FEV_COU_BIT, COU_NAU_BIT])    # 11100
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, FEV_COU_BIT, COU_NAU_BIT], [NAUSEA_BIT])    # 11011
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, FEV_COU_BIT], [NAUSEA_BIT, COU_NAU_BIT])    # 11010
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT, COU_NAU_BIT], [NAUSEA_BIT, FEV_COU_BIT])    # 11001
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEVER_BIT], [NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 11000
            p_A_given_B(COUGH_BIT, [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT], [FEVER_BIT])    # 10111
            p_A_given_B(COUGH_BIT, [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT], [FEVER_BIT, COU_NAU_BIT])    # 10110
            p_A_given_B(COUGH_BIT, [COVID_BIT, NAUSEA_BIT, COU_NAU_BIT], [FEVER_BIT, FEV_COU_BIT])    # 10101
            p_A_given_B(COUGH_BIT, [COVID_BIT, NAUSEA_BIT], [FEVER_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 10100
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEV_COU_BIT, COU_NAU_BIT], [FEVER_BIT, NAUSEA_BIT])    # 10011
            p_A_given_B(COUGH_BIT, [COVID_BIT, FEV_COU_BIT], [FEVER_BIT, NAUSEA_BIT, COU_NAU_BIT])    # 10010
            p_A_given_B(COUGH_BIT, [COVID_BIT, COU_NAU_BIT], [FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 10001
            p_A_given_B(COUGH_BIT, [COVID_BIT], [FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 10000
            p_A_given_B(COUGH_BIT, [FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT], [COVID_BIT])    # 01111
            p_A_given_B(COUGH_BIT, [FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT], [COVID_BIT, COU_NAU_BIT])    # 01110
            p_A_given_B(COUGH_BIT, [FEVER_BIT, NAUSEA_BIT, COU_NAU_BIT], [COVID_BIT, FEV_COU_BIT])    # 01101
            p_A_given_B(COUGH_BIT, [FEVER_BIT, NAUSEA_BIT], [COVID_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 01100
            p_A_given_B(COUGH_BIT, [FEVER_BIT, FEV_COU_BIT, COU_NAU_BIT], [COVID_BIT, NAUSEA_BIT])    # 01011
            p_A_given_B(COUGH_BIT, [FEVER_BIT, FEV_COU_BIT], [COVID_BIT, NAUSEA_BIT, COU_NAU_BIT])    # 01010
            p_A_given_B(COUGH_BIT, [FEVER_BIT, COU_NAU_BIT], [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 01001
            p_A_given_B(COUGH_BIT, [FEVER_BIT], [COVID_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 01000
            p_A_given_B(COUGH_BIT, [NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT])    # 00111
            p_A_given_B(COUGH_BIT, [NAUSEA_BIT, FEV_COU_BIT], [COVID_BIT, FEVER_BIT, COU_NAU_BIT])    # 00110
            p_A_given_B(COUGH_BIT, [NAUSEA_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT, FEV_COU_BIT])    # 00101
            p_A_given_B(COUGH_BIT, [NAUSEA_BIT], [COVID_BIT, FEVER_BIT, FEV_COU_BIT, COU_NAU_BIT])    # 00100
            p_A_given_B(COUGH_BIT, [FEV_COU_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT, NAUSEA_BIT])    # 00011
            p_A_given_B(COUGH_BIT, [FEV_COU_BIT], [COVID_BIT, FEVER_BIT, NAUSEA_BIT, COU_NAU_BIT])    # 00010
            p_A_given_B(COUGH_BIT, [COU_NAU_BIT], [COVID_BIT, FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT])    # 00001
            p_A_given_B(COUGH_BIT, [0], [COVID_BIT, FEVER_BIT, NAUSEA_BIT, FEV_COU_BIT, COU_NAU_BIT]) # 00000
    except IndexError:
        pass

    print()
    try:
        if input('Nausea Tables? (Y/N) ').strip().upper()[0] == 'Y':
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT])      # 11111
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, COUGH_BIT, FEV_NAU_BIT], [COU_NAU_BIT])    # 11110
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, COUGH_BIT, COU_NAU_BIT], [FEV_NAU_BIT])    # 11101
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, COUGH_BIT], [FEV_NAU_BIT, COU_NAU_BIT])    # 11100
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, FEV_NAU_BIT, COU_NAU_BIT], [COUGH_BIT])    # 11011
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, FEV_NAU_BIT], [COUGH_BIT, COU_NAU_BIT])    # 11010
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT, COU_NAU_BIT], [COUGH_BIT, FEV_NAU_BIT])    # 11001
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEVER_BIT], [COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 11000
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT], [FEVER_BIT])    # 10111
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, COUGH_BIT, FEV_NAU_BIT], [FEVER_BIT, COU_NAU_BIT])    # 10110
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, COUGH_BIT, COU_NAU_BIT], [FEVER_BIT, FEV_NAU_BIT])    # 10101
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, COUGH_BIT], [FEVER_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 10100
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEV_NAU_BIT, COU_NAU_BIT], [FEVER_BIT, COUGH_BIT])    # 10011
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, FEV_NAU_BIT], [FEVER_BIT, COUGH_BIT, COU_NAU_BIT])    # 10010
            p_A_given_B(NAUSEA_BIT, [COVID_BIT, COU_NAU_BIT], [FEVER_BIT, COUGH_BIT, FEV_NAU_BIT])    # 10001
            p_A_given_B(NAUSEA_BIT, [COVID_BIT], [FEVER_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 10000
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT], [COVID_BIT])    # 01111
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, COUGH_BIT, FEV_NAU_BIT], [COVID_BIT, COU_NAU_BIT])    # 01110
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, COUGH_BIT, COU_NAU_BIT], [COVID_BIT, FEV_NAU_BIT])    # 01101
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, COUGH_BIT], [COVID_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 01100
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, FEV_NAU_BIT, COU_NAU_BIT], [COVID_BIT, COUGH_BIT])    # 01011
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, FEV_NAU_BIT], [COVID_BIT, COUGH_BIT, COU_NAU_BIT])    # 01010
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT, COU_NAU_BIT], [COVID_BIT, COUGH_BIT, FEV_NAU_BIT])    # 01001
            p_A_given_B(NAUSEA_BIT, [FEVER_BIT], [COVID_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 01000
            p_A_given_B(NAUSEA_BIT, [COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT])    # 00111
            p_A_given_B(NAUSEA_BIT, [COUGH_BIT, FEV_NAU_BIT], [COVID_BIT, FEVER_BIT, COU_NAU_BIT])    # 00110
            p_A_given_B(NAUSEA_BIT, [COUGH_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT, FEV_NAU_BIT])    # 00101
            p_A_given_B(NAUSEA_BIT, [COUGH_BIT], [COVID_BIT, FEVER_BIT, FEV_NAU_BIT, COU_NAU_BIT])    # 00100
            p_A_given_B(NAUSEA_BIT, [FEV_NAU_BIT, COU_NAU_BIT], [COVID_BIT, FEVER_BIT, COUGH_BIT])    # 00011
            p_A_given_B(NAUSEA_BIT, [FEV_NAU_BIT], [COVID_BIT, FEVER_BIT, COUGH_BIT, COU_NAU_BIT])    # 00010
            p_A_given_B(NAUSEA_BIT, [COU_NAU_BIT], [COVID_BIT, FEVER_BIT, COUGH_BIT, FEV_NAU_BIT])    # 00001
            p_A_given_B(NAUSEA_BIT, [0], [COVID_BIT, FEVER_BIT, COUGH_BIT, FEV_NAU_BIT, COU_NAU_BIT]) # 00000
    except IndexError:
        pass

    print()
    try:
        if input('Fever&Cough Tables? (Y/N) ').strip().upper()[0] == 'Y':
            try:
                if input('N=T & F&N=T subspace? (Y/N) ').strip().upper()[0] == 'Y':
                    p_A_given_B(FEV_COU_BIT, [NAUSEA_BIT, FEV_NAU_BIT, FEVER_BIT, COUGH_BIT])   # 11
                    p_A_given_B(FEV_COU_BIT, [NAUSEA_BIT, FEV_NAU_BIT, FEVER_BIT], [COUGH_BIT]) # 10
                    p_A_given_B(FEV_COU_BIT, [NAUSEA_BIT, FEV_NAU_BIT, COUGH_BIT], [FEVER_BIT]) # 01
                    p_A_given_B(FEV_COU_BIT, [NAUSEA_BIT, FEV_NAU_BIT], [FEVER_BIT, COUGH_BIT]) # 00
                else:
                    p_A_given_B(FEV_COU_BIT, [FEVER_BIT, COUGH_BIT])      # 11
                    p_A_given_B(FEV_COU_BIT, [FEVER_BIT], [COUGH_BIT])    # 10
                    p_A_given_B(FEV_COU_BIT, [COUGH_BIT], [FEVER_BIT])    # 01
                    p_A_given_B(FEV_COU_BIT, [0], [FEVER_BIT, COUGH_BIT]) # 00
            except IndexError:
                p_A_given_B(FEV_COU_BIT, [FEVER_BIT, COUGH_BIT])      # 11
                p_A_given_B(FEV_COU_BIT, [FEVER_BIT], [COUGH_BIT])    # 10
                p_A_given_B(FEV_COU_BIT, [COUGH_BIT], [FEVER_BIT])    # 01
                p_A_given_B(FEV_COU_BIT, [0], [FEVER_BIT, COUGH_BIT]) # 00
    except IndexError:
        pass

    print()
    try:
        if input('Fever&Nausea Tables? (Y/N) ').strip().upper()[0] == 'Y':
            try:
                if input('N=T & F&N=T subspace? (Y/N) ').strip().upper()[0] == 'Y':
                    p_A_given_B(FEV_NAU_BIT, [FEVER_BIT, NAUSEA_BIT])      # 11
                    p_A_given_B(FEV_NAU_BIT, [NAUSEA_BIT], [FEVER_BIT])    # 01
                else:
                    p_A_given_B(FEV_NAU_BIT, [FEVER_BIT, NAUSEA_BIT])      # 11
                    p_A_given_B(FEV_NAU_BIT, [FEVER_BIT], [NAUSEA_BIT])    # 10
                    p_A_given_B(FEV_NAU_BIT, [NAUSEA_BIT], [FEVER_BIT])    # 01
                    p_A_given_B(FEV_NAU_BIT, [0], [FEVER_BIT, NAUSEA_BIT]) # 00
            except IndexError:
                p_A_given_B(FEV_NAU_BIT, [FEVER_BIT, NAUSEA_BIT])      # 11
                p_A_given_B(FEV_NAU_BIT, [FEVER_BIT], [NAUSEA_BIT])    # 10
                p_A_given_B(FEV_NAU_BIT, [NAUSEA_BIT], [FEVER_BIT])    # 01
                p_A_given_B(FEV_NAU_BIT, [0], [FEVER_BIT, NAUSEA_BIT]) # 00
    except IndexError:
        pass

    print()
    try:
        if input('Nausea Tables? (Y/N) ').strip().upper()[0] == 'Y':
            try:
                if input('N=T & F&N=T subspace? (Y/N) ').strip().upper()[0] == 'Y':
                    p_A_given_B(COU_NAU_BIT, [COUGH_BIT, NAUSEA_BIT, FEV_NAU_BIT])   # 11
                    p_A_given_B(COU_NAU_BIT, [NAUSEA_BIT, FEV_NAU_BIT], [COUGH_BIT]) # 01
                else:
                    p_A_given_B(COU_NAU_BIT, [COUGH_BIT, NAUSEA_BIT])      # 11
                    p_A_given_B(COU_NAU_BIT, [COUGH_BIT], [NAUSEA_BIT])    # 10
                    p_A_given_B(COU_NAU_BIT, [NAUSEA_BIT], [COUGH_BIT])    # 01
                    p_A_given_B(COU_NAU_BIT, [0], [COUGH_BIT, NAUSEA_BIT]) # 00
            except IndexError:
                p_A_given_B(COU_NAU_BIT, [COUGH_BIT, NAUSEA_BIT])      # 11
                p_A_given_B(COU_NAU_BIT, [COUGH_BIT], [NAUSEA_BIT])    # 10
                p_A_given_B(COU_NAU_BIT, [NAUSEA_BIT], [COUGH_BIT])    # 01
                p_A_given_B(COU_NAU_BIT, [0], [COUGH_BIT, NAUSEA_BIT]) # 00
    except IndexError:
        pass
    print()

    print("Expected probability value of P(COVID | N=T, F&N=T):")
    p_A_given_B(COVID_BIT, [NAUSEA_BIT, FEV_NAU_BIT])
    print()

def main():
    '''
    Program driver. Completes Gibbs sampling of Bayesian Network, 
    evaluate conditional probabilities and print requested data/values.
    '''
    global Probabilties, StatesVisited, TransitTable, COVID_Graph
    Probabilties = determine_probability(Probabilties)
    
    try:
        if input('Generate probability tables? (Y/N) ').strip().upper()[0] == 'Y':
            probability_charts()
    except IndexError:
        pass

    try:
        if input("Run Gibb's sampling? (Y/N) ").strip().upper()[0] != 'Y':
            print('Program exit')
            exit(0)
    except IndexError:
        print('Program exit')
        exit(0)
    
    try:
        makeTransitTable = input('Generate transition table? (Y/N) ').strip().upper()[0] == 'Y'
    except IndexError:
        makeTransitTable = False

    print()

    init_state = state_gen()
    state = init_state
    num_experiments = NUM_RUNS * EXPERIMENTS_PER_RUN
    for i in range(1,num_experiments+1):
        
        prev_state = state 

        iterate_counters(state)

        # Time, t = 0
        state = probability_flip(state, COVID_BIT)
        
        # Time, t = 1
        state = probability_flip(state, FEVER_BIT)
        state = probability_flip(state, COUGH_BIT)
        
        # Time, t = 2
        state = probability_flip(state, FEV_COU_BIT)
        state = probability_flip(state, COU_NAU_BIT)

        if state not in StatesVisited:
            StatesVisited[state] = 0
        StatesVisited[state] += 1

        if makeTransitTable:
            transition = f'{prev_state:07b} -> {state:07b}'
            if transition not in TransitTable:
                TransitTable[transition] = 0
            TransitTable[transition] += 1

        if (i % VAL_CHECK == 0) and (VAL_CHECK > 0):
            print(f'Probability of COVID given Nausea, Fever&Nausea, i={i}: {COVID_Counter/i*100}%')
            COVID_Graph[i] = COVID_Counter/i * 100

    print()

    if makeTransitTable:
        print('------------------')
        print('Transition Table')
        print('------------------')
        for transition in TransitTable:
            print(f'{transition} : {TransitTable[transition]}')
        print('------------------')
    
    try:
        if (input('Show state count table? (Y/N) ').strip().upper()[0] == 'Y'):
            print('------------------')
            print(f'Start: {init_state:07b}')
            print('------------------')
            print(' BitStr | Count')
            print('--------|---------')
            for key, value in StatesVisited.items():
                print(f"{key:07b}", ' | ', value, sep='')
            print('------------------')
    except IndexError:
        pass

    try:
        if (input('Show variable ratios? (Y/N) ').strip().upper()[0] == 'Y'):
            print(f'COVID:   {COVID_Counter/num_experiments}')
            print(f'FEVER:   {Fever_Counter/num_experiments}')
            print(f'COUGH:   {Cough_Counter/num_experiments}')
            print(f'NAUSEA:  {Nausea_Counter/num_experiments}')
            print(f'FEV+COU: {FevCou_Counter/num_experiments}')
            print(f'FEV+NAU: {FevNau_Counter/num_experiments}')
            print(f'FEV+COU: {CouNau_Counter/num_experiments}')
    except IndexError:
        pass

    print(f'\nProbability of COVID given Nausea, Fever&Nausea, i={num_experiments}: {COVID_Counter/num_experiments*100}%\n')
main()