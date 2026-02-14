#!/bin/bash
# 星座任务规划系统 - 后端启动脚本

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  星座任务规划系统 - 后端服务${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，使用默认配置"
    echo "   如需自定义配置，请复制 .env.example 到 .env"
else
    echo -e "${GREEN}✓${NC} 已加载 .env 配置文件"
fi

# 显示当前配置
echo ""
echo "数据库配置:"
echo "  主机: ${DB_HOST:-localhost}"
echo "  端口: ${DB_PORT:-3306}"
echo "  用户: ${DB_USER:-root}"
echo "  数据库: ${DB_NAME:-constellation_planning}"
echo ""

# 启动服务
echo -e "${BLUE}启动 FastAPI 服务...${NC}"
echo "  API地址: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
