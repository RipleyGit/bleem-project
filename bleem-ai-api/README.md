# AI工具
## 🚀 快速开始 (Getting Started)

### 前置要求 (Prerequisites)
*   **Python**: v3.10+
*   **API Keys**:
    *   [Google Gemini API Key](https://aistudio.google.com/app/apikey) 或 OpenAI Key


### 1. 环境配置

在 目录下创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 文件，填入您的 API Key 和其他配置
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv .ai_venv
# 激活虚拟环境:
# Windows: .ai_venv\Scripts\activate
# Mac/Linux: source .ai_venv/bin/activate
pip install -r requirements.txt
```

### 3. 一键启动 (Run)

我们在根目录提供了便捷的启动脚本：

**Mac / Linux:**
```bash
#!/bin/bash


# AI Api - 启动脚本

echo "🚀 启动AI Api..."

# 检查环境变量
if [ ! -f ./.env ]; then
    echo "⚠️  请先配置 ./.env 文件（参考 ./.env.example）"
    echo "   设置您的 GEMINI_API_KEY"
fi

# 启动后端
echo "📦 启动后端服务 (FastAPI)..."

# 检查是否在 conda 环境中
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    # 不在 conda 环境中，尝试激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "⚠️  请先激活 conda 环境: conda activate aiwardrobe"
        exit 1
    fi
fi
# 关闭当前后端
kill -9 $(sudo lsof -t -i :8000)

uvicorn main:app --host 0.0.0.0 --reload --port 8000 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3
# 打印日志
echo ""
echo "✅ 服务已启动："
echo "   - 后端 API: http://localhost:8000"
echo "   - 后端文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait

```

**Windows:**
在命令行运行：
```cmd
@echo off
chcp 65001 >nul
echo 🚀 启动 AI 智能衣橱...

REM 检查 backend/.env 是否存在
if not exist "backend\.env" (
    echo ⚠️  请先配置 backend\.env 文件（参考 backend\.env.example）
    echo    即把 backend\.env.example 复制为 backend\.env 并填入 API Key
    pause
    exit /b
)

REM 启动后端
echo 📦 正在启动后端服务 (FastAPI)...
start "AI Wardrobe Backend" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --reload --port 8000"

REM 等待几秒
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🎨 正在启动前端服务 (React)...
start "AI Wardrobe Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ 服务已在很多新窗口中启动：
echo    - 后端 API: http://localhost:8000
echo    - 前端界面: http://localhost:5173
echo.
```

启动后访问：
*   📄 **后端文档**: [http://localhost:8000/docs](http://localhost:8000/docs)