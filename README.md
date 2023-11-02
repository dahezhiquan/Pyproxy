# Pyproxy
Pyproxy，一个支持自定义包的TCP代理工具

# 使用示例

通过以下参数启动代理监控FTP流量：

```python
python3 proxy.py 192.168.65.129 21 ftp.sun.ac.za 21 True
```
![image](https://github.com/dahezhiquan/Pyproxy/assets/76278560/65400243-76c0-42e0-8d8a-109554b66d10)


在Kali虚拟机上另开一个终端，新建一个FTP会话，连接到Kali虚拟机的默认FTP端口，使用匿名用户登录（21）：

![image](https://github.com/dahezhiquan/Pyproxy/assets/76278560/bdc44de5-2404-4363-8d8f-259fb6ec63c3)


代理接收到流量内容：

![image](https://github.com/dahezhiquan/Pyproxy/assets/76278560/3388616b-a183-45f9-99e7-58904371c594)


