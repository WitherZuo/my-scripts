import argparse
import requests
from datetime import datetime
import os
import ctypes
import subprocess
import time

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 受支持的分辨率
supported_resolutions = [
    "UHD",  # 3840x2160
    "1920x1080",
    "1366x768",
    "1280x768",
    "1024x768",
    "800x600",
    "800x480",
    "640x480",
]


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="下载并设置必应每日壁纸")
    parser.add_argument(
        "-p",
        "--photosize",
        metavar="PHOTO_SIZE",
        help="指定壁纸分辨率：UHD | 1920x1080 | 1366x768 | 1280x768 | 1024x768 | 800x600 | 800x480 | 640x480",
        type=str,
        default=None,
        choices=supported_resolutions,  # 从受支持的分辨率列表中获取选项，区分大小写
    )
    return parser.parse_args()


def get_screen_size():
    """
    获取当前屏幕分辨率并匹配合适的图片分辨率
    返回：包含屏幕分辨率和匹配的图片分辨率的字典
    """
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    if screen_width >= 3840 or screen_height >= 2160:
        matched_resolution = "UHD"
    elif screen_width >= 1920 or screen_height >= 1080:
        matched_resolution = "1920x1080"
    elif screen_width >= 1366 or screen_height >= 768:
        matched_resolution = "1366x768"
    elif screen_width >= 1280 or screen_height >= 768:
        matched_resolution = "1280x768"
    elif screen_width >= 1024 or screen_height >= 768:
        matched_resolution = "1024x768"
    elif screen_width >= 800 or screen_height >= 600:
        matched_resolution = "800x600"
    elif screen_width >= 800 or screen_height >= 480:
        matched_resolution = "800x480"
    elif screen_width >= 640 or screen_height >= 480:
        matched_resolution = "640x480"
    else:
        matched_resolution = "UHD"

    return {
        "screen_resolution": f"{screen_width}x{screen_height}",
        "matched_resolution": matched_resolution,
    }


def get_bing_wallpaper(photo_size):
    """
    获取必应每日壁纸信息并下载图片
    参数：
        photo_size: 图片分辨率，必须是支持的分辨率之一
    返回：标题、版权信息和下载链接
    异常：
        ValueError: 当分辨率不支持时抛出
        Exception: 当下载失败3次后抛出
    """
    if photo_size not in supported_resolutions:
        raise ValueError(f"不支持的分辨率: {photo_size}")

    # 必应壁纸 API
    bing_api = "https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"

    try:
        # 获取壁纸信息
        response = requests.get(bing_api)
        data = response.json()

        # 提取图片信息
        image_data = data["images"][0]
        title = image_data["title"]
        copyright_info = image_data["copyright"]

        # 根据分辨率构建图片URL
        image_url = f"https://cn.bing.com{image_data['urlbase']}_{photo_size}.jpg"

        # 下载图片 - 添加重试逻辑
        max_retries = 3
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                print("下载壁纸……")
                image_response = requests.get(image_url, timeout=20)  # 添加超时设置

                if image_response.status_code == 200:
                    # 创建保存图片的文件夹
                    save_dir = os.path.join(os.path.expanduser("~"), "BingWallpapers")
                    os.makedirs(save_dir, exist_ok=True)

                    # 生成文件名（使用当前日期和分辨率）
                    today = datetime.now().strftime("%Y%m%d")
                    image_filename = f"bing_wallpaper_{today}_{photo_size}.jpg"
                    image_path = os.path.join(save_dir, image_filename)

                    # 保存图片
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)

                    print("下载成功！")
                    return {
                        "title": title,
                        "copyright": copyright_info,
                        "url": image_url,
                        "local_path": image_path,
                        "resolution": photo_size,
                    }
                else:
                    print(f"下载失败: HTTP状态码 {image_response.status_code}")
                    last_error = f"HTTP错误: {image_response.status_code}"

            except Exception as e:
                print(f"下载过程中出错: {str(e)}")
                last_error = str(e)

            retry_count += 1
            if retry_count < max_retries:
                wait_time = 2 * retry_count  # 随着重试次数增加等待时间
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

        # 如果所有重试都失败，抛出异常
        raise Exception(f"下载壁纸失败，已尝试 {max_retries} 次: {last_error}")

    except Exception as e:
        print(f"获取壁纸时发生错误: {str(e)}")
        raise  # 将异常往上传递，而不是返回None


