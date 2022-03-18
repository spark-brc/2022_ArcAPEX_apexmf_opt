import os
from datetime import datetime
from time import time
import pandas as pd
from apexmf import apexmf_pst_par, apexmf_utils
from apexmf import apexmf_pst_utils
import pyemu

wd = os.getcwd()
os.chdir(wd)
print(wd)

def time_stamp(des):
    time = datetime.now().strftime('[%m/%d/%y %H:%M:%S]')
    print('\n' + 35*'+ ')
    print(time + ' |  {} ...'.format(des))
    print(35*'+ ' + '\n')

def modify_riv_pars():
    mf_wd = wd + "\MODFLOW"
    des = "updating river parameters"
    time_stamp(des)
    apexmf_pst_par.riv_par(mf_wd)

def modify_hk_sy_pars_pp(pp_included):
    mf_wd = wd + "\MODFLOW"
    os.chdir(mf_wd)
    des = "modifying MODFLOW HK, VHK, and SY parameters"
    time_stamp(des)
    data_fac = pp_included
    for i in data_fac:
        outfile = i + '.ref'
        pyemu.utils.geostats.fac2real(i, factors_file=i+'.fac', out_file=outfile)
    os.chdir(wd)

def execute_apexmf():
    des = "running model"
    time_stamp(des)
    # pyemu.os_utils.run('APEX-MODFLOW3.exe >_s+m.stdout', cwd='.')
    pyemu.os_utils.run('apexmf', cwd='.')

def extract_stf_results(cha_file, subs, sim_start, cal_start, cal_end):
    if time_step == 'day':
        des = "simulation successfully completed | extracting daily simulated streamflow"
        time_stamp(des)
        apexmf_pst_utils.extract_day_stf(cha_file, subs, sim_start, cal_start, cal_end)
    elif time_step == 'month':
        des = "simulation successfully completed | extracting monthly simulated streamflow"
        time_stamp(des)
        apexmf_pst_utils.extract_month_stf(cha_file, subs, sim_start, cal_start, cal_end)

def extract_gw_level_results(grids, sim_start, cal_end):
    des = "simulation successfully completed | extracting depth to water values"
    time_stamp(des)
    apexmf_pst_utils.extract_depth_to_water(grids, sim_start, cal_end)

def extract_lai_results(lai_file, lai_subs, sim_start, cal_start, cal_end):
    if time_step == 'day':
        des = "simulation successfully completed | extracting daily simulated lai"
        time_stamp(des)
        sao_df = apexmf_utils.read_sao(lai_file)
        apexmf_pst_utils.extract_day_lai(sao_df, lai_subs, sim_start, cal_start, cal_end)
    elif time_step == 'month':
        des = "simulation successfully completed | extracting monthl simulated lai"
        time_stamp(des)
        sao_df = apexmf_utils.read_sao(lai_file)
        apexmf_pst_utils.extract_day_mon(sao_df, lai_subs, sim_start, cal_start, cal_end)

def extract_baseflow_results(cha_file, subs, sim_start, cal_start, cal_end):
    des = "simulation successfully completed | calculating baseflow ratio"
    time_stamp(des)
    apexmf_pst_utils.extract_month_baseflow(cha_file, subs, sim_start, cal_start, cal_end)

def extract_slopes(cha_file, subs, sim_start, cal_start, cal_end, 
            min_fdc, max_fdc, interval_num, time_step=None):
    des = "simulation successfully completed | extracting fdc slopes from streamflow"
    time_stamp(des)
    apexmf_pst_utils.extract_slopesFrTimeSim(cha_file, subs, sim_start, cal_start, cal_end, 
            min_fdc, max_fdc, interval_num, time_step=None)


    # extract_watertable_sim([5699, 5832], '1/1/1980', '12/31/2005')

if __name__ == '__main__':
    cwd = os.getcwd()
    os.chdir(cwd)
    apexmf_con = pd.read_csv('apexmf.con', sep='\t', names=['names', 'vals'], index_col=0, comment="#")
    # get default vals
    wd = apexmf_con.loc['wd', 'vals']
    sim_start = apexmf_con.loc['sim_start', 'vals']
    cal_start = apexmf_con.loc['cal_start', 'vals']
    cal_end = apexmf_con.loc['cal_end', 'vals']
    cha_file = apexmf_con.loc['cha_file','vals']
    time_step = apexmf_con.loc['time_step','vals']
    lai_file = apexmf_con.loc['lai_file','vals']
    min_fdc = float(apexmf_con.loc['min_fdc','vals'])
    max_fdc = float(apexmf_con.loc['max_fdc','vals'])
    interval_num = int(apexmf_con.loc['interval_num','vals'])

    # modifying river pars
    if apexmf_con.loc['riv_parm', 'vals'] != 'n':
        modify_riv_pars()
    if apexmf_con.loc['pp_included', 'vals'] != 'n':
        pp_included = apexmf_con.loc['pp_included','vals'].strip('][').split(', ')
        pp_included = [i.replace("'", "").strip() for i in pp_included]  
        modify_hk_sy_pars_pp(pp_included)
    # execute model
    execute_apexmf()
    # extract sims
    # if apexmf_con.loc['cha_file', 'vals'] != 'n' and apexmf_con.loc['fdc', 'vals'] != 'n':
    if apexmf_con.loc['cha_file', 'vals'] != 'n':
        subs = apexmf_con.loc['subs','vals'].strip('][').split(', ')
        subs = [int(i) for i in subs]
        extract_stf_results(cha_file, subs, sim_start, cal_start, cal_end)
    if apexmf_con.loc['gw_level', 'vals'] == 'y':
        grids = apexmf_con.loc['grids','vals'].strip('][').split(', ')
        grids = [int(i) for i in grids]        
        extract_gw_level_results(grids, sim_start, cal_end)
    if apexmf_con.loc['lai_file', 'vals'] != 'n':
        lai_subs = apexmf_con.loc['lai_subs','vals'].strip('][').split(', ')
        lai_subs = [int(i) for i in lai_subs]
        extract_lai_results(lai_file, lai_subs, sim_start, cal_start, cal_end)
    if apexmf_con.loc['baseflow', 'vals'] != 'n':
        extract_baseflow_results(cha_file, subs, sim_start, cal_start, cal_end)
    if apexmf_con.loc['fdc', 'vals'] == 'y':
        extract_slopes(cha_file, subs, sim_start, cal_start, cal_end, 
            min_fdc, max_fdc, interval_num, time_step=None)
