# SetBingWallpapers - 更换必应壁纸  

此脚本可根据设备分辨率自动下载当日必应图片，或手动指定分辨率下载当日必应图片，然后设置为桌面壁纸。  

**适用平台：Windows 11 或更新版本。**  

## 包含的文件  

- **`SetBingWallpapers.BootStrapper.ahk`**  
基于 AutoHotKey 的外壳启动脚本，可让主程序以隐藏命令行窗口方式运行。  
- **`VirtualDesktop11.cs`**  
`VirtualDesktop11` 的源代码文件，需要编译后使用。**（适用于 Windows 11 24H2 之前版本）**  
- **`VirtualDesktop11-24H2.cs`**  
`VirtualDesktop11` 的源代码文件，需要编译后使用。**（适用于 Windows 11 24H2 及之后版本）**  
- **`bing-svgrepo-com.svg`**  
程序图标源文件（svg 格式）  
- **`icon.ico`**  
程序图标  
- **`SetBingWallpapers.py`**  
主程序源码  

## 如何编译/生成可执行文件  

### 1. 生成 VirtualDesktop11 主程序：  

根据目标系统版本，使用以下命令生成：  

**Windows 11 24H2 之前版本：**  

```
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe VirtualDesktop11.cs
```  

**Windows 11 24H2 及之后版本：**  

```
C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe VirtualDesktop11-24H2.cs
```  

然后将生成的最终可执行文件重命名为 `VirtualDesktop11.exe`，放在脚本 `SetBingWallpapers.py` 的同级目录下。  

### 2. 生成 `SetBingWallpapers.BootStrapper`：  

安装并配置好 AutoHotKey，使用 `Ahk2Exe` 生成 `SetBingWallpapers.BootStrapper.exe` 文件，放在脚本 `SetBingWallpapers.py` 的同级目录下。  

### 3. 生成 `SetBingWallpapers.CoreCli`：  

安装并配置好 Python，以及所需依赖：requests 和 Nuitka。  

```
pip install requests nuitka
```  

然后执行以下命令，生成 `SetBingWallpapers.CoreCli`：  

```
nuitka --windows-icon-from-ico=icon.ico --mode=standalone --include-data-files=VirtualDesktop11.exe=VirtualDesktop11.exe --include-data-files=SetBingWallpapers.BootStrapper.exe=SetBingWallpapers.BootStrapper.exe --lto=yes --remove-output --output-filename=SetBingWallpapers.CoreCli.exe .\SetBingWallpapers.py
```  

完成后将在脚本同级目录下生成 `SetBingWallpapers.dist` 文件夹，其中包含所有所需文件。  

## 帮助  

```
> .\SetBingWallpapers.CoreCli.exe --help
usage: SetBingWallpapers.CoreCli.exe [-h] [-p PHOTO_SIZE]

下载并设置必应每日壁纸

options:
  -h, --help            show this help message and exit
  -p PHOTO_SIZE, --photosize PHOTO_SIZE
                        指定壁纸分辨率：UHD | 1920x1080 | 1366x768 | 1280x768 | 1024x768 | 800x600 | 800x480 | 640x480
```