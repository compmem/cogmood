#listgen
import random
import os
import pickle
import glob

from decimal import *
import config


def range_shuffle(ranges):
    random.shuffle(ranges)
    return ranges

#Balloon Randomization function.  Returns a list of dictionaries that determine
#the order of the bags and the number of balloons per bag.
def balloon_probability_orders(total_number_of_balloons,balloon_setup,randomize):
    num_ranges = len(balloon_setup)
    b_sets = range_shuffle(balloon_setup)
    balloons_per_dist=[]
    if randomize==True:
        while sum(balloons_per_dist) is not total_number_of_balloons or len(balloons_per_dist) is not num_ranges:
            if len(balloons_per_dist) > num_ranges:
                balloons_per_dist= []
            balloons_per_dist.append(random.randint(5,13))
        for i in range(0,num_ranges):
            b_sets[i]['number_of_balloons']=balloons_per_dist[i]
    else:

        for i in range(0,num_ranges):
            b_sets[i]['number_of_balloons']=total_number_of_balloons/num_ranges
    return b_sets
#function that returns a single reward for a single pump
def reward_calc(set_low,set_high):
    cash_money=round((random.uniform(set_low, set_high)),2)
    return cash_money
#Generates the bags of balloons and the balloons themselves
def add_air(total_number_of_balloons,num_ranges,balloon_setup,randomize,reward_low,reward_high,
            subject_directory,practice=False,shuffle_bags=True):
    #calling the balloon randomize function, setting it to x.  Returns a list of dictionaries
    x = balloon_probability_orders(total_number_of_balloons,balloon_setup,randomize)
    #g_code is a list of bags.  Each bag contains balloons of the same pop range
    g_code=[] #g_code: it really is that cool
    bag_ID=0 #counter used to identify what bag a balloon is in
    balloon_counter = 0     #A counter used to mark the balloon's number out of the total number of balloons
  
    colors = ["red", "orange", "yellow", "green", "lime", "mustard", "salmon", "purple", "lavender", "navy", "blue", "maroon"]
    random.shuffle(colors)
    if practice == True:
        colors = ["practice", "pink", "teal"]

    for balloon_set in x:
        limits=balloon_set['range']
        number_of_balloons=balloon_set['number_of_balloons']
        color = colors[x.index(balloon_set)]
        bag=[]
        for i in range(0,int(number_of_balloons)):
            g_set={'pop':[],'rewards':[],'max_pumps':[],'pump_range':limits,
                   'balloon_in_bag':i,'balloon_number':balloon_counter,
                   'bag_ID_number':bag_ID, 'color':color,
                   'number_of_balloons_in_bag':number_of_balloons}
            balloon_counter+=1
            xx=random.randint(limits[0],limits[1])
            f = [1]*xx
            g_set['max_pumps']=len(f)
            f.append(0)
            pump_rewards=[]
            # reward_dist_type=[]
            for pump in range(60):              #Loop that determines which uniform reward distribtuion to use
            #     reward_dist=random.randint(1,100)    #There is a 10% chance the reward is from the higher distribtuion, 90% lower dist
            #     if reward_dist>7.5:
            #         set_low=H_reward_low
            #         set_high=H_reward_high
            #         reward_dist_type.append('high')
            #     else:
            #         set_low=L_reward_low
            #         set_high=L_reward_high
            #         reward_dist_type.append('low')
            #         f.insert(pump,1)
                money=reward_calc(reward_low,reward_high) #Calling the reward_calc function, setting it to money
                pump_rewards.append(money)   #append reward to list of rewards
            g_set['pop']=f
            g_set['rewards']=pump_rewards    #add list of rewards to ballon dictionary
            #g_set['reward_dist']=reward_dist_type  #add list of reward dist type to balloon dictionary
            bag.append(g_set)    #add the balloon to the bag
        g_code.append(bag)    #add the bag to the g_code
        bag_ID +=1    #increase bag ID number by one
    all_balloons = []
    for bgx in g_code:
        for bx in bgx:
            all_balloons.append(bx)
    g_code = all_balloons
    if practice == False and shuffle_bags == True:
        random.shuffle(g_code)
    else:
        pass
    if practice == True:
        pass
    else:
        try:
            pickles = glob(subject_directory+'/obart_pickles')
            session_num = str(len(pickles))
            pickle.dump(g_code,open(subject_directory+'/obart_pickles/bags_session_'+session_num+'.p','wb'))
        except:
            os.makedirs(subject_directory+'/obart_pickles')
            pickle.dump(g_code,open(subject_directory+'/obart_pickles/bags_session_0.p','wb'))
    return g_code

    return g_code

# x = add_air(total_number_of_balloons=config.NUM_BALLOONS,
#                   num_ranges=len(config.BALLOON_SETUP),
#                   balloon_setup=config.BALLOON_SETUP,
#                   randomize=config.RANDOMIZE_BALLOON_NUM,
#                   reward_low=config.REWARD_LOW,
#                   reward_high=config.REWARD_HIGH,
#                   subject_directory="1",
#                   practice=False,
#                   shuffle_bags=config.SHUFFLE_BAGS)
# print(x)
