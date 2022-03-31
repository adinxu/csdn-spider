#!/usr/bin/env python
# coding: utf-8


import os, re
import requests
from bs4 import BeautifulSoup, Comment
from .tomd import Tomd

dbg_flag = False


def result_file(folder_username, file_name, folder_name):
	folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", folder_name, folder_username)
	if not os.path.exists(folder):
		try:
			os.makedirs(folder)
		except Exception:
			pass
		path = os.path.join(folder, file_name)
		file = open(path,"w")
		file.close()
	else:
		path = os.path.join(folder, file_name)
	return path


def get_headers(cookie_path:str):
	cookies = {}
	with open(cookie_path, "r", encoding="utf-8") as f:
		cookie_list = f.readlines()
	for line in cookie_list:
		cookie = line.split(":")
		cookies[cookie[0]] = str(cookie[1]).strip()
	return cookies


def delete_ele(soup:BeautifulSoup, tags:list):
	for ele in tags:
		for useless_tag in soup.select(ele):
			useless_tag.decompose()


def delete_ele_attr(soup:BeautifulSoup, attrs:list):
	for attr in attrs:
		for useless_attr in soup.find_all():
			del useless_attr[attr]


def delete_blank_ele(soup:BeautifulSoup, eles_except:list):
	for useless_attr in soup.find_all():
		try:
			if useless_attr.name not in eles_except and useless_attr.text == "":
				useless_attr.decompose()
		except Exception:
			pass


class CSDN(object):
	def __init__(self, username, folder_name, cookie_path):
		self.headers = get_headers(cookie_path)
		self.s = requests.Session()
		self.username = username
		self.TaskQueue = list()
		self.folder_name = folder_name
		self.title=''
		#self.nickname=''#博客名称
		#self.mdate=''#修改日期
		#self.mtime=''#修改时间
		self.classify=[]
		self.tags=[]

	def start(self):
		global dbg_flag
		if not dbg_flag:
			num = 0
			articles = [None]
			#访问文章列表页面，获取每页包含的文章
			while len(articles) > 0:
				num += 1
				url = u'https://blog.csdn.net/' + self.username + '/article/list/' + str(num)
				response = self.s.get(url=url, headers=self.headers)
				html = response.text
				soup = BeautifulSoup(html, "html.parser")
				articles = soup.find_all('div', attrs={"class":"article-item-box csdn-tracking-statistics"})
				gettitle=re.compile("(?<= )\S+")
				getctime=re.compile('\d\d\d\d-\d\d-\d\d')
				for article in articles:
					article_title = gettitle.search(article.a.text).group()
					article_href = article.a['href']
					article_createdate = getctime.search(article.select_one('span.date').text).group()
					self.TaskQueue.append((article_title, article_href,article_createdate))
		else:
			#调试单篇文章的获取内容
			self.TaskQueue.append(("重定向与管道符", "https://blog.csdn.net/m0_37565736/article/details/80385398",'2022-01-01'))
	
	def get_md(self, url):
		response = self.s.get(url=url, headers=self.headers)
		html = response.text
		soup = BeautifulSoup(html, 'lxml')
		content = soup.select_one("#mainBox > main > div.blog-content-box")
		self.title=soup.select_one("h1.title-article").string
		self.title = re.sub(r'[_\/:*?"<>|\n]','-', self.title)
		#self.nickname=soup.select_one("a.follow-nickName").string
		#createtime=soup.select_one("span.time").string
		#self.mdate=re.search("\d\d\d\d-\d\d-\d\d",createtime).group()
		#self.mtime=re.search("\d\d:\d\d:\d\d",createtime).group()
		candt=soup.select("a.tag-link") 
		self.classify.clear()
		self.tags.clear()
		for t in candt:
			if t.has_attr('data-report-click'):
				self.tags.append(t.string)
			else:
				self.classify.append(t.string)
		# 删除注释
		for useless_tag in content(text=lambda text: isinstance(text, Comment)):
			useless_tag.extract()
		# 删除无用标签
		tags = ["svg", "ul", ".hljs-button.signin"]
		delete_ele(content, tags)
		# 删除标签属性
		attrs = ["class", "name", "id", "onclick", "style", "data-token", "rel"]
		delete_ele_attr(content,attrs)
		# 删除空白标签
		eles_except = ["img", "br", "hr"]
		delete_blank_ele(content, eles_except)
		#添加头信息
		md = '-'*3+'\n'
		md += "title: {}\n".format(self.title)
		md += "categories:\n"
		for cla in self.classify:
			md += "  - {}\n".format(cla)
		md += "tags:\n"
		for tag in self.tags:
			md += "  - {}\n".format(tag)
		md += '-'*3+'\n'
		#添加目录
		#md += '{% include toc %}\n'
		# 转换为markdown
		md += Tomd(str(content)).markdown
		return md

	def write_readme(self):
		global dbg_flag
		if not dbg_flag:
			print("+"*100)
			print("[++] 开始爬取 {} 的博文 ......".format(self.username))
			print("+"*100)
			reademe_path = result_file(self.username,file_name="README.md",folder_name=self.folder_name)
			url_num=1
			with open(reademe_path,'w', encoding='utf-8') as reademe_file:
				readme_head = "# " + self.username + " 的博文\n"
				reademe_file.write(readme_head)
				self.TaskQueue.reverse()
				for (article_title,article_href,time) in self.TaskQueue:
						text = str(url_num) + '. [' + article_title + ']('+ article_href +')\n'
						reademe_file.write(text)
						url_num += 1
		else:
			pass
	
	def get_all_articles(self):
		listlen=len(self.TaskQueue)
		currnum=1
		while len(self.TaskQueue) > 0:
			(article_title,article_href,article_createtime) = self.TaskQueue.pop()
			md = self.get_md(article_href)
			#适配jekll文件名,使用创建时间作为文件名第一部分
			file_name = article_createtime + '-' + self.title + ".md"
			print("[++++] 正在第{0}/{1}处理文章:{2}".format(currnum,listlen,file_name))
			artical_path = result_file(folder_username=self.username, file_name=file_name, folder_name=self.folder_name)
			with open(artical_path, "w", encoding="utf-8") as artical_file:
				artical_file.write(md)
			currnum+=1

def spider(username: str, cookie_path:str, folder_name: str = "blog"):
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
	csdn = CSDN(username, folder_name, cookie_path)
	csdn.start()
	csdn.write_readme()
	csdn.get_all_articles()


