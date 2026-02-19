#!/bin/bash

# 星座任务规划系统 - 快速启动脚本
# 同时启动前端和后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  星座任务规划系统 - 启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 创建日志目录（如果不存在）
mkdir -p logs

# 检查后端依赖
echo -e "${YELLOW}[1/4] 检查后端正端依赖...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${RED}虚拟环境不存在，请先运行: python3 -m venv venv${NC}"
    exit 1
fi

# 启动后端
echo -e "${YELLOW}[2/4] 启动后端服务 (FastAPI)...${NC}"
if pgrep -f "uvicorn main:app" > /dev/null; then
    echo -e "${GREEN}后端服务已在运行${NC}"
else
    source venv/bin/activate
    cd web_interface/backend
    nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../../logs/backend.log 2>&1 &
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}后端服务已启动 (http://localhost:8000)${NC}"
    echo -e "${GREEN}后端日志: logs/backend.log${NC}"
fi

# 检查前端依赖
echo -e "${YELLOW}[3/4] 检查前端依赖...${NC}"
if [ ! -d "web_interface/frontend/node_modules" ]; then
    echo -e "${RED}前端依赖未安装，请先运行: cd web_interface/frontend && npm install${NC}"
    exit 1
fi

# 启动前端
echo -e "${YELLOW}[4/4] 启动前端服务 (Vite)...${NC}"
if pgrep -f "vite" > /dev/null; then
    echo -e "${GREEN}前端服务已在运行${NC}"
else
    cd web_interface/frontend
    nohup npm run dev > ../../logs/frontend.log 2>&1 &
    cd "$SCRIPT_DIR"
    echo -e "${GREEN}前端服务已启动 (http://localhost:5173)${NC}"
    echo -e "${GREEN}前端日志: logs/frontend.log${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已启动成功!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}访问地址:${NC}"
echo -e "  前端界面: ${YELLOW}http://localhost:5173${NC}"
echo -e "  后端API:  ${YELLOW}http://localhost:8000${NC}"
echo -e "  API文档:  ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}日志文件:${NC}"
echo -e "  后端: logs/backend.log"
echo -e "  前端: logs/frontend.log"
echo ""
echo -e "${BLUE}常用命令:${NC}"
echo -e "  停止服务: ${YELLOW}./stop_servers.sh${NC}"
echo -e "  查看状态: ${YELLOW}./status_servers.sh${NC}"
echo ""
