'''
Eric Eckert
Derek Wang
eric95
d95wang
Infecting the World's population with a virus
'''

#<METADATA>
QUIET_VERSION = "0.2"
PROBLEM_NAME = "Infecting the World"
PROBLEM_VERSION = "0.2"
PROBLEM_AUTHORS = ['E. Eckert', 'D. Wang']
PROBLEM_CREATION_DATE = "28-APR-2017"
PROBLEM_DESC=\
        '''
Hello
'''

#</METADATA>

#<COMMON_CODE>
# state_changes is a dictionary of all state change parameters and whether they
# are activated or not

import random
import itertools

i_threshold = 0.9
r_threshold = 0.9

# Test to see which moves are illegal
def can_move(s, city):
    try:
        #moves are illegal if....
        if (s.world.cities[city].i_pop == 0):
            #City has not been touched by virus yet
            return False
        if (s.world.cities[city].i_pop/s.world.cities[city].total_pop > i_threshold):
            #City is fully infected (concquered) at > 90% infected population
            return False
        if (s.world.cities[city].r_pop/s.world.cities[city].total_pop > 0.9):
            #City is fully removed (either everyone's dead or vaccinated, we've lost the city)
            #at >90% removed
            return False

        return True

    except (Exception) as e:
        print(e)

# performe a move- the world progresses a single unit of time.
def move(s, state_changes, cityname):

    news = s.__copy__()
    world2 = news.world
    inf2 = news.infection
    city = world2.cities[cityname]

    #check if city is quarantined. If it's quarantined, it can't infect neighbors
    #and can't be quarantined again.
    if not cityname in world2.quarantined:

        if state_changes['neighbor']:
            #infect neighboring city
            # list of cities neighboring this city
            if cityname in news.world.routes:
                routeDestinations = news.world.routes[cityname]

                #iterate through destination cities in routes
                #TODO: change the way we infect other cities
                for destCity in routeDestinations:
                    #randomly determine if that city will be infected or not
                    infect = random.randint(0,1)

                    if (infect):
                        target = world2.cities[destCity]
                        #check if target is quarantined
                        if not target in world2.quarantined:
                            # Add flow rate * infect rate to target's infected population
                            target.i_pop += inf2.irate * world2.countries[city.country].flow_rate * city.s_pop

        if state_changes['quarantine']:
        # a city begins to quarantine
            # remove ciy from routes dictionary
            if cityname in news.world.routes:
                del news.world.routes[cityname]
            #add city to quarantine list
            world2.quarantined.append(cityname)

    if state_changes['mutation']:
        #mutate virus

        #increase infection rate
        #generate random int between -2 and 2
        dirate = random.randint(-2,2)
        #if change causes irate to be less than 0, make sure it goes positive (can't have negative infection rate)
        if (inf2.irate + dirate < 0):
            dirate = -dirate

        #Irate will be increased or decreased by up to 2%
        inf2.irate += 0.01 * dirate

        #change removal rate
        dremrate = random.randint(-2,2)
        if (inf2.remrate + dremrate < 0):
            dremrate = -dremrate
        inf2.remrate += 0.01 * dremrate


    if state_changes['medicine']:
        #city starts developing resistance, figting back
        #calculate a logaritmic increase in resistance
        world2.cities[cityname].medicine = city.medicine + (1/city.medicine)

    if state_changes['infect']:
        #further infection occurs
        temp = world2.cities[cityname]
        world2.cities[cityname] = inf2.infect(temp)

    return news

def goal_test(state):
    takencount = 0
    for cityname, city in state.world.cities.items():
        if (city.i_pop / city.total_pop > 0.4):
            takencount += 1

    return (takencount == 3)

def goal_message(s):
    return "The world is infected!"

class Operator:
    def __init__(self, name, precond, state_transf):
        self.name = name
        self.precond = precond
        self.state_transf = state_transf

    def is_applicable(self, s):
        return self.precond(s)

    def apply(self, s):
        return self.state_transf(s)

