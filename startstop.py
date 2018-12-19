#############################################################################
#
# StartAndStopInstancesByTagReview
# Start or stop EC2 instances regarding the StatrDailyTime or StopDailyTime Tags
#
#############################################################################
#
# Version 5
#
#############################################################################

import os
import time
import stdexplib

region = 'eu-west-1'

#
# Principal function
# As the start and stop commands take in option a list of instances ID
# we are working to build a complete instances ID list, beginnning with all
# runnig instances and remove from the list the instances ID which the stop time is not past
#
def checkthem(actiontime):

    myec2instanceslist = []

    #First step : arret des serveurs qui tournent
    print ("Get Running EC2 Instances and stop them if necessary....")
    myec2instanceslist = stdexplib.get_instanceid_by_state("running",region)
    get_check_actions("Name","StartDailyTime","StopDailyTime","OpeningDays",["i-01a9be017b577d7f8"],"stop",actiontime)

    myec2instanceslist = []

    #Second step : demarrage des serveurs arretes
#    print ("Get Stopped EC2 Instances and start them if necessary....")
#    myec2instanceslist = stdexplib.get_instanceid_by_state("stopped",region)
#█  get_check_actions("Name","StartDailyTime","StopDailyTime","OpeningDays",myec2instanceslist,"start",actiontime)

#
# Get some tags values, and ask some other function to check the values
# Input :
#   tag1 => Name
#   tag2 => StartDailyTime
#   tag3 => StopDailyHour
#   tag4 => OpeningDays
#   instanceslist => EC2 instances list to check
#   action => start or stop
# Output : Nothing
def get_check_actions(tag1,tag2,tag3,tag4,instanceslist,action,actiontime):

    idtodel = []
    
    if action == "start" :
            state = "Stopped"
    else :
            state = "Running"

    taglist = [tag1,tag2,tag3,tag4]
    instancesdata = stdexplib.get_ec2tagsvalues(region,instanceslist,[tag1,tag2,tag3,tag4])

    for index in range(0, len(instancesdata), 1):
        print (instancesdata[index])
        if instancesdata[index][1] == "NO TAG":
            InstanceName = instancesdata[index][0]
        else:
            InstanceName = instancesdata[index][1]

        if instancesdata[index][2] == "NO TAG":
            StartTime = ""
        else:
            StartTime = instancesdata[index][2]

        if instancesdata[index][3] == "NO TAG":
            Stoptime = ""
        else:
            StopTime = instancesdata[index][3]
    
        if instancesdata[index][4] == "NO TAG":
            OpDays = ""
        else:
            OpDays = instancesdata[index][4]
        
#    # For each instance in instancelist, get the tags values
#    for instanceid in instanceslist:
#
#        InstanceName = stdexplib.get_ec2tagvalue(instanceid,tag1,region)
#        if InstanceName == "":
#            InstanceName = instanceid
#
#        StartTime = stdexplib.get_ec2tagvalue(instanceid,tag2,region)
#        StopTime = stdexplib.get_ec2tagvalue(instanceid,tag3,region)
#        OpDays = stdexplib.get_ec2tagvalue(instanceid,tag4,region) 

     




        
#        # check the consistency of the values
#        if not(verify_time_format(StartTime)) or not(verify_time_format(StopTime)) or not(verify_days_format(OpDays)):
#            print (InstanceName+" - "+state+" - Tags missing or format ko : leaving in the actual state")
#            idtodel.append(instanceid)
#        # Check if we have something todo regarding the different values
#        else:
#            # if it's a working day
#            if check_day(OpDays):
#                if check_slot(StartTime,StopTime,action,actiontime) == 0:
#                    print (InstanceName+" - "+state+" - State OK")
#                    idtodel.append(instanceid)
#                elif check_slot(StartTime,StopTime,action,actiontime) == 1:
#                    print (InstanceName+" - "+state+" - To "+action)
#                elif check_slot(StartTime,StopTime,action,actiontime) == 2:
#                    if action == "start":
#                        print (InstanceName+" - "+state+" - To Start")
#            # If it's not a working day
#            elif (not(check_day(OpDays))):
#                if action == "stop":
#                    print (InstanceName+" - "+state+" - To Stop")
#                elif action == "start":
#                    print (InstanceName+" - "+state+" - State OK")
#                    idtodel.append(instanceid)
#            # Fall back
#            else:
#                print (InstanceName+" : WARNING - Do not know which action to take : leaving in the actual state")
#                idtodel.append(instanceid)
#
#    for id in idtodel:
#        instanceslist.remove(id)
#
#    if len(instanceslist) > 0:
#        print (len(instanceslist)," instance(s) to ",action)
#        ec2instances_action(instanceslist,action)
#    else:
#        print ("0 instance to ",action)


