import sys, time, random

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        secondsToSleep = float(sys.argv[1])
    else:
        milissecondsToSleep = random.randint(0, 10000)
        secondsToSleep = float(milissecondsToSleep / 1000.0)

    print(f'[APP] Sleeping for {secondsToSleep} seconds')  

    time.sleep(secondsToSleep)

    print('[APP] Finishing sleep')
