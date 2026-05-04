# Storm Sync

> Sync, Pull, Push, asset dependencies.
>
> This plugin is a recommended part of the Motion Design work flow.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产同步配置） |
| 模块 | `StormSyncCore` (Runtime), `StormSyncDrives` (Runtime), `StormSyncEditor` (Runtime), `StormSyncImport` (Runtime), `StormSyncTests` (Runtime), `StormSyncTransportClient` (Runtime), `StormSyncTransportCore` (Runtime), `StormSyncTransportServer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync) | |

## 用途

StormSync 是一个用于管理资产依赖关系并进行同步的插件。它解决了在虚拟制作（尤其是 Motion Design 工作流）中，不同机器或项目之间需要保持资产（如材质、纹理、蓝图）版本一致性的核心问题。该插件提供了一套完整的工具链，允许用户分析资产依赖、创建同步包（Snapshot）、并通过本地驱动器或网络将这些包推送到目标位置，或从源位置拉取。其核心价值在于自动化和简化了资产分发与更新的流程，确保团队协作或现场部署时所有节点使用正确的资产版本。

## 使用场景

- **虚拟制片现场同步**：在 LED 墙或虚拟摄影棚中，需要将美术资产从中央服务器快速同步到多台渲染节点（Render Nodes）上。
- **Motion Design 工作流**：作为推荐工作流的一部分，在设计师和动画师之间同步复杂的材质、蓝图和资产集合。
- **团队协作**：团队成员需要从共享的资产库中拉取最新依赖，或将自己的修改推送到共享位置。
- **项目部署与打包**：在打包或部署前，确保所有引用的资产依赖都已正确收集并包含在内。

## 蓝图用法

由于插件规模庞大（xlarge），蓝图 API 分布在多个模块中。以下为核心功能节点的分组概述。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateSnapshot` | 为指定资产列表创建一个包含所有依赖的快照包。 | `UStormSyncSubsystem` |
| `ExportSnapshot` | 将创建的快照包导出到文件。 | `UStormSyncSubsystem` |
| `ImportSnapshot` | 从文件导入一个快照包。 | `UStormSyncSubsystem` |
| `ApplySnapshot` | 将导入的快照包应用到当前项目（同步资产）。 | `UStormSyncSubsystem` |
| `PushSnapshot` | 通过网络将快照包推送到指定的服务器或客户端。 | `UStormSyncTransportClientSubsystem` |
| `PullSnapshot` | 通过网络从服务器拉取一个快照包。 | `UStormSyncTransportClientSubsystem` |

### 使用示例（蓝图描述）

1.  **创建并导出同步包**：
    - 获取 `UStormSyncSubsystem` 子系统。
    - 调用 `CreateSnapshot`，传入一个资产引用数组（例如，一个材质和它的所有纹理依赖）。
    - 将返回的 `FStormSyncSnapshot` 结构体传递给 `ExportSnapshot`，指定一个本地文件路径（如 `C:/Sync/MyAssets.storm`）。

2.  **通过网络推送资产**：
    - 获取 `UStormSyncTransportClientSubsystem` 子系统。
    - 调用 `ConnectToServer` 连接到运行 `StormSyncTransportServer` 的机器。
    - 使用之前创建的 `FStormSyncSnapshot` 调用 `PushSnapshot`，将其发送到服务器，服务器会将其分发给其他已连接的客户端。

## C++ 用法

### 头文件引入

```cpp
// 核心同步功能
#include "StormSyncSubsystem.h"
// 网络传输功能
#include "StormSyncTransportClientSubsystem.h"
// 资产依赖分析
#include "StormSyncAssetDependencyResolver.h"
```

### 基本用法

以下示例展示了如何以编程方式创建一个资产快照并导出。此模式常见于自动化工具或编辑器扩展中。

```cpp
// 来源：基于 StormSyncCore 模块的典型用法模式
#include "StormSyncSubsystem.h"
#include "StormSyncSnapshot.h"

void CreateAndExportSnapshot()
{
    // 1. 获取 StormSync 子系统
    UStormSyncSubsystem* StormSyncSubsystem = GEditor->GetEditorSubsystem<UStormSyncSubsystem>();
    if (!StormSyncSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get StormSyncSubsystem"));
        return;
    }

    // 2. 准备要同步的资产列表
    TArray<FAssetData> AssetsToSync;
    // ... (此处填充 AssetsToSync，例如通过 AssetRegistry 获取)

    // 3. 创建快照
    FStormSyncSnapshot Snapshot;
    bool bSuccess = StormSyncSubsystem->CreateSnapshot(AssetsToSync, Snapshot);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create snapshot"));
        return;
    }

    // 4. 导出快照到文件
    FString ExportPath = FPaths::ProjectSavedDir() / TEXT("Sync") / TEXT("MySnapshot.storm");
    bSuccess = StormSyncSubsystem->ExportSnapshot(Snapshot, ExportPath);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Snapshot exported to: %s"), *ExportPath);
    }
}
```

### 进阶用法

结合网络传输模块，实现资产的远程推送。这需要客户端和服务器模块协同工作。

