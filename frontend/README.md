# Vue 3 + Vite

==============================
DrugTarget Backend 部署说明
==============================

一、环境要求
------------------------------
1. Python 版本：
   - 推荐 Python 3.9
   - 不要使用 Python 3.11 / 3.12


二、项目结构要求
------------------------------
backend/
│
├─ main.py
├─ model_infer.py
├─ pubmed_search.py
├─ requirements.txt
└─ venv/            （部署时本地生成）


三、创建并激活虚拟环境
------------------------------

【Windows PowerShell】
python -m venv venv
venv\Scripts\activate


四、安装依赖
------------------------------
在 backend 目录下执行：

pip install -r requirements.txt


五、启动后端服务
------------------------------
在 backend 目录下执行：

python -m uvicorn main:app --host 0.0.0.0 --port 8000

启动成功标志：

Application startup complete.

六、启动前端服务
------------------------------
1. npm install
2. npm run dev

