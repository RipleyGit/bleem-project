#!/bin/bash


echo "🚀 启动 AI 智能衣橱..."

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
        echo "⚠️  请先激活 conda 环境: conda create -n ai_api"
        echo "⚠️  请先激活 conda 环境: conda activate ai_api"
        exit 1
    fi
fi
# 关闭当前后端
kill -9 $(sudo lsof -t -i :8000)
# 安装依赖
pip3 install -r requirements.txt
# 启动后端
uvicorn main:app --host 0.0.0.0 --reload --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 3


echo ""
echo "✅ 服务已启动："
echo "   - 后端 API: http://localhost:8000"
echo "   - 后端文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
