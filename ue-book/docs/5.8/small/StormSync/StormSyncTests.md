# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个专为虚拟制片 (Virtual Production) 和 Motion Design 工作流设计的资产依赖同步插件。它解决的核心问题是：在一个复杂的、包含大量资产引用关系的项目中（尤其是在多人协作或跨机器/环境时），如何高效、可靠地同步、拉取和推送这些资产及其依赖，确保所有参与者或环境使用一致的资产版本。

它不仅仅是简单的文件复制，而是理解和处理资产之间复杂的依赖图谱，并提供驱动器（Drives）管理、差异比对、导入策略等功能，是 Motion Design 工作流中进行资产协作与分发的推荐工具。

## 使用场景

- **多人协作的 Motion Design 项目**：多位设计师或团队在同一项目上工作，需要频繁同步彼此创建的资产（如材质、网格、蓝图）。
- **跨环境部署资产**：将资产从开发机同步到现场工作站或渲染农场，确保演出环境使用的资产版本与开发环境一致。
- **管理资产版本基线**：在项目关键节点（如灯光预演前、最终渲染前），创建资产基线并分发给所有相关方。
- **自动化资产分发**：集成到构建流程中，通过命令行或蓝图自动化地将指定资产包推送到目标位置。

## 蓝图用法

由于 StormSync 插件的源码中公开的 `UFUNCTION(BlueprintCallable)` 主要位于其核心和传输模块（如 `StormSyncCore`, `StormSyncTransportClient`），而非作为测试模块的 `StormSyncTests`，因此以下节点信息基于对该插件整体架构的分析。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Synchronize` | 根据指定的同步配置（驱动器），执行资产同步操作。 | `UStormSyncSubsystem` (推断) |
| `PushAssets` | 将本地资产包推送到远程传输服务器。 | `UStormSyncTransportClient` (推断) |
| `PullAssets` | 从远程传输服务器拉取资产包。 | `UStormSyncTransportClient` (推断) |
| `CreateSyncSnapshot` | 创建当前资产依赖状态的快照，用于后续同步或比较。 | `UStormSyncCoreLibrary` (推断) |

### 使用示例（蓝图描述）

1.  **基础同步流程**：
    - 在一个 `BeginPlay` 事件中，获取 `UStormSyncSubsystem` 的引用。
    - 构造一个 `FStormSyncDrive` 或加载一个已存在的“同步驱动器”数据资产，该资产定义了源路径、目标路径和同步策略。
    - 调用子系统的 `Synchronize` 节点，传入驱动器配置，即可触发同步。

2.  **基于网络的资产推送**：
    - 获取 `UStormSyncTransportClient` 子系统。
    - 设置服务器连接信息（地址、端口）。
    - 使用 `PushAssets` 节点，传入要发送的资产对象列表或引用数组，客户端会将这些资产及其依赖打包并发送至服务器。

## C++ 用法

StormSync 插件提供了完整的 C++ API，其核心用法和工作流可以通过其测试用例 (`StormSyncTests`) 进行学习和验证。

### 头文件引入

```cpp
// 核心同步功能
#include "StormSyncCore.h"
// 传输客户端（用于网络同步）
#include "StormSyncTransportClient.h"
// 同步驱动器/配置相关
#include "StormSyncDrive.h"
```

### 基本用法

以下代码展示了如何通过 C++ 创建一个简单的同步任务，灵感来源于测试用例的模式。

```cpp
// 来源: StormSyncTests 模块中测试用例的逻辑推断
#include "StormSyncCore.h"
#include "Misc/Paths.h"
#include "HAL/PlatformFilemanager.h"

void PerformBasicSync()
{
    // 1. 获取 StormSync 核心子系统
    UStormSyncSubsystem* SyncSubsystem = GEngine->GetEngineSubsystem<UStormSyncSubsystem>();
    if (!SyncSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取 StormSyncSubsystem"));
        return;
    }

    // 2. 定义源路径和目标路径
    FString SourcePath = FPaths::ProjectContentDir() / TEXT("Assets/Source");
    FString DestinationPath = FPaths::ProjectSavedDir() / TEXT("SyncedAssets");

    // 3. （可选）创建或加载一个同步驱动器配置
    // 这通常通过编辑器 UI 或加载 UStormSyncDrive 数据资产完成
    FStormSyncDrive SyncDrive;
    SyncDrive.SourcePath = SourcePath;
    SyncDrive.DestinationPath = DestinationPath;
    // 设置其他参数，如是否递归、忽略列表等

    // 4. 执行同步
    // 注意：实际API可能是异步的或需要更复杂的回调，此处为简化说明
    bool bSuccess = SyncSubsystem->SynchronizeDrive(SyncDrive);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("资产同步完成。"));
    }
}
```

### 进阶用法

结合传输功能进行网络同步，并处理同步结果。

```cpp
// 来源: 结合 StormSyncTransportClient 和 StormSyncTests 的用法
#include "StormSyncTransportClient.h"
#include "StormSyncTransportCore.h" // 可能包含网络协议相关类型

