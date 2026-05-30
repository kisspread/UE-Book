# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于管理和同步资产包（Package）及其依赖关系的高级工具。它并非简单的文件复制，而是针对虚幻引擎资产的依赖图进行分析，旨在解决**团队协作**和**分布式生产**环境中的资产一致性问题。其核心是提供一套协议和驱动，让你能够安全地将一组特定资产及其所有依赖项“打包”为一个可传输的“风暴包”，并将其推送到目标位置（如网络共享、版本控制系统、云存储），或从目标位置拉取。它是 Epic 官方 **Motion Design** 工作流中推荐使用的工具，特别适用于处理大型、复杂的 Motion Design 项目，确保所有参与者和渲染节点拥有完全一致的资产环境。

## 模块列表

| 模块 | 一句话说明 |
|---|---|
| `StormSyncCore` | 核心逻辑，定义资产包（Storm Sync Package）的数据结构、依赖分析和序列化。 |
| `StormSyncDrives` | 抽象存储驱动层，提供对本地文件系统、网络共享、Pak 文件等不同存储位置的统一访问接口。 |
| `StormSyncEditor` | 编辑器集成，提供 UI 工具（如导出向导、状态浏览器）用于在编辑器内打包、管理和同步资产。 |
| `StormSyncImport` | 负责处理导入流程，将“风暴包”中的资产安全地导入到当前项目中。 |
| `StormSyncTransportClient` | 传输客户端，实现与传输服务器通信以执行实际的推/拉操作。 |
| `StormSyncTransportCore` | 传输核心，定义客户端与服务器之间的通信协议和消息格式。 |
| `StormSyncTransportServer` | 传输服务器，监听并响应来自客户端的同步请求，管理资产包的推送和拉取。 |
| `StormSyncTests` | 包含该插件的自动化测试用例。 |

## 使用场景

-   **团队协作**：多个设计师使用 Motion Design 工具制作大型场景，通过 StormSync 将相互依赖的资产包同步到共享服务器，确保每个人使用的素材版本完全一致。
-   **分布式渲染**：将渲染所需的资产包打包并同步到渲染农场的所有节点，避免因素材缺失或版本不一致导致的渲染失败。
-   **资产备份与迁移**：将一个项目的关键资产及其依赖项打包，用于备份或迁移到另一个项目或机器，无需手动追踪和拷贝所有文件。
-   **版本控制集成**：结合自定义驱动，可以将资产包推送到 Git LFS 或 Perforce 等版本控制系统，作为资产管理的一种方式。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)