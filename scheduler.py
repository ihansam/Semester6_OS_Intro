#! /usr/bin/env python

# SKKU JKD
# OS Intro HW#1
# ver 1.2. implementing STCF. start. 19.10.04.

# [time arrival option 설계]
# job의 runtime을 받는 jlist처럼, job의 arrival time을 직접 받을 수 있는 alist 구현

# <case 1 (random workLoad)>
# -a option 미사용시 arrival time은 모두 0이다
# -a option 사용시 적어도 한 숫자를 입력해야 하며, 어떤 수를 입력하든 random arrival time이 설정된다
# 이때 MAX arrival time은 jobs * maxlen로 가정했다

# <case 2 (given workLoad)>
# alist가 null이면 arrival time은 모두 0이다
# alist가 null이 아니면, alist의 각 값을 arrival time으로 설정한다
# alist size가 jlist size와 다를 시, exception을 발생시킨다

import sys
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", 
                  action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system",
                  action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times",
                  action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job",
                  action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: FIFO, SJF, STCF, RR",
                  action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, 
                  action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")
# arrival time을 list로 입력할 수 있는 옵션 -a
parser.add_option("-a", "--alist", default="", help="instead zero arrival time, provide arrival time assign option.",
                  action="store", type="string", dest="alist")

(options, args) = parser.parse_args()

random.seed(options.seed)

print('ARG policy', options.policy)
if options.jlist == '':
    print('ARG jobs', options.jobs)
    print('ARG maxlen', options.maxlen)
    print('ARG seed', options.seed)
else:
    print('ARG jlist', options.jlist)

if options.alist != '':                                                 # print alist ARG if not NULL
    print('ARG alist', options.alist)

print('')

print('Here is the job list, with the run time of each job: ')

import operator

# job list
joblist = []                                                            # joblist is the list of job [jobnum, runtime, arrival time]
if options.jlist == '':                                                 # <case 1> /Random workload/
    for jobnum in range(0,options.jobs):
        runtime = int(options.maxlen * random.random()) + 1             
        if options.alist == '':                                         # alist == NULL -> arr time = 0
            arrtime = 0
        else:                                                           # alist != NULL -> random arr time
            arrtime = int(options.maxlen*options.jobs*random.random())  
        joblist.append([jobnum, runtime, arrtime])                      
        print('  Job', jobnum, '( length = ' + str(runtime) + ', arrival time = ' + str(arrtime) + ' )')
else:                                                                   # <case 2> /Given workload/    
    RTlist = options.jlist.split(',')                                   # given run time list by jlist    
    ATlist = []                                                         # given arr time list by alist
    if options.alist == '':                                             # alist == NULL -> all arr time = 0
        for filler in range(0,len(RTlist)):
            ATlist.append(0)
    else:
        ATlist = options.alist.split(',')                               # alist != NULL -> given alist를 arr time으로 할당
        if len(RTlist)!=len(ATlist):                                    # alist와 jlist의 size가 다를 때 exception
            print('ERROR: number of alist args must be same of jlist')
            exit(1)

    print("test:", len(RTlist))
    jobnum = 0
    for runtime in RTlist:
        arrtime = ATlist[jobnum]
        joblist.append([jobnum, float(runtime), arrtime])               
        jobnum += 1

    for job in joblist:        
        print('  Job', job[0], '( length = ' + str(job[1]) + ', arrival time = ' + str(job[2]) + ' )')
print('\n')

if options.solve == True:
    print('** Solutions **\n')
    if options.policy == 'SJF':
        joblist = sorted(joblist, key=operator.itemgetter(1))
        options.policy = 'FIFO'
    
    if options.policy == 'FIFO':
        thetime = 0
        print('Execution trace:')
        for job in joblist:
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
            thetime += job[1]

        print('\nFinal statistics:')
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for tmp in joblist:
            jobnum  = tmp[0]
            runtime = tmp[1]
            
            response   = t
            turnaround = t + runtime
            wait       = t
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (jobnum, response, turnaround, wait))
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            t += runtime
            count = count + 1
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))
                     
    if options.policy == 'RR':
        print('Execution trace:')
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        for i in range(0,jobcount):
            lastran[i] = 0.0
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        runlist = []
        for e in joblist:
            runlist.append(e)

        thetime  = 0.0
        while jobcount > 0:
            # print '%d jobs remaining' % jobcount
            job = runlist.pop(0)
            jobnum  = job[0]
            runtime = float(job[1])
            if response[jobnum] == -1:
                response[jobnum] = thetime
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, runtime])
            else:
                ranfor = runtime
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor
                jobcount -= 1
            thetime += ranfor
            lastran[jobnum] = thetime
        
        print('\nFinal statistics:')
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in range(0,len(joblist)):
            turnaroundSum += turnaround[i]
            responseSum += response[i]
            waitSum += wait[i]
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i, response[i], turnaround[i], wait[i]))
        count = len(joblist)
        
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count))

    # [STCF Algorighm 구현] =================================================================================
    if options.policy == 'STCF':
        # Execution Trace
        print('Execution trace:')

        count = len(joblist)

        for i in range(0,count):        # job: [jobnum, runtime, arrival time, time left, response time, turnaround time, wait time]
            j = joblist.pop(0)          # 각 job에 남은 시간 원소를 추가
            j.extend([j[1],0,0,0])            
            joblist.append(j)

        Decision_Times = []             # job arrival time마다 어떤 job을 실행할 지 결정해야한다          
        for j in joblist:
            Decision_Times.append(j[2])
        Decision_Times.sort()

        thetime = Decision_Times[0]     # 현재 시간. 가장 작은 arrival time부터 시작한다
        Memory = []                     # job이 도착해 wait하고 실행되는 공간
        Disk = []                       # 끝난 job이 옮겨지는 공간
        IDLE = True                     # CPU가 쉬고 있는 상태인지 나타내는 flag

        print(joblist)#test

        while len(Disk)!= count:        # job이 모두 끝날 때까지 반복
            if thetime in Decision_Times:           # 현재 시간이 decision time이면 새로 도착한 job을 memory로 옮긴다
                pass

                                            # 기존 실행하던 job을 중단한다 (print)
                                            # 어떤 job을 실행시킬지 판단한다
                                        # elif, 기존 실행하던 job이 끝나면
                                            # job이 끝났음을 표시한다 (print)
                                            # job을 disk로 옮긴다
                                            # 새로 실행할 job을 판단한다
                                                # 새로 실행할 job이 없다면 cpu를 쉬게하고 기다린다
                                        # 판단한 job을 1초동안 실행시킨다                                        

            break




        print(joblist)
        print(Memory)
        print(Decision_Times)





        # print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))



    # ========================================================================================================    
    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'STCF' and options.policy != 'RR': 
        print('Error: Policy', options.policy, 'is not available.')
        sys.exit(0)
else:
    print('Compute the turnaround time, response time, and wait time for each job.')
    print('When you are done, run this program again, with the same arguments,')
    print('but with -c, which will thus provide you with the answers. You can use')
    print('-s <somenumber> or your own job list (-l 10,15,20 for example)')
    print('to generate different problems for yourself.')
    print('')


