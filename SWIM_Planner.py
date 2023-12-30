_Author_ = "Karthik Vaidhyanathan"

# The class for planning. This uses RL for selecting the actions
from Decision_Maker_RL_Update import Reinforcer
from Custom_Logger import logger
from InitializerClass import Initialize
from Utility_Evaluator import Utility_Evaluator
from SWIM_Executor import Executor
import json
import datetime
from datetime import datetime


class Planner():

    def __init__(self,response_time,server_in_use, arrival_rate,dimmer_value,connection_obj,rl_obj):
        self.response_time = response_time
        self.server_in_use = server_in_use
        self.arrival_rate = arrival_rate
        self.dimmer_value = dimmer_value
        self.connection_obj = connection_obj
        self.rl_obj = rl_obj


    def generate_adaptation_plan(self,mode,count):
        # Use the reinforceer to generate the adaptation plan
        logger.info("Inside the planner: Generating the adaptation plan")

        util_obj = Utility_Evaluator(self.server_in_use,self.arrival_rate,self.dimmer_value)
        U_rt, U_ct, U_rt_star = util_obj.calculate_utility()

        # Check if server can be added

        adap_status_json = {}
        with open("adap_status.json", "r") as json_file:
            adap_status_json = json.load(json_file)

        server_add_time_string = adap_status_json["server_added_time"]
        server_count = adap_status_json["current_server_count"]
        server_added_time = datetime.strptime(server_add_time_string, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()

        server_add_flag = True
        # Check if a server can be added by considering the latency of server addition
        if (current_time - server_added_time).seconds >= 80:
            server_add_flag = False

        # Check if dimmer can be increased or decreased
        dimmer_increase = True
        dimmer_decrease = True

        logger.info("Current dimmer value " + str(self.dimmer_value))

        if self.dimmer_value == 1.0:
            dimmer_increase = False
        elif self.dimmer_value == 0.0:
            dimmer_decrease = False

        print (" dimmer flag status, increase : decrease " + str(dimmer_increase) + " : " + str(dimmer_decrease))
        logger.info(" dimmer flag status, increase : decrease " + str(dimmer_increase) + " : " + str(dimmer_decrease))

        if mode=="ADA" or mode == "FEEDADA" or mode == "FEED":


            action,change_factor = self.rl_obj.select_action(mode,self.response_time,self.dimmer_value,U_rt,U_ct,U_rt_star,self.arrival_rate,
                                                 self.server_in_use,server_add_flag=server_add_flag, server_remove_flag=False,
                                                 verification_flag=False,dimmer_increase_flag=dimmer_increase,dimmer_decrease_flag=dimmer_decrease)

            execute_obj = Executor(self.dimmer_value,self.server_in_use,self.connection_obj)
            execute_obj.adaptation_executor(action)

        elif mode == "FEED_TEST":
            action, change_factor = self.rl_obj.select_action(mode, self.response_time, self.dimmer_value, U_rt, U_ct,
                                                              U_rt_star, self.arrival_rate,
                                                              self.server_in_use, server_add_flag=False,
                                                              server_remove_flag=False,
                                                              verification_flag=False)

            print (" RL Feedback updated, no adaptation executed")



