# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产、测试资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个完整的资产同步框架，专为虚拟制作（Virtual Production）和 Motion Design 工作流设计。它解决的核心问题是：如何在多个 Unreal Engine 实例（如编辑器、渲染农场、实时渲染节点）之间高效、可靠地同步资产及其依赖关系。

它不仅仅是一个简单的文件复制工具，而是一个智能的同步系统，能够：
1.  **分析依赖**：自动解析资产（如材质、纹理、蓝图）的完整依赖树。
2.  **打包传输**：将资产及其依赖打包成一个自包含的 `.spak` 文件或内存缓冲区。
3.  **差异比较**：通过文件大小、时间戳和哈希值比较，只同步发生变化的文件。
4.  **网络同步**：通过内置的客户端-服务器架构，在局域网内发现设备并进行资产推送/拉取。
5.  **热重载**：在同步完成后，支持对修改的资产进行热重载，避免重启编辑器。

## 使用场景

-   **虚拟制片现场**：在 LED 墙渲染节点和主控编辑器之间同步实时更新的资产（如场景、材质、蓝图）。
-   **Motion Design 工作流**：在多个艺术家的工作站之间同步复杂的动态图形资产和依赖。
-   **分布式渲染**：将资产包推送到渲染农场的各个节点，确保所有节点使用完全一致的资产版本。
-   **资产备份与迁移**：将项目中的特定资产集（连同所有依赖）打包成一个文件，用于备份或迁移到另一个项目。

## 蓝图用法

StormSync 主要通过 `FStormSyncCoreUtils` 静态工具类和 `FStormSyncCoreDelegates` 委托系统在蓝图中暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Asset Data` | 根据包名获取资产数据及其依赖列表。 | `FStormSyncCoreUtils` |
| `Get Dependencies` | 递归获取一组包名的所有磁盘依赖。 | `FStormSyncCoreUtils` |
| `Create Pak Buffer` | 将一组资产及其依赖打包到内存缓冲区。 | `FStormSyncCoreUtils` |
| `Extract Pak Buffer` | 从内存缓冲区中提取资产到磁盘。 | `FStormSyncCoreUtils` |
| `Create Pak File` | 将资产包保存到本地 `.spak` 文件。 | `FStormSyncCoreUtils` |
| `Extract Pak File` | 从 `.spak` 文件中提取资产。 | `FStormSyncCoreUtils` |
| `On Pak Pre Extract` | 委托：在提取过程开始前触发。 | `FStormSyncCoreDelegates` |
| `On Pak Asset Extracted` | 委托：每提取一个资产后触发。 | `FStormSyncCoreDelegates` |

### 使用示例（蓝图描述）

1.  **打包资产**：
    -   创建一个 `TArray<FName>` 变量，填入要同步的资产包名（如 `/Game/MyAsset`）。
    -   调用 `Get Dependencies` 节点，输入该数组，获取完整的依赖列表。
    -   调用 `Create Pak Buffer` 节点，输入依赖列表，得到一个 `FStormSyncBufferPtr`。
    -   （可选）将缓冲区通过网络发送，或调用 `Create Pak File` 保存为文件。

2.  **提取资产**：
    -   从网络接收缓冲区，或从文件加载得到 `FStormSyncBufferPtr`。
    -   调用 `Extract Pak Buffer` 节点，输入缓冲区，资产将被提取到项目目录。
    -   绑定 `On Pak Asset Extracted` 委托以监控提取进度。

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncCoreUtils.h"
#include "StormSyncCoreDelegates.h"
#include "StormSyncPackageDescriptor.h"
```

### 基本用法

以下代码展示了如何获取资产依赖并创建一个 pak 缓冲区。
*（来源：基于 `StormSyncCoreUtils.h` 中的 API 设计和常见用法模式）*

```cpp
// 1. 定义要打包的资产列表
TArray<FName> PackageNamesToSync;
PackageNamesToSync.Add(FName(TEXT("/Game/Characters/Hero")));
PackageNamesToSync.Add(FName(TEXT("/Game/Weapons/Sword")));

// 2. 获取所有依赖（包括自身）
TArray<FName> AllDependencies;
FStormSyncCoreUtils::GetDependencies(PackageNamesToSync, AllDependencies);

// 3. 创建 pak 缓冲区
FStormSyncBufferPtr PakBuffer = FStormSyncCoreUtils::CreatePakBuffer(AllDependencies);
if (PakBuffer.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("Pak buffer created successfully. Size: %lld bytes"), PakBuffer->Num());
    // 此处可以将 PakBuffer 通过网络发送或保存到文件
}
```

### 进阶用法

