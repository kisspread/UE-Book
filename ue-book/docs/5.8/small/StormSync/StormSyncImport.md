# Storm Sync Import

> Sync, Pull, Push, asset dependencies. This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步导入 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产同步工具） |
| 模块 | `StormSyncImport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSyncImport 是 StormSync 插件的核心资产导入模块，专门负责从 `.spak`（Storm Pak）归档文件中提取资产并导入到本地项目。

**解决的问题**：在虚拟制片/Motion Design 工作流中，多个制作站点需要同步资产。传统方式依赖源码控制或手动拷贝，效率低下且容易出错。StormSyncImport 提供了智能差异对比机制——它会自动比较传入文件与本地文件的哈希值/大小，只提取和更新发生变化的资产，避免不必要的重复导入。

**核心能力**：
- 从本地文件路径或内存缓冲区导入 Storm Pak 归档
- 智能差异检测：仅处理有变更的文件
- 处理资产编辑器状态：导入前自动关闭正在编辑的资产，导入后可重新打开
- 源码控制集成：自动 checkout 被覆盖的文件
- 热重载：导入后自动刷新已修改的包
- 支持向导模式和试运行（dry run）模式

## 使用场景

- 你在多个 Motion Design 工作站间需要同步资产 → 使用 StormSync 的导出/导入功能
- 你从网络请求或本地文件收到 `.spak` 包，需要提取到当前项目 → 使用 StormSyncImport
- 你需要在导入前预览哪些文件会被更改 → 使用 `PerformImport` 的 `bDryRun` 模式
- 你在游戏模式下需要处理资产同步请求 → 使用 `UStormSyncImportWorldSubsystem`

## 蓝图用法

该模块主要通过 C++ 子系统接口工作，`UStormSyncImportSubsystem` 是 `UEngineSubsystem`，提供静态便捷方法。以下为主要入口点：

### 核心节点

| 函数 | 说明 | 所在类 |
|---|---|---|
| `Get()` | 获取导入子系统单例 | `UStormSyncImportSubsystem` |
| `PerformFileImport()` | 从本地文件路径导入 .spak 包 | `UStormSyncImportSubsystem` |
| `PerformBufferImport()` | 从内存缓冲区导入 .spak 包 | `UStormSyncImportSubsystem` |
| `PerformImport()` | 执行导入（支持向导和试运行） | `UStormSyncImportSubsystem` |
| `EnqueueImportTask()` | 队列化导入任务（延迟到下一 tick） | `UStormSyncImportSubsystem` |

### 使用示例

基本导入流程：
1. 通过 `UStormSyncImportSubsystem::Get()` 获取子系统实例
2. 调用 `PerformFileImport(Filename)` 导入本地文件，或 `PerformBufferImport(Descriptor, Archive)` 导入缓冲区
3. 系统自动执行：解析 pak → 差异比较 → 关闭编辑器 → 提取文件 → 热重载

## C++ 用法

### 头文件引入

```cpp
#include "Subsystems/StormSyncImportSubsystem.h"
```

### 基本用法

**从文件路径导入**：

```cpp
// 简单的文件导入
FString PakFilePath = FPaths::ProjectDir() / TEXT("Exports/MyAssets.spak");
bool bSuccess = UStormSyncImportSubsystem::PerformFileImport(PakFilePath);
```

**从缓冲区导入**：

```cpp
// 从网络接收的缓冲区导入
FStormSyncPackageDescriptor PackageDescriptor;
PackageDescriptor.Name = TEXT("SyncedAssets");

FStormSyncArchivePtr Archive = /* 从网络或其他来源获取的归档 */;

bool bSuccess = UStormSyncImportSubsystem::PerformBufferImport(PackageDescriptor, Archive);
```

### 进阶用法

**带向导的导入（显示 UI 预览）**：

```cpp
// 显示导入向导，让用户确认后再执行
FStormSyncPackageDescriptor PackageDescriptor;
PackageDescriptor.Name = TEXT("MotionDesignSync");

FStormSyncArchivePtr Archive = /* ... */;

// bShowWizard = true 会弹出 UI 让用户查看差异
bool bSuccess = UStormSyncImportSubsystem::PerformImport(
    PackageDescriptor, 
    Archive, 
    true,  // bShowWizard
    false  // bDryRun
);
```

**试运行模式（只分析不执行）**：

```cpp
// 试运行：只输出日志，不实际提取文件
bool bSuccess = UStormSyncImportSubsystem::PerformImport(
    PackageDescriptor, 
    Archive, 
    false, // bShowWizard
    true   // bDryRun - 仅分析，不提取
);
```

**延迟任务队列**：

```cpp
// 创建任务并队列化（避免重复导入）
UStormSyncImportSubsystem& Subsystem = UStormSyncImportSubsystem::Get();

