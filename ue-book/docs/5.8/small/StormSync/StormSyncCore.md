# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、内容资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于**多个 Unreal Engine 实例之间同步资产依赖**的插件，主要服务于 Motion Design（运动设计）工作流。

它解决的核心问题是：在虚拟制片场景中，多个编辑器实例（或不同机器上的工作站）需要保持资产的同步状态。StormSync 通过以下方式实现：

1. **资产依赖解析**：递归分析 `.uasset` 包的依赖关系，生成完整的文件依赖树
2. **自定义 .spak 打包格式**：将资产及其依赖打包为 `.spak` 缓冲区（内存归档），便于网络传输
3. **差异比较**：通过文件大小和 MD5 哈希值对比本地与远程资产状态，自动判断需要新增、覆盖或已缺失的文件
4. **网络传输**：基于消息总线（Message Bus）的客户端/服务器架构，支持实时的资产推送和拉取
5. **服务发现**：自动发现局域网内运行 StormSync 服务的其他引擎实例，跟踪连接状态

该插件从 `/Plugins/Experimental` 迁移到 `/Plugins/VirtualProduction`，表明已成为 Motion Design 工作流的正式推荐组件。

## 使用场景

- **多机协作虚拟制片**：多台工作站同步同一项目的资产，确保画面内容一致
- **Motion Design 迭代**：在 Motion Design 工作流中，资产频繁修改，需要快速同步到其他实例
- **远程资产分发**：将特定资产包（.spak）发送给远程团队，自动处理依赖关系
- **版本对齐**：通过哈希比对快速识别哪些文件需要更新，避免全量传输

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| `StormSyncCore` | Runtime | 核心功能：依赖解析、pak 打包/解包、差异比较、设置 |
| `StormSyncDrives` | Runtime | 驱动器相关功能 |
| `StormSyncEditor` | Runtime | 编辑器集成（UI、向导、操作菜单） |
| `StormSyncImport` | Runtime | 导入处理逻辑 |
| `StormSyncTests` | Runtime | 自动化测试 |
| `StormSyncTransportClient` | Runtime | 网络客户端（发送资产） |
| `StormSyncTransportCore` | Runtime | 传输层核心（消息定义、共享类型） |
| `StormSyncTransportServer` | Runtime | 网络服务器（接收资产） |

---

# StormSyncCore 模块文档

StormSyncCore 是整个 StormSync 插件的核心运行时模块，负责资产依赖解析、.spak 缓冲区创建与解包、文件差异比较以及项目设置管理。

## 蓝图用法

StormSyncCore 主要通过委托（Delegate）和静态工具类提供 C++ 接口。以下是从源码提取的核心蓝图可访问类型：

### 核心类型

| 类型 | 说明 |
|---|---|
| `FStormSyncPackageDescriptor` | 包描述符，包含包名、版本、作者、描述及文件依赖列表 |
| `FStormSyncFileDependency` | 文件依赖信息，包含包名、文件大小、时间戳、MD5 哈希 |
| `FStormSyncFileModifierInfo` | 同步修改信息，包含操作类型（新增/覆盖/缺失）和文件依赖 |
| `EStormSyncModifierOperation` | 修改操作枚举：`Addition`（新增）、`Missing`（缺失）、`Overwrite`（覆盖） |
| `EStormSyncConnectedDeviceState` | 连接设备状态：`State_Active`、`State_Unresponsive`、`State_Disconnected` |
| `EStormSyncEngineType` | 引擎实例类型：Server / Commandlet / Editor / Game / Other / Unknown |
| `FStormSyncConnectedDevice` | 连接设备信息持有结构体 |

### 核心委托

| 委托 | 参数 | 说明 |
|---|---|---|
| `OnRequestImportBuffer` | `FStormSyncPackageDescriptor`, `FStormSyncArchivePtr` | 收到网络导入缓冲区时触发 |
| `OnRequestImportFile` | `FString` | 通过内容浏览器导入 .spak 文件时触发 |
| `OnFileImported` | `FString` | 文件导入完成时触发 |
| `OnPakAssetExtracted` | `FName`, `FString` | 从 pak 中提取单个资产时触发 |
| `OnPreStartSendingBuffer` | `FString`, `FString`, `int32` | 客户端即将开始发送缓冲区前触发 |
| `OnStartSendingBuffer` | `FString`, `int32` | 客户端开始发送缓冲区时触发 |
| `OnReceivingBytes` | `FString`, `int32` | 客户端收到服务端字节接收确认时触发 |
| `OnTransferComplete` | `FString` | 传输完成时触发 |
| `OnServiceDiscoveryConnection` | `FString`, `FStormSyncConnectedDevice` | 发现新连接时触发 |
| `OnServiceDiscoveryStateChange` | `FString`, `EStormSyncConnectedDeviceState` | 连接状态变化时触发 |
| `OnServiceDiscoveryDisconnection` | `FString` | 连接断开时触发 |
| `OnStormSyncServerStarted` | 无 | 服务端启动时触发 |
| `OnStormSyncServerStopped` | 无 | 服务端停止时触发 |

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncCoreUtils.h"
#include "StormSyncPackageDescriptor.h"
#include "StormSyncCoreDelegates.h"
#include "StormSyncCoreSettings.h"
```

### 基本用法：获取资产依赖

```cpp
// 来源: Public/StormSyncCoreUtils.h

