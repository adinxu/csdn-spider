---
title: release版本core推导与相应工具学习-incomplete
categories:
  - Linux
tags:
  - 面试
  - 数据结构
  - 算法
---

# release版本core推导与相应工具学习_incomplete

一般进行开发工作时，会有debug版本和release版本之分，debug版本方便调试，但与release版本相比，体积臃肿，运行速度慢。一般debug版本会带有符号表与调试信息，而release版本会把符号表和调试信息等strip掉。这时候，如果release版本出现core，而又不具备在debug版本复现的条件，就需要直接在release版本定位，由于没有符号表与调试信息，定位难度极大。<br/> 先补充一下基础知识，涉及以下几个方面：<br/> 1.nm<br/> 2.readelf<br/> 3.objdump<br/> 4.objcopy<br/> 5.strip<br/> 6.obj文件段结构<br/> 7.符号表与调试信息<br/> 8.gdb命令<br/> (gdb) help add-symbol-file<br/> Load symbols from FILE, assuming FILE has been dynamically loaded.<br/> Usage: add-symbol-file FILE ADDR [-s &lt;SECT_ADDR&gt; -s &lt;SECT_ADDR&gt; …]<br/> ADDR is the starting address of the file’s text.<br/> The optional arguments are section-name section-address pairs and<br/> should be specified if the data and bss segments are not contiguous<br/> with the text. SECT is a section name to be loaded at SECT_ADDR.<br/> 注意需要正确指定加载地址<br/> info proc mappings

x与disassemble的异同

未完待续。。。<br/> 相关文章供参考：<br/> [Linux环境Release版本的符号表剥离及调试方法](https://blog.csdn.net/qq_34176606/article/details/114554009?spm=1001.2014.3001.5501)
