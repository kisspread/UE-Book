# RemoteSession

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession) | |

## 总体用途

RemoteSession 允许一个虚幻引擎实例作为薄客户端（仅负责渲染和输入），连接到另一个实例（主实例）进行远程控制。它基于 PixelStreaming 技术栈，提供低延迟的远程渲染和输入回传能力，适用于远程调试、多机协作、非量产环境下的快速预览等场景。插件包含运行时模块和编辑器模块，支持在编辑器中启动远程会话并管理连接。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `RemoteSession` | Runtime | 远程会话核心模块，实现信令连接、帧渲染传输、输入回传等运行时逻辑 |
| `RemoteSessionEditor` | Runtime | 编辑器扩展模块，提供会话启动/停止的 UI 和设置管理（在运行时模块中引入编辑器依赖） |

详情请参阅各模块文档：
- [RemoteSession 模块](RemoteSession.md)
- [RemoteSessionEditor 模块](RemoteSessionEditor.md)

## 使用场景

- 你在开发游戏或交互内容，需要在一台高性能机器上运行主实例，另一台设备（如平板、笔记本）作为薄客户端进行交互预览 → 使用 RemoteSession 实现远程控制与渲染回传
- 需要多人协作调试编辑器中的场景，不同人员可在各自机器上查看同一实例渲染的画面 → 通过 RemoteSession 的 PixelStreaming 集成实现
- 在非发行版环境中，快速测试客户端/服务器分离的远程渲染流程，无需打包 → 直接启用插件并启动会话

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession)
- [RemoteSession 模块文档](RemoteSession.md)
- [RemoteSessionEditor 模块文档](RemoteSessionEditor.md)