使用委托系统来精细控制提取过程。
*（来源：基于 `FStormSyncCoreExtractArgs` 结构体的设计）*

```cpp
// 创建提取参数对象
FStormSyncCoreExtractArgs ExtractArgs;

// 注册委托以自定义提取行为
ExtractArgs.OnPakPreExtract.BindLambda([](int32 FileCount) {
    UE_LOG(LogTemp, Log, TEXT("Starting extraction of %d files..."), FileCount);
});

ExtractArgs.OnFileExtract.BindLambda([](const FStormSyncFileDependency& FileDep, FString DestPath, const FStormSyncBufferPtr& Buffer) {
    UE_LOG(LogTemp, Log, TEXT("Extracted: %s to %s"), *FileDep.PackageName.ToString(), *DestPath);
    // 可以在此处对单个文件的缓冲区进行额外处理
});

// 使用自定义参数进行提取
FStormSyncCoreUtils::ExtractPakBuffer(PakBuffer, ExtractArgs);
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何打包和提取资产。
*（注意：此示例假设在编辑器模块或游戏模块中运行，且 `StormSyncCore` 模块已正确依赖）*

**StormSyncDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FStormSyncDemo
{
public:
    /** 执行一个完整的打包和提取演示 */
    static void RunDemo();
};
```

**StormSyncDemo.cpp**
```cpp
#include "StormSyncDemo.h"
#include "StormSyncCoreUtils.h"
#include "StormSyncPackageDescriptor.h"
#include "Misc/FileHelper.h"

void FStormSyncDemo::RunDemo()
{
    // 1. 准备资产列表
    TArray<FName> Assets;
    Assets.Add(FName(TEXT("/Game/TestAsset")));

    // 2. 获取依赖
    TArray<FName> Dependencies;
    if (!FStormSyncCoreUtils::GetDependencies(Assets, Dependencies))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get dependencies."));
        return;
    }

    // 3. 创建内存中的 pak 缓冲区
    FStormSyncBufferPtr Buffer = FStormSyncCoreUtils::CreatePakBuffer(Dependencies);
    if (!Buffer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create pak buffer."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Created pak buffer with %d files, size: %lld bytes"), Dependencies.Num(), Buffer->Num());

    // 4. 将缓冲区保存到临时文件（模拟网络传输）
    FString TempFilePath = FPaths::ProjectSavedDir() / TEXT("TempSync.spak");
    FFileHelper::SaveArrayToFile(*Buffer, *TempFilePath);

    // 5. 从文件加载缓冲区（模拟接收）
    FStormSyncBufferPtr LoadedBuffer = MakeShared<FStormSyncBuffer, ESPMode::ThreadSafe>();
    FFileHelper::LoadFileToArray(*LoadedBuffer, *TempFilePath);

    // 6. 提取资产
    UE_LOG(LogTemp, Log, TEXT("Extracting assets from buffer..."));
    FStormSyncCoreUtils::ExtractPakBuffer(LoadedBuffer);

    UE_LOG(LogTemp, Log, TEXT("Demo completed. Check project content for extracted assets."));
}
```

## 模块依赖

从 `StormSyncCore.Build.cs` 分析，使用此插件（特别是 `StormSyncCore` 模块）需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `StormSyncTransportCore` | 提供网络传输的核心协议和消息定义。 |
| `Json` | 用于序列化和反序列化包描述符（`FStormSyncPackageDescriptor`）等元数据。 |
| `JsonUtilities` | 辅助 JSON 与 UObject/UStruct 之间的转换。 |
| `AssetRegistry` | 用于查询资产依赖关系（`GetDependencies` 功能的核心）。 |
| `PakFile` | 底层用于处理 `.pak` 文件格式的读写。 |

## 维护状态

### 近期更新

```
- 2024-01-28 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ... StormSync ...
```
*解读：这是将插件从实验性目录正式迁移到虚拟制作目录的提交，标志着插件被认为已足够稳定，适合生产环境使用。*

### 维护评价

-   **创建时间**：2024年1月，插件相对年轻。
-   **最近更新**：最近一次提交是目录迁移，没有功能性更新记录。这可能意味着插件在迁移后进入了稳定期，或者主要开发在内部进行。
-   **活跃度**：基于公开的 git 历史，近期没有活跃的功能开发或 bug 修复提交。
-   **状态**：插件已从“实验性”毕业，成为虚拟制作官方推荐工作流的一部分，表明其核心功能已稳定。
-   **推荐**：**推荐使用**。作为 Epic 官方推荐的 Motion Design 工作流组件，其设计目标和架构是可靠的。尽管近期公开更新不多，但作为已发布的官方插件，其稳定性和兼容性有保障。适合在虚拟制作项目中采用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)