// 获取单个包名的资产数据和依赖
TArray<FAssetData> Assets;
TArray<FName> Dependencies;
bool bSuccess = FStormSyncCoreUtils::GetAssetData(
    TEXT("/Game/MyAsset"), Assets, Dependencies
);

// 获取多个包名的递归依赖列表（扁平化、字母排序）
TArray<FName> PackageNames = { TEXT("/Game/MyAsset"), TEXT("/Game/AnotherAsset") };
TArray<FName> AllDependencies;
FText ErrorText;
bool bSuccess = FStormSyncCoreUtils::GetDependenciesForPackages(
    PackageNames, AllDependencies, ErrorText
);
```

### 基本用法：创建 Pak 缓冲区

```cpp
// 来源: Public/StormSyncCoreUtils.h

// 创建包含递归依赖的 pak 缓冲区
TArray<FName> PackageNames = { TEXT("/Game/MotionDesign/Scene") };
TArray<uint8> Buffer;
FMemoryWriter Writer(Buffer);
FText ErrorText;

// 自定义回调：追踪每个被添加的文件
FStormSyncCoreUtils::FOnFileAdded OnFileAdded;
OnFileAdded.BindLambda([](const FStormSyncFileDependency& FileDep)
{
    UE_LOG(LogStormSyncCore, Log, TEXT("Added: %s (Size: %llu)"),
        *FileDep.PackageName.ToString(), FileDep.FileSize);
});

bool bSuccess = FStormSyncCoreUtils::CreatePakBufferWithDependencies(
    PackageNames, Writer, ErrorText, OnFileAdded
);

// 不查找递归依赖的简化版本
bool bSuccess = FStormSyncCoreUtils::CreatePakBuffer(
    PackageNames, Writer, ErrorText, OnFileAdded
);
```

### 基本用法：解包 Pak 缓冲区

```cpp
// 来源: Public/StormSyncCoreUtils.h, Public/StormSyncPackageDescriptor.h

// 从缓冲区解包资产到当前项目
FMemoryReader Reader(Buffer);
FStormSyncCoreExtractArgs ExtractArgs;
TArray<FText> Errors;

// 注册提取过程中的委托
ExtractArgs.OnPakPreExtract.BindLambda([](int32 FileCount)
{
    UE_LOG(LogStormSyncCore, Log, TEXT("开始提取 %d 个文件"), FileCount);
});

ExtractArgs.OnPakPostExtract.BindLambda([](int32 FileCount)
{
    UE_LOG(LogStormSyncCore, Log, TEXT("完成提取 %d 个文件"), FileCount);
});

ExtractArgs.OnFileExtract.BindLambda(
    [](const FStormSyncFileDependency& FileDep, FString DestPath, const FStormSyncBufferPtr& Buffer)
{
    UE_LOG(LogStormSyncCore, Log, TEXT("提取文件: %s -> %s"),
        *FileDep.PackageName.ToString(), *DestPath);
});

bool bSuccess = FStormSyncCoreUtils::ExtractPakBuffer(Reader, ExtractArgs, Errors);
```

### 进阶用法：差异比较与同步

```cpp
// 来源: Public/StormSyncCoreUtils.h

// 比较本地和远程依赖，找出需要同步的文件
TArray<FName> LocalPackageNames = { TEXT("/Game/MyScene") };
TArray<FStormSyncFileDependency> RemoteDependencies; // 从远程实例获取

TArray<FStormSyncFileModifierInfo> Modifiers =
    FStormSyncCoreUtils::GetSyncFileModifiers(LocalPackageNames, RemoteDependencies);

