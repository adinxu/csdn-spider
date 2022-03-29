---
title: Regex Golf题目分析-incomplete
categories:
  - 平台无关
tags:
  - regex
  - 正则
---
{% include toc %}

# Regex Golf题目分析_incomplete

[网站网址](https://alf.nu/RegexGolf)<br/> 做的时候，有的不会，有的不是最少字符数量，这里做个记录。<br/> 先附上之前关于正则的[文章](https://blog.csdn.net/m0_37565736/article/details/80369306)，方便查看。

```
^(?!.*(.)(.)\2\1)

```

后来从这个[网站](https://gist.github.com/Davidebyzero/9221685)搜索到了14个字符的答案，这个应该算讨巧了，匹配数据多一点就不行了。

```
^(?!(.)+\1)|ef

```

未完待续