def set_wallpaper(image_path):
    """
    使用VirtualDesktop设置所有虚拟桌面的壁纸
    参数：
        image_path: 本地图片路径
    异常：
        FileNotFoundError: 当VirtualDesktop11-24H2.exe不存在时抛出
    """
    # 获取 VirtualDesktop11.exe 所在目录
    virtual_desktop_exe = os.path.join(script_dir, "VirtualDesktop11.exe")

    # 检查 VirtualDesktop11.exe 是否存在
    if not os.path.exists(virtual_desktop_exe):
        print(f"错误: 未找到 {virtual_desktop_exe}")
        raise FileNotFoundError(f"VirtualDesktop11.exe 不存在于 {script_dir}")

    # 构建命令
    command = [virtual_desktop_exe, f"/AllWallpapers:{image_path}"]

    try:
        # 使用subprocess.run执行命令
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("已设置壁纸。")
        else:
            print(f"设置壁纸失败: {result.stderr}")
            raise Exception(f"命令执行失败，返回码: {result.returncode}")
    except Exception as e:
        print(f"设置壁纸时发生错误: {str(e)}")
        raise


def send_message(title, icon_path, message, url):
    """
    发送消息通知
    参数:
        title: 通知标题
        icon_path: 图标路径
        message: 通知消息
        url: 壁纸链接
    """
    # 获取图标所在目录，PowerShell 脚本内容
    powershell_script = rf"""
# 添加必要的引用
Add-Type -AssemblyName System.Runtime.WindowsRuntime

# 导入命名空间
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

# 绑定到文件资源管理器（默认应用）
$AppID = "Microsoft.Windows.Explorer"

# 定义 XML 格式的通知
$ToastXml = @"
<toast activationType="protocol" launch="{url}">
    <visual>
        <binding template="ToastGeneric">
            <text>{title}</text>
            <image placement="appLogoOverride" src="{icon_path}"/>
            <text>{message}</text>
        </binding>
    </visual>
</toast>
"@

# 解析 XML
$XmlDocument = New-Object Windows.Data.Xml.Dom.XmlDocument
$XmlDocument.LoadXml($ToastXml)

# 创建通知
$Toast = [Windows.UI.Notifications.ToastNotification]::new($XmlDocument)

# 发送通知
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppID).Show($Toast)
    """
    # 运行 PowerShell 命令
    subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-NoProfile",
            "-Command",
            powershell_script,
        ],
        shell=False,
    )


# 主函数
if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()

    # 确定使用的分辨率
    if args.photosize:
        photo_size = args.photosize  # 从 argparse choices 中获取图片分辨率/尺寸
        print(f"使用指定的分辨率: {photo_size}")
    else:
        # 获取屏幕分辨率
        screen_info = get_screen_size()
        photo_size = screen_info["matched_resolution"]
        print(f"当前屏幕分辨率: {screen_info['screen_resolution']}")
        print(f"匹配的图片分辨率: {photo_size}")

    # 使用选定的分辨率下载壁纸
    result = get_bing_wallpaper(photo_size)
    if result:
        print(f"标题: {result['title']}")
        print(f"版权: {result['copyright']}")
        print(f"下载链接: {result['url']}")
        print(f"本地保存路径: {result['local_path']}")
        print(f"图片分辨率: {result['resolution']}")

        # 设置壁纸
        set_wallpaper(result["local_path"])
        # 显示壁纸相关信息通知
        send_message(
            result["title"], result["local_path"], result["copyright"], result["url"]
        )
    else:
        print("未找到合适的壁纸")