# An infection is an arbitrary disease with an infection rate as well as
# a removal rate (the rate at which a virus kills and/or fails to infect.
# The result is a member of the population that cannot be infected and cannot
# disribute the virus)
class Infection():
    def __init__(self, name ,irate, remrate):
        self.irate = irate
        self.remrate = remrate
        self.name = name

    def infect(self, city):

        # natural removal rate of virus plus removal rate caused by the city's
        # medicine combatting the infection
        true_remrate = self.remrate + city.medicine / 100

        #Using the SIR model for a viral epidemic:
        #calculate delta values for S (susceptible population), I (Infected population),
        # and R (removed population: dead or immune to virus)
        dS = -(self.irate * city.s_pop * city.i_pop) / city.total_pop
        dI = ((self.irate * city.s_pop * city.i_pop) / city.total_pop) - (true_remrate * city.i_pop)
        dR = true_remrate * city.i_pop

        #update values for city
        city.s_pop += dS
        city.i_pop += dI
        city.r_pop += dR
        return city

# The world object contains a set of cities and a set of countries
class World():
    def __init__(self, cities, countries, routes):
        self.cities = cities
        self.countries = countries
        self.quarantined = []
        self.routes = routes

    def addRoute(dest, source):
        self.routes[source].append(dest)

    def __lt__(self, s2):
        return True

# City object containing infected population count, the non infected population
# count, the cities medical effectiveness, city size in area, and the country
# the city resides in
class City():
    def __init__(self, name, i_pop, s_pop, r_pop, medicine, country):
        self.name = name # name of city
        self.i_pop = i_pop # infected population
        self.s_pop = s_pop # susceptible population
        self.r_pop = r_pop # removed population
        self.medicine = medicine # medicine to determine resistance to combat infection
        #self.area = area # currently not used: area of city to calculate population density
        self.country = country # country that city exists in
        self.total_pop = i_pop + s_pop + r_pop # total population
        self.rem_rate = medicine / 100

    def __eq__(self, city2):
        if not (type(self)==type(city2)): return False
        return self == city2

    def __lt__(self, s2):
        return True

# A country contains helper information for dictating the spread rate of the
# infection between cities. Each country contains a travel cost, flow rate
class Country():
    def __init__(self, name, flow_rate):
        self.name = name
        #self.t_cost = t_cost #t_cost is unused right now
        self.flow_rate = flow_rate #the density of travel from this country

#</COMMON_CODE>
complete = "?"


#<STATE>
class State():
    def __init__(self, world, infection):
        self.world = world
        self.infection = infection

    def __str__(self):
        # Produces a brief textual description of a state.
        worldname = "World1"
        infectionname = self.infection.name
        txt = "The infection state of " + worldname + " for the infection " + infectionname + ". \n"
        txt += "   Infection Status -- infection rate: " + str(self.infection.irate) + "   removal rate: " + str(self.infection.remrate) + "\n"
        for city in self.world.cities:
            txt += "   Infected for " + city + " " + str(self.world.cities[city].i_pop) + "   Total Population for " + city + ": " + str(self.world.cities[city].total_pop) + "\n"
        return txt

    def __eq__(self, s2):
        if not (type(self)==type(s2)): return False
        w1 = self.world; w2 = s2.world; i1 = self.infection; i2 = s2.infection
        return (w1==w2 and i1==i2)

    def __hash__(self):
        return (str(self)).__hash__()

    def __copy__(self):
        # Performs an appropriately deep copy of a state,
        # for use by operators in creating new states.
        new_infection = Infection(self.infection.name,self.infection.irate, self.infection.remrate)
        #new_infection = self.infection

        new_city_map = {}
        for cityname, city in self.world.cities.items():
            #temp_city = City(city.name, city.i_pop, city.s_pop, city.r_pop, city.medicine, city.country)
            temp_city = self.world.cities[cityname]
            new_city_map[cityname] = temp_city

        new_country_map = {}
        for countryname, country in self.world.countries.items():
            temp_country = self.world.countries[countryname]
            new_country_map[countryname] = Country(country.name, country.flow_rate)

        new_routes_map = {}
        for source, destinations in self.world.routes.items():
            new_routes_map[source] = destinations

        new_world = World(new_city_map, new_country_map, new_routes_map)

        news = State(new_world, new_infection)

        return news

    def __lt__(self, s2):
        return True

