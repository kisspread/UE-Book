# RemoteSession

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例应用资源） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-03-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession) | |

## 用途

RemoteSession 提供了一套轻量级远程连接框架，允许一个 UE 实例作为"薄客户端"连接到另一个 UE 实例，前者负责渲染和输入转发，后者充当主服务器。

插件的核心架构基于**通道（Channel）**机制：服务器端和客户端各自维护多个 Channel（如输入、屏幕画面、AR 数据等），通过 WebSocket 协议进行通信。这种设计使得主实例可以将渲染画面推送到远程设备，同时接收远程设备的触摸/键盘输入回传。

插件解决的核心问题是：在移动设备等轻量端上运行高质量 UE 应用时，渲染算力不足的问题——通过将渲染卸载到桌面端，移动端仅作为显示和输入终端。

**注意**：该插件默认未启用（`EnabledByDefault: false`），需要手动在项目设置中启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `RemoteSession` | Runtime | 核心远程会话框架，包含连接管理、通道协议、输入/画面/AR 数据传输 |
| `RemoteSessionEditor` | Runtime | 编辑器扩展，提供远程会话管理面板和调试工具 |

详细 API 文档见各模块子页面：
- [RemoteSession.md](RemoteSession.md)
- [RemoteSessionEditor.md](RemoteSessionEditor.md)

## 使用场景

- **移动端串流应用**：在 iPhone/Android 上查看桌面端 UE 渲染的画面，仅需低算力设备即可体验高质量内容
- **远程设备测试**：开发者在桌面端运行编辑器/游戏，将画面推送到远程设备进行触控交互测试
- **AR 远程预览**：通过 ARChannel 传输 AR 跟踪数据，支持远程 AR 体验
- **多人调试会话**：一个开发者运行主实例，其他人通过薄客户端远程观察和交互

## 蓝图用法

RemoteSession 的核心功能通过 `FRemoteSessionModule` 的单例接口访问，蓝图层面主要通过编辑器工具和 C++ 暴露的工厂方法使用。

### 核心通道类型

| 通道 | 说明 |
|---|---|
| `IInputRemoteSessionChannel` | 接收/转发触屏、键盘、鼠标等输入事件 |
| `IScreenRemoteSessionChannel` | 管理远程渲染画面的传输与显示 |
| `IARRemoteSessionChannel` | 传输 AR 跟踪数据（相机姿态、锚点等） |

### 典型蓝图工作流

在蓝图中，RemoteSession 主要通过 C++ 端注册的服务端/客户端启动。编辑器中可通过 `Window > Developer Tools > Remote Session` 打开管理面板查看当前连接状态。

## C++ 用法

### 头文件引入

```cpp
#include "RemoteSession.h"
```

### 基本用法

```cpp
// 获取 RemoteSession 模块
FRemoteSessionModule& RemoteSessionModule = FModuleManager::GetModuleChecked<FRemoteSessionModule>("RemoteSession");

// 作为主机端启动，等待客户端连接
TSharedPtr<IRemoteSessionRole> Host = RemoteSessionModule.CreateHost(/* port */);

// 或作为客户端连接到主机
TSharedPtr<IRemoteSessionRole> Client = RemoteSessionModule.CreateClient(/* host address */);
```

*（基于模块公共接口推断，具体实现细节见子模块文档）*

### 进阶用法

自定义 Channel 通道：插件支持扩展自定义通道类型，通过 `IRemoteSessionChannelFactory` 注册新的通道处理器。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `92167537` | Support other analytics providers for RemoteSession | 支持更多第三方分析服务提供商 |
| 2026-05-12 | `1af5af49` | RemoteSession analytics | 为远程会话添加分析功能 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新版 UE_LOGF 格式 |
| 2026-04-13 | `fb2897b0` | IPv6 support for RemoteSession client and server | 客户端和服务端新增 IPv6 网络支持 |
| 2026-04-13 | `015f61a1` | Fixed a bunch of unreachable code warnings causing errors on some targets | 修复不可达代码警告导致的编译错误 |

### 维护评价

RemoteSession 从 2018 年创建至今约 8 年，一直处于 **Experimental** 分类且默认未启用。最近的提交（2026 年 5 月）显示该插件仍在持续维护，近期添加了 IPv6 支持和分析功能，说明 Epic 仍在投入资源。

但需要注意：
- 插件始终标记为实验性，API 可能随版本变动
- 长达 8 年未毕业到稳定分类，说明其适用场景相对小众
- 默认未启用，非开箱即用

**建议**：如果你需要 UE 的远程渲染/输入转发功能，这是一个可用的方案，但要做好应对 API 变化的准备。适合有远程串流或设备测试需求的项目使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RemoteSession)
- [官方文档]()（无）