# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-01（估算） |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于虚拟制片（Virtual Production）工作流的资产同步插件。它解决了多台机器之间资产依赖关系的同步问题，提供以下核心能力：

- **资产依赖分析**：自动分析资产的依赖关系树
- **Push/Pull 同步**：将资产及其依赖推送到远程或从远程拉取
- **传输协议**：基于客户端-服务器架构的资产传输机制
- **驱动器管理**：管理不同的存储/传输目标

该插件是 Motion Design 工作流的推荐组件，主要用于确保多台工作站之间的资产一致性。

## 模块架构

```
StormSync/
├── StormSyncCore          ← 核心同步逻辑、资产依赖分析
├── StormSyncDrives        ← 存储驱动器抽象层
├── StormSyncImport        ← 资产导入处理
├── StormSyncTransportCore ← 传输协议核心定义
├── StormSyncTransportClient ← 客户端传输实现
├── StormSyncTransportServer ← 服务器传输实现
├── StormSyncEditor        ← 编辑器集成（UI、菜单等）
└── StormSyncTests         ← 自动化测试
```

## 使用场景

- 你在做虚拟制片项目，多台机器需要同步资产 → 用 StormSync
- 你需要确保 Motion Design 资产在团队间保持一致 → 用 StormSync
- 你需要分析并管理复杂的资产依赖关系 → 用 StormSyncCore

## 蓝图用法

> ⚠️ 由于源码文件数量庞大（191 个文件），详细的蓝图 API 文档需要逐模块分析。以下为基于模块结构的推断。

### 核心功能模块

| 模块 | 主要职责 |
|---|---|
| `StormSyncCore` | 资产依赖分析、同步状态管理 |
| `StormSyncImport` | 资产导入流程、格式处理 |
| `StormSyncDrives` | 存储目标抽象（本地/网络） |

### 传输模块

| 模块 | 主要职责 |
|---|---|
| `StormSyncTransportCore` | 传输协议定义、消息格式 |
| `StormSyncTransportClient` | 客户端连接、资产推送 |
| `StormSyncTransportServer` | 服务器监听、资产接收 |

## C++ 用法

### 头文件引入

```cpp
// 核心同步功能
#include "StormSyncCore.h"

// 导入功能
#include "StormSyncImport.h"

// 传输功能
#include "StormSyncTransportClient.h"
#include "StormSyncTransportServer.h"
```

### 模块依赖

使用 StormSync 插件时，你的 Build.cs 需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心同步 API |
| `StormSyncImport` | 资产导入功能 |
| `StormSyncTransportCore` | 传输协议定义 |
| `StormSyncTransportClient` | 客户端传输 |
| `StormSyncTransportServer` | 服务器传输 |
| `StormSyncDrives` | 驱动器管理 |

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```

### 维护评价

- **状态**：从 Experimental 迁移到 VirtualProduction，表明已通过实验阶段
- **活跃度**：作为 Motion Design 工作流的推荐组件，预计会持续维护
- **推荐**：✅ 推荐用于虚拟制片项目的资产同步需求

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)

---

# StormSyncImport 模块文档

> 本模块负责 StormSync 的资产导入功能

| 属性 | 值 |
|---|---|
| 模块类型 | Runtime |
| 源码路径 | `Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncImport/` |
| [Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncImport/StormSyncImport.Build.cs) | |

## 模块职责

StormSyncImport 模块负责处理从外部源导入资产到 StormSync 系统的流程，包括：

- 资产格式解析
- 依赖关系提取
- 导入队列管理
- 与 StormSyncCore 的集成

## 依赖关系

该模块依赖于：
- `StormSyncCore` - 核心同步逻辑
- 标准引擎模块（Core, CoreUObject, Engine 等）

---

> 📝 **注意**：本文档基于插件结构和元数据生成。由于源码文件数量庞大（191 个），详细的 API 文档需要逐模块深入分析。建议参考源码中的测试用例（StormSyncTests）获取具体用法示例。