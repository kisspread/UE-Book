# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、配置） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于虚拟制作（Virtual Production）工作流的资产依赖同步系统。它解决的核心问题是：在复杂的 Motion Design 项目中，如何确保不同机器、不同项目或不同艺术家之间，资产及其所有依赖项（如材质、纹理、蓝图等）能够被完整、准确地同步。

该插件提供了一套完整的客户端-服务器架构，支持资产的“拉取”（Pull）、“推送”（Push）和“同步”（Sync）操作，并能深入分析资产依赖关系，确保传输的完整性。它是 Epic Games 推荐的 Motion Design 工作流中的关键组成部分。

## 使用场景

-   **虚拟制片 LED 墙拍摄**：在 LED 墙工作站与渲染农场或资产服务器之间同步场景资产，确保所有机器使用完全一致的资产版本。
-   **团队协作**：多个艺术家在同一个 Motion Design 项目中工作时，通过中央服务器同步各自的资产更新，避免依赖冲突。
-   **资产迁移与备份**：将项目资产及其完整依赖关系打包、推送到网络驱动器或云存储，用于备份或迁移到其他工作站。
-   **自动化流水线集成**：在 CI/CD 流程中，自动同步构建所需的资产依赖。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| **StormSyncCore** | Runtime | 插件的核心逻辑，负责资产依赖分析、同步状态管理和操作调度。 |
| **StormSyncDrives** | Runtime | 提供对不同存储驱动器（如本地磁盘、网络共享）的抽象和访问接口。 |
| **StormSyncEditor** | Runtime | 编辑器集成模块，提供 UI 面板、资产操作菜单和编辑器内的同步工作流。 |
| **StormSyncImport** | Runtime | 处理从外部源（如服务器、驱动器）导入资产及其依赖的逻辑。 |
| **StormSyncTests** | Runtime | 包含插件的自动化测试用例，用于验证核心功能的正确性。 |
| **StormSyncTransportClient** | Runtime | 传输层的客户端实现，负责与 StormSync 服务器建立连接并发送同步请求。 |
| **StormSyncTransportCore** | Runtime | 传输层的核心协议和数据结构定义，供客户端和服务器模块共同使用。 |
| **StormSyncTransportServer** | Runtime | 传输层的服务器实现，负责监听客户端请求、管理资产仓库并处理同步操作。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)