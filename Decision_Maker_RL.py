_Author_ = "Karthik Vaidhyanathan"

# Script to perform Reinforcment Learning for selecting the pattern to be used in a given state

# State space is formed by the possible energy states
# Action space denotes the possible actions that can be performed in a given state, this actions are basically moving right,
# left bottom and top

#import gym
import numpy as np
import time
import random
from Custom_Logger import logger
import os
'''
Possible states are low, medium and high

Possible actions are adaptation options which include
1. Add Server
2. Remove Server
3. increase dimer by 0.25
4. decrease dimer by 0.25
5. do nothing
6. Add server and increase dimer by 0.25
7. Add server and decrease dimer by 0.25
8. Remove server and increase dimer by 0.25
9. Remove server and decrease dimer by 0.25


s* = get_active_servers
a = get_arrival_rate
d = get_dimmer
T = 60
c = 1 
k = 140 requests/second

U_rt = t*a*(d*r_o + (1-d)*r_m)
U_ct = t*c*(s*-s)




Total of 9 possible adaptation options given a state
'''
from InitializerClass import Initialize

reward_action_map = {0:-2,1:0,2:-3,3:-2,4:-1,5:0,6:-4,7:-5,8:-4,9:-3,10:-1,11:-2,12:1,13:2,14:3,15:4,16:0}
init_object = Initialize()   # Initialize the configurations
class Env():
    # Create the environment with states and actions to perform reinforcement learning
    def __init__(self):
        self.qos_states = 3 # The MXM matrix for state action space
        self.columns = 10
        self.posX = 0  # The initial X and Y coordinate
        self.posY = 0
        self.endX = self.qos_states-1
        self.endY = self.columns - 1
        self.actions = [i for i in range(0,9)]    # 9 possible actions are there
        self.stateCount = self.qos_states
        self.actionCount = len(self.actions)

    def reset(self):
        # To reset the board back to the original state
        self.posX = 0
        self.posY = 0
        self.done = False
        return  0,0,False



    def step(self,action,response_time,dimmer_value, U_rt,U_ct,U_rt_star,arrival_rate):
        # state can take 3 values
        reward = 0
        state  = 0
        if response_time >= init_object.swim_response_time_threshold:
            # Greater than the threshold
            state = 0
            #reward = 5 * (0.60-response_time)  + reward_action_map[action]
            #reward = init_object.swim_time_interval * min(0,arrival_rate-init_object.swim_k_value)*init_object.r_opt + -1*1000
            #reward = -1*1000
            # for high penalty
            reward = -5
        #elif response_time > init_object.swim_response_base_time and response_time < init_object.swim_response_time_threshold:
        elif response_time < init_object.swim_response_time_threshold and U_rt == U_rt_star:
        #elif response_time < init_object.swim_response_time_threshold and dimmer_value >= 0.5:
            state = 1
            #reward = U_rt + U_ct
            #reward = 2000
            reward = 10
        #elif response_time > 0 and response_time <=init_object.swim_response_base_time:
        #elif  response_time < init_object.swim_response_time_threshold and dimmer_value < 0.5:
        elif  response_time < init_object.swim_response_time_threshold and U_rt < U_rt_star:
            state = 2
            #reward = 5*(0.40-response_time) + reward_action_map[action]
            #reward = U_rt   # little less penalty
            #reward = -1*500
            reward = 1
        next_state = state
        logger.info(" state reward " + str(state)  + "   " +  str(reward))
        return next_state,reward


    def random_action(self,server_add_flag,server_remove_flag, current_server_count):
        # Return a random action from the set of available actions
        logger.info("Random action selection -- Exploration")
        if server_remove_flag is True or server_add_flag is True:
            # Only change of dimmer and no action can be performed
            print("latency action --random")
            logger.info("random -- latency action")
            possible_choice = [2,3,4]
            return np.random.choice(possible_choice)
        elif current_server_count == 3:
            # find the second maximum element which inturn finds the next best action that can be performed
            print("no server addition --random")
            logger.info(" random -- no server addition allowed action")
            possible_choice = [1, 2, 3, 4, 6, 7]
            return np.random.choice(possible_choice)

        elif current_server_count == 1:
            # Find the second maximum element
            print("no server removal --random")
            logger.info("random -- no server removal allowed action")
            possible_choice = [0, 2, 3, 4, 5, 6]
            return np.random.choice(possible_choice)
        else:
            print("all actions --random")
            logger.info("random --all actions allowed")
            return np.random.choice(self.actions)