auto ImportTask = MakeShared<FStormSyncImportBufferTask>(PackageDescriptor, Archive);
bool bEnqueued = Subsystem.EnqueueImportTask(ImportTask, GetWorld());
// 任务将在下一 tick 自动执行
```

## Demo 示例

### 完整的资产同步导入器

```cpp
// MyAssetSyncManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "StormSyncImportSubsystem.h"
#include "MyAssetSyncManager.generated.h"

UCLASS()
class UMyAssetSyncManager : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    
    /** 从指定路径导入并报告结果 */
    UFUNCTION(BlueprintCallable, Category = "Asset Sync")
    bool ImportFromFile(const FString& InPakFilePath);
    
    /** 模拟从网络接收缓冲区导入 */
    UFUNCTION(BlueprintCallable, Category = "Asset Sync")
    bool ImportFromNetworkBuffer(const FString& InBufferName, const FStormSyncArchivePtr& InArchive);
    
    /** 试运行分析（不实际导入） */
    UFUNCTION(BlueprintCallable, Category = "Asset Sync")
    bool DryRunImport(const FString& InPakFilePath);

private:
    void OnImportCompleted(bool bSuccess, const FString& Source);
};
```

```cpp
// MyAssetSyncManager.cpp
#include "MyAssetSyncManager.h"
#include "StormSyncImportSubsystem.h"

void UMyAssetSyncManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("MyAssetSyncManager initialized"));
}

bool UMyAssetSyncManager::ImportFromFile(const FString& InPakFilePath)
{
    if (!FPaths::FileExists(InPakFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Pak file not found: %s"), *InPakFilePath);
        return false;
    }
    
    bool bSuccess = UStormSyncImportSubsystem::PerformFileImport(InPakFilePath);
    OnImportCompleted(bSuccess, InPakFilePath);
    
    return bSuccess;
}

bool UMyAssetSyncManager::ImportFromNetworkBuffer(const FString& InBufferName, const FStormSyncArchivePtr& InArchive)
{
    FStormSyncPackageDescriptor Descriptor;
    Descriptor.Name = InBufferName;
    
    bool bSuccess = UStormSyncImportSubsystem::PerformBufferImport(Descriptor, InArchive);
    OnImportCompleted(bSuccess, TEXT("Network Buffer: ") + InBufferName);
    
    return bSuccess;
}

bool UMyAssetSyncManager::DryRunImport(const FString& InPakFilePath)
{
    FStormSyncPackageDescriptor Descriptor;
    Descriptor.Name = FPaths::GetBaseFilename(InPakFilePath);
    
    // 创建一个简化的归档进行试运行
    // 实际实现需要解析文件创建归档
    FStormSyncArchivePtr Archive = /* ... */;
    
    // bShowWizard=false, bDryRun=true
    return UStormSyncImportSubsystem::PerformImport(Descriptor, Archive, false, true);
}

void UMyAssetSyncManager::OnImportCompleted(bool bSuccess, const FString& Source)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Import completed successfully from: %s"), *Source);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Import failed from: %s"), *Source);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心类型定义（FStormSyncPackageDescriptor, FStormSyncArchivePtr 等） |
| `AssetTools` | 资产编辑器操作（关闭/打开编辑器） |
| `SourceControl` | 源码控制集成（checkout 文件） |
| `UnrealEd` | 编辑器功能（资产删除、编辑器管理） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复安全漏洞：防止恶意 .spak 包利用包名进行攻击 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导 UI 创建大量嵌套文件夹的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化说明符的 32/64 位匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换后的二次修正 |

### 维护评价

- **活跃维护**：该插件在过去 6 个月内有多次实质性更新，包括安全漏洞修复和功能改进
- **安全意识**：2026-05-12 的安全漏洞修复表明 Epic 正在积极审查和加固该模块
- **Motion Design 核心组件**：作为 Motion Design 工作流的推荐组件，有持续的维护保障
- **建议**：✅ 推荐使用，特别是对于虚拟制片和 Motion Design 项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档](https://docs.unrealengine.com/)（无特定文档，属于 Motion Design 工作流一部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)