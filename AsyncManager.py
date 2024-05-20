import subprocess
import os
import time
import sys
import random

class AsyncManager():
    def __init__(self, maxProcessParallel):
        self.maxProcessParallel = maxProcessParallel
        self.executionQueue = list()
        self.processes = list()

    def add_execution(self, key, command, outputFile=None):
        newExecution = {
            'key' : key,
            'command' : command,
            'outputFile' : outputFile
        }
        self.executionQueue.append(newExecution)
        

    def start(self):
        processTotal = len(self.executionQueue)
        processCounter = 0

        for execution in self.executionQueue:
            command = execution['command']
            #outputFile = execution['outputFile'] if not(execution['outputFile'] is None) else subprocess.STDOUT
            
            if execution['outputFile'] != None:
                popen = subprocess.Popen(
                    command.split(),
                    stdout = outputFile,
                    stderr = subprocess.DEVNULL
                )
            else:
                popen = subprocess.Popen(
                    command.split(),
                    stdout = subprocess.PIPE,
                    stderr = subprocess.DEVNULL
                )

            self.processes.append({
                'command' : command,
                'popen' : popen, 
                'outputFile' : execution['outputFile'],
                'key' : execution['key']
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
                    outputFile = finished_process['outputFile']
                    
                    if not(outputFile is None):
                        outputFile.close()

                    self.processes.remove(finished_process)

                    executionKey = finished_process['key']
                    print(f'[INFO] Execution ended: {executionKey}')                    

                else:                    
                    # Live presentation of stdout
                    """
                    for p in self.processes:
                        if p['outputFile'] is None:
                            process = p['popen']
                            while True:
                                output = process.stdout.readline()
                                if output == '' and process.poll() is not None:
                                    break
                                if output:
                                    print(output.strip())
                    """
                    # Waits 1 minute before verifying the processes again
                    time.sleep(1)

        # Wait for remaining processes
        for process in self.processes:
            popen = process['popen']
            outputFile = process['outputFile']
            executionKey = process['key']
            
            popen.wait()

            if not(outputFile is None):
                outputFile.close()

            print(f'[INFO] Execution ended: {executionKey}')     


if __name__ == '__main__':
    manager = AsyncManager(maxProcessParallel=4)

    baseCommand = 'python3 samples/sleeper_test.py'
    for i in range(50):
        command = f'{baseCommand} {random.random() * 10}'
        key = f'SLEEP_{i}'

        manager.add_execution(
            key = key,
            command = command
        )
    
    manager.start()

