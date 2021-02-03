#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 08:30:39 2021

@author: cclark2
"""

from GridModel import *
import matplotlib.pyplot as plt
import numpy as np


np.random.seed(57)  # to make sure that the randomness is always the same
Nt = 1440 # minutes in a day
num_agents = 37 #number of agents/buses #10


#Visualize how much electricity each agent has after a day of steps of giving/taking

all_electricity = []
#all_electricity = np.zeros((num_agents, Nt))

for j in range(Nt):
    # Run the model
    model = GridModel(num_agents)
    for i in range(num_agents):
        model.step()

    # Store the results in a num_agent x Nt matrix
    for agent in model.schedule.agents:
        all_electricity.append(agent.electricity)
#        print(agent.electricity)
        
#        all_electricity[agent,:] = agent.electricity
#        print(all_electricity)



## plot the profiles of each of the nodes
#plt.figure(figsize=(10,7))
#for i in range(N):
#    plt.plot(power_used[i,:])
#    
#plt.xlabel('Time (min)', fontsize=15)
#plt.ylabel('Power (kW)')        
#
## plot the total power requested by the substation
#plt.figure(figsize=(10,7))
#plt.plot(np.sum(power_used,axis=0))
#plt.xlabel('Time (min)', fontsize=15)
#plt.ylabel('Total Power out of Substation (kW)', fontsize=15)
#plt.grid()

#agent_wealth = [a.electricity for a in model.schedule.agents]
#plt.hist(agent_wealth)

agent_wealth = [a.electricity_over_time for a in model.schedule.agents]
for ii in range(len(agent_wealth)):
    plt.plot(agent_wealth[ii])
#
#plt.hist(all_electricity, bins=range(max(all_electricity)+1))
#plt.show()


#%% DEFINING GENERATION AND LOAD NODES

# define the power used by each of the nodes - this is where you would put your human behavior decisions 
# for each of these nodes

power_used = np.zeros((N,Nt))              # keep track of power used by each node
power_used[:,0] = 100 * np.random.randn(N) # kW - starting power at time = 0

# Assume each node has solar and can generate power or consume power, if generated power, the power will be positive
# and if consuming power the power will be negative 

# TODO: we don't need to worry currently about control of solar 
# eventually we will want to add some controls to make the output at the substation near zero
for i in range(1,Nt):
    for j in range(N):
        # TODO: correlation with time of day 
        power_used[j,i] = power_used[j,i-1] + 1 * np.random.randn(1)   
        # change the power by a small amount for each minute 
        # Caity - this is where you would add your inputs

# plot the profiles of each of the nodes
plt.figure(figsize=(10,7))
for i in range(N):
    plt.plot(power_used[i,:])
    
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Power (kW)')        

# plot the total power requested by the substation
plt.figure(figsize=(10,7))
plt.plot(np.sum(power_used,axis=0))
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Total Power out of Substation (kW)', fontsize=15)
plt.grid()