# Check the correct configuration of a time data based on REGEXP
# Input : StartDailyTime or StopDailyTime tag value
# Output :
#   True if formzt is ok
#   False if format is ko
#
def verify_time_format(tagvalue):

    import re

    if re.match('^[0-9]{2}\:[0-9]{2}\:[0-9]{2}\+[0-9]{2}\:[0-9]{2}$',tagvalue):
        if int(tagvalue[:2])==99:
            return True
        if (int(tagvalue[:2])>23) or (int(tagvalue[3:5])>59) or (int(tagvalue[6:8])>59):
            print (tagvalue+" : Time Format OK - Data KO")
            return False
        else:
            return True
    else:
        # print (tagvalue+" : Time Format KO")
        return False

#
# Check the correct configuration of a day data based on REGEXP
# Input : Openingays tag value
# Output :
#   True if formzt is ok
#   False if format is ko
#
def verify_days_format(tagvalue):

    import re

    if re.match('^[aA-zZ]{3}(,[aA-zZ]{3})*$',tagvalue):
        return True
        print (tagvalue + " : OpeningDays Format KO")
    else:
        return False

#
# Check if today we must start the instances
# Input : Openingays tag value
# Output :
#   True if it's a working day
#   False if it's not a working day
#
def check_day(tagvalue):

    from time import strftime
    n = 0

    actualday = strftime("%a").upper()

    tagsplit=tagvalue.split(",")
    for day in tagsplit:
        if day == actualday:
            n=1

    if n == 1:
        return True
    else:
        return False


#
# Check if it is the good time to do something
# Input :
#   StartTime
#   StopTime
#   State of the instance
#
# Output
#   0 : do nothing
#   1 : start or stop the instance
#   2 : start and stop time are the same (but not 99)
#
def check_slot(tagvalue1,tagvalue2,state,actiontime):

    #print ("StartTime : "+tagvalue1)
    #print ("StopTime : "+tagvalue2)

    if int(tagvalue1[:2]) == 99:
        if int(tagvalue2[:2]) == 99:
            return 0
        else:
            if state == "stop" and check_time(tagvalue2,actiontime) == 1:
                return 1
            else:
                return 0
    elif int(tagvalue2[:2]) == 99:
        if int(tagvalue1[:2]) == 99:
            return 0
        else:
            if state == "start" and check_time(tagvalue1,actiontime) == 1:
                return 1
            else:
                return 0
    elif (int(tagvalue1[:2]) != 99) and (int(tagvalue2[:2]) != 99) and (tagvalue1 == tagvalue2):
        return 2
    else:
        if state == "start":
            if check_time(tagvalue1,actiontime) == 1 and check_time(tagvalue2,actiontime) == 0:
                return 1
            else:
                return 0
        elif state == "stop":
            if (check_time(tagvalue1,actiontime) == 1 and check_time(tagvalue2,actiontime) == 1) or (check_time(tagvalue1,actiontime) == 0 and check_time(tagvalue2,actiontime) == 0):
                return 1
            else:
                return 0
        else:
            return 0

#
# Check if it is the good time to do something
# Input : StartDailyTime or StopDailyTime tag value
# Output : 0 if ok / 1 if ko / 2 if 99
#
def check_time(tagvalue,actiontime):

    from datetime import time
    
    actualtime = time(int(actiontime[:2]), int(actiontime[3:5]), int(actiontime[6:8]))
    idgmttime = time(int(tagvalue[:2]), int(tagvalue[3:5]), int(tagvalue[6:8]))
    
    #now = datetime.now()
    #actualtime = now.time()
    #if tagvalue[8:9] == "+":
    #    idgmttime = time(int(tagvalue[:2])-int(tagvalue[9:11]), int(tagvalue[3:5]), int(tagvalue[6:8]))
    #else:
    #    idgmttime = time(int(tagvalue[:2])+int(tagvalue[9:11]), int(tagvalue[3:5]), int(tagvalue[6:8]))

    if idgmttime <= actualtime:
        return 1
    else:
        return 0

#
# Start or Stop EC2 instances
# Input :
#   instanceslist => list of EC2 instances ID
#   action => action to perform on the instances in the list
# Output : Nothing
#
def ec2instances_action(instanceslist,action):

    ec2 = boto3.client('ec2', region_name=region)

    if action == "start":
        for id in instanceslist:
            print (id+" starting")
        #ec2.start_instances(InstanceIds=instanceslist)
    else:
        for id in instanceslist:
            print (id+" stopping")
        #ec2.stop_instances(InstanceIds=instanceslist)

#
# Main for Lambda
#
def lambda_handler(event, context):
    
    from time import strftime
    
    # Print default lambda time
    print ("Lambda default TimeZone : " + os.environ['TZ'])
    
    # Get the MYTIMEZONE environment variable, if not exist set it to Paris timezone
    myTZ=os.getenv('MYTIMEZONE','Europe/Paris')
    # Set the lambda local TZ
    os.environ['TZ'] = myTZ
    time.tzset()
    lambdatime=strftime("%H:%M:%S").upper()
    print ("Right local TimeZone/Time : "+myTZ+"/"+ lambdatime)
    
    # go 
    checkthem(lambdatime)

#
# Main for Python Origin
#
#print ("Gooooo !!!!")
#lambda_handler("","")
