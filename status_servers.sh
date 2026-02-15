#!/bin/bash

# 星座任务规划系统 - 查看服务状态脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  星座任务规划系统 - 服务状态${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查后端服务
echo -e "${YELLOW}后端服务 (FastAPI):${NC}"
if pgrep -f "uvicorn main:app" > /dev/null; then
    PID=$(pgrep -f "uvicorn main:app" | head -1)
    echo -e "  状态: ${GREEN}运行中${NC} (PID: $PID)"
    echo -e "  地址: ${GREEN}http://localhost:8000${NC}"
    echo -e "  文档: ${GREEN}http://localhost:8000/docs${NC}"
else
    echo -e "  状态: ${RED}未运行${NC}"
fi

echo ""

# 检查前端服务
echo -e "${YELLOW}前端服务 (Vite):${NC}"
if pgrep -f "vite" > /dev/null; then
    PID=$(pgrep -f "vite" | head -1)
    echo -e "  状态: ${GREEN}运行中${NC} (PID: $PID)"
    echo -e "  地址: ${GREEN}http://localhost:5173${NC}"
else
    echo -e "  状态: ${RED}未运行${NC}"
fi

echo ""

# 检查日志文件
echo -e "${YELLOW}日志文件:${NC}"
if [ -f "logs/backend.log" ]; then
    echo -e "  后端日志: logs/backend.log ($(wc -l < logs/backend.log) 行)"
else
    echo -e "  后端日志: ${RED}不存在${NC}"
fi

if [ -f "logs/frontend.log" ]; then
    echo -e "  前端日志: logs/frontend.log ($(wc -l < logs/frontend.log) 行)"
else
    echo -e "  前端日志: ${RED}不存在${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
