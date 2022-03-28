## 写在前面@adinxu
此仓库在原仓库基础上修改，爬取csdn博客，用于迁移文章至jekll搭建的github pages个人博客下。  
目标：
- [x] 修改文章命名为：xxxx-xx-xx-title.markdown格式
- [x] 为每篇文章添加yaml头信息
- [ ] 转化markdown效果优化
- [ ] 记录爬取的博客，可以定时同步
# CSDN 爬虫

> 主要功能：爬取 csdn 博客指定用户的所有博文并转换为 markdown 格式保存到本地。

## 下载脚本
```shell
git clone https://github.com/ds19991999/csdn-spider.git
cd csdn-spider
python3 -m pip install -r requirements.txt

# 测试
python3 test.py # 需要先配置登录 cookie
```

## 获取 cookie

登录 `csdn` 账号，进入：https://blog.csdn.net ，按 `F12` 调试网页，复制所有的 `Request Headers`，保存到`cookie.txt`文件中

![1571482112632](assets/1571482112632.png)


## 爬取用户全部博文
```python
import csdn
csdn.spider("ds19991999", "cookie.txt")
# 参数 usernames: str, cookie_path:str, folder_name: str = "blog"
```

* 示例爬取博文效果： [ds19991999 的博文](https://github.com/ds19991999/csdn-spider/tree/master/blog/ds19991999)

## LICENSE

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a>



`PS`：随意写的爬虫脚本，佛系更新。