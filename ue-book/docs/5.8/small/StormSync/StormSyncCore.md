# Storm Sync

> Sync, Pull, Push, asset dependencies.
> 
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 中文名 | 风暴同步 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个**资产依赖同步、传输和管理框架**，专为 Motion Design 工作流设计。它解决了在分布式团队或跨项目协作中，**资产包（包含其所有依赖）的版本控制、差异比较和高效同步**的问题。

通过 StormSync，开发者可以将一组资产及其依赖打包成一个 `.spak` 文件或通过网络发送，接收方可以精确地更新或添加缺失的资产，而不会破坏现有的项目结构。它具备：
1.  **依赖分析**：自动递归查找资产的所有依赖。
2.  **差异比较**：通过文件大小、时间戳和哈希值比较本地与远程资产状态。
3.  **增量同步**：仅传输缺失或过期的资产，避免全量复制。
4.  **网络服务发现**：通过消息总线自动发现局域网内的其他 StormSync 实例，实现点对点同步。
5.  **热重载支持**：在导入后尝试热重载修改的包，避免重启编辑器。

## 使用场景

-   你在使用 **Motion Design 工具**进行虚拟制作，需要在多个艺术家或机器之间同步复杂场景资产。
-   你需要将一组带有复杂依赖关系的资产（如材质、网格体、蓝图）**打包并发送给外部合作伙伴**，而无需发送整个项目。
-   你需要在一个项目中**集成另一个插件包中的特定资产**，并确保其依赖项也被正确拉取。
-   你需要在**编辑器运行时（-game）模式**下也能正确获取资产依赖信息，进行后台同步或验证。
-   你需要一个**自动化的资产同步管道**，可以通过命令行工具（如 Commandlet）执行。

## 蓝图用法

StormSync 核心模块主要提供 C++ API，蓝图接口主要集中在 `StormSyncDrives` 和 `StormSyncEditor` 等上层模块。核心模块通过 `FStormSyncCoreDelegates` 暴露了一系列委托，供蓝图或其他系统监听同步过程中的事件。

### 核心委托

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnRequestImportBuffer` | 当收到网络包或本地 `.spak` 文件，请求开始导入时广播 | `FStormSyncCoreDelegates` |
| `OnFileImported` | 当一个文件从包中提取完成时广播 | `FStormSyncCoreDelegates` |
| `OnPakAssetExtracted` | 当单个资产从包中提取时广播（提供原始包名和目标路径） | `FStormSyncCoreDelegates` |
| `OnServiceDiscoveryConnection` | 当通过服务发现检测到一个新的网络连接时广播 | `FStormSyncCoreDelegates` |
| `OnServiceDiscoveryStateChange` | 当已连接设备的状态发生变化（如变为无响应）时广播 | `FStormSyncCoreDelegates` |
| `OnStormSyncServerStarted` | 当 StormSync 服务端模块启动时广播 | `FStormSyncCoreDelegates` |

### 使用示例（蓝图描述）

在蓝图中，你可以**绑定到 `FStormSyncCoreDelegates` 中的静态委托**来监听和响应同步事件。
1.  在任意蓝图的 `BeginPlay` 节点或你希望开始监听的时机。
2.  使用 `Assign` 节点将 `FStormSyncCoreDelegates::OnFileImported` 绑定到一个自定义的蓝图函数（例如 `Handle File Imported`）。
3.  在 `Handle File Imported` 函数中，你可以获取导入的文件路径，并执行相应的逻辑，如刷新UI或更新本地数据库。
4.  当有文件被同步导入时，该函数将自动被调用。

## C++ 用法

### 头文件引入

```cpp
#include "StormSyncCoreUtils.h"
#include "StormSyncPackageDescriptor.h"
#include "StormSyncCoreDelegates.h"
```

### 基本用法：获取资产依赖并创建包缓冲区

以下代码演示如何获取一个包名的所有依赖，并将其打包到内存缓冲区中。
**来源**: 分析自 `FStormSyncCoreUtils` 的公共API和委托模式。

```cpp
// 假设你有一个要同步的资产包名列表
TArray<FName> PackageNamesToSync;
PackageNamesToSync.Add(FName("/Game/Characters/Hero"));

// 1. 获取这些包的所有依赖（递归）
TArray<FStormSyncFileDependency> FileDependencies;
FText ErrorText;
bool bSuccess = FStormSyncCoreUtils::GetAvaFileDependenciesForPackages(
    PackageNamesToSync,
    FileDependencies,
    ErrorText,
    true // 验证包是否存在
);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Found %d dependencies."), FileDependencies.Num());
    
    // 2. 创建一个内存归档来存放打包数据
    TArray<uint8> PakBuffer;
    FMemoryWriter PakArchive(PakBuffer);
    
    // 3. 打包这些资产到归档中
    FText PakErrorText;
    FStormSyncCoreUtils::FOnFileAdded OnFileAddedDelegate;
    OnFileAddedDelegate.BindLambda([](const FStormSyncFileDependency& FileDep)
    {
        UE_LOG(LogTemp, Log, TEXT("Added to pak: %s"), *FileDep.PackageName.ToString());
    });
    
    bSuccess = FStormSyncCoreUtils::CreatePakBuffer(
        PackageNamesToSync,
        PakArchive,
        PakErrorText,
        OnFileAddedDelegate
    );
    
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Pak buffer created with size: %d bytes"), PakBuffer.Num());
        // 现在可以将 PakBuffer 通过网络发送，或保存为 .spak 文件
    }
}
```

### 进阶用法：比较远程与本地状态并执行同步

以下代码演示如何使用 `GetSyncFileModifiers` 来计算需要同步的文件列表。
**来源**: 分析自 `FStormSyncCoreUtils::GetSyncFileModifiers` 的功能描述和 `FStormSyncFileModifierInfo` 结构体。

```cpp
// 假设我们从远程收到了一个文件依赖列表（例如通过网络消息解析）
TArray<FStormSyncFileDependency> RemoteDependencies; // 这是从网络消息中解析出来的

