
'''
Eric Eckert
eric95
'''

import sys
from queue import PriorityQueue


# DO NOT CHANGE THIS SECTION
if sys.argv==[''] or len(sys.argv)<2:
    import EightPuzzleWithHeuristics as Problem
    heuristics = lambda s: Problem.HEURISTICS['h_manhattan'](s)

else:
    import importlib
    Problem = importlib.import_module(sys.argv[1])
    heuristics = lambda s: Problem.HEURISTICS[sys.argv[2]](s)


print("\nWelcome to AStar")
COUNT = None
BACKLINKS = {}

# DO NOT CHANGE THIS SECTION
def runAStar():
    #initial_state = Problem.CREATE_INITIAL_STATE(keyVal)
    initial_state = Problem.CREATE_INITIAL_STATE()
    print("Initial State:")
    print(initial_state)
    global COUNT, BACKLINKS
    COUNT = 0
    BACKLINKS = {}
    path, name = AStar(initial_state)
    print(str(COUNT)+" states examined.")
    return path, name

def AStar(initial_state):
    global COUNT, BACKLINKS
    # priority queue with respective priority
    # add any auxiliary data structures as needed
    OPEN = PriorityQueue()
    OPEN.put((heuristics(initial_state), initial_state))
    OPENlist = [initial_state]
    #OPEN.put(initial_state)
    CLOSED = []
    BACKLINKS[initial_state] = -1
    prioritycount = 0

    while not OPEN.empty():
        S = OPEN.get()[1]
        OPENlist.remove(S)
        while S in CLOSED:
            S = OPEN.get()[1]
        CLOSED.append(S)

        # DO NOT CHANGE THIS SECTION: begining
        if Problem.GOAL_TEST(S):
            print(Problem.GOAL_MESSAGE_FUNCTION(S))
            path = backtrace(S)
            return path, Problem.PROBLEM_NAME
        # DO NOT CHANGE THIS SECTION: end

        COUNT += 1
        for op in Problem.OPERATORS:
            prioritycount += 2
            #print(prioritycount)
            #print("Trying operator: "+op.name)
            if op.precond(S):
                new_state = op.state_transf(S)
                if not (new_state in CLOSED) and not (new_state in OPENlist):
                    #print(heuristics(new_state) +prioritycount)
                    #print(new_state)
                    #print(OPEN.qsize())
                    OPEN.put((heuristics(new_state), new_state))
                    OPENlist.append(new_state)
                    BACKLINKS[new_state] = S
                    #OPEN.put(new_state)

# DO NOT CHANGE
def backtrace(S):
    global BACKLINKS
    path = []
    while not S == -1:
        path.append(S)
        S = BACKLINKS[S]
    path.reverse()
    print("Solution path: ")
    for s in path:
        print(s)
    print("\nPath length = "+str(len(path)-1))
    return path

if __name__=='__main__':
    path, name = runAStar()
