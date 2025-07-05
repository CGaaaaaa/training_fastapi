# training_fastapi

## 项目描述
这是一个基于FastAPI框架开发的RESTful API示例项目，用于展示FastAPI的各种功能，包括路由、依赖注入、认证授权、中间件等。项目包含电影管理系统的基本CRUD操作示例。

## 项目结构
```
app/
├── models/          # Pydantic模型定义
├── routers/         # API路由模块
├── static/          # 静态资源文件
├── utils/           # 工具类和辅助函数
└── main.py          # 应用入口点
```

## 安装说明
1. 克隆项目到本地:
```bash
git clone <项目地址>
cd training_fastapi
```

2. 创建虚拟环境并安装依赖:
```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
pip install -r requirements.txt
```

## 运行应用
```bash
uvicorn app.main:app --reload
```
应用将在 http://localhost:8000 上运行

## API文档
启动应用后，可以通过以下URL访问自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能
- 电影管理 CRUD 操作 (/movies)
- 用户认证 (JWT和基本认证)
- 静态文件服务
- Cookie处理
- 依赖注入示例