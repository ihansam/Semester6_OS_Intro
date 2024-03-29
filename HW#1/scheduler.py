#! /usr/bin/env python
# SKKU EEE KD JIN. ihansam@skku.edu
# OS Intro HW#1
# ver 4.0 RR Done 19.10.06.

# [time arrival option 설계]
# job의 runtime을 받는 jlist처럼, job의 arrival time을 직접 받을 수 있는 alist 구현

# <case 1 (random workLoad)>
# -a option 미사용시 arrival time은 모두 0이다
# -a option 사용시 적어도 한 숫자를 입력해야 하며, 어떤 수를 입력하든 random arrival time이 설정된다
# 이때 MAX arrival time은 job 개수 * 평균 job 길이로 가정했다

# <case 2 (given workLoad)>
# -a option 미사용시 arrival time은 모두 0이다
# -a option 사용시 alist의 각 값을 arrival time으로 설정한다
# alist size가 jlist size와 다를 때, 각 list에 음수가 들어왔을 때 exception을 발생시킨다

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
            arrtime = int((options.maxlen)/2*(options.jobs)*random.random())  
        joblist.append([jobnum, runtime, arrtime])                      
        print('  Job', jobnum, '( length = ' + str(runtime) + ', arrival time = ' + str(arrtime) + ' )')
else:                                                                   # <case 2> /Given workload/    
    RTlist = options.jlist.split(',')                                   # given run time list by jlist    
    ATlist = []                                                         # given arr time list by alist
    if options.alist == '':                                             # alist == NULL -> all arr time = 0
        for filler in range(0,len(RTlist)):
            ATlist.append(0)
    else:
        templist = options.alist.split(',')                             # alist != NULL -> given alist를 arr time으로 할당
        ATlist = list(map(int, templist))
        if len(RTlist)!=len(ATlist):                                    # alist와 jlist의 size가 다를 때 exception
            print('ERROR: number of alist args must be same of jlist')
            exit(1)
            
    jobnum = 0
    for runtime in RTlist:
        arrtime = ATlist[jobnum]
        if arrtime < 0:                                                      # alist에 음수 시간이 들어왔을 때 exception
            print('ERROR: provide unsigned integer value to alist args')
            exit(1)
        if int(runtime) < 0:                                                 # jlist에 음수 시간이 들어왔을 때 exception
            print('ERROR: provide unsiged integer value to jlist args')
            exit(1)
        joblist.append([jobnum, int(runtime), arrtime])               
        jobnum += 1

    for job in joblist:        
        print('  Job', job[0], '( length = ' + str(job[1]) + ', arrival time = ' + str(job[2]) + ' )')
print('\n')

