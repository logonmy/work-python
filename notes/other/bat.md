### 通过一个脚本取执行多个脚本

示例：
```html
@echo off
title start worker

%~d0 
cd %~dp0

cd ..
cd node-changeip
start start.bat

cd ..
cd worker
start start.bat

exit
```
其中：  
`%~d0 是当前盘符，是当前被执行的脚本所在的盘符`  
`%cd% 是当前目录，是执行最开始脚本的目录`  
`cd/d %~dp0 直接切换到当前盘符`  
`start 命令会新开一个窗口，调用其他脚本`

    @echo off
    echo 当前盘符：%~d0
    echo 当前盘符和路径：%~dp0
    echo 当前盘符和路径的短文件名格式：%~sdp0
    echo 当前批处理全路径：%~f0
    echo 当前CMD默认目录：%cd%
    pause


### windows 定时任务命令
`schtasks.exe`

#### 创建任务
    schtasks.exe /create /tn "init" /ru Administrator /sc ONSTART /tr "C:\test\init.bat"

#### 删除任务
    schtasks /delete /tn init

#### 查询任务
    schtasks /query /fo TABLE
    schtasks /query /fo TABLE /tn init
    
    schtasks /query /fo LIST
    schtasks /query /fo LIST /tn init

#### 手动运行任务
    schtasks /run /tn init
