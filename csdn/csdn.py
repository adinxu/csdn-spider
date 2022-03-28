#!/usr/bin/env python
# coding: utf-8


import os, re
import requests
from bs4 import BeautifulSoup, Comment
from .tomd import Tomd


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
		self.url_num = 1
		self.title=''
		self.nickname=''
		self.cdate=''
		self.ctime=''
		self.classify=[]
		self.tags=[]

	def start(self):
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
			for article in articles:
				article_title = gettitle.search(article.a.text).group()
				article_href = article.a['href']
				self.TaskQueue.append((article_title, article_href))
	
	def get_md(self, url):
		response = self.s.get(url=url, headers=self.headers)
		html = response.text
		soup = BeautifulSoup(html, 'lxml')
		content = soup.select_one("#mainBox > main > div.blog-content-box")
		self.title=soup.select_one("h1.title-article").string
		self.title = re.sub(r'[_\/:*?"<>|\n]','-', self.title)
		self.nickname=soup.select_one("a.follow-nickName").string
		createtime=soup.select_one("span.time").string
		self.cdate=re.search("\d\d\d\d-\d\d-\d\d",createtime).group()
		self.ctime=re.search("\d\d:\d\d:\d\d",createtime).group()
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
		# 转换为markdown
		md += Tomd(str(content)).markdown
		return md

	def write_readme(self):
		print("+"*100)
		print("[++] 开始爬取 {} 的博文 ......".format(self.username))
		print("+"*100)
		reademe_path = result_file(self.username,file_name="README.md",folder_name=self.folder_name)
		with open(reademe_path,'w', encoding='utf-8') as reademe_file:
			readme_head = "# " + self.username + " 的博文\n"
			reademe_file.write(readme_head)
			self.TaskQueue.reverse()
			for (article_title,article_href) in self.TaskQueue:
					text = str(self.url_num) + '. [' + article_title + ']('+ article_href +')\n'
					reademe_file.write(text)
					self.url_num += 1
		self.url_num = 1
	
	def get_all_articles(self):
		while len(self.TaskQueue) > 0:
			(article_title,article_href) = self.TaskQueue.pop()
			md = self.get_md(article_href)
			print("[++++] 正在处理URL:{}".format(article_href))
			#适配jekll文件名
			file_name = self.cdate + '-' + self.title + ".md"
			artical_path = result_file(folder_username=self.username, file_name=file_name, folder_name=self.folder_name)
			with open(artical_path, "w", encoding="utf-8") as artical_file:
				artical_file.write(md)
			self.url_num += 1

def spider(username: str, cookie_path:str, folder_name: str = "blog"):
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
	csdn = CSDN(username, folder_name, cookie_path)
	csdn.start()
	csdn.write_readme()
	csdn.get_all_articles()


