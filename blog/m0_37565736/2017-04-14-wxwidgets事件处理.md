---
title: wxwidgets事件处理
categories:
  - 上位机
  - wxWidgets
tags:
  - 事件处理
  - wxwidgets
  - 自定义事件
---

# wxwidgets事件处理

# Event

严谨来说，wxwidgets中每个事件都可以被以下三个事件描述：

1.事件类型  

它是一个唯一标识事件类型的东西，当然是宏定义的形式，例如#define wxEVT_COMMAND_BUTTON_CLICKED          wxEVT_BUTTON它标识按键点击这个事件类型

2.事件所携带的事件类  

每个事件都会有与之相关的信息，这些数据的传递是通过那些从wxevent派生的类实现的，而不同类型的事件可以使用相同的事件类，比如按button和选择listbox都使用wxcommandevent类（所有的control events都是用它）。但是键盘事件使用wxkeyevent，因为它们携带的信息不同。

3.事件源 

wxevent（事件所携带的事件类）保存了产生事件的东西，对窗口来说，就是他的标识id，而很多时候会有许多object产生相同种类的事件（比如一个窗口有好几个按键， 它们都产生相同的按键点击事件），检查事件源或id来分辨它们。

                                                                              event

Event Handling

               evenhanding

上面说了事件，下面谈谈事件处理。每一个<a title="A class that can handle events from the windowing system.">wxEvtHandler</a>的派生类（所有继承自wxwindows的窗口类及应用程序类都是<a title="A class that can handle events from the windowing system.">wxEvtHandler</a>的派生类），例如frame，按钮，菜单等都在内部维护一个事件表（这里指静态事件表与动态绑定），通过这个表将事件与事件处理函数关联在一起。

在wxwi中有两种主要的处理事件的方法，即事件表宏和动态绑定。事件表将在编译期间将事件与其处理函数静态的关联，而动态绑定发生在运行期间，而且还可以解除绑定。动态绑定可以直接将事件和以下处理绑定：1.别的object的处理2.普通函数3.一些库函数，像boost::function&lt;&gt;和std::function&lt;&gt;。

# 事件表：

3.为每一个你想处理的事件定义一个事件处理函数。<br/>

例如：

```
MyFrame::OnButton1（wxCommandEvent&amp; event）
{.../*处理*/}
```

例如：

```
wxBEGIN_EVENT_TABLE(MyFrame, wxFrame)
    EVT_BUTTON(BUTTON1, MyFrame::OnButton1)
wxEND_EVENT_TABLE()
```

# 动态绑定：

```
MyFrame::MyFrame(...)
{
      Bind(wxEVT_COMMAND_BUTTON_CLICKED, &amp;MyFrame::OnButton1, this, BUTTON1);
}
```

```
void wxEvtHandler::Bind
(
const EventTag &amp; 
eventType,
void(Class::*)(EventArg &amp;) 
method,
EventHandler * 
handler,
int 
id = wxID_ANY,
int 
lastId = wxID_ANY,
wxObject * 
userData = NULL
 
)
[inline]
```

## 动态与静态事件表不同如下：

```
MyFrame::MyFrame(...)
{
  m_child-&gt;Bind(wxEVT_LEAVE_WINDOW, &amp;MyFrame::OnMouseLeave, this);
}
```