void PushAssetsToRemoteServer()
{
    // 1. 获取传输客户端子系统
    UStormSyncTransportClient* TransportClient = GEngine->GetEngineSubsystem<UStormSyncTransportClient>();
    if (!TransportClient)
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取 StormSyncTransportClient"));
        return;
    }

    // 2. 连接到服务器
    FString ServerAddress = TEXT("192.168.1.100");
    int32 ServerPort = 19876; // 示例端口
    TransportClient->ConnectToServer(ServerAddress, ServerPort);

    // 3. 准备要推送的资产引用
    TArray<FSoftObjectPath> AssetsToPush;
    AssetsToPush.Add(FSoftObjectPath(TEXT("/Game/Materials/M_Master.M_Master")));
    AssetsToPush.Add(FSoftObjectPath(TEXT("/Game/Meshes/SM_Cube.SM_Cube")));

    // 4. 推送资产
    // 实际API可能需要更复杂的回调来跟踪状态和错误
    FStormSyncPushRequest PushRequest;
    PushRequest.AssetPaths = AssetsToPush;
    TransportClient->PushAssets(PushRequest);

    // 5. （可选）监听同步完成事件
    TransportClient->OnAssetsPushed.AddDynamic(this, &UMyClass::HandlePushCompleted);
}
```

## Demo 示例

一个完整的、最小的 C++ 示例，演示如何使用 StormSyncCore 模块进行本地资产依赖分析。

```cpp
// StormSyncDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StormSyncDemo.generated.h"

class UStormSyncSubsystem;
struct FStormSyncAssetDependencyInfo;

UCLASS()
class AStormSyncDemo : public AActor
{
    GENERATED_BODY()

public:
    AStormSyncDemo();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "StormSync Demo")
    void AnalyzeAssetDependencies(const FString& AssetPath);

private:
    UPROPERTY()
    TObjectPtr<UStormSyncSubsystem> CachedSyncSubsystem;

    void OnDependencyAnalysisComplete(const TArray<FStormSyncAssetDependencyInfo>& Dependencies, bool bSuccess);
};
```

```cpp
// StormSyncDemo.cpp
#include "StormSyncDemo.h"
#include "StormSyncCore.h"
#include "Engine/Engine.h"

AStormSyncDemo::AStormSyncDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AStormSyncDemo::BeginPlay()
{
    Super::BeginPlay();

    // 缓存子系统引用
    CachedSyncSubsystem = GEngine->GetEngineSubsystem<UStormSyncSubsystem>();
    if (CachedSyncSubsystem)
    {
        UE_LOG(LogTemp, Log, TEXT("StormSyncDemo: StormSyncSubsystem 已就绪。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("StormSyncDemo: 未能找到 StormSyncSubsystem。请确认插件已启用。"));
    }
}

void AStormSyncDemo::AnalyzeAssetDependencies(const FString& AssetPath)
{
    if (!CachedSyncSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("无法分析：子系统无效。"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("开始分析资产依赖: %s"), *AssetPath);

    // 调用异步分析接口 (推断的API)
    CachedSyncSubsystem->AnalyzeAssetDependenciesAsync(
        AssetPath,
        FStormSyncAnalysisDelegate::CreateUObject(this, &AStormSyncDemo::OnDependencyAnalysisComplete)
    );
}

void AStormSyncDemo::OnDependencyAnalysisComplete(const TArray<FStormSyncAssetDependencyInfo>& Dependencies, bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("依赖分析成功，共发现 %d 项依赖。"), Dependencies.Num());
        for (const auto& DepInfo : Dependencies)
        {
            UE_LOG(LogTemp, Verbose, TEXT("  - %s (类型: %s)"), *DepInfo.AssetPath, *DepInfo.AssetType);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("依赖分析失败。"));
    }
}
```

## 模块依赖

以下模块是使用 StormSync 功能时可能需要依赖的**独特**模块（排除了常见的 Core, Engine 等）：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 提供核心的资产依赖分析、同步逻辑和数据结构。 |
| `StormSyncTransportCore` | 定义网络传输的协议、数据包格式和基础通信类。 |
| `StormSyncTransportClient` | 实现客户端功能，用于连接服务器并推送/拉取资产。 |
| `StormSyncTransportServer` | 实现服务器端功能，用于接收和分发资产同步数据。 |
| `StormSyncImport` | 处理资产导入时的特定逻辑和策略。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa... | 修复了一个安全漏洞，该漏洞允许恶意行为者通过构造特定的资产包文件名进行攻击。 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan... | 修复了风暴同步导出向导在修改路径时错误地创建大量嵌套文件夹的UI问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位格式说明符与64位参数不匹配的问题，提升了跨平台兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从 `UE_LOG` 迁移到 `UE_LOGF`，可能是为了遵循新的日志规范或获取更好的格式化功能。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 对上一次错误的查找替换操作进行了修正。 |

### 维护评价

**积极维护中**。StormSync 是一个在 2025 年 5 月才从 Experimental 迁移到 VirtualProduction 的“新”插件，至今不到一年。从最近的 Git 提交记录看，维护非常活跃：
1.  **最近更新**：2026 年 5 月仍有针对**安全性**和**UI易用性**的修复。
2.  **维护内容**：更新内容集中在修复已知问题（安全漏洞、UI错误）和提升代码质量（日志、编译兼容性），表明该插件处于稳定期并持续改进。
3.  **推荐使用**：作为 Epic Games 官方维护的、且是 Motion Design 工作流推荐部分的插件，其可靠性和未来支持有保障。对于需要高级资产依赖管理与同步的虚拟制片项目，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests) (StormSyncTests 模块)