# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、资产依赖配置） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是 Motion Design 工作流中的资产同步系统，解决的核心问题是：**如何在多台编辑器实例或多人协作之间高效地同步 Unreal 资产及其依赖关系**。

它提供了资产的打包（Export）、推送（Push）、拉取（Pull）能力，能够自动解析资产依赖图、检测文件差异（通过哈希和文件大小比较），并仅传输需要更新的部分。底层使用自定义的 `.spak`（Storm Sync Pak）归档格式来打包资产，支持从本地文件或网络缓冲区导入。

本文档聚焦于 **StormSyncImport** 模块——负责将 `.spak` 归档中的资产提取到本地项目的核心引擎。

### 模块架构

| 模块 | 职责 |
|---|---|
| `StormSyncCore` | 核心数据类型、归档格式、差异比较逻辑、委托定义 |
| `StormSyncImport` | **本文档重点** — 从归档中提取资产到本地项目 |
| `StormSyncEditor` | 编辑器 UI（导出向导、导入向导、资产详情面板等） |
| `StormSyncDrives` | 驱动器/存储抽象层 |
| `StormSyncTransportCore` | 传输协议核心（消息格式、会话管理） |
| `StormSyncTransportClient` | 传输客户端（连接服务器、发送请求） |
| `StormSyncTransportServer` | 传输服务器端（接收请求、广播资产） |
| `StormSyncTests` | 自动化测试 |

## 使用场景

- 你在团队中使用 Motion Design 制作虚拟制片内容 → 需要同步资产到其他工作站 → 用 StormSync Push/Pull
- 你有多台渲染节点需要保持资产一致 → 用 StormSync Transport 自动分发
- 你需要在 Game 模式下动态加载远程资产 → 用 `UStormSyncImportWorldSubsystem`
- 你需要构建自定义的资产导入管线 → 用 `UStormSyncImportSubsystem` 的任务队列机制

## 蓝图用法

StormSyncImport 模块以 C++ 子系统形式实现，主要面向程序化集成，不直接暴露蓝图节点。如需在蓝图中使用，请通过 `StormSyncEditor` 模块提供的编辑器蓝图接口进行调用。

## C++ 用法

### 头文件引入

```cpp
#include "Subsystems/StormSyncImportSubsystem.h"
```

### 基本用法 — 从文件导入

最简单的使用方式：给定一个 `.spak` 文件的绝对路径，执行导入。

```cpp
// 从本地 .spak 文件导入资产
// 来源: Subsystems/StormSyncImportSubsystem.h::PerformFileImport
FString PakFilePath = TEXT("C:/Exports/MyProject.stormsync.pak");
bool bSuccess = UStormSyncImportSubsystem::PerformFileImport(PakFilePath);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("资产导入成功"));
}
```

### 基本用法 — 从缓冲区导入

从内存中的归档数据导入资产，适用于网络传输场景。

```cpp
#include "Subsystems/StormSyncImportSubsystem.h"
#include "StormSyncCoreDelegates.h" // FStormSyncPackageDescriptor, FStormSyncArchivePtr

// 从内存缓冲区导入（例如从网络接收到的数据）
FStormSyncPackageDescriptor PackageDesc;
PackageDesc.PackageName = TEXT("MySyncPackage");
PackageDesc.Description = TEXT("从远程工作站推送的资产包");

FStormSyncArchivePtr Archive = /* 从网络或本地读取的归档数据 */;

bool bSuccess = UStormSyncImportSubsystem::PerformBufferImport(PackageDesc, Archive);
```

### 进阶用法 — 带选项的导入

使用 `PerformImport` 可以控制是否显示向导以及是否仅做干运行（不实际提取文件，仅输出日志）。

```cpp
// 干运行模式：仅解析并输出归档内容，不实际写入文件
// 来源: Subsystems/StormSyncImportSubsystem.h::PerformImport
FStormSyncPackageDescriptor PackageDesc;
FStormSyncArchivePtr Archive = /* ... */;

// bShowWizard = true  → 显示导入向导 UI
// bDryRun = true      → 仅解析，不提取
bool bSuccess = UStormSyncImportSubsystem::PerformImport(
    PackageDesc,
    Archive,
    /* bShowWizard */ true,
    /* bDryRun */ true
);
```

### 进阶用法 — 自定义导入任务

通过 `EnqueueImportTask` 提交自定义导入任务，子系统会在下一帧自动执行（防止重复排队）。

