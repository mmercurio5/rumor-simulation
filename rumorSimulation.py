import numpy as np
import random
import math
import matplotlib.pyplot as plt
import pandas as pd

class Person:
    def __init__(self, IDnum, role, maxInteractions):
        self.ID = IDnum                         #each person has unique ID
        self.rep = self.getRandomReputation()   #Repuation
        self.maxInteractions = maxInteractions  #Max Interactions in each step
        self.dailyInteractions = 0              #Interactions in each step

        self.belief = 0   #0 if they don't believe rumor, 1 if they do

        """
        roles:
        100 - ignorant
        200 - spreader
        300 - stifler
        """
        self.role = role



    def getRandomReputation(self):
        """set random repuation sampled from pareto distribution
        ranges between zero and one
        """
        x = np.random.uniform(0, 3) + 1
        return 1.0/x**(1.16)


class Simulation:
    #SF is surprise Factor
    #CF is trust Level - CF < 1: rep matters less if CF < 1 as CF -> 0

    def __init__(self, numPeople, SF, CF, randInteractions, probStifle):
        """Simulation class

            numPeople - size of the population
            SF - surprise factor
            CF - confidence level if greater than 1, repuation matters more
            randInteractions - if true, the number interactions of each
                               person is randomized and normally distributed

                               if false,  each persons interactions each day
                               is the same
            probStifle - the probability someone becomes a stifler can be
                         can be preset to anything between 0 and 1
        """
        self.numPeople = numPeople
        self.SF = SF
        self.CF = CF
        self.randNumInteractions = randInteractions
        self.probStifle = probStifle

        self.peopleList = []
        for i in np.arange(0, numPeople):
            person = Person(i, 100, self.setNumInteractions())
            self.peopleList.append(person)

        self.bully = None
        self.victim = None

        self.numBelievers = 1
        self.numStiflers = 0
        self.numIgnorant = self.numPeople - 1

        self.victimRepList = []
        self.beliefList = []
        self.ignorantList = []
        self.stiflerlist = []

        #precentage of population that knows the rumor
        #when the victim first hears it
        self.victimHears = 0

        #test variables
        self.victimKnows = False
        self.victimHit = False




    def setNumInteractions(self):
        if self.randNumInteractions == True:
            x = np.random.normal(self.numPeople*.01, self.numPeople*.005)
            return max(int(x), 1)

        else:
            return max(int(self.numPeople * .1), 1)


    #get person ms trust level of person n, can't be greater than 1
    def getTrustLevel(self, n, m):
        """ get person m's trust level of person n, can't be greater than 1 """
        trustLevel = (n.rep/m.rep)**self.CF

        return min([trustLevel, 1])


    def interaction(self, p1, p2):
        """ An interaction between two people
            What happens is dependent on each persons role
        """

        #both people are ignorant
        if (p1.role == 100) and (p2.role == 100):
            return
        # both people are stiflers
        elif (p1.role == 300) and (p2.role == 300):
            return

        #one spreader and one ignorant
        elif p1.role + p2.role == 300:
            #person1 is a spreader
            if p1.role == 200:

                #victim doesn't believe rumor about themselves
                if p2 == self.victim:
                    self.victimHit = True
                    self.victimKnows = True
                    self.victim.role = 200
                    return

                #probability the trust the person * prob the rumor is true

                if p1.belief == 1:
                    acceptanceProb = self.getTrustLevel(p1, p2) * (2**(-self.SF))
                else:
                    acceptanceProb = self.getTrustLevel(p1, p2) * (1 - 2**(-self.SF))


                if np.random.uniform(0,1) <= acceptanceProb:
                    p2.belief = p1.belief
                    p2.role = 200

                return

            #person2 is a spreader
            else:

                #victim doesn't believe rumor about themselves
                if p1 == self.victim:
                    self.victimHit = True
                    self.victimKnows = True
                    self.victim.role = 200
                    return

                if p2.belief == 1:
                    acceptanceProb = self.getTrustLevel(p2, p1) * (2**(-self.SF))
                else:
                    acceptanceProb = self.getTrustLevel(p2, p1) * (1 - 2**(-self.SF))

                if np.random.uniform(0,1) <= acceptanceProb:
                    p1.belief = p2.belief
                    p1.role = 200
                return

        #two spreaders or one spreader and one stifler
        #it doesn't make a difference to the spreader
        #nothing happens to the stifler, the just influence the other
        elif (p1.role != 100) and (p2.role != 100):

            if p1.belief == p2.belief:

                if np.random.uniform() <= self.probStifle:
                    if p1 != self.victim:
                        p1.role = 300
                if np.random.uniform() <= self.probStifle:
                    if p2 != self.victim:
                        p2.role = 300
                return

            p1B = p1.belief
            p2B = p2.belief
            if (p1.role == 200) and (p1B != p2B):

                if p2.belief == 1:
                    switchProb = self.getTrustLevel(p1, p2) * (2**(-self.SF))
                else:
                    switchProb = self.getTrustLevel(p1, p2) * (1 - 2**(-self.SF))


                if p1 == self.victim:
                    switchProb = -99

                if np.random.uniform(0,1) <= switchProb:

                    p1.belief = p2B

                #victim never becomes a stifler
                elif switchProb <= 2:
                    stifleProb = np.random.uniform()
                    if stifleProb <= self.probStifle:
                        p1.role = 300 #with prob to be determined



            if (p2.role == 200) and (p1B != p2B):
                if p1.belief == 1:
                    switchProb = self.getTrustLevel(p1, p2) * (2**(-self.SF))
                else:
                    switchProb = self.getTrustLevel(p1, p2) * (1 - 2**(-self.SF))

                if p2 == self.victim:
                    switchProb = -99

                if np.random.uniform(0,1) <= switchProb:
                    p2.belief = p1B

                #victim never becomes a stifler
                elif switchProb <= 2:
                    stifleProb = np.random.uniform()
                    if stifleProb <= self.probStifle:
                        p2.role = 300 #with prob to be determined

            return
        return



    def runSimulation(self, steps):
        """ Runs simulation for assigned number of steps.
            Analysis of similation can be done by calling the instance
            variables of the simulation after the simulation has finished.
        """

        #assign bully
        bullyID = np.random.randint(0, len(self.peopleList))
        self.bully = self.peopleList[bullyID]
        self.bully.role = 200
        self.bully.belief = 1

        self.beliefList.append(self.numBelievers)
        self.stiflerlist.append(0)

        #assign victim
        victimID = bullyID
        while victimID == bullyID:
            victimID = np.random.randint(0, len(self.peopleList))

        self.victim = self.peopleList[victimID]

        #victims max interaction is doubled
        self.victim.maxInteractions *= 2


        self.victimRepList.append(self.victim.rep)
        self.ignorantList.append(self.numIgnorant)

        stepsRun = 0

        while stepsRun < steps:
            interactionMatrix = np.zeros((self.numPeople, self.numPeople))
            for i in self.peopleList:

                #skipcount protects against infinite while loop
                skipcount = 0
                while i.dailyInteractions < i.maxInteractions:
                    if skipcount >= self.numPeople * 2:
                        break
                    randID = np.random.randint(self.peopleList.index(i), len(self.peopleList))

                    #a person cannot interact with themselves
                    if randID == i.ID:
                        continue

                    randomPerson = self.peopleList[randID]

                    if randomPerson.dailyInteractions == randomPerson.maxInteractions:
                        skipcount += 1
                        continue

                    #two people can't interact in the same step twice
                    if interactionMatrix[i.ID][randomPerson.ID] == 1:
                        continue

                    self.interaction(i, randomPerson)

                    #victim can never become stifler
                    if self.victim.role == 300:
                        self.victim.role = 200

                    if self.victimKnows == True:
                        self.victimHears = self.numBelievers / self.numPeople
                        self.victimKnows = False


                    interactionMatrix[i.ID][randomPerson.ID] == 1
                    i.dailyInteractions += 1
                    randomPerson.dailyInteractions += 1


            stepsRun += 1


            #bookkeeping after each step
            self.numBelievers = 0
            self.numIgnorant = 0
            self.numStiflers = 0
            for i in self.peopleList:
                i.dailyInteractions = 0
                if i.belief == 1:
                    self.numBelievers += 1

                if i.role == 100:
                    self.numIgnorant += 1

                if i.role == 300:
                    self.numStiflers +=1


            percentBelief = self.numBelievers / self.numPeople
            self.victim.rep = self.victim.rep*np.exp(-percentBelief * self.SF)
            self.victimRepList.append(self.victim.rep)

            self.beliefList.append(self.numBelievers)
            self.ignorantList.append(self.numIgnorant)
            self.stiflerlist.append(self.numStiflers)



        return
