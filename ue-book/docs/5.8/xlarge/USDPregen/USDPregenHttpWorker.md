# USDPregen HTTP Worker

> Library to assist with pre-generating USD-based content.

| 属性 | 值 |
|---|---|
| 中文名 | USD 预生成 HTTP 工作进程 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `USDPregenHttpWorker` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Source/USDPregenHttpWorker) | |

## 用途

`USDPregenHttpWorker` 是 `USDPregen` 插件中的一个独立的“无头工作者”模块。它的主要职责是**通过 HTTP 接口接收指令，触发并执行基于 USD（Universal Scene Description）资产的预生成任务**。

它解决的核心问题是：允许**外部系统、脚本或命令行工具**远程驱动 UE 的 USD 导入和资产生成流程，而无需启动完整的编辑器界面。这使得将 USD 资产处理整合到自动化管线（如 CI/CD 流水线、渲染农场调度）成为可能。

## 使用场景

- **自动化资产管线**：在服务器或构建机器上，通过 HTTP 请求批量导入 USD 文件，并将其转换为 UE 的资产（如静态网格体、材质）。
- **远程触发与控制**：从其他微服务、Web 界面或运维脚本中，动态发起 USD 内容的预生成任务。
- **无头模式（Headless）渲染准备**：为大规模离线渲染准备资产，所有操作通过网络 API 控制，无需人工交互。

## 蓝图用法

此模块是一个底层的 `IModuleInterface`，主要用于程序化启动和关闭 HTTP 服务。其核心逻辑不通过蓝图直接暴露节点，而是通过模块的生命周期管理。

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图 API） | 该模块通过 `FModuleManager` 加载/卸载，不提供 `BlueprintCallable` 函数 | `FUSDPregenHttpWorkerModule` |

## C++ 用法

此模块的核心是 `FUSDPregenHttpWorkerModule` 类。你通常不需要直接实例化它，而是依赖 `FModuleManager` 来管理其生命周期。

### 头文件引入

```cpp
// 包含模块接口头文件，用于检查模块状态或加载模块
#include "USDPregenHttpWorkerModule.h"
```

### 基本用法

**启动与停止模块**
此模块作为 `IModuleInterface` 的实现，由引擎模块管理系统控制。

```cpp
// 检查模块是否已加载并处于活动状态
FModuleManager& ModuleManager = FModuleManager::Get();
bool bIsHttpWorkerActive = ModuleManager.IsModuleLoaded(TEXT("USDPregenHttpWorker"));

// 通常情况下，模块会随着包含它的插件一起自动加载。
// 如果你开发另一个依赖于此模块的插件，确保在你的 .uplugin 文件中声明依赖关系。
```

### 进阶用法

**自定义扩展**
由于 `FUSDPregenHttpWorkerModule` 使用了 `FHttpModule` 和 `FTicker`，其内部实现很可能包含一个持续运行的 HTTP 服务器（或定时轮询器）来监听请求。高级用户可能会：
1.  **修改监听端口或地址**：可能通过 `Engine.ini` 配置文件或模块启动参数。
2.  **注册新的 HTTP 路由/处理程序**：扩展其功能，以支持自定义的 USD 处理命令。
3.  **与 `UsdPregenCore` 模块协作**：接收请求后，调用核心模块的 API 执行实际的 USD 解析和资产生成逻辑。

**关键内部结构**
头文件中声明的 `TSharedPtr<FUSDPregenWorkerState>` 是该模块的核心状态容器，很可能封装了 HTTP 服务器实例、当前正在处理的任务队列以及 USD 操作的上下文信息。

## Demo 示例

这是一个最小的模块使用示例，展示如何在一个独立的编辑器工具模块中依赖并检查 `USDPregenHttpWorker` 的状态。

```cpp
// MyEdToolModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEdToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 检查 USD 预生成 HTTP 工作进程是否就绪 */
    bool IsUSDPregenWorkerReady() const;
};

// MyEdToolModule.cpp
#include "MyEdToolModule.h"
#include "USDPregenHttpWorkerModule.h" // 引入目标模块头文件

#define LOCTEXT_NAMESPACE "FMyEdToolModule"

void FMyEdToolModule::StartupModule()
{
    // 模块启动时的初始化
    UE_LOG(LogTemp, Log, TEXT("MyEdToolModule 已启动"));
}

void FMyEdToolModule::ShutdownModule()
{
    // 清理资源
}

bool FMyEdToolModule::IsUSDPregenWorkerReady() const
{
    // 使用 FModuleManager 检查 USDPregenHttpWorker 模块是否已加载
    return FModuleManager::Get().IsModuleLoaded(TEXT("USDPregenHttpWorker"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEdToolModule, MyEdTool)
```

## 模块依赖

从 `USDPregenHttpWorker.Build.cs` 分析，此模块的核心依赖如下（已省略 `Core`, `Engine` 等常见基础模块）：

| 模块 | 用途 |
|---|---|
| `HTTP` (Runtime) | 提供 HTTP 请求和响应的基础功能，用于搭建或访问内部 HTTP 服务 |
| `USDPregenCore` (Runtime) | 核心业务逻辑模块，提供 USD 文件的解析、处理和资产生成能力。`HttpWorker` 可能是它的客户端或触发器 |
| `Json` (Runtime) | 用于序列化和反序列化 HTTP 请求与响应中的 JSON 数据 |

*注：此模块还可能依赖 `UnrealUSDWrapper` 或 `Usd` 等更底层的 USD SDK 封装模块，具体取决于其内部实现对 USD 库的调用方式。*

## 维护状态

### 近期更新

```
- 2026-05-14 `9e86e007` [USD] UsdPregen: Fixes regression introduced by recent clean up, where an item can get incorrectly p... (修复近期清理导致的回归，物品可能被错误处理的问题)
- 2026-05-14 `ddc18470` [USD] UsdPregen: On definition conflicts during registry population, return the existing definition (在注册表填充时遇到定义冲突，返回现有定义)
- 2026-05-14 `60206a86` USD Pregen: Batch renaming for consistency. Also changes the default storage plugin in UE to the UOb... (为保持一致性进行批量重命名。同时将UE中的默认存储插件更改为UObject存储)
- 2026-05-14 `bad2257d` USD Pregen: User-configurable template string with placeholders for determining asset path; (用户可配置的模板字符串，使用占位符来确定资产路径)
- 2026-05-14 `9f286b30` USD Pregen: Fix _VT and _NonVT textures not being saved from worker imports. (修复从工作进程导入时，VT和NonVT纹理未被保存的问题)
```

### 维护评价

1.  **活动状态**：**活跃开发中**。所有近期提交均来自同一天，表明该模块正处于密集的开发和调试阶段。
2.  **成熟度**：**实验性/测试版**（`.uplugin` 中 `IsBetaVersion=true`, `IsExperimentalVersion=true`）。这表示其 API 和功能可能会发生重大变化，不建议在生产环境的稳定项目中直接使用。
3.  **稳定性**：从提交信息看，仍在处理回归 bug 和进行重构，因此当前稳定性可能不高。
4.  **推荐建议**：如果你正在评估或研究 Epic 对 USD 资产管线自动化的新方案，可以关注此模块。但**不推荐**直接用于需要长期稳定的生产项目中。适合在实验性分支、研究项目或学习 Epic 内部开发实践时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/USDPregen/Source/USDPregenHttpWorker)
- [官方文档]() （暂无）
- [测试用例]() （需在 `Engine/Tests/` 或插件目录内进一步查找）