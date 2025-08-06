
import pandas as pd
def read_log(pth=None):
    if pth is None:
        pth = r'/home/zzj/projects/CCE/logs/AccQ-R_log.csv'
    try:
        df = pd.read_csv(pth)
        # 去除重复行
        df2 = df.drop_duplicates()
        # 重置索引
        df2.reset_index(drop=True, inplace=True)
        # saving
        print("Original number of rows:", len(df))
        print(len(df2), "rows after removing duplicates.")

        df2.to_csv(pth, index=False)
    except FileNotFoundError:
        print(f"File not found: {pth}")
        return pd.DataFrame()  # Return an empty DataFrame if the file does not exist

# read_log()
def test_time():
    import time
    start_time = time.time()
    # 模拟一些处理
    time.sleep(2)  # 假设处理耗时2秒
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    st_time = time.perf_counter()
    time.sleep(2)  # 假设处理耗时2秒
    en_time = time.perf_counter()
    elapsed_time2 = (en_time - st_time)*1000
    print(f"Elapsed time (perf_counter): {elapsed_time2:.2f} ms")

# test_time()
def split_files():
    pth = r'/home/zzj/projects/CCE/logs/LowDisAccQ_log.csv'
    pth = r'/home/zzj/projects/CCE/logs/AccQ-R_log.csv'
    d1 = pd.read_csv(pth)
    # 找到metric_name==CCE的
    d_cce = d1[d1['metric_name'] == 'CCE']
    d_f1 = d1[d1['metric_name'] == 'F1']
    print(len(d1),len(d_cce), len(d_f1))

def cal_acc_q_r_num():
    num_model_type_list = 60 + 120
    num_exp_cnt = 3
    num_case = 30 + 7
    accq = 10 * num_exp_cnt * num_case
    print("AccQ:", accq)


# cal_acc_q_r_num()
# split_files()
# read_log('CCE/logs/LowDisAccQ-R_log.csv')
# read_log('CCE/logs/PreQ-NegP_log.csv')
read_log('/home/zzj/projects/CCE/logs/PreQ-NegP-R_log.csv')