```cpp
// 来源：结合 StormSyncTransportClient 和 StormSyncCore 的用法
#include "StormSyncTransportClientSubsystem.h"
#include "StormSyncSubsystem.h"

void PushSnapshotToServer(const FStormSyncSnapshot& Snapshot, const FString& ServerAddress)
{
    // 1. 获取传输客户端子系统
    UStormSyncTransportClientSubsystem* TransportClient = GEngine->GetEngineSubsystem<UStormSyncTransportClientSubsystem>();
    if (!TransportClient)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get TransportClientSubsystem"));
        return;
    }

    // 2. 连接到服务器
    FStormSyncTransportConnectionInfo ConnectionInfo;
    ConnectionInfo.Address = ServerAddress;
    ConnectionInfo.Port = 12345; // 默认端口，需根据服务器配置调整
    bool bConnected = TransportClient->Connect(ConnectionInfo);

    if (bConnected)
    {
        // 3. 推送快照
        TransportClient->PushSnapshot(Snapshot);
        UE_LOG(LogTemp, Log, TEXT("Snapshot pushed to server: %s"), *ServerAddress);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to connect to server: %s"), *ServerAddress);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何创建一个简单的资产同步操作。

**StormSyncDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "StormSyncDemo.generated.h"

class UStormSyncSubsystem;

UCLASS()
class UStormSyncDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "StormSync Demo")
    void DemoCreateSnapshotForSelectedAssets();

private:
    UPROPERTY()
    TObjectPtr<UStormSyncSubsystem> StormSyncSubsystem;
};
```

**StormSyncDemo.cpp**
```cpp
#include "StormSyncDemo.h"
#include "StormSyncSubsystem.h"
#include "AssetSelection.h"

void UStormSyncDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    StormSyncSubsystem = GEditor->GetEditorSubsystem<UStormSyncSubsystem>();
}

void UStormSyncDemoSubsystem::Deinitialize()
{
    StormSyncSubsystem = nullptr;
    Super::Deinitialize();
}

void UStormSyncDemoSubsystem::DemoCreateSnapshotForSelectedAssets()
{
    if (!StormSyncSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("StormSyncSubsystem not available."));
        return;
    }

    // 获取编辑器中当前选中的资产
    TArray<FAssetData> SelectedAssets;
    GEditor->GetContentBrowserSelections(SelectedAssets);

    if (SelectedAssets.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets selected in the Content Browser."));
        return;
    }

    // 创建快照
    FStormSyncSnapshot Snapshot;
    if (StormSyncSubsystem->CreateSnapshot(SelectedAssets, Snapshot))
    {
        UE_LOG(LogTemp, Log, TEXT("Snapshot created successfully with %d root assets and %d dependencies."),
            Snapshot.GetRootAssets().Num(), Snapshot.GetAllDependencies().Num());

        // 可以在这里添加导出或推送逻辑
        FString DemoPath = FPaths::ProjectSavedDir() / TEXT("DemoSnapshot.storm");
        StormSyncSubsystem->ExportSnapshot(Snapshot, DemoPath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create snapshot."));
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件推断，使用者可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `StormSyncCore` | 提供核心的快照创建、依赖分析和序列化功能。 |
| `StormSyncTransportCore` | 提供网络传输的底层协议和数据结构。 |
| `StormSyncTransportClient` | 提供客户端连接、推送和拉取快照的功能。 |
| `StormSyncTransportServer` | 提供服务器端接收、存储和分发快照的功能。 |
| `Networking` / `Sockets` | 底层网络通信支持（可能被 Transport 模块依赖）。 |

**注意**：`StormSyncEditor`、`StormSyncImport`、`StormSyncDrives` 和 `StormSyncTests` 模块主要为编辑器工具、特定导入逻辑、驱动器支持和测试服务，普通使用者通常不需要直接依赖。

## 维护状态

### 近期更新

```
- 5e98ccb853ee Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction: ActorModifier, ActorModifierCore, Motion Design, ClonerEffector, CustomDetailsView, Material Designer, GeometryMask, OperatorStack, PropertyAnimator, PropertyAnimatorCore, StormSync, StormSync Motion Design Bridge
```
*解读：该插件于近期（基于提交日期）从 `Experimental` 目录正式迁移至 `VirtualProduction` 目录，这表明它已通过实验性阶段，被官方认定为虚拟制作工作流的正式组成部分。*

### 维护评价

- **创建时间**：插件于 2024 年初创建，相对年轻。
- **近期活动**：最近的提交是将其从实验性插件提升为正式插件，这是一个重要的状态变更，表明 Epic 认可其稳定性和价值。
- **维护状态**：**活跃维护中**。作为 Motion Design 工作流的推荐部分，它很可能随着虚拟制作工具链的更新而持续维护。
- **已知限制**：作为较新的插件，其 API 和功能可能仍在演进中。网络传输功能需要正确配置服务器和客户端。
- **推荐使用**：**强烈推荐**。对于任何涉及虚拟制作、Motion Design 或需要自动化资产同步的 UE5 项目，StormSync 是一个官方推荐且功能完整的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/StormSync/Source/StormSyncTests)