# cyc_firmware

本项目用于管理和分发 CYC 相关固件文件，包含不同型号和版本的固件二进制文件、校验信息及相关工具。

## 目录说明

- `cyc/`：**生产目录**, 存放主固件文件及其校验信息。
  - `firmware.json`：固件的所有信息。
  - `firmware.md5`：固件信息文件的 MD5 校验值。
  - `*.bin`：不同型号和版本的固件二进制文件。
  - `*.json`：不同型号和版本固件的更新信息。
- test：**测试目录**, 相关代码与固件。
  - `main.go`：Go 语言测试主程序，运行程序后可在本地测试。
  - `gen_md5.sh`：用于生成 MD5 校验脚本， 运行：`bash gen_md5.sh`。
  - `cyc/`：测试固件及校验文件，和生产环境的内容相同。

## 注意事项

- 本项目支持`生产环境`、`线上测试`和 `本地测试`
- 修改 `firmware.json` 后一定要同步修改 `firmware.md5`
- `firmware.json`文件中的 `content` 字段，以 `## ` 开头表示标题，否则表示普通本文