---
title: SetCommMask应用实例（事件处理部分）
categories:
  - WIN32API
tags:
  - SetCommMask
  - 实例
---
{% include toc %}

# SetCommMask应用实例（事件处理部分）

MFC下：<br/> 

```
// begin forever loop. This loop will run as long as the thread is alive.
for (;;)
{ // Make a call to WaitCommEvent(). This call will return immediatly
// because our port was created as an async port (FILE_FLAG_OVERLAPPED
// and an m_OverlappedStructerlapped structure specified). This call will cause the
// m_OverlappedStructerlapped element m_OverlappedStruct.hEvent, which is part of the m_hEventArray to
// be placed in a non-signeled state if there are no bytes available to be read,
// or to a signeled state if there are bytes available. If this event handle
// is set to the non-signeled state, it will be set to signeled when a
// character arrives at the port.
// we do this for each port!
bResult = WaitCommEvent(port-&gt;m_hComm, &amp;Event, &amp;port-&gt;m_ov);//设置等待
if (!bResult)//未有期待事件发生
{ // If WaitCommEvent() returns FALSE, process the last error to determin
// the reason..
switch (dwError = GetLastError())
{
case ERROR_IO_PENDING:
{
// This is a normal return value if there are no bytes
// to read at the port.
// Do nothing and continue
break;
}
case 87:
{
// Under Windows NT, this value is returned for some reason.
// I have not investigated why, but it is also a valid reply
// Also do nothing and continue.
break;
}
default:
{
// All other error codes indicate a serious error has
// occured. Process this error.
port-&gt;ProcessErrorMessage("WaitCommEvent()");
break;
}
}
}
else//等待的事件已经发生
{// If WaitCommEvent() returns TRUE, check to be sure there are
// actually bytes in the buffer to read.
//
// If you are reading more than one byte at a time from the buffer
// (which this program does not do) you will have the situation occur
// where the first byte to arrive will cause the WaitForMultipleObjects()
// function to stop waiting. The WaitForMultipleObjects() function
// resets the event handle in m_OverlappedStruct.hEvent to the non-signelead state
// as it returns.
//
// If in the time between the reset of this event and the call to
// ReadFile() more bytes arrive, the m_OverlappedStruct.hEvent handle will be set again
// to the signeled state. When the call to ReadFile() occurs, it will
// read all of the bytes from the buffer, and the program will
// loop back around to WaitCommEvent().
//
// At this point you will be in the situation where m_OverlappedStruct.hEvent is set,
// but there are no bytes available to read. If you proceed and call
// ReadFile(), it will return immediatly due to the async port setup, but
// GetOverlappedResults() will not return until the next character arrives.
//
// It is not desirable for the GetOverlappedResults() function to be in
// this state. The thread shutdown event (event 0) and the WriteFile()
// event (Event2) will not work if the thread is blocked by GetOverlappedResults().
//
// The solution to this is to check the buffer with a call to ClearCommError().
// This call will reset the event handle, and if there are no bytes to read
// we can loop back through WaitCommEvent() again, then proceed.
// If there are really bytes to read, do nothing and proceed.
bResult = ClearCommError(port-&gt;m_hComm, &amp;dwError, &amp;comstat);
if (comstat.cbInQue == 0)
continue;
} // end if bResult
// Main wait function. This function will normally block the thread
// until one of nine events occur that require action.
Event = WaitForMultipleObjects(3, port-&gt;m_hEventArray, FALSE, INFINITE);
switch (Event)
{
case 0:
{
// Shutdown event. This is event zero so it will be
// the higest priority and be serviced first.
port-&gt;m_bThreadAlive = FALSE;
// Kill this thread. break is not needed, but makes me feel better.
AfxEndThread(100);
break;
}
case 1: // read event
{
GetCommMask(port-&gt;m_hComm, &amp;CommEvent);
if (CommEvent &amp; EV_CTS)
::SendMessage(port-&gt;m_pOwner-&gt;m_hWnd, WM_COMM_CTS_DETECTED, (WPARAM) 0, (LPARAM) port-&gt;m_nPortNr);
if (CommEvent &amp; EV_RXFLAG)
::SendMessage(port-&gt;m_pOwner-&gt;m_hWnd, WM_COMM_RXFLAG_DETECTED, (WPARAM) 0, (LPARAM) port-&gt;m_nPortNr);
if (CommEvent &amp; EV_BREAK)
::SendMessage(port-&gt;m_pOwner-&gt;m_hWnd, WM_COMM_BREAK_DETECTED, (WPARAM) 0, (LPARAM) port-&gt;m_nPortNr);
if (CommEvent &amp; EV_ERR)
::SendMessage(port-&gt;m_pOwner-&gt;m_hWnd, WM_COMM_ERR_DETECTED, (WPARAM) 0, (LPARAM) port-&gt;m_nPortNr);
if (CommEvent &amp; EV_RING)
::SendMessage(port-&gt;m_pOwner-&gt;m_hWnd, WM_COMM_RING_DETECTED, (WPARAM) 0, (LPARAM) port-&gt;m_nPortNr);
if (CommEvent &amp; EV_RXCHAR)
// Receive character event from port.
ReceiveChar(port, comstat);
break;
}
case 2: // write event
{
// Write character event from port
WriteChar(port);
break;
}
} // end switch
} // close forever loop
```