```cpp
#include "Tasks/IStormSyncImportTask.h"
#include "Subsystems/StormSyncImportSubsystem.h"

// 实现自定义导入任务接口
class FMyCustomImportTask : public IStormSyncImportSubsystemTask
{
public:
    virtual void Run() override
    {
        // 自定义导入逻辑
        UE_LOG(LogTemp, Log, TEXT("执行自定义导入任务"));
    }
};

// 提交任务（引擎子系统在下一 tick 执行）
UStormSyncImportSubsystem& ImportSubsystem = UStormSyncImportSubsystem::Get();
UWorld* World = GEditor->GetEditorWorldContext().World();

TSharedPtr<FMyCustomImportTask> Task = MakeShared<FMyCustomImportTask>();
bool bQueued = ImportSubsystem.EnqueueImportTask(Task, World);
// bQueued == false 说明已有待处理任务，本次被跳过
```

### 进阶用法 — Game 模式下的导入

`UStormSyncImportWorldSubsystem` 是一个 World 子系统，专为运行时（Game 模式）设计，通过注册 `FStormSyncCoreDelegates` 的委托来响应导入请求。

```cpp
#include "Subsystems/StormSyncImportWorldSubsystem.h"

// 在 Game 模式下，通过 World Subsystem 响应导入请求
UWorld* World = GetWorld();
UStormSyncImportWorldSubsystem* WorldImportSub = World->GetSubsystem<UStormSyncImportWorldSubsystem>();
if (WorldImportSub)
{
    // 从文件导入
    WorldImportSub->HandleImportFile(TEXT("/path/to/package.spak"));

    // 或从缓冲区导入
    FStormSyncPackageDescriptor Desc;
    FStormSyncArchivePtr Archive = /* ... */;
    WorldImportSub->HandleImportBuffer(Desc, Archive);
}
```

## Demo 示例

一个完整的最小示例：创建自定义导入任务并在编辑器中触发导入。

```cpp
// MyStormSyncImportExample.h
#pragma once

#include "CoreMinimal.h"
#include "Tasks/IStormSyncImportTask.h"

class FExampleImportTask : public IStormSyncImportSubsystemTask
{
public:
    explicit FExampleImportTask(const FString& InFilename)
        : Filename(InFilename)
    {
    }

    virtual void Run() override;

private:
    FString Filename;
};
```

```cpp
// MyStormSyncImportExample.cpp
#include "MyStormSyncImportExample.h"
#include "Subsystems/StormSyncImportSubsystem.h"

void FExampleImportTask::Run()
{
    UStormSyncImportSubsystem::PerformFileImport(Filename);
}

// 调用示例（在编辑器工具或自定义菜单项中）
void ExecuteStormSyncImport()
{
    UStormSyncImportSubsystem& Subsystem = UStormSyncImportSubsystem::Get();
    UWorld* World = GEditor->GetEditorWorldContext().World();

    auto Task = MakeShared<FExampleImportTask>(TEXT("C:/Exports/sync.spak"));
    Subsystem.EnqueueImportTask(Task, World);
}
```

## 模块依赖

> 注意：以下为 StormSyncImport 模块的依赖关系推断。完整 Build.cs 未提供，依赖基于源码中的 `#include` 和类型使用推导。

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心数据类型（`FStormSyncPackageDescriptor`、`FStormSyncArchivePtr`、`FStormSyncImportFileInfo`、`FStormSyncEditorFileReport`）、归档解析、差异比较、委托定义 |
| `AssetRegistry` | 资产数据查询（`FAssetData`）、资产注册与发现 |
| `AssetTools` | 资产编辑器操作（打开/关闭 Asset Editor） |
| `ObjectTools` | 资产删除工具（自定义覆盖版本 `DeleteAssets`） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复恶意 .spak 文件包含特定包名路径导致的安全漏洞 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导切换路径时创建大量嵌套文件夹的 UI 问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正之前批量查找替换导致的错误 |

### 维护评价

- **创建时间**：2025-05-09，约 1 年历史
- **近期活跃度**：活跃维护中，最近 3 个月内有多次功能性更新和安全修复
- **维护趋势**：
  - 2026-05 修复了安全漏洞（恶意 .spak 包名注入），说明 Epic 将其视为生产级工具
  - 持续进行代码现代化（UE_LOG → UE_LOGF 迁移、32/64 位格式修复）
  - UI 问题持续被修复，说明有活跃的用户群
- **推荐程度**：✅ 推荐使用。作为 Motion Design 工作流的官方推荐组件，有 Epic 持续维护，安全性问题被及时修复。但需注意 `Installed: false`，需手动在插件列表中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)