_Author_ = "Karthik Vaidhyanthan"

from InitializerClass import Initialize
from Custom_Logger import logger
from SWIM_Planner import Planner
# Analyzes the data to check if the reponse time is above the threshold
# When using machine learning this will use the ML models to predict the expected reponse time


init_obj = Initialize()

class Analyzer():
    def __init__(self):
        #self.monitor_response_time = monitor_dict["response_time"]
        #self.monitor_arrival_rate = monitor_dict["arrival_rate"]
        #self.monitor_dimmer_value = monitor_dict["dimmer_value"]
        #self.monitor_active_servers = monitor_dict["active_servers"]
        self.threshold = init_obj.swim_response_time_threshold
        self.prev_adaptation_flag = False # This allows to check if the planner needs to be invoked only for the feedback or for adaptation
        self.count = 0


    def perform_analysis(self,monitor_dict,connection_obj,rl_obj):
        logger.info("Inside the Analyzer: Performing the analysis")
        monitor_response_time = monitor_dict["response_time"]
        if monitor_response_time > self.threshold and self.prev_adaptation_flag is False:
            logger.info(" RT crossing threshold, triggering the planner ")
            mode = "ADA"  # the adaptation needs to be performed
            self.prev_adaptation_flag = True
            # call the planner class object
            server_in_use = monitor_dict["active_servers"]
            arrival_rate = monitor_dict["arrival_rate"]
            dimmer_value = monitor_dict["dimmer_value"]
            self.count+=1 # To check the number of adaptations as well as to check if it is the first run of the approach
            plan_obj = Planner(monitor_response_time,server_in_use,arrival_rate,dimmer_value,connection_obj,rl_obj)
            plan_obj.generate_adaptation_plan(mode,self.count)
            self.prev_adaptation_flag = True


        elif monitor_response_time > self.threshold and self.prev_adaptation_flag  is True:
            print (" Setting mode to adaptation and Feedback ")
            mode = "FEEDADA"  # the adaptation needs to be performed
            self.prev_adaptation_flag = True
            # call the planner class object
            server_in_use = monitor_dict["active_servers"]
            arrival_rate = monitor_dict["arrival_rate"]
            dimmer_value = monitor_dict["dimmer_value"]
            self.count += 1  # To check the number of adaptations as well as to check if it is the first run of the approach
            plan_obj = Planner(monitor_response_time, server_in_use, arrival_rate, dimmer_value, connection_obj, rl_obj)
            plan_obj.generate_adaptation_plan(mode, self.count)
            self.prev_adaptation_flag = True

        elif monitor_response_time <= self.threshold and self.prev_adaptation_flag is True:
            mode = "FEED" # no need to perform the adpatation but this is just for the feedback
            server_in_use = monitor_dict["active_servers"]
            response_time = monitor_dict["response_time"]
            arrival_rate = monitor_dict["arrival_rate"]
            dimmer_value = monitor_dict["dimmer_value"]
            plan_obj = Planner(monitor_response_time, server_in_use, arrival_rate, dimmer_value, connection_obj,
                               rl_obj)
            plan_obj.generate_adaptation_plan(mode, self.count)
            self.prev_adaptation_flag = False # change the flag back to false

        else:

            mode = "FEED" # no need to perform the adpatation but this is just for the feedback
            server_in_use = monitor_dict["active_servers"]
            response_time = monitor_dict["response_time"]
            arrival_rate = monitor_dict["arrival_rate"]
            dimmer_value = monitor_dict["dimmer_value"]
            plan_obj = Planner(monitor_response_time, server_in_use, arrival_rate, dimmer_value, connection_obj,
                               rl_obj)
            plan_obj.generate_adaptation_plan(mode, self.count)
            self.prev_adaptation_flag = False # change the flag back to false
            print (" Below threshold -- Check for revenue")
