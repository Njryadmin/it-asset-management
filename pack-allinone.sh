#!/bin/bash
# IT资产管理系统 All-in-One 打包脚本
# 打包所有镜像为一个文件

set -e

VERSION="v1.0.0-beta"
OUTPUT_DIR="/mnt/sda1/Downloads"
PACKAGE_NAME="it-asset-management-${VERSION}-allinone.tar.gz"

echo "=========================================="
echo "  IT资产管理系统 All-in-One 打包工具"
echo "=========================================="
echo ""

# 检查镜像是否存在
echo "检查镜像..."
IMAGES=(
    "it-asset-management-frontend:latest"
    "it-asset-management-backend:latest"
    "postgres:15-alpine"
    "redis:7-alpine"
)

for img in "${IMAGES[@]}"; do
    if ! docker image inspect "$img" > /dev/null 2>&1; then
        echo "镜像 $img 不存在，跳过..."
    else
        echo "✓ $img"
    fi
done

# 打包为单个文件
echo ""
echo "打包镜像到: $PACKAGE_NAME"

# 使用 docker save 打包所有镜像
IMAGES_TO_SAVE=()
for img in "${IMAGES[@]}"; do
    if docker image inspect "$img" > /dev/null 2>&1; then
        IMAGES_TO_SAVE+=("$img")
    fi
done

if [ ${#IMAGES_TO_SAVE[@]} -eq 0 ]; then
    echo "错误: 没有找到任何镜像"
    echo "请先运行: docker-compose build"
    exit 1
fi

# 打包
docker save "${IMAGES_TO_SAVE[@]}" | gzip > "$OUTPUT_DIR/$PACKAGE_NAME"

echo ""
echo "=========================================="
echo "  打包完成!"
echo "=========================================="
echo "文件: $OUTPUT_DIR/$PACKAGE_NAME"
echo "大小: $(ls -lh "$OUTPUT_DIR/$PACKAGE_NAME" | awk '{print $5}')"
echo ""
echo "在新机器上部署:"
echo "  gunzip < $PACKAGE_NAME | docker load"
echo "  docker-compose up -d"
echo "=========================================="
