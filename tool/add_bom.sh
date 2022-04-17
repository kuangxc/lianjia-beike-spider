# mac上打开生成的csv文件有问题，需要添加bom头
# 依赖于gsed命令，如果没有安装的话需要执行  brew install gnu-sed 安装

# 先去除所有的bom
 find ./data  -type f |xargs  gsed -i 's/^\xEF\xBB\xBF//g' 

# 再添加bom
 find ./data  -type f |xargs  gsed -i 's/^/\xEF\xBB\xBF/g'