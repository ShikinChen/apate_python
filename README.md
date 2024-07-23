## 根据[apate是一款能够简洁、快速地对文件进行格式伪装的工具，可以在某些情况下绕过限制。](https://github.com/rippod/apate)进行移植成python版本方便不同系统使用命令形式进行伪装和去伪装

### 运行环境需要python3.4以上 请自行[安装和下载](https://www.python.org/downloads/)

### 将文件和文件夹里面的文件进行伪装,并且自动增加mp4后缀

```shell
python3 apate.py -p 文件路径或者文件夹路径 -d
```

### 将文件和文件夹里面的文件进行去伪装,会自动去除伪装后缀

```shell
python3 apate.py -p 文件路径或者文件夹路径 -r
```