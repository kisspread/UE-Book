# Android File Server

> Adds support for remote file management to Android projects.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓文件服务器 |
| 分类 | Android |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidFileServer` (Runtime), `AndroidFileServerEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-02-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer) | |

## 用途

为 Android 平台提供远程文件管理能力。该插件在 Android 设备上运行一个文件服务器，允许开发主机通过网络直接向设备推送/拉取文件，替代传统的 ADB 文件传输方式。主要用于加速 Android 项目的部署和安装流程，解决了 ADB 传输速度慢、连接不稳定等痛点。

核心功能包括：
- 在 Android 设备上运行文件服务器进程
- 从开发主机远程管理设备文件系统（上传、下载、删除）
- 集成到 UE5 的打包部署流程中，自动推送构建产物到设备
- 支持压缩文件传输以提升速度

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AndroidFileServer` | Runtime | 运行时模块，在 Android 设备上运行文件服务器，处理文件传输和管理请求 |
| `AndroidFileServerEditor` | Editor | 编辑器模块，提供将文件服务器推送到设备的工具集成，以及相关编辑器设置 |

## 使用场景

- 你在为 Android 平台开发 UE5 项目，希望加快迭代速度 → 使用本插件替代 ADB 进行文件部署
- 你需要频繁将构建产物推送到测试设备 → 自动集成到部署流程，无需手动 adb push
- 你需要远程管理 Android 设备上的项目文件 → 通过文件服务器直接操作设备文件系统

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidFileServer)
- 模块详细文档：[AndroidFileServer](AndroidFileServer.md) | [AndroidFileServerEditor](AndroidFileServerEditor.md)