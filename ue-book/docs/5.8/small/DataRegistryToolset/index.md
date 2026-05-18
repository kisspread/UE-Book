# Data Registry Toolset

> Toolset for querying and inspecting Data Registries（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据注册表工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DataRegistryToolset` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataRegistryToolset) | |

## 用途

该插件提供了一套命令行工具，专门用于在编辑器中查询、检查和调试 UE5 的 Data Registry 系统。Data Registry 是用于集中管理和动态加载游戏数据（如物品、技能、配置等）的框架。此工具集允许开发者快速查看所有注册表的概览信息、检查特定注册表或数据源的状态，从而解决数据加载、配置错误或性能问题。它不是运行时必需的功能，而是一个纯编辑器开发和调试辅助工具。

## 使用场景

- 你需要在编辑器中快速检查所有 Data Registry 的初始化状态和可用性。
- 你需要排查某个特定数据源（如曲线表、数据表资产）未正确加载到 Data Registry 中的问题。
- 你需要查看某个 Data Registry 中包含多少项数据，以及它所使用的 ID 格式。
- 你需要调试 Data Registry 的依赖和继承关系（通过查看父源信息）。

## 蓝图用法

此插件主要面向 C++ 和命令行用法，未发现公开的蓝图函数。

## C++ 用法

### 头文件引入

```cpp
#include "DataRegistryTools.h"
```

### 基本用法

此插件的典型用法是通过自定义的命令行或编辑器扩展来调用其内部工具函数。以下是一个虚构的示例，展示了如何在你自己的编辑器工具中集成 Data Registry 的查询功能。

```cpp
// 假设在一个编辑器工具类中
#include "DataRegistryTools.h"
#include "DataRegistrySubsystem.h"

void UMyEditorTools::QueryDataRegistries()
{
    // 1. 获取 DataRegistry 工具集提供的所有注册表信息
    TArray<FDataRegistryInfo> RegistryInfos;
    UDataRegistrySubsystem::Get()->GetAllRegistryInfo(/* 输出参数 */RegistryInfos);
    
    // 2. 遍历并打印基本信息
    for (const FDataRegistryInfo& Info : RegistryInfos)
    {
        UE_LOG(LogTemp, Log, TEXT("Registry: %s, Items: %d, Availability: %s"),
            *Info.RegistryName,
            Info.ItemCount,
            *UEnum::GetValueAsString(Info.Availability));
    }
}
```

### 进阶用法

查询特定数据源的详细信息，这对于调试数据加载链路很有用。

```cpp
void UMyEditorTools::InspectRegistrySource(const FName& RegistryName)
{
    // 假设我们有一个名为 “LootTable” 的注册表
    TArray<FDataRegistrySourceSummary> SourceSummaries;
    // 通过工具函数获取该注册表下所有数据源的摘要
    UDataRegistrySubsystem::Get()->GetSourceSummariesForRegistry(RegistryName, /* 输出参数 */SourceSummaries);
    
    for (const FDataRegistrySourceSummary& Summary : SourceSummaries)
    {
        UE_LOG(LogTemp, Log, TEXT("  Source Class: %s, Asset: %s, Initialized: %s"),
            Summary.SourceClass ? *Summary.SourceClass->GetName() : TEXT("None"),
            *Summary.SourceAssetPath.ToString(),
            Summary.bIsInitialized ? TEXT("True") : TEXT("False"));
            
        // 如果是临时子源，可以查看其父源
        if (Summary.bIsTransient && !Summary.ParentSourceDebugString.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("    Parent Source: %s"), *Summary.ParentSourceDebugString);
        }
    }
}
```

## Demo 示例

以下示例创建一个简单的编辑器控制台命令，用于打印所有数据注册表的摘要。这展示了如何在不创建完整编辑器 UI 的情况下利用工具集。

```cpp
// MyRegistryConsoleCommands.h
#pragma once
#include "CoreMinimal.h"
#include "DataRegistryTools.h"

class FMyRegistryConsoleCommands
{
public:
    static void RegisterConsoleCommands();
    
private:
    // 控制台命令处理函数
    static void OnListRegistries(const TArray<FString>& Args, UWorld* World, FOutputDevice& Ar);
};

// MyRegistryConsoleCommands.cpp
#include "MyRegistryConsoleCommands.h"
#include "DataRegistrySubsystem.h"
#include "HAL/IConsoleManager.h"

static FAutoConsoleCommandWithWorldAndArgs CmdListRegistries(
    TEXT("DR.ListRegistries"),
    TEXT("Lists all registered Data Registries and their info"),
    FConsoleCommandWithWorldAndArgsDelegate::CreateStatic(&FMyRegistryConsoleCommands::OnListRegistries)
);

void FMyRegistryConsoleCommands::OnListRegistries(const TArray<FString>& Args, UWorld* World, FOutputDevice& Ar)
{
    Ar.Logf(TEXT("=== Listing All Data Registries ==="));
    
    TArray<FDataRegistryInfo> AllInfos;
    // 注意：此处的 GetAllRegistryInfo 是示例函数名，实际 API 需参考源码
    if (UDRSubsystem* DRS = UDataRegistrySubsystem::Get())
    {
        // 实际的 API 可能有所不同，这里仅为逻辑演示
        // DRS->GetAllRegistryInfo(AllInfos);
        
        for (const FDataRegistryInfo& Info : AllInfos)
        {
            Ar.Logf(TEXT("  Name: %s | Items: %d | Struct: %s"),
                *Info.RegistryName,
                Info.ItemCount,
                Info.ItemStruct ? *Info.ItemStruct->GetName() : TEXT("None"));
        }
    }
    else
    {
        Ar.Logf(TEXT("Data Registry Subsystem not available."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 此插件仅依赖 `Core` 模块。其关键功能依赖于 `DataRegistry` 和 `ToolsetRegistry` 这两个**插件**，而非模块。 |

## 维护状态

### 近期更新

- 2026-04-28 `ffe59a83` Added toolsets for data registries. Current implemented commands include:
  *初始提交，添加了数据注册表的查询和检查工具集。*

### 维护评价

- **创建时间**: 2026-04-28（日期显示为未来时间，可能存在录入错误，但基于信息判断为新近创建的插件）。
- **最近更新**: 仅有一次提交，说明这是一个非常新的插件。
- **活跃状态**: 处于早期开发阶段，所有代码为初始提交。
- **已知限制**: 功能可能不完整，且作为 `Experimental` 和 `EditorOnly` 插件，其 API 和行为可能随版本发生重大变化。
- **是否推荐**: ✅ **推荐用于探索和内部工具开发**。不推荐在面向用户的正式产品中直接依赖此插件。适合希望提前了解或为 Data Registry 系统构建自定义调试工具的开发者。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataRegistryToolset)
- [官方文档](https://docs.unrealengine.com) (暂无专门文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/DataRegistryToolset/Tests) (未在源码信息中发现独立的测试文件)