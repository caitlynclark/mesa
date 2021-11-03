#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 08:30:39 2021

@author: cclark2
"""

#Initial state
    #Calc power flow
#Perterbation/outage
    #for x in length of power outage:
        #calc power flow
        #human response
            #for each human/matrix
                #what do they do? add or subtract power?
                #how much?
                
                
from mesa.mesa import Agent, Model
from mesa.mesa.time import RandomActivation
import numpy as np



class GridAgent(Agent):
    """An agent with fixed initial electricity take a step. """ # gives some electricity to another agent.."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.electricity = 1 #100*np.random.randn()                # initial "wealth" of each agent
        self.electricity_over_time = [self.electricity]

    def step(self):
        if self.electricity <= 0:                               # agents check to see if they have or need electricity
            self.electricity_over_time.append(float(self.electricity))
            return
        else:                                                   # if agent has electricity, they can give it away (later, add keep it)
            give_electricity = 1 #1 * np.random.randn(1)           # this is so that the electricity given is the same as the electricity taken
            self.electricity -= give_electricity
            self.electricity_over_time.append(float(self.electricity))
            
            other_agent = self.random.choice(self.model.schedule.agents) # this is random rn, will change to better fit grid physics (electron pool)
            other_agent.electricity += give_electricity
#            other_agent.electricity_over_time.append(float(other_agent.electricity))
    
    
class GridModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)               # rn, this is activate all agents per step, in random order, make it simultaneous activation

        # Create agents
        for i in range(self.num_agents):
#            print('I am agent ' + str(i)) 
            a = GridAgent(i, self)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()                        # And this is where the grid, irrespective of the buses, is changing at each timestep









