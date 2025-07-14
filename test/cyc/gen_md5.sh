#!/bin/bash
# 提取 firmware.json 的 md5 值并保存到 firmware.md5
#
# 示例：
# ./gen_md5.sh

md5val=$(md5 -q firmware.json)
echo -n "$md5val" > firmware.md5
echo "已保存 firmware.json 的 md5 到 firmware.md5"
