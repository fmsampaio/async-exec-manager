import subprocess
import os
import time
import random
import select

class AsyncManager():
    def __init__(self, maxProcessParallel):
        self.maxProcessParallel = maxProcessParallel
        self.executionQueue = list()
        self.processes = list()

    def addExecution(self, key, command, outputFileName=None):
        newExecution = {
            'key' : key,
            'command' : command,
            'outputFileName' : outputFileName
        }
        self.executionQueue.append(newExecution)
        

    def start(self):
        processTotal = len(self.executionQueue)
        processCounter = 0        

        for execution in self.executionQueue:
            command = execution['command']
            #outputFile = execution['outputFile'] if not(execution['outputFile'] is None) else subprocess.STDOUT
            
            if execution['outputFileName'] != None:
                execution['outputFile'] = open(execution['outputFileName'], 'w')
                popen = subprocess.Popen(
                    command.split(),
                    stdout = execution['outputFile'],
                    stderr = subprocess.DEVNULL
                )
            else:
                popen = subprocess.Popen(
                    command.split(),
                    stdout = subprocess.PIPE,
                    stderr = subprocess.DEVNULL
                )            

            self.processes.append({
                'execution' : execution,
                'popen' : popen
            })

            processCounter += 1
            print(f'[INFO] New execution started: {execution["key"]} -> {execution["command"]}')
            print(f'[INFO] Execution summary [{processCounter}/{processTotal}]')

            print(len(self.processes))

            while len(self.processes) >= self.maxProcessParallel:
                for process in self.processes:
                    popen = process['popen']
                    
                    return_code = popen.poll()

                    if return_code == 0:
                        finished_process = process
                        break
                    else:
                        finished_process = None

                if finished_process is not None:
                    outputFileName = finished_process['execution']['outputFileName']
                    if not(outputFileName is None):
                        finished_process['execution']['outputFile'].close()

                    self.processes.remove(finished_process)

                    executionKey = finished_process['execution']['key']
                    print(f'[INFO] Execution ended: {executionKey}')                    

                else:                    
                    # Live presentation of stdout           
                    
                    for process in self.processes:
                        outputFileName = process['execution']['outputFileName']
                        if outputFileName is None:
                            popen = process['popen']
                            key = process['execution']['key']
                            y = select.poll()
                            y.register(popen.stdout, select.POLLIN)
                            if y.poll(1):
                                print(f'[OUTPUT] {key} --> {str(popen.stdout.readline())}')
                    
                    # Waits 1 minute before verifying the processes again
                    #time.sleep(1)

        # Wait for remaining processes
        for process in self.processes:
            popen = process['popen']
            outputFileName = process['execution']['outputFile']
            executionKey = process['execution']['key']
            
            popen.wait()

            if not(outputFileName is None):
                process['execution']['outputFile'].close()

            print(f'[INFO] Execution ended: {executionKey}')     


#Test application

def testApp():
    manager = AsyncManager(maxProcessParallel=20)

    baseCommand = 'python3 samples/sleeper_test.py'
    for i in range(50):
        command = f'{baseCommand} {random.random() * 10}'
        key = f'SLEEP_{i}'

        manager.addExecution(
            key = key,
            command = command,
            outputFileName = f'samples/output/sleep_{key}.txt'
        )
    
    manager.start()

if __name__ == '__main__':
    testApp()

