from pywinauto.application import Application
import pywinauto
import time
import psutil
import pandas as pd
import numpy as np

def get_wechat_pid():
    try:
        print('>>> 正在获取 WeChat 进程 PID...')
        for pid in psutil.pids():
            p = psutil.Process(pid)
            if p.name() == 'WeChat.exe':
                print(f'>>> 找到 WeChat 进程，PID: {pid}')
                return pid
    except psutil.Error as e:
        print(f'Error while getting WeChat PID: {e}')
    print('>>> 未找到 WeChat 进程')
    return None

def get_name_list(pid):
    try:
        print(f'>>> WeChat.exe PID: {pid}')
        print('>>> 请打开【微信 => 目标群聊 => 聊天成员 => 查看更多】，尤其是【查看更多】，否则查找不全！')
        for i in range(10):
            print('\r({:2d} 秒)'.format(10 - i), end='')
            time.sleep(1)
        
        print('>>> 正在连接 WeChat 窗口...')
        app = Application(backend='uia').connect(process=pid)
        win_main_Dialog = app.window(class_name='WeChatMainWndForPC')
        
        print('>>> 获取聊天成员列表...')
        chat_list = win_main_Dialog.child_window(control_type='List', title='聊天成员')
        
        all_members = []
        for i in chat_list.items():
            p = i.descendants()
            if p and len(p) > 5:
                name = p[5].texts()[0].strip()
                wechat_name = p[3].texts()[0].strip()
                if name and name not in ['添加', '移出']:
                    all_members.append([name, wechat_name])
        
        df = pd.DataFrame(np.array(all_members), columns=['群昵称', '微信昵称'])
        df.to_csv('all_members.csv', index=False, encoding='utf-8-sig')
        
        print(f'\r>>> 群成员共 {len(all_members)} 人，结果已保存至 all_members.csv')
        return all_members
    
    except pywinauto.findwindows.ElementNotFoundError:
        print('\r>>> 未找到【聊天成员】窗口，程序终止！')
        print('>>> 若已开启【聊天成员】窗口但仍报错，请重启微信（原因：可能存在多个 WeChat 进程）')
        return []
    except Exception as e:
        print(f'Unexpected error: {e}')
        return []

def main():
    try:
        pid = get_wechat_pid()
        if pid is None:
            print('>>> 找不到 WeChat.exe，请先打开 WeChat.exe 再运行此脚本！')
            return
        
        get_name_list(pid)
    except Exception as e:
        print(f'Unexpected error: {e}')
    finally:
        input('>>> 按任意键退出...')

if __name__ == '__main__':
    main()
