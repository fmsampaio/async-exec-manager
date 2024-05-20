import subprocess
import os
import itertools
import time
import sys

from exp_logger_python import ExpLogger

LOGGER_PROJ_ID = 2

MAX_PROCS_PARALLEL = 20

VTM_APP = '/home/research-data/felipe/ndp-repos/VVCSoftware_VTM/bin/EncoderAppStatic'
CFGS_PATH = '/home/research-data/felipe/ndp-repos/cfgs_vtm/'
OUTPUTS_PATH = '/home/research-data/felipe/ndp-repos/outputs/'
YUVS_PATH = '/home/research-data/video-sequences/'

qps = ['37', '22', '27', '32']

FRAMES_TO_BE_CODED = '97'

videos = [
    #C Class
    {'name' : 'RaceHorsesC','cfg' : 'RaceHorsesC.cfg','yuv' : 'RaceHorsesC_832x480_30.yuv','res' : '832x480'},
    {'name' : 'BasketballDrill','cfg' : 'BasketballDrill.cfg','yuv' : 'BasketballDrill_832x480_50.yuv','res' : '832x480'},
    {'name' : 'BQMall','cfg' : 'BQMall.cfg','yuv' : 'BQMall_832x480_60.yuv','res' : '832x480'},
    {'name' : 'PartyScene','cfg' : 'PartyScene.cfg','yuv' : 'PartyScene_832x480_50.yuv','res' : '832x480'},

    #B Class
    {'name' : 'BasketballDrive','cfg' : 'BasketballDrive.cfg','yuv' : 'BasketballDrive_1920x1080_50.yuv','res' : '1920x1080'},
    {'name' : 'MarketPlace','cfg' : 'MarketPlace.cfg','yuv' : 'MarketPlace_1920x1080_60fps_10bit_420.yuv','res' : '1920x1080'},
    {'name' : 'RitualDance','cfg' : 'RitualDance.cfg','yuv' : 'RitualDance_1920x1080_60fps_10bit_420.yuv','res' : '1920x1080'},
    {'name' : 'Cactus','cfg' : 'Cactus.cfg','yuv' : 'Cactus_1920x1080_50.yuv','res' : '1920x1080'},
    {'name' : 'BQTerrace','cfg' : 'BQTerrace.cfg','yuv' : 'BQTerrace_1920x1080_60.yuv','res' : '1920x1080'},
    
    #A2 Class
    {'name' : 'CatRobot','cfg' : 'CatRobot.cfg','yuv' : 'CatRobot_3840x2160_60fps_10bit_420_jvet.yuv','res' : '3840x2160'},
    {'name' : 'DaylightRoad2','cfg' : 'DaylightRoad2.cfg','yuv' : 'DaylightRoad2_3840x2160_60fps_10bit_420.yuv','res' : '3840x2160'},
    {'name' : 'ParkRunning3','cfg' : 'ParkRunning3.cfg','yuv' : 'ParkRunning3_3840x2160_50fps_10bit_420.yuv','res' : '3840x2160'},

    #A1 Class
    {'name' : 'Campfire','cfg' : 'Campfire.cfg','yuv' : 'Campfire_3840x2160_30fps_bt709_420_videoRange.yuv','res' : '3840x2160'},
    {'name' : 'Tango2','cfg' : 'Tango2.cfg','yuv' : 'Tango2_3840x2160_60fps_10bit_420.yuv','res' : '3840x2160'},
    {'name' : 'FoodMarket4','cfg' : 'FoodMarket4.cfg','yuv' : 'FoodMarket4_3840x2160_60fps_10bit_420.yuv','res' : '3840x2160'},


    #Others
    #{'name' : 'BQSquare','cfg' : 'BQSquare.cfg','yuv' : 'BQSquare_416x240_60.yuv','res' : '416x240'},
]

encCfgs = [
    #{'name' : 'LD', 'cfg' : 'encoder_lowdelay_vtm.cfg'},
    #{'name' : 'RA', 'cfg' : 'encoder_randomaccess_vtm.cfg'},
    {'name' : 'LD_NDP', 'cfg' : 'encoder_lowdelay_vtm_ndp.cfg'},
    {'name' : 'RA_NDP', 'cfg' : 'encoder_randomaccess_vtm_ndp.cfg'},
]


def wasAlreadyExecuted(experimentID): #search for VTM report at {OUTPUTS_PATH}vtm-reports
    reportPath = f'{OUTPUTS_PATH}vtm-reports/{experimentID}.report'
    return os.path.exists(reportPath)

processes = list()

experimentsToBeExecuted = []

if __name__ == '__main__':

    isDebug = False
    if len(sys.argv) >= 2:
        isDebug = True if sys.argv[1] == '-dbg' else False

    for video, encCfg, qp in itertools.product(videos, encCfgs, qps):
        experimentID = f'{video["name"]}_{encCfg["name"]}_{qp}'

        experiment = {
            'id' : experimentID,
            'video' : video,
            'encCfg' : encCfg,
            'qp' : qp
        }
        
        if not wasAlreadyExecuted(experimentID):
            experimentsToBeExecuted.append(experiment)
        else:
            print(f'[INFO] Experiment {experimentID} already executed...')
            ExpLogger.log(
                projectId=LOGGER_PROJ_ID,
                experimentName=experimentID,
                logMessage=f'[INFO] Experiment already executed...'
            )
    
    simtotal = len(experimentsToBeExecuted)
    simrun = 0

    for experiment in experimentsToBeExecuted:
        experimentID = experiment['id']
        video = experiment['video']
        qp = experiment['qp']
        encCfg = experiment['encCfg']
        
        vtmEncCmd = f'{VTM_APP} -c {CFGS_PATH}{encCfg["cfg"]} -c {CFGS_PATH}{video["cfg"]} -i {YUVS_PATH}{video["yuv"]} -b {OUTPUTS_PATH}bitstreams/{experimentID}.bin -q {qp} -f {FRAMES_TO_BE_CODED}'
        vtmReport =  f'{OUTPUTS_PATH}vtm-reports/{experimentID}.report'
        

        if isDebug:
            print(f'[DBG] {vtmEncCmd}')
            continue
   
        vtmReportFile = open(vtmReport, 'w')

        popen = subprocess.Popen(
            vtmEncCmd.split(),
            stdout=vtmReportFile,
            stderr=subprocess.DEVNULL
        )
        processes.append((popen, vtmReportFile))

        print(f'Experiment key: {experimentID}')
        ExpLogger.log(
            projectId=LOGGER_PROJ_ID,
            experimentName=experimentID,
            logMessage='Experiment STARTED execution.'
        )

        simrun += 1
        print(f'Execution [{simrun}/{simtotal}]')
        ExpLogger.log(
            projectId=LOGGER_PROJ_ID,
            experimentName='Overall',
            logMessage=f'Execution [{simrun}/{simtotal}]'
        )

        while len(processes) >= MAX_PROCS_PARALLEL:
            for process in processes:
                popen, _ = process

                
                return_code = popen.poll()

                if return_code == 0:
                    finished_process = process
                    break
                else:
                    finished_process = None

            if finished_process is not None:
                _, simoutfile = process
                simoutfile.close()

                processes.remove(finished_process)
                
                ExpLogger.log(
                    projectId=LOGGER_PROJ_ID,
                    experimentName=experimentID,
                    logMessage='Experiment ENDED execution.'
                )

            else:
                # Waits 5 minutes before verifying the processes again
                time.sleep(300)

    # Wait for remaining processes
    for process in processes:
        popen, simoutfile = process
        popen.wait()
        simoutfile.close()