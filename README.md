# DDNS Python Script for DNSPOD

## 特性

* 安装卸载功能
* 定时检测并更新解析记录

## 测试环境

`Ubuntu 20.04 LTS on WSL2 ` ，`Python 3.8.5 64-bit ` ，装有 `requests`、 `python-crontab` 模块.

## 使用方法

1. 确保已经安装`python3` `pip3` `python-crontab`;
2. 登录DNSPOD后台，账号中心 -> 密钥管理 -> 创建密钥，保存好密钥;
3. 下载打包好的程序并解压，得到`setup.py`和`DDNS.py`;
4. 运行`setup.py`, 首次运行会在`setup.py`所在位置自动生成配置文件 `config.json`;
5. 打开`config.json`，填入对应信息，保存后重新打开`setup.py`，程序会自动校验填入信息的正确性；
6. 校验成功后，先选择第一项尝试手动更新记录；
7. 如果没有问题重新打开程序设置`DDNS.py`自动运行，可根据个人需要设置自动更新频率；

## 注意事项

* 程序支持形如

  ```
  example.com
  www.example.com
  ```

  的[二级或三级域名]([https://zh.wikipedia.org/wiki/%E5%9F%9F%E5%90%8D#%E5%9F%9F%E5%90%8D%E5%B1%82%E6%AC%A1](https://zh.wikipedia.org/wiki/域名#域名层次))；

* 每次尝试自动更新DNS记录，都会在程序所在目录下的`DDNS.log`中生成日志，日志内容包括每次更新的时间、提示信息和DNSPOD返回的完整内容；

  （手动更新DNS记录则日志会直接显示在控制台中）

* 若要修改配置文件，请修改后打开 `setup.py ` 手动更新一次，测试之后再设定自动执行以保正常；

* 若要卸载，请打开 `setup.py`，内有卸载选项，一键清除自动任务和所有文件；

* 请保管好 `config.json`.

 **这是第一个版本，难免存在各种问题，欢迎指正。**