if options.solve == True:
    print('** Solutions **\n')
    
    if options.policy == 'FIFO' or options.policy == 'SJF':
        joblist = sorted(joblist, key=operator.itemgetter(2))   # FIFO는 arrival time 순으로 정렬하고 차례로 실행하면 된다
        
        if options.policy == 'SJF':                             # SJF일 때 추가 정렬 과정이 필요하다
            jobs = len(joblist)                         
            sortDone = 0                
            loadDone = 0
            MEM = []                    # 실행 대기중인 (도착 시간이 현재 시간 이전인)job들의 공간.
            DISK = joblist              # DISK는 sorting (실행)전의 공간 
            joblist = []                # joblist는 sorting (실행)후의 공간
            thetime = DISK[0][2]                 # 현재시간
            
            while sortDone < jobs:          # 모든 job을 실행할 때까지 반복
                if MEM == [] and thetime <= DISK[loadDone][2]:       # 메모리가 실행할 일이 없고 현재 시간이 load되지 않은 첫 job의
                    thetime = DISK[loadDone][2]                      # arrival time보다 작으면 그때까지 기다린다
                for i in range(loadDone,jobs):      # 이미 load된 job을 제외하고, arrival time이 현재 시간보다 작은 job을 MEM에 load한다
                    if DISK[i][2] <= thetime:
                        MEM.append(DISK[i])
                        loadDone += 1
                    else:                           
                        break                 
                MEM.sort(key=operator.itemgetter(1))    # MEM에 load된 job을 runtime순으로 정렬한다    
                joblist.append(MEM[0])                  # 1개의 job만 그 job의 runtime만큼 계속 실행한다 (nonpreemptive)
                thetime += MEM[0][1]                    # 실행된 job은 joblist로 옮겨진다. (그 결과, joblist는 SJF 알고리즘에 맞게 정렬된다)
                MEM.pop(0)                              # 이제 이 정렬된 joblist를 그저 순서대로 실행하면 된다.
                sortDone += 1
        
        thetime = joblist[0][2]                                 # start time: first job arrival
        print('Execution trace:')
        for job in joblist:
            if thetime < job[2]:                                # 현재시간이 실행할 arrival time보다 작으면
                thetime = job[2]                                # arrival time까지 기다렸다 실행
            print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], thetime + job[1]))
            thetime += job[1]
        
        print('\nFinal statistics:')
        t     = joblist[0][2]           # start time: first job arrival
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for tmp in joblist:
            if t < tmp[2]:              # 현재 시간이 arrival time보다 작으면 arrival time까지 기다렸다 실행
                t = tmp[2]
            jobnum  = tmp[0]
            runtime = tmp[1]            
            response   = t - tmp[2]     # response time = firstruntime - arrival time
            turnaround = t + runtime - tmp[2]   # turnaroud time = end time - arrival time = (firstrun+runtime)-arrtime
            wait       = t - tmp[2]     # wait time = response time (cuz nonpreemtive)
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
            lastran[i] = joblist[i][2]  #lastran의 초기값은 그 job의 arrval time
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        joblist.sort(key=operator.itemgetter(2))   # sort by arrival time
        runlist = []            # memory
        endruncount = 0         # 위 알고리즘들과 달리 원래의 코드처럼 DISK list는 사용하지 않고 설계
        endloadcount = 0        # runlist에 load한 job의 index
        thetime  = 0.0

        while endruncount < jobcount:
            if runlist == [] and thetime < joblist[endloadcount][2]:    # memory가 비어있고 현재 시간<다음 job의 arrival time이면  
                thetime = joblist[endloadcount][2]                      # 그 시간까지 기다림
            
            for i in range(endloadcount,jobcount):                      # arrival 시간이 된 job을 runlist에 복사 
                if joblist[i][2] <= thetime:
                    runlist.append(joblist[i])
                    endloadcount += 1
                else:                                                   # 이미 joblist가 arrtime으로 정렬되어있으므로
                    break                                               # 아직 arrival하지 않은 job 이후 job들은 판단할 필요 없음 
            
            # print '%d jobs remaining' % jobcount
            job = runlist.pop(0)
            jobnum  = job[0]
            runtime = float(job[1])
            arvtime = job[2]                            # arrival time
            if response[jobnum] == -1:
                response[jobnum] = thetime - arvtime    # response time은 첫 run시간 - 도착시간
            currwait = thetime - lastran[jobnum]
            wait[jobnum] += currwait
            if runtime > quantum:
                runtime -= quantum
                ranfor = quantum
                print('  [ time %3d ] Run job %3d for %.2f secs' % (thetime, jobnum, ranfor))
                runlist.append([jobnum, runtime, arvtime])      # add updated runtime and arrival time
            else:
                ranfor = runtime
                print('  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (thetime, jobnum, ranfor, thetime + ranfor))
                turnaround[jobnum] = thetime + ranfor - arvtime # turnaround time = 끝난시간 - 도착시간
                endruncount += 1            # 1개의 job 실행 종료
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

        jobs = len(joblist)             # 처음 job 개수

        for i in range(0,jobs):         # job: [jobnum, runtime, arrival time, time left, response time, turnaround time, wait time]
            j = joblist.pop(0)          # 각 job에 남은 시간, 각 performance 원소를 추가
            j.extend([j[1],-1,0,0])            
            joblist.append(j)

        Decision_Times = []             # job arrival time마다 어떤 job을 실행할 지 결정해야한다          
        for j in joblist:
            Decision_Times.append(j[2])
        Decision_Times.sort()

        thetime = 0                     # 현재 시간.
        Memory = []                     # job이 도착해 wait하고 실행되는 공간
        Disk = []                       # 끝난 job이 옮겨지는 공간
        CPUrun = False                  # shecedule된 job이 있어 CPU가 실행상태인지 나타내는 flag
        Excution_Time = 0               # CPU가 한 job을 실행시킨 시간
        count = 0                       # 완료된 job의 개수

        while count < jobs:                 # job이 모두 끝날 때까지 반복
            if thetime in Decision_Times:       # [현재 시간이 decision time일 때]
                if CPUrun:                          # 실행중이던 job이 있으면 종료한다
                    CPUrun = False
                    print('  [ time %3d ] Run job %d for %.2f secs' % (thetime-Excution_Time, Memory[0][0], Excution_Time))
                    Excution_Time = 0
                                 
                for job in joblist:             # Desition time에 새로 arrival한 job들을 MEM으로 load한다
                    if job[2] == thetime:
                        Memory.append(job)

                Memory = sorted(Memory, key=operator.itemgetter(3))    # 스케쥴할 job을 정하기 위해 timeleft순으로 정렬한다 
                CPUrun = True

            else:                               # [현재 시간이 decition time이 아닐 때]
                if not CPUrun:                      # CPU가 쉬는 중일 때
                    if Memory == []:                # memory가 비어있으면 찰때까지 쉰다.
                        thetime += 1
                    else:                           # memory에 할 job이 있으면 다음 job을 스케쥴링한다. (재정렬할 필요는 없다)
                        CPUrun = True

            if CPUrun:                          # [CPU 동작] 스케쥴링이 완료되면 CPU를 1초간 실행시킨다
                if Memory[0][4] == -1:              # 처음 실행된 job은 response time을 기록한다
                    Memory[0][4] = thetime - Memory[0][2]

                thetime += 1
                Excution_Time += 1
                Memory[0][3] -= 1                   # timeleft 1 감소
                if len(Memory) > 1:                 # 실행중이 아닌 MEM의 job wait time을 1 증가
                    for i in range(1,len(Memory)):      
                        Memory[i][6] += 1
                
                if Memory[0][3] == 0:               # timeleft가 0일때, 즉 job이 끝나면 Disk로 옮긴다
                    CPUrun = False
                    print('  [ time %3d ] Run job %d for %.2f secs ( DONE at %.2f )' \
                        % (thetime-Excution_Time, Memory[0][0], Excution_Time, thetime))                    
                    Memory[0][5] = thetime - Memory[0][2]       # turnaround time 기록
                    Disk.append(Memory[0])
                    count += 1
                    Memory.pop(0)
                    Excution_Time = 0

        # Performance
        print('\nFinal statistics:')
        works = len(Disk)
        responseSum = turnaroundSum = waitSum = 0.0
        for job in Disk:
            print('  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (job[0], job[4], job[5], job[6]))
            responseSum += job[4]
            turnaroundSum += job[5]
            waitSum += job[6]
        print('\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/works, turnaroundSum/works, waitSum/works))
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


