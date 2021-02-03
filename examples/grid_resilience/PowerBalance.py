#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 10:29:43 2021

@author: cclark2
"""

import matplotlib.pyplot as plt
#%matplotlib inline

from scipy.optimize import minimize
import numpy as np
import copy
import time
import imp
import pandas as pd
from random import randint, uniform, choice, choices

#%% STEP 1: POWER BALANCE (JEN)

# ASSUMPTIONS:

# Copper plate: power can flow anywhere, i.e. power balance is the main metric
# power in = power out
# whatever the power imbalance is, it is the power that will be requested by the substation

# PLOTS: 
# Network: currently this is a fake network that is not being used by anything.  It is for show only and may be 
# used once we start caring about AC/DC power flow
# Total power used and total power generated

# OUTPUT: total power requested or given by the substation

# ===============================================
# Step 1: graph topology
# ===============================================
print('Defining the network...')

# this will get the network for the 8500 - we can use this network once we feel comfortable going to bigger sizes
# filename = 'inputs/IEEE_8500_locations.csv'
# x,y = network.get_locations(filename, plot=True)

# start with a smaller system - start with the 37 bus system with a copper plate assumption
N = 37
np.random.seed(57) # -> to make sure that the randomness is always the same - helpful for debugging
# communication constants
comm_delay = 0.0050 # 5 ms per communication iteration

# length of time
Nt = 1440 # minutes in a day

# DEFINING GENERATION AND LOAD NODES

# define the power used by each of the nodes - this is where you would put your human behavior decisions 
# for each of these nodes

power_used = np.zeros((N,Nt))              # keep track of power used by each node
power_used[:,0] = 1000 * np.random.randn(N) # kW - starting power at time = 0

# Assume each node has solar and can generate power or consume power, if generated power, the power will be positive
# and if consuming power the power will be negative 

# TODO: More accurate grid behavior model
# TODO: we don't need to worry currently about control of solar 
# eventually we will want to add some controls to make the output at the substation near zero
for i in range(1,Nt):
    for j in range(N):
        # TODO: correlation with time of day 
        power_used[j,i] = power_used[j,i-1] - 15 * np.random.randn(1)   
        # change the power by a small amount for each minute 

# plot the profiles of each of the nodes
plt.figure(figsize=(10,7))
for i in range(N):
    plt.plot(power_used[i,:])

plt.title('Nominal Solar Output and Electricity Usage (Without Human Behavior)')    
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Power (W)')        


#%% STEP 2: BRING IN THE HUMANS (CAITY)

behaviors = [0, 1, 2] #Three choices: 0) keep using power as normal, 1) enhance power consumption (ex: plug in EV (assumption of 3-6kW)), 2) reduce power consumption
weights = (80, 10, 10) #probability of a behavior post-event (we assume weights are equal and random prior to an event happening)

pre_event_power_used = power_used.copy() #initial copies of power_used enables us to modify it under different behavioral conditions we define
post_event_power_used = power_used.copy()

substation_power = np.sum(power_used,axis=0)

pre_event_choices = np.zeros((N,Nt)) #these will keep track of what choices were made and when by each agent under different behavior conditions
post_event_choices = np.zeros((N,Nt))


#FOR A PRE-EVENT SCENARIO (Humans are interacting with the grid randomly)
for i in range (1, Nt):
    for j in range(N):
# TODO: Enable multiple decisions to be made, not just one
        if all(v == 0 for v in pre_event_choices[j,:i]):                   #if they haven't made a decision yet, they can make a decision
            # TODO: add in ability to make multiple decisions over time with if statements like line 101
            pre_event_choices[j,i] = randint(0,2)                        # agents make random choice at every timestep to do nothing differently (0), plug in their EV (1), or unplug (2)
            if pre_event_power_used[j,i] > 0:                            # if they are contributing power...
                if pre_event_choices[j,i] == 1:                           # and made a choice to plug in the EV, then...
                    pre_event_power_used[j,i:] -= uniform(300.0, 600.0)    # plug in EV, which is assumed to consume 3-6kW, and plugging in for 500 mins
                elif pre_event_choices[j,i] == 2:                         # to reduce power consumption, then...
                    pre_event_power_used[j,i:] += uniform(100.0, 200.0)   # use less, which assumes the house is using 1-2kW, and unplugging for 250 mins
    
            elif pre_event_power_used[j,i] < 0:                          # if they are drawing power from the grid... 
                if pre_event_choices[j,i] == 1:                           # and made a choice to plug in the EV, then...
                    pre_event_power_used[j,i:] -= uniform(300.0, 600.0)     # they can plug in EV, which is assumed to consume 3-6kW
    #Let's pretend this isn't a choice right now, since there is plenty of power for everyone
                elif pre_event_choices[j,i] == 2:
                    pre_event_power_used[j,i:] += uniform(100.0, 200.0) #= 0.0   # disconnect, which assumes the house is using 1-2kW

print(np.sum(pre_event_choices,axis=1))#making choices in columns, not rows
print(np.sum(post_event_choices, axis=1))

# plot the profiles of each of the nodes with human behavior
plt.figure(figsize=(10,7))
for i in range(N):
    plt.plot(pre_event_power_used[i,:])

plt.title('Output to Grid from Nodes With Human Behavior (Pre-Event)')    
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Power (W)')        


#%%
#FOR A POST-EVENT SCENARIO (Humans are interacting with the grid in a conditioned way)

#now shift the probability that people rush to the grid
for i in range (1, Nt):
    for j in range(N):
# TODO: Enable multiple decisions to be made, not just one
        if all(v == 0 for v in post_event_choices[j,:i]):                   #if they haven't made a decision yet, they can make a decision
            # TODO: make this choice non-random...add weights
            post_event_choices[j,i] = choices(behaviors, weights=weights, k=1)[0] # agents make random choice at every timestep to do nothing differently (0), plug in their EV (1), or unplug (2)
            if post_event_power_used[j,i] > 0:                            # if they are contributing power...
                if post_event_choices[j,i] == 1:                           # and made a choice to plug in the EV, then...
                    post_event_power_used[j,i:] -= uniform(300.0, 600.0)    # plug in EV, which is assumed to consume 3-6kW, and plugging in for 500 mins
                elif post_event_choices[j,i] == 2:                         # to reduce power consumption, then...
                    post_event_power_used[j,i:] += uniform(100.0, 200.0)   # use less, which assumes the house is using 1-2kW, and unplugging for 250 mins
    
            elif post_event_power_used[j,i] < 0:                          # if they are drawing power from the grid... 
                if post_event_choices[j,i] == 1:                           # and made a choice to plug in the EV, then...
                    post_event_power_used[j,i:] -= uniform(300.0, 600.0)     # they can plug in EV, which is assumed to consume 3-6kW
    #Let's pretend this isn't a choice right now, since there is plenty of power for everyone
                elif post_event_choices[j,i] == 2:
                    post_event_power_used[j,i:] += uniform(100.0, 200.0) #= 0.0   # disconnect, which assumes the house is using 1-2kW

print(np.sum(post_event_choices, axis=1))


# plot the profiles of each of the nodes with human behavior
plt.figure(figsize=(10,7))
for i in range(N):
    plt.plot(post_event_power_used[i,:])

plt.title('Output to Grid from Nodes With Weighted Human Behavior')    
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Power (W)')        

# TODO: Plot choices

# plot the total power requested by the substation
plt.figure(figsize=(10,7))
plt.plot(substation_power, label = 'With No Interaction')
plt.plot(np.sum(pre_event_power_used,axis=0), label = 'With Interaction (Pre-Event)')
plt.plot(np.sum(post_event_power_used,axis=0), label = 'With Interaction (Post-Event)')

plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=2) #, labelspacing=0.05)
    
plt.xlabel('Time (min)', fontsize=15)
plt.ylabel('Total Power out of Substation (W)', fontsize=15)
plt.grid()