for (const FStormSyncFileModifierInfo& Modifier : Modifiers)
{
    switch (Modifier.ModifierOperation)
    {
    case EStormSyncModifierOperation::Addition:
        UE_LOG(LogStormSyncCore, Log, TEXT("需要新增: %s"),
            *Modifier.FileDependency.PackageName.ToString());
        break;
    case EStormSyncModifierOperation::Overwrite:
        UE_LOG(LogStormSyncCore, Log, TEXT("需要覆盖: %s"),
            *Modifier.FileDependency.PackageName.ToString());
        break;
    case EStormSyncModifierOperation::Missing:
        UE_LOG(LogStormSyncCore, Log, TEXT("远程缺失: %s"),
            *Modifier.FileDependency.PackageName.ToString());
        break;
    }
}
```

### 进阶用法：异步获取文件依赖

```cpp
// 来源: Public/StormSyncCoreUtils.h

// 异步获取文件依赖信息，避免阻塞主线程
TArray<FName> PackageNames = { TEXT("/Game/LargeScene") };
TFuture<TArray<FStormSyncFileDependency>> Future =
    FStormSyncCoreUtils::GetAvaFileDependenciesAsync(PackageNames);

// 在回调中处理结果
Future.Then([](TFuture<TArray<FStormSyncFileDependency>> Result)
{
    TArray<FStormSyncFileDependency> Dependencies = Result.Get();
    for (const FStormSyncFileDependency& Dep : Dependencies)
    {
        UE_LOG(LogStormSyncCore, Log, TEXT("依赖: %s | 大小: %llu | 哈希: %s"),
            *Dep.PackageName.ToString(), Dep.FileSize, *Dep.FileHash);
    }
});
```

### 进阶用法：监听网络连接事件

```cpp
// 来源: Public/StormSyncCoreDelegates.h

// 监听服务发现事件
FStormSyncCoreDelegates::OnServiceDiscoveryConnection.AddLambda(
    [](const FString& MessageBusId, const FStormSyncConnectedDevice& Device)
{
    UE_LOG(LogStormSyncCore, Log, TEXT("发现新设备: %s (项目: %s)"),
        *Device.HostName, *Device.ProjectName);
});

FStormSyncCoreDelegates::OnServiceDiscoveryStateChange.AddLambda(
    [](const FString& MessageBusId, EStormSyncConnectedDeviceState State)
{
    // State_Active, State_Unresponsive, State_Disconnected
});

FStormSyncCoreDelegates::OnServiceDiscoveryDisconnection.AddLambda(
    [](const FString& MessageBusId)
{
    UE_LOG(LogStormSyncCore, Warning, TEXT("设备断开: %s"), *MessageBusId);
});

// 监听服务端启停
FStormSyncCoreDelegates::OnStormSyncServerStarted.AddLambda([]
{
    UE_LOG(LogStormSyncCore, Log, TEXT("Storm Sync 服务器已启动"));
});
```

## Demo 示例

### 获取资产依赖并打印信息

```cpp
// StormSyncDemo.h
#pragma once

#include "CoreMinimal.h"

class FStormSyncDemo
{
public:
    /** 分析指定包的完整依赖链并打印结果 */
    static void AnalyzePackageDependencies(const FName& InPackageName);

    /** 创建 .spak 缓冲区并保存到文件 */
    static bool ExportPackageToSpak(const TArray<FName>& InPackageNames, const FString& InOutputPath);

    /** 比较本地和远程状态并报告差异 */
    static void ReportSyncDifferences(
        const TArray<FName>& InLocalPackages,
        const TArray<FStormSyncFileDependency>& InRemoteDependencies
    );
};
```

```cpp
// StormSyncDemo.cpp
#include "StormSyncDemo.h"
#include "StormSyncCoreUtils.h"
#include "StormSyncPackageDescriptor.h"

void FStormSyncDemo::AnalyzePackageDependencies(const FName& InPackageName)
{
    TArray<FName> PackageNames = { InPackageName };
    TArray<FStormSyncFileDependency> FileDependencies;
    FText ErrorText;

    bool bSuccess = FStormSyncCoreUtils::GetAvaFileDependenciesForPackages(
        PackageNames, FileDependencies, ErrorText
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("=== 依赖分析: %s ==="), *InPackageName.ToString());
        UE_LOG(LogTemp, Log, TEXT("共 %d 个依赖文件:"), FileDependencies.Num());

        for (const FStormSyncFileDependency& Dep : FileDependencies)
        {
            UE_LOG(LogTemp, Log, TEXT("  %s | 大小: %s | 哈希: %s"),
                *Dep.PackageName.ToString(),
                *FStormSyncCoreUtils::GetHumanReadableByteSize(Dep.FileSize),
                *Dep.FileHash);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("依赖分析失败: %s"), *ErrorText.ToString());
    }
}

