package main

/**
本项目是一个基于 Go 语言实现的简单文件下载服务。用户可以通过 HTTP 接口下载 `test/cyc` 目录下的任意文件。

启动服务：
go run main.go

下载文件：
在浏览器中访问 http://<你的IP>:8080/download/<文件名>
*/

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	http.HandleFunc("/download/", func(w http.ResponseWriter, r *http.Request) {
		// 获取文件名
		fileName := r.URL.Path[len("/download/"):]
		if fileName == "" {
			http.Error(w, "文件名不能为空", http.StatusBadRequest)
			return
		}
		// 构建文件路径
		filePath := filepath.Join("cyc", fileName)
		// 检查文件是否存在
		if _, err := os.Stat(filePath); os.IsNotExist(err) {
			http.Error(w, "文件不存在", http.StatusNotFound)
			return
		}
		// 设置下载头
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"", fileName))
		w.Header().Set("Content-Type", "application/octet-stream")
		// 打印下载日志
		log.Printf("文件被下载: %s, 来自: %s", fileName, r.RemoteAddr)
		http.ServeFile(w, r, filePath)
	})

	fmt.Println("文件下载服务已启动: http://localhost:8080/download/<filename>")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