// 我们要检查的本地资产包名
TArray<FName> LocalPackageNames;
LocalPackageNames.Add(FName("/Game/Scenes/MainLevel"));

// 1. 计算差异：哪些文件需要添加、覆盖或删除
TArray<FStormSyncFileModifierInfo> SyncModifiers = 
    FStormSyncCoreUtils::GetSyncFileModifiers(LocalPackageNames, RemoteDependencies);

// 2. 遍历差异列表，决定如何处理
for (const FStormSyncFileModifierInfo& Modifier : SyncModifiers)
{
    switch (Modifier.ModifierOperation)
    {
        case EStormSyncModifierOperation::Addition:
            UE_LOG(LogTemp, Log, TEXT("需要添加: %s"), *Modifier.FileDependency.PackageName.ToString());
            // 可以触发从远程下载该文件的操作
            break;
            
        case EStormSyncModifierOperation::Overwrite:
            UE_LOG(LogTemp, Warning, TEXT("需要覆盖（已过时）: %s"), *Modifier.FileDependency.PackageName.ToString());
            // 触发下载并覆盖本地文件的操作
            break;
            
        case EStormSyncModifierOperation::Missing:
            UE_LOG(LogTemp, Log, TEXT("本地存在但远程缺失: %s"), *Modifier.FileDependency.PackageName.ToString());
            // 通常忽略，除非你想将本地资产推送到远程
            break;
    }
}

// 3. 如果没有差异，说明已是最新
if (SyncModifiers.Num() == 0)
{
    UE_LOG(LogTemp, Log, TEXT("资产已是最新，无需同步。"));
}
```

## Demo 示例

以下是一个最小的 C++ 类，演示如何使用 StormSync 核心功能来检查指定资产的依赖。
**注**：此示例假设你已经将 `StormSyncCore` 模块添加到你的项目依赖中。

```cpp
// StormSyncDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StormSyncDemoActor.generated.h"

UCLASS()
class YOURPROJECT_API AStormSyncDemoActor : public AActor
{
    GENERATED_BODY()
    
public:
    AStormSyncDemoActor();

    /** 要检查依赖的资产路径 */
    UPROPERTY(EditAnywhere, Category="Storm Sync Demo")
    FString PackageNameToCheck;

    /** 在蓝图中调用，打印依赖信息 */
    UFUNCTION(BlueprintCallable, Category="Storm Sync Demo")
    void PrintAssetDependencies();

    /** 在蓝图中调用，将资产及其依赖打包到内存 */
    UFUNCTION(BlueprintCallable, Category="Storm Sync Demo")
    bool CreatePakBufferForAsset();
};
```

```cpp
// StormSyncDemoActor.cpp
#include "StormSyncDemoActor.h"
#include "StormSyncCoreUtils.h"
#include "StormSyncPackageDescriptor.h"

AStormSyncDemoActor::AStormSyncDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    PackageNameToCheck = TEXT("/Game/Props/Cube");
}

void AStormSyncDemoActor::PrintAssetDependencies()
{
    TArray<FName> PackageNames = { FName(*PackageNameToCheck) };
    TArray<FName> Dependencies;
    FText ErrorText;

    bool bSuccess = FStormSyncCoreUtils::GetDependenciesForPackages(
        PackageNames,
        Dependencies,
        ErrorText,
        true
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("=== 依赖项列表 (共 %d 个) ==="), Dependencies.Num());
        for (const FName& Dep : Dependencies)
        {
            UE_LOG(LogTemp, Log, TEXT("  -> %s"), *Dep.ToString());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("获取依赖失败: %s"), *ErrorText.ToString());
    }
}

bool AStormSyncDemoActor::CreatePakBufferForAsset()
{
    TArray<FName> PackageNames = { FName(*PackageNameToCheck) };
    TArray<uint8> PakBuffer;
    FMemoryWriter PakArchive(PakBuffer);
    FText ErrorText;

    bool bSuccess = FStormSyncCoreUtils::CreatePakBuffer(
        PackageNames,
        PakArchive,
        ErrorText
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("打包成功！缓冲区大小: %d 字节"), PakBuffer.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("打包失败: %s"), *ErrorText.ToString());
    }
    
    return bSuccess;
}
```

## 模块依赖

从提供的模块列表和头文件包含关系推断，使用者主要需要依赖 `StormSyncCore`。

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 核心同步逻辑、依赖分析、包创建与提取 |
| `Messaging` | 用于网络服务发现和消息总线通信 |
| `Sockets` | 底层TCP套接字通信，用于网络传输 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c830b630` | Storm Sync: fixed vulnerability where a malicious actor can make an spak containing package names/pa | 修复了恶意 `.spak` 文件中包名导致的安全漏洞 |
| 2026-05-12 | `3e9d09b7` | Motion Design: fixed storm sync export wizard UI creating a large number of nested folders when chan | 修复了导出向导UI在更改路径时错误创建大量嵌套文件夹的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符混用导致的潜在问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 `UE_LOG` 迁移至 `UE_LOGF` |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 再次修复一个糟糕的查找替换错误 |

### 维护评价

**活跃维护**。StormSync 是 Motion Design 工作流的核心推荐插件，由 Epic Games 官方维护。虽然创建时间仅约一年，但近期有持续的更新，包括**安全修复、UI 优化、底层日志系统迁移和关键 bug 修复**。这表明该插件处于**积极开发和维护阶段**，是虚拟制作项目中资产同步的可靠选择。建议在使用中关注其与 `Motion Design` 插件的协同工作情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)