bool FStormSyncDemo::ExportPackageToSpak(
    const TArray<FName>& InPackageNames,
    const FString& InOutputPath)
{
    TArray<uint8> Buffer;
    FMemoryWriter Writer(Buffer);
    FText ErrorText;

    bool bSuccess = FStormSyncCoreUtils::CreatePakBufferWithDependencies(
        InPackageNames, Writer, ErrorText
    );

    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Pak 创建失败: %s"), *ErrorText.ToString());
        return false;
    }

    // 将缓冲区写入文件
    bool bFileSuccess = FFileHelper::SaveArrayToFile(Buffer, *InOutputPath);
    if (bFileSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("导出成功: %s (%s)"),
            *InOutputPath,
            *FStormSyncCoreUtils::GetHumanReadableByteSize(Buffer.Num()));
    }

    return bFileSuccess;
}

void FStormSyncDemo::ReportSyncDifferences(
    const TArray<FName>& InLocalPackages,
    const TArray<FStormSyncFileDependency>& InRemoteDependencies)
{
    TArray<FStormSyncFileModifierInfo> Modifiers =
        FStormSyncCoreUtils::GetSyncFileModifiers(InLocalPackages, InRemoteDependencies);

    UE_LOG(LogTemp, Log, TEXT("=== 同步差异报告 ==="));
    UE_LOG(LogTemp, Log, TEXT("需要操作的文件: %d"), Modifiers.Num());

    int32 Additions = 0, Overwrites = 0, Missing = 0;
    for (const FStormSyncFileModifierInfo& Mod : Modifiers)
    {
        switch (Mod.ModifierOperation)
        {
        case EStormSyncModifierOperation::Addition:
            UE_LOG(LogTemp, Log, TEXT("  [新增] %s"), *Mod.FileDependency.PackageName.ToString());
            ++Additions;
            break;
        case EStormSyncModifierOperation::Overwrite:
            UE_LOG(LogTemp, Log, TEXT("  [覆盖] %s"), *Mod.FileDependency.PackageName.ToString());
            ++Overwrites;
            break;
        case EStormSyncModifierOperation::Missing:
            UE_LOG(LogTemp, Log, TEXT("  [缺失] %s"), *Mod.FileDependency.PackageName.ToString());
            ++Missing;
            break;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("合计: 新增 %d, 覆盖 %d, 远程缺失 %d"),
        Additions, Overwrites, Missing);
}
```

## 模块依赖

从 StormSyncCore 的 Build.cs 及头文件推断，以下是该模块**独特**的依赖关系：

| 模块 | 用途 |
|---|---|
| `StormSyncTransportCore` | 传输层核心类型定义（消息、网络协议） |
| `MessageBus` | 引擎消息总线，用于服务发现和跨进程通信 |
| `Networking` | TCP 网络传输支持 |

## 项目设置

通过 **Project Settings → Plugins → Storm Sync → Core Settings** 配置（`UStormSyncCoreSettings`）：

| 设置 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExportOnlyGameContent` | bool | `true` | 导出时仅包含 `/Game` 目录下的包 |
| `bFilterInvalidReferences` | bool | `true` | 过滤掉无效引用（本地不存在的文件），避免导出错误 |
| `IgnoredPackages` | TSet\<FName\> | 空 | 忽略的包名列表（前缀匹配），如 `/SomePlugin` |
| `ExportDefaultNameFormatString` | FString | - | 导出文件名的日期时间格式字符串 |
| `bEnableHotReloadPackages` | bool | `true` | 同步操作后启用包热重载，避免临时无效状态传播 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复安全漏洞：恶意 .spak 文件可包含特定包名路径进行攻击 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复导出向导 UI 在切换路径时创建大量嵌套文件夹的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数类型不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 宏 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次批量替换导致的错误 |

### 维护评价

- **状态**：**活跃维护中**
- 创建于 2025 年 5 月，至今约 1 年，属于较新的插件
- 最近一次更新距今不到 1 个月（2026-05-12），且包含**安全漏洞修复**，表明 Epic 持续关注其安全性
- 从 Experimental 迁移到 VirtualProduction 目录，已进入正式生产支持阶段
- 作为 Motion Design 工作流的推荐组件，有明确的应用场景和持续投入
- 推荐使用，尤其在 Motion Design / 虚拟制片多机协作场景中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [官方文档]()（暂无）