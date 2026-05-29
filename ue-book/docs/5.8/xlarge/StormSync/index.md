# Storm Sync

> Sync, Pull, Push, asset dependencies. This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

Storm Sync 是一个用于在不同设备（工作站、服务器）或项目间同步、拉取和推送资产及其依赖关系的工具。它解决了在 Motion Design 等协作工作流中，如何高效、可靠地分发和更新复杂资产图（例如一个包含材质、纹理、蓝图和外部文件的资产包）的问题。其核心是生成包含资产依赖信息的清单（manifest），并基于此清单进行数据打包和分发，确保接收方能够完整地重建资产环境，而无需手动处理依赖。

## 使用场景

- **跨设备协作**：设计师在 A 工作站上完成了一套 Motion Design 资产，需要快速将完整包（包括所有引用）同步到 B 工作站或渲染农场节点。
- **版本管理与归档**：将某个项目的关键资产及其依赖关系打包为一个独立的 `.spak` 文件，用于存档或在不同项目间复用。
- **自动化流程集成**：在构建管道中，自动将最新的资产包推送到指定位置，供下游系统（如虚拟制片系统）消费。
- **资产依赖检查与清理**：在打包前分析并可视化资产的依赖树，避免遗漏。

## 蓝图用法

由于插件规模较大，蓝图 API 分布在多个模块中。以下是核心功能的概括：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSyncAction` | 创建一个同步操作，指定源和目标路径 | `UStormSyncActionFactory` |
| `ExecuteSync` | 执行一个配置好的同步操作 | `UStormSyncAction` |
| `ExportAssetDependencies` | 将指定资产及其依赖关系导出为清单或 `.spak` 包 | `UStormSyncExportUtils` |
| `ImportFromSpak` | 从一个 `.spak` 包文件导入资产 | `UStormSyncImportUtils` |
| `GetSyncStatus` | 查询当前同步操作的状态（成功、失败、进行中） | `UStormSyncStatus` |

**使用示例（蓝图描述）**：
一个典型的同步蓝图：使用 `CreateSyncAction` 节点，输入源资产路径和目标文件夹路径，然后连接到 `ExecuteSync` 节点。在 `ExecuteSync` 的输出引脚可以获取一个委托，用于监听同步完成或失败的事件。

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncActionFactory.h"
#include "StormSyncImportUtils.h"
```

### 基本用法

从测试用例中提取的同步工作流示例。

```cpp
// 来源：Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests/Tests/StormSyncAction.spec.cpp

// 创建同步动作
UStormSyncActionFactory* ActionFactory = NewObject<UStormSyncActionFactory>();
UStormSyncAction* SyncAction = ActionFactory->CreateSyncAction(SourcePath, DestPath);

// 绑定完成回调
SyncAction->OnSyncComplete.AddLambda([](bool bSuccess, const FString& Message) {
    UE_LOG(LogTemp, Log, TEXT("Sync completed: %s - %s"), bSuccess ? TEXT("Success") : TEXT("Failed"), *Message);
});

// 执行同步
SyncAction->Execute();
```

### 进阶用法

更复杂的用法，结合导出和导入。

```cpp
// 来源：Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncImport/Tests/StormSyncImportUtils.spec.cpp

// 准备资产清单
TArray<FAssetIdentifier> AssetsToExport;
AssetsToExport.Add(FAssetIdentifier(MyImportantAsset));

// 导出为 .spak 包
FString SpakFilePath = TEXT("/Game/Exports/MyAssetBundle.spak");
bool bExportSuccess = UStormSyncExportUtils::ExportToSpakFile(AssetsToExport, SpakFilePath);

if (bExportSuccess)
{
    // 在另一个位置导入
    TArray<UObject*> ImportedAssets = UStormSyncImportUtils::ImportFromSpakFile(SpakFilePath);
    // ... 处理导入的资产
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何使用 C++ 触发一个简单的同步操作。

**MySyncDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMySyncDemo
{
public:
    static void RunSimpleSync(const FString& SourceDir, const FString& DestDir);
};
```

**MySyncDemo.cpp**
```cpp
#include "MySyncDemo.h"
#include "StormSyncActionFactory.h"
#include "StormSyncAction.h"

void FMySyncDemo::RunSimpleSync(const FString& SourceDir, const FString& DestDir)
{
    UStormSyncActionFactory* Factory = NewObject<UStormSyncActionFactory>();
    if (UStormSyncAction* Action = Factory->CreateSyncAction(SourceDir, DestDir))
    {
        Action->OnSyncComplete.AddStatic([](bool bSuccess, const FString& Msg) {
            UE_LOG(LogTemp, Warning, TEXT("Sync Result: %s"), *Msg);
        });
        Action->Execute();
    }
}
```

## 模块依赖

为了使用此插件，你的模块通常需要依赖其核心模块。以下是除常见 Core/Engine 依赖外的独特模块。

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心同步逻辑、资产清单定义和操作 |
| `StormSyncDrives` | 驱动器映射与路径解析 |
| `StormSyncEditor` | 编辑器内的同步 UI 和工具 |
| `StormSyncImport` | `.spak` 包的导入功能 |
| `StormSyncTransportClient` | 用于将同步任务分发到远程客户端的客户端网络模块 |
| `StormSyncTransportCore` | 传输层的共享协议和数据结构 |
| `StormSyncTransportServer` | 接收并处理来自客户端同步任务的服务端网络模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa... | 修复安全漏洞，防止恶意 .spak 包通过包名路径进行攻击。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan... | 修复导出向导UI在切换路径时会创建大量嵌套文件夹的界面 bug。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化打印中，64位参数使用了32位格式说明符的问题，提升兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，可能是为了增强日志功能。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正一次错误的查找替换后的第二次尝试（修复代码问题）。 |

### 维护评价

**维护状态：活跃维护中**

- 创建时间很新（2025年5月），且是虚拟制片/动态设计工作流的核心组成部分。
- 近期（2026年内）有多次提交，包括**安全漏洞修复**、**UI 优化**和**代码质量改进**，表明 Epic 正在积极维护和加固此插件。
- 作为 Motion Design 工作流的推荐部分，其重要性较高，预计会持续更新。
- 尚无已知废弃标记。
- **强烈推荐**在涉及 Motion Design 或复杂资产同步的虚拟制片项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]() （暂无链接）