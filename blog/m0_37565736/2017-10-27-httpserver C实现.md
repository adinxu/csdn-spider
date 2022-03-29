---
title: httpserver C实现
categories:
  - 网络通信
tags:
  - c语言
  - http协议
  - 传输层
  - tcp
  - 10054错误
---
{% include toc %}

# httpserver C实现

折腾的有点累，传输层用TCP解简单的http协议，然后实现了两个假的按钮233，这个是在别人的基础上完成的–&gt;[地址](http://blog.csdn.net/u012291157/article/details/46391189)， <br/> 下面是源码：

```
// HTTP1.1 与 1.0不同，默认是持续连接的(keep-alive)
#include &lt;Winsock2.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
_CRTIMP char* __cdecl __MINGW_NOTHROW _getcwd (char*, int);

#define BACKLOG 10
#define DEFAULT_PORT 8080
#define BUF_LENGTH 1024
#define MIN_BUF 128
#define _MAX_PATH MAX_PATH
#define USER_ERROR -1
#define SERVER "Server: Server\r\n"

char recv_buf[BUF_LENGTH];
char method[MIN_BUF];
char url[MIN_BUF];
char path[_MAX_PATH];

void ProcessRequst(SOCKET sAccept);
int file_not_found(SOCKET sAccept);
int file_ok(SOCKET sAccept, long flen);
int send_file(SOCKET sAccept, FILE *resource);
int send_not_found(SOCKET sAccept);

const char *FileNotFoundPage=
"&lt;html&gt;"
"&lt;head&gt;&lt;title&gt;404 not found&lt;/title&gt;&lt;link rel='icon' href='http://oygwu7lhj.bkt.clouddn.com/favicon.ico' type='image/x-ico' /&gt; &lt;/head&gt;"
"&lt;body bgcolor=\"#FFFFCC\"&gt;&lt;br&gt;&lt;br&gt;&lt;center&gt;"
"&lt;span style=\"font-size:50px;color:CC9999\"&gt;对方给你发送了一个404，并向你扔了一只小明&lt;/span&gt;"
"&lt;br&gt;&lt;br&gt;&lt;br&gt;"
"&lt;img src=\"http://oygwu7lhj.bkt.clouddn.com/dog.JPEG\" alt=\"dog\"&gt;"
"&lt;/center&gt;&lt;/body&gt;"
"&lt;/html&gt;"
;
const char *DefaultPage=
"&lt;html&gt;"
"&lt;head&gt;&lt;title&gt;Default&lt;/title&gt;&lt;link rel='icon' href='http://oygwu7lhj.bkt.clouddn.com/favicon.ico' type='image/x-ico' /&gt; &lt;/head&gt;"
"&lt;body bgcolor=\"#70000\"&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;&lt;br&gt;"
"&lt;center&gt;&lt;span style=\"font-size:50px;color:A0A0A0;font-family:century\"&gt;你是小明吗&lt;/span&gt;&lt;hr&gt;&lt;/center&gt;"
"&lt;br&gt;"
"&lt;table width=100% height=10%&gt;&lt;tr&gt;&lt;td&gt;&lt;center&gt;"
"&lt;a href=\"yes\"&gt;&lt;button type=\"button\" style=\"height:30px;width:100px;\"&gt;yes&lt;/button&gt;&lt;/a&gt;"
"&amp;nbsp&amp;nbsp&amp;nbsp&amp;nbsp"
"&lt;a href=\"no\"&gt;&lt;button type=\"button\" style=\"height:30px;width:100px;\"&gt;no&lt;/button&gt;&lt;/a&gt;"
"&lt;/center&gt;&lt;/td&gt;&lt;/tr&gt;&lt;/table&gt;"
"&lt;/body&gt;"
"&lt;/html&gt;"
;
const char *ConfirmPage=
"&lt;html&gt;"
"&lt;head&gt;&lt;title&gt;Default&lt;/title&gt;&lt;link rel='icon' href='http://oygwu7lhj.bkt.clouddn.com/favicon.ico' type='image/x-ico' /&gt; &lt;/head&gt;"
"&lt;body bgcolor=\"#FFFFCC\"&gt;&lt;center&gt;"
"&lt;span style=\"font-size:30px;color:000000;font-family:century\"&gt;恭喜你发现一只认真学习的小明&lt;/span&gt;"
"&lt;br&gt;"
"&lt;img src=\"http://oygwu7lhj.bkt.clouddn.com/ql.jpg\" alt=\"ql\"&gt;"
"&lt;/center&gt;&lt;/body&gt;"
"&lt;/html&gt;"
;

void ProcessRequst(SOCKET sAccept)
{
    int i, j;
    //example:GET /su?wd=ww&amp;action=opensearch&amp;ie=UTF-8 HTTP/1.1\r\n
    //处理接收数据
    i = 0; j = 0;
    // 取出第一个单词，一般为HEAD、GET、POST
    while (!(' ' == recv_buf[j]) &amp;&amp; (i &lt; sizeof(method) - 1))
    {
        method[i] = recv_buf[j];
        i++; j++;
    }
    method[i] = '\0';   // 结束符，这里也是初学者很容易忽视的地方

    printf("method: %s\n", method);
    // 如果不是GET或HEAD方法，则直接断开本次连接
    // 如果想做的规范些可以返回浏览器一个501未实现的报头和页面
    if (stricmp(method, "GET") &amp;&amp; stricmp(method, "HEAD"))//比较，相等返回0
    {
        printf("not get or head method.\n");
        printf("***********************\n\n\n\n");
        return;
    }

    // 提取出第二个单词(url文件路径，空格结束)，并把'/'改为windows下的路径分隔符'\'
    // 这里只考虑静态请求(比如url中出现'?'表示非静态，需要调用CGI脚本，'?'后面的字符串表示参数，多个参数用'+'隔开
    i = 0;
    while ((' ' == recv_buf[j]) &amp;&amp; (j &lt; sizeof(recv_buf)))
        j++;
    while (!(' ' == recv_buf[j]) &amp;&amp; (i &lt; sizeof(recv_buf) - 1) &amp;&amp; (j &lt; sizeof(recv_buf)))
    {
        if (recv_buf[j] == '/')
            url[i] = '\\';
        else
            url[i] = recv_buf[j];
        i++; j++;
    }
    url[i] = '\0';
    printf("url: %s\n",url);

    if(1==strlen(url))//默认请求
    {
        printf("send default page\n");
        file_ok(sAccept, strlen(DefaultPage));
        send(sAccept, DefaultPage, strlen(DefaultPage), 0);
        printf("***********************\n\n\n\n");
        return;
    }
    else if(0 == stricmp(url, "\\yes"))//假按钮处理
    {
        printf("send confirm page\n");
        file_ok(sAccept, strlen(ConfirmPage));
        send(sAccept, ConfirmPage, strlen(ConfirmPage), 0);
        printf("***********************\n\n\n\n");
        return;
    }

    // 将请求的url路径转换为本地路径
    _getcwd(path,_MAX_PATH);//获取当前工作路径
    strcat(path,url);//将两字符串连接
    printf("path: %s\n",path);


    // 打开本地路径下的文件，网络传输中用r文本方式打开会出错
    FILE *resource = fopen(path,"rb");

    // 没有该文件则发送一个简单的404-file not found的html页面，并断开本次连接
    if(resource==NULL)
    {
        file_not_found(sAccept);
        // 如果method是GET，则发送自定义的file not found页面
        if(0 == stricmp(method, "GET"))
            send_not_found(sAccept);

        printf("file not found.\n");
        printf("***********************\n\n\n\n");
        return;
    }
    /*
    SEEK_SET    档案开头
    SEEK_CUR    文件指针的当前位置
    SEEK_END    文件结尾*
    */

    // 求出文件长度，记得重置文件指针到文件头
    fseek(resource,0,SEEK_END);
    long flen=ftell(resource);//返回当前文件读写位置
    printf("file length: %ld\n", flen);
    fseek(resource,0,SEEK_SET);

    // 发送200 OK HEAD
    file_ok(sAccept, flen);

    // 如果是GET方法则发送请求的资源
    if(0 == stricmp(method, "GET"))
    {
        if(0 == send_file(sAccept, resource))
            printf("file send ok.\n");
        else
            printf("file send fail.\n");
    }

    printf("***********************\n\n\n\n");

    return;
}
// 发送200 ok报头
int file_ok(SOCKET sAccept, long flen)
{
    char send_buf[MIN_BUF];
//  time_t timep;
//  time(&amp;timep);
    sprintf(send_buf, "HTTP/1.1 200 OK\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "Connection: keep-alive\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
//  sprintf(send_buf, "Date: %s\r\n", ctime(&amp;timep));
//  send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, SERVER);
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "Content-Length: %ld\r\n", flen);
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "Content-Type: text/html\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    return 0;
}

// 发送404 file_not_found报头
int file_not_found(SOCKET sAccept)
{
    char send_buf[MIN_BUF];
//  time_t timep;
//  time(&amp;timep);
    sprintf(send_buf, "HTTP/1.1 404 NOT FOUND\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
//  sprintf(send_buf, "Date: %s\r\n", ctime(&amp;timep));
//  send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "Connection: keep-alive\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, SERVER);
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "Content-Type: text/html\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    sprintf(send_buf, "\r\n");
    send(sAccept, send_buf, strlen(send_buf), 0);
    return 0;
}

// 发送自定义的file_not_found页面
int send_not_found(SOCKET sAccept)
{
    send(sAccept, FileNotFoundPage, strlen(FileNotFoundPage), 0);
    return 0;
}

// 发送请求的资源
int send_file(SOCKET sAccept, FILE *resource)
{
    char send_buf[BUF_LENGTH];
    while (1)
    {
        memset(send_buf,0,sizeof(send_buf));       //缓存清0
        fgets(send_buf, sizeof(send_buf), resource);
    //  printf("send_buf: %s\n",send_buf);
        if (SOCKET_ERROR == send(sAccept, send_buf, strlen(send_buf), 0))
        {
            printf("send() Failed:%d\n",WSAGetLastError());
            return USER_ERROR;
        }
        if(feof(resource))
        return 0;
    }
}

int main()
{
    WSADATA wsaData;
    SOCKET sListen,sAccept;        //服务器监听套接字，连接套接字
    int serverport=DEFAULT_PORT;   //服务器端口号
    struct sockaddr_in ser,cli;   //服务器地址，客户端地址
    int iLen;
    int iResult;

    printf("-----------------------\n");
    printf("Server waiting\n");
    printf("-----------------------\n");

    //第一步：加载协议栈
    if (WSAStartup(MAKEWORD(2,2),&amp;wsaData) !=0)
    {
        printf("Failed to load Winsock.\n");
        return USER_ERROR;
    }

    //第二步：创建监听套接字，用于监听客户请求
    sListen =socket(AF_INET,SOCK_STREAM,0);
    if (sListen == INVALID_SOCKET)
    {
        printf("socket() Failed:%d\n",WSAGetLastError());
        return USER_ERROR;
    }

    //创建服务器地址：IP+端口号
    ser.sin_family=AF_INET;
    ser.sin_port=htons(serverport);               //服务器端口号
    ser.sin_addr.s_addr=htonl(INADDR_ANY);   //服务器IP地址，默认使用本机IP
    memset(&amp;(ser.sin_zero), 0, 8);
    //第三步：绑定监听套接字和服务器地址
    if (bind(sListen,(LPSOCKADDR)&amp;ser,sizeof(ser))==SOCKET_ERROR)
    {
        printf("blind() Failed:%d\n",WSAGetLastError());
        return USER_ERROR;
    }

    //第五步：通过监听套接字进行监听
    if (listen(sListen,BACKLOG)==SOCKET_ERROR)
    {
        printf("listen() Failed:%d\n",WSAGetLastError());
        return USER_ERROR;
    }
    //第六步：接受客户端的连接请求，返回与该客户建立的连接套接字
    iLen=sizeof(cli);
    while (1)  //循环等待客户的请求
    {
        sAccept=accept(sListen,(struct sockaddr*)&amp;cli,&amp;iLen);
        if (sAccept==INVALID_SOCKET)
        {
            printf("accept() Failed:%d\n",WSAGetLastError());
            break;
        }
        printf( "Client IP：%s \n", inet_ntoa(cli.sin_addr));
        printf( "Client PORT：%d \n", ntohs(cli.sin_port));
        while(1)
        {
            memset(recv_buf,0,sizeof(recv_buf));
            printf("wait to rec...\n");
            if ((iResult=recv(sAccept,recv_buf,sizeof(recv_buf),0))&lt;0)   //接收错误
            {
                printf("recv() Failed:%d\n",WSAGetLastError());
                printf("***********************\n\n\n\n");
                closesocket(sAccept);
                break;
            }
            else if(iResult==0)
            {
                printf("connection has been closed!\n");
                printf("***********************\n\n\n\n");
                printf("waiting for next connection!\n");
                break;
            }
            else
            {
                printf("recv data from client:%s\n",recv_buf); //接收成功，打印请求报文
                ProcessRequst(sAccept);
            }
        }
    }
    closesocket(sListen);
    WSACleanup();
    return 0;
}

```

还有就是我之前一直遇到10054错误。。。最后查出来是因为我一时手痒设置的网页小图标的问题。。。因为当时给的地址是本地，发往客户端之后，客户端会来GET，结果GET之后就是奇葩错误了。。。10054是中间见到，有的时候是客户端不关网页这边就不显示接收的数据。。。。
