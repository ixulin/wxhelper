import json
import threading
import socketserver
import tkinter as tk
from tkinter import messagebox
import queue


root = tk.Tk()
event_queue = queue.Queue()

class ReceiveMsgSocketServer(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self):
        conn = self.request
        while True:
            try:
                ptr_data = b""
                while True:
                    data = conn.recv(1024)
                    ptr_data += data
                    if len(data) == 0 or data[-1] == 0xA:
                        break

                msg = json.loads(ptr_data)
                ReceiveMsgSocketServer.msg_callback(msg)

            except OSError:
                break
            except json.JSONDecodeError:
                pass
            conn.sendall("200 OK".encode())
        conn.close()

    @staticmethod
    def msg_callback(msg):
        if "content" in msg:
            if "全图鉴" in msg["content"]:
            # 弹出提示窗口
            
            # 在主线程中创建并操作Tkinter窗口小部件
            # messagebox.showinfo("提示窗口", "这是一个提示信息")
            # root.after(0.1, lambda: messagebox.showinfo("提示窗口", "这是一个提示信息"))
                event_queue.put( msg["content"])
                print("包含全图鉴")
            else:
                print("content")
        else:
            print("未包含全图鉴")
        print(msg)

def handle_event():
    try:
        event = event_queue.get(block=False)
        # 处理事件
        messagebox.showinfo(event)
        print("Event received:", event)
    except queue.Empty:
        pass
    root.after(100, handle_event)  # 每隔100毫秒检查一次事件队列
    # print("update event")

def start_socket_server(port: int = 19099,
                        request_handler=ReceiveMsgSocketServer,
                        main_thread: bool = True) -> int or None:
    ip_port = ("127.0.0.1", port)
    try:
        s = socketserver.ThreadingTCPServer(ip_port, request_handler)
        if main_thread:
            print("main_thread")
            s.serve_forever()
        else:
            socket_server = threading.Thread(target=s.serve_forever)
            socket_server.setDaemon(True)
            socket_server.start()
            return socket_server.ident
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    return None


if __name__ == '__main__':# 创建主窗口
    start_socket_server(main_thread=False)
    root.withdraw()  # 隐藏主窗口
    root.after(100, handle_event)  # 每隔100毫秒检查一次事件队列
    root.mainloop()
