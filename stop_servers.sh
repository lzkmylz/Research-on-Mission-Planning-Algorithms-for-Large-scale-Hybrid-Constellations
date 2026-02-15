#!/bin/bash

# 星座任务规划系统 - 停止服务脚本
# 停止前端和后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  星座任务规划系统 - 停止脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 停止后端服务
echo -e "${YELLOW}[1/2] 停止后端服务...${NC}"
if pgrep -f "uvicorn main:app" > /dev/null; then
    pkill -f "uvicorn main:app"
    echo -e "${GREEN}后端服务已停止${NC}"
else
    echo -e "${YELLOW}后端服务未运行${NC}"
fi

# 停止前端服务
echo -e "${YELLOW}[2/2] 停止前端服务...${NC}"
if pgrep -f "vite" > /dev/null; then
    pkill -f "vite"
    echo -e "${GREEN}前端服务已停止${NC}"
else
    echo -e "${YELLOW}前端服务未运行${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已停止!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
