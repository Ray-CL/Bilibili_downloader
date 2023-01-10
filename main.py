import requests
import re
import json
import time
from moviepy.editor import *
import PySimpleGUI as sg


# url = 'https://www.bilibili.com/video/BV1BU4y1H7E3'
def get_file_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "referer": "https://www.bilibili.com"
    }

    resp = requests.get(url, headers=headers)
    palyinfo = re.findall(r'<script>window.__playinfo__=(.*?)</script>', resp.text)[0]
    palyinfo_data = json.loads(palyinfo)

    title = re.findall(r'<h1 title="(.*?)" class="video-title tit">', resp.text)[0]

    video_url = palyinfo_data['data']['dash']['video'][2]['base_url']
    audio_url = palyinfo_data['data']['dash']['audio'][2]['base_url']

    return title, video_url, audio_url


def down_file(title, file_url, file_type):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "referer": "https://www.bilibili.com"
    }
    resp = requests.get(url=file_url, headers=headers)
    print(resp.status_code)

    print(f'文件名称：{title}')
    # 设置单次写入数据的块大小
    chunk_size = 1024
    # 获取文件大小
    file_size = int(resp.headers['content-length'])
    # 用于记录已经下载的文件大小
    done_size = 0
    # 将文件大小转化为MB
    file_size_MB = file_size / 1024 / 1024
    print(f'文件大小：{file_size_MB:0.2f} MB')
    start_time = time.time()
    with open(title + '.' + file_type, mode='wb') as f:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            done_size += len(chunk)
            print(f'\r下载进度：{done_size / file_size * 100:0.2f}%', end='')
    end_time = time.time()
    cost_time = end_time - start_time
    print(f'累计耗时：{cost_time:0.2f} 秒')
    print(f'下载速度：{file_size_MB / cost_time:0.2f}M/s')


def merge(title):
    video_path = title + '.mp4'
    audio_path = title + '.mp3'
    # 提取音轨
    audio = AudioFileClip(audio_path)
    # 读入视频
    video = VideoFileClip(video_path)
    # 将音轨合并到视频中
    video = video.set_audio(audio)
    # 输出
    video.write_videofile(f"{title}(含音频).mp4")


# 主题设置
sg.theme('SystemDefaultForReal')

# 布局设置
layout = [[sg.Text('选择B站视频地址:', font=("微软雅黑", 12)), sg.InputText(key='url', size=(50, 1), font=("微软雅黑", 10), enable_events=True)],
          # [sg.Output(size=(66, 8),font=("微软雅黑", 10))],
          [sg.Button('开始下载', font=("微软雅黑", 10), button_color='Orange'),
           sg.Button('关闭程序', font=("微软雅黑", 10), button_color='red'), ]
          ]

# 创建窗口
window = sg.Window('Ray', layout, font=("微软雅黑", 12), default_element_size=(50, 1))

# 事件循环
while True:
    event, values = window.read()
    if event in (None, '关闭程序'):
        break
    if event == '开始下载':
        url = values['url']
        print('获取视频信息')
        title, video_url, audio_url = get_file_info(url)
        print('下载视频资源')
        down_file(title, video_url, 'mp4')
        print('下载音频资源')
        down_file(title, audio_url, 'mp3')
        print('合并视频与音频')
        merge(title)
        print('处理完成!!!')
window.close()