#</STATE>


#<INITIAL_STATE>

#TODO add an initial state
city1 = City("City1", 100, 20000, 0, 1, "Nation1")
city2 = City("City2", 0, 40000, 0, 2, "Nation1")
city3 = City("City3", 0, 30000, 0, 3, "Nation1")
city4 = City("City4", 0, 20000, 0, 4, "Nation1")
city5 = City("City5", 0, 10000, 0, 1, "Nation1")

cities = {
    "City1" : city1,
    "City2" : city2,
    "City3" : city3,
    "City4" : city4,
    "City5" : city5
    }

temp = {}

routes = {
    'City1': ["City2", "City3"],
    'City5': ["City1", "City2", "City3", "City4"],
    'City4': ["City5"],
    'City3': ["City1", "City4"],
    'City2': ["City5", "City1", "City3"]
}

infection = Infection("Best_Infection",0.02, 0.03)

Nation1 = Country("Nation1", 0.05)

countries = {"Nation1" : Nation1}

World1 = World(cities, countries, routes)

INITIAL_STATE = State(World1, infection)
CREATE_INITIAL_STATE = lambda: INITIAL_STATE

#</INITIAL_STATE>

#<OPERATORS>
# Calculate all possible legal movement combination

# list of state change keys
state_changes = ['neighbor', 'medicine', 'quarantine', 'infect', 'mutation']
state_change_possibilities = []

# generate every possible combination of 1 and 0 of length 5
for x in itertools.product(range(2), repeat=5):
    #print(x)
    # map key list to combination of 1 and 0s
    temp = dict(zip(state_changes, x))
    #print(temp)
    # add mapped dictionary to list
    state_change_possibilities.append(temp)

    # TODO cities is a list of cities derived from the INITIAL_STATE


move_possibilities = []

for a in itertools.product(state_change_possibilities, INITIAL_STATE.world.cities):
    move_possibilities.append(a)

#print(combinations)

#every single possible state change possibility for every single city
OPERATORS = [Operator((state_changes, city),
                      lambda s, c = city: can_move(s, c),
                      # The default value construct is needed
                      # here to capture the values of p&q separately
                      # in each iteration of the list comp. iteration.
                      lambda s, sc = state_changes, c = city: move(s,sc, c) )
             #for (state_changes, city) in (state_change_possibilities, s.world.cities)
             for (state_changes, city) in move_possibilities]



#</OPERATORS>

#<HEURISTICS> (optional)
# Heuristic Function for A star search algorithm
def h_custom(state):
    # Using A star search, a 'better' heuristic would yield a smaller value if the board is closer to total infection
    # This means that the heuristic should be based on a summarization of the state of each city
    # This value will be shifted based on the state of the infection as well as the combativeness of cities and
    city_list = state.world.cities
    infection_ratio_sum = 0
    medicine_weight = 0
    taken_counter = 0
    vaccine_rate = 0

    for city in city_list:
        infection_ratio_sum += state.world.cities[city].i_pop / state.world.cities[city].s_pop
        taken_counter += (1 if (state.world.cities[city].i_pop / state.world.cities[city].total_pop) > i_threshold else 0)
        medicine_weight += (1/ state.world.cities[city].medicine)
        vaccine_rate += state.world.cities[city].rem_rate

    sum_cities = ((infection_ratio_sum * 7) + (medicine_weight * 5) + taken_counter) / len(city_list)
    quarantine_weight = len(state.world.quarantined) / len(city_list) * 5
    infectivity_weight = state.infection.irate * 5
    infect_rem_rate_weight = state.infection.remrate / 100
    vaccine_rate = vaccine_rate / len(city_list) / 100
    return 1 / (sum_cities + quarantine_weight + infectivity_weight + infect_rem_rate_weight - vaccine_rate)

HEURISTICS = {'h_custom': h_custom}
#</HEURISTICS>

#<GOAL_TEST>
GOAL_TEST = lambda s: goal_test(s)
#</GOAL_TEST>

#<GOAL_MESSAGE_FUNCTION>
GOAL_MESSAGE_FUNCTION = lambda s: goal_message(s)
#</GOAL_MESSAGE_FUNCTION>
