import os
import argparse
import subprocess
import json


def get_video_width_height(input_file):
    try:
        # 使用 ffprobe 获取视频流信息，格式为 JSON
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-select_streams', 'v:0', input_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        # 解析 JSON 输出
        info = json.loads(result.stdout)
        width = info['streams'][0]['width']
        height = info['streams'][0]['height']
        print(f'ORIGINAL SIZE: {width}×{height}')

        width, height = height, width
        print(f'NEW SIZE: {width}×{height}')
        return width, height
    except subprocess.CalledProcessError as e:
        print('ffprobe launching failed', e.stderr)
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print('Decoding video info failed', str(e))
        return None


def process_video(input_file, width, height):
    # 解析传入的导入文件完整路径，解包出文件路径和完整文件名
    path, filename = os.path.split(input_file)
    output_file = os.path.join(path, f'【mod】{filename}')

    # 处理导入的视频
    subprocess.run(
        ['ffmpeg', '-hide_banner', '-i', input_file, '-vf', f'scale={width}:{height}', '-metadata:s:v:0', 'rotate=0',
         '-c:v', 'h264_qsv', '-crf', '0', '-c:a', 'copy', output_file])


def process_single_file(input_file):
    # 处理单个文件
    if os.path.isfile(input_file):
        print(f"Processing {input_file}")
        width, height = get_video_width_height(input_file)
        process_video(input_file, width, height)
    else:
        print(f"Error when processing {input_file}: is not a file")


def process_directory(input_dir):
    # 处理目录中所有文件
    if os.path.isdir(input_dir):
        print(f"Processing {input_dir}")
        for filename in os.listdir(input_dir):
            filepath = os.path.join(input_dir, filename)

            print(f"\nProcessing {filepath}")
            width, height = get_video_width_height(filepath)

            process_video(filepath, width, height)
    else:
        print(f"Error when processing {input_dir}: is not a directory")


def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='Process some video files')

    # 添加参数
    parser.add_argument('path', help='Path to the video file or directory')
    parser.add_argument('-d', '--directory', action='store_true', help='Process the directory if defined it')

    # 解析命令行参数
    args = parser.parse_args()

    # 根据参数决定处理方式
    if args.directory:
        process_directory(input_dir=args.path)
    else:
        process_single_file(input_file=args.path)


# 程序入口
if __name__ == "__main__":
    main()