env = Env() # Initalize the environment

class Reinforcer():
    # Class which is reponsible for leanring and updating the Q-Table
    def __init__(self):
        # Start with random values that's always the best choice to go forward
        #self.qTable = np.random.rand(env.stateCount, env.actionCount).tolist()
        self.qTable = np.zeros((env.stateCount, env.actionCount)).tolist()
        #self.qTable = np.load("Qtable_Reactive_RL_5.txt.npy").tolist()
        #self.qTable = np.load("Qtable_Reactive_RLMC_V2.npy").tolist()
        self.state = 2
        self.gamma = 0.02 # relevance of future rewards
        self.epsilon = 0.08
        self.decay = 0.2
        self.count = 0  # Keep a copunt on the number of adaptations
        self.action  = 8 #inital action
        self.alpha  = 0.4  # Learning rate
        print (self.qTable)


    def learn(self,epochs,gamma,epsilon,decay):
        # Function to perform the learning of Q-Table and then storing it
        # For every state,pattern we need to keep a check on the reward for each of the four actions in a Q-Table
        # print (np.random.rand(3,4).tolist())
        # hyperparameters


        # training loop
        for i in range(epochs):
            state, reward, done = env.reset()
            steps = 0

            while not done:
                os.system('clear')
                print("epoch #", i + 1, "/", epochs)
                # env.render()
                time.sleep(0.05)

                # count steps to finish game
                steps += 1

                # act randomly sometimes to allow exploration
                if np.random.uniform() < epsilon:
                    action = env.random_action()
                # if not select max action in Qtable (act greedy)
                else:
                    action = self.qTable[state].index(max(self.qTable[state]))

                # take action
                response_time = random.uniform(0.05,1.5)
                print (response_time)
                next_state, reward = env.step(action,response_time=response_time)

                # update qtable value with Bellman equation
                self.qTable[state][action] = reward + gamma * max(self.qTable[next_state])

                # update state
                state = next_state
                # The more we learn, the less we take random actions
                print (state)
                print (action)

                time.sleep(3)
            epsilon -= decay * epsilon

            print("\nDone in", steps, "steps".format(steps))
            time.sleep(0.8)

        print(self.qTable)

    def select_action(self,mode,response_time,dimmer_value,U_rt,U_ct,U_rt_star,arrival_rate,current_server_count,server_add_flag, server_remove_flag,verification_flag=False):
        # response time is the one obtained from SWIM
        # U_rt is the utlity of the revenue
        # U_ct is the utility component of the cost
        # K_value denotes the number of requests that can be processed for the given interval
        self.count+=1
        change_factor = False # To make sure an adaptation is triggered when rewward is negative
        # Given the state, predict the action based on the learning performed by the Q-Learning algorithm
        # self.action will give reward of the previous action performed
        # calculate the reward obtained for the previous action and then select the next best state
        if self.count<=1 or mode == "ADA":
            print (" not updating Q Table")
        else:
            next_state, reward = env.step(self,response_time, dimmer_value, U_rt, U_ct, U_rt_star, arrival_rate)
            # print (self.qTable[0][17])
            self.qTable[self.state][self.action] = (1 - self.alpha) * self.qTable[self.state][self.action] + self.alpha * (
                    reward + self.gamma * max(
                self.qTable[next_state]))
            np.save("Qtable_Test", self.qTable)
            self.state = next_state

        if np.random.uniform() < self.epsilon:
            #Allow little random exploration
            action = env.random_action(server_add_flag,server_remove_flag,current_server_count)
        else:
            if server_remove_flag is True or server_add_flag is True:
                # Only change of dimmer and no action can be performed
                print ("latency action")
                logger.info("latency action")
                index_action_map = {}
                possible_choice = [2,3,4]
                if verification_flag is True:
                    backup_choice = possible_choice
                    if self.action in possible_choice:
                        possible_choice.remove(self.action)
                        print(" removed " + str(self.action))
                        print("possible choice :", possible_choice)
                    if len(possible_choice) == 0:
                        # If all the actions have been tried
                        print ("reassigning possible choice")
                        possible_choice = backup_choice
                for index in possible_choice:
                    index_action_map[index] = self.qTable[self.state][index]

                action  = max(index_action_map, key=index_action_map.get)
                #first_list = self.qTable[self.state][2:6]
                #first_list.append(self.qTable[self.state][17])
                #index_value = first_list.index(max(first_list))
                #action = self.qTable[self.state].index(max(first_list))
            elif current_server_count == 3:
                # find the second maximum element which inturn finds the next best action that can be performed
                print ("no server addition")
                logger.info("no server addition allowed action")
                #first_list = self.qTable[self.state][1:6]
                #first_list.extend(self.qTable[self.state][12:17]) # include only those actions where add server is not present
                index_action_map = {}
                possible_choice = [1, 2, 3, 4,7,8]
                if verification_flag is True:
                    backup_choice = possible_choice
                    if self.action in possible_choice:
                        possible_choice.remove(self.action)
                        print(" removed " + str(self.action))
                        print("possible choice :", possible_choice)
                    if len(possible_choice) == 0:
                        # If all the actions have been tried
                        possible_choice = backup_choice
                for index in possible_choice:
                    index_action_map[index] = self.qTable[self.state][index]

                action = max(index_action_map, key=index_action_map.get)
                # action = self.qTable[self.state].index(max(first_list))
                #if  action == 1 and current_server_count ==1:
                #    first_list = self.qTable[self.state][2:6]
                #    first_list.extend([self.qTable[self.state][17]])
                #    action = self.qTable[self.state].index(max(first_list))
            elif  current_server_count ==1:
                # Find the second maximum element
                print ("no server removal")
                logger.info("no server removal allowed action")
                #first_list = self.qTable[self.state][2:6] # only dimmer changes
                #first_list.append(self.qTable[self.state][0]) # add server is also allowed
                #first_list.extend(self.qTable[self.state][7:11])  # include only those actions where remove is not present
                #first_list.append(self.qTable[self.state][17]) # no action is also allowed

                index_action_map = {}
                possible_choice = [0, 2, 3, 4, 5, 6]
                if verification_flag is True:
                    backup_choice = possible_choice
                    if self.action in possible_choice:
                        possible_choice.remove(self.action)
                        print(" removed " + str(self.action))
                        print("possible choice :", possible_choice)
                    if len(possible_choice) == 0:
                        # If all the actions have been tried
                        possible_choice = backup_choice

                for index in possible_choice:
                    index_action_map[index] = self.qTable[self.state][index]

                action = max(index_action_map, key=index_action_map.get)


                    #action = self.qTable[self.state].index(max(first_list))
                    #if action == 0 and current_server_count == 3:
                    #    # addition cannot be perfromed
                    #    print(self.qTable[self.state][2:6])
                    #    first_list = self.qTable[self.state][2:6]
                    #    first_list = first_list.extend([self.qTable[self.state][17]])
                    #    action = self.qTable[self.state].index(max(first_list))
            else:
                # any action is allowed
                print ("all actions ")
                possible_choice = [i for i in range(0,9)]
                index_action_map = {}
                if verification_flag is True:
                    backup_choice = [i for i in range(0,9)]
                    if self.action in possible_choice:
                        possible_choice.remove(self.action)
                        print (" removed " + str(self.action))
                        print ("possible choice :" ,possible_choice)
                    if len(possible_choice) == 0:
                        # If all the actions have been tried
                        print("reassigning possible choice")
                        print ("backup choice ", backup_choice)
                        possible_choice = backup_choice
                    for index in possible_choice:
                        index_action_map[index] = self.qTable[self.state][index]
                    action = max(index_action_map, key=index_action_map.get)
                else:
                    action = self.qTable[self.state].index(max(self.qTable[self.state]))




        print ("action ", action)
        print (self.qTable)
        logger.info("RL action " + str(action))
        self.action = action
        return action,change_factor




if __name__ == '__main__':

    reinforce_object = Reinforcer()
    #epochs = 10  # Number of Iterations
    #gamma = 0.1  # Learning rate
    #epsilon = 0.08
    #decay = 0.1
    #reinforce_object.learn(epochs,gamma,epsilon,decay)
    reinforce_object.select_action(0.10,0.50,15.0,12.0,12.5,120,1, True, False)
    #next_state,reward,posX,posY = reinforce_object.predict(1)
    #print (posX,posY)