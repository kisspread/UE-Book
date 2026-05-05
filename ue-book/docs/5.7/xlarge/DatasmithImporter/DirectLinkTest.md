# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

DatasmithImporter 是一个用于导入 Datasmith 文件（.udatasmith）的插件。Datasmith 是 Epic Games 提供的一套工具和流程，用于将来自各种 CAD、BIM 和 DCC（数字内容创建）应用程序的复杂场景和资产转换并导入到 Unreal Engine 中。

该插件的核心价值在于：
1.  **格式转换**：将非原生 UE 格式（如来自 3ds Max, Revit, SketchUp, CATIA 等软件）的场景数据，转换为 UE 可用的资产（静态网格体、材质、灯光、Actor 等）。
2.  **数据保真**：在转换过程中尽可能保留原始设计数据的层次结构、元数据、材质参数和几何体细节。
3.  **工作流集成**：提供与源设计软件的实时链接（DirectLink）功能，允许在源软件中修改后，一键更新 UE 中的场景。
4.  **企业级支持**：作为“Enterprise”分类下的插件，它面向建筑、工程、施工（AEC）和汽车、产品设计等专业领域，处理大规模、高精度的工业数据。

**DirectLinkTest** 模块是该插件中用于测试和验证 DirectLink 通信功能的子模块。它提供了一组蓝图和 C++ 函数，用于创建、管理和测试 DirectLink 的端点（Endpoint）、源（Source）和目的地（Destination），确保实时同步链路工作正常。

## 使用场景

-   **建筑可视化**：将 Revit 或 ArchiCAD 的 BIM 模型导入 UE，用于创建交互式建筑漫游或营销材料。
-   **产品设计评审**：将 CATIA、SolidWorks 或 NX 的 CAD 模型导入 UE，进行实时渲染和设计评审。
-   **虚拟制片**：将复杂的 3D 场景（可能来自 3ds Max 或 Cinema 4D）快速导入 UE，用于虚拟制片环境。
-   **开发与调试**：当使用 Datasmith 的 DirectLink 功能进行实时同步时，如果遇到连接或数据同步问题，可以使用 `DirectLinkTest` 模块来诊断和验证通信链路。

## 蓝图用法

`DirectLinkTest` 模块提供了一个蓝图函数库 `UDirectLinkTestLibrary`，其中包含用于测试 DirectLink 功能的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeEndpoint` | 创建一个 DirectLink 端点，并返回其 ID。 | `UDirectLinkTestLibrary` |
| `DeleteEndpoint` | 根据 ID 删除一个 DirectLink 端点。 | `UDirectLinkTestLibrary` |
| `AddPublicSource` | 向指定端点添加一个公共源（数据发送方）。 | `UDirectLinkTestLibrary` |
| `AddPublicDestination` | 向指定端点添加一个公共目的地（数据接收方）。 | `UDirectLinkTestLibrary` |
| `SetupSender` / `StartSender` / `StopSender` | 配置、启动和停止一个发送端测试。 | `UDirectLinkTestLibrary` |
| `SetupReceiver` / `StartReceiver` / `StopReceiver` | 配置、启动和停止一个接收端测试。 | `UDirectLinkTestLibrary` |
| `SendScene` | 通过 DirectLink 发送一个场景文件（如 .udatasmith）。 | `UDirectLinkTestLibrary` |
| `DumpReceivedScene` | 将接收到的场景数据输出到日志，用于调试。 | `UDirectLinkTestLibrary` |
| `TestParameters` | 测试 DirectLink 参数。 | `UDirectLinkTestLibrary` |
| `DeleteAllEndpoint` | 删除所有已创建的端点。 | `UDirectLinkTestLibrary` |

### 使用示例（蓝图描述）

1.  **基本连接测试**：
    *   使用 `MakeEndpoint` 节点创建两个端点，一个作为发送方，一个作为接收方。
    *   在发送方端点上调用 `AddPublicSource`，在接收方端点上调用 `AddPublicDestination`。
    *   调用 `SetupSender` 和 `SetupReceiver` 进行配置。
    *   调用 `StartSender` 和 `StartReceiver` 启动测试。
    *   使用 `SendScene` 节点发送一个测试场景文件。
    *   在接收端使用 `DumpReceivedScene` 检查是否成功接收数据。
    *   测试完成后，调用 `StopSender`、`StopReceiver` 和 `DeleteEndpoint` 清理资源。

2.  **快速诊断**：
    *   如果怀疑 DirectLink 有问题，可以创建一个简单的蓝图，顺序调用 `TestParameters` -> `MakeEndpoint` -> `SetupSender` -> `StartSender` -> `SendScene` -> `DumpReceivedScene`，观察日志输出来定位问题。

## C++ 用法

### 头文件引入

```cpp
#include "DirectLinkTestLibrary.h"
```

### 基本用法

`UDirectLinkTestLibrary` 中的所有函数都是静态的，可以直接调用。

```cpp
// 创建一个发送端点
int32 SenderEndpointId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("MySender"), true);
if (SenderEndpointId != INDEX_NONE)
{
    // 为该端点添加一个公共源
    UDirectLinkTestLibrary::AddPublicSource(SenderEndpointId, TEXT("TestSource"));

    // 配置并启动发送端
    UDirectLinkTestLibrary::SetupSender();
    UDirectLinkTestLibrary::StartSender();

    // 发送一个场景文件
    FString ScenePath = FPaths::ProjectContentDir() / TEXT("TestScene.udatasmith");
    UDirectLinkTestLibrary::SendScene(ScenePath);

    // ... 进行其他操作或等待 ...

    // 停止并清理
    UDirectLinkTestLibrary::StopSender();
    UDirectLinkTestLibrary::DeleteEndpoint(SenderEndpointId);
}
```

### 进阶用法

可以结合多个端点模拟完整的发送-接收流程。

```cpp
// 创建发送和接收端点
int32 SenderId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("Sender"));
int32 ReceiverId = UDirectLinkTestLibrary::MakeEndpoint(TEXT("Receiver"));

// 设置源和目的地
UDirectLinkTestLibrary::AddPublicSource(SenderId, TEXT("Source"));
UDirectLinkTestLibrary::AddPublicDestination(ReceiverId, TEXT("Dest"));

// 配置双方
UDirectLinkTestLibrary::SetupSender();
UDirectLinkTestLibrary::SetupReceiver();

// 启动双方
UDirectLinkTestLibrary::StartSender();
UDirectLinkTestLibrary::StartReceiver();

// 发送数据
UDirectLinkTestLibrary::SendScene(TEXT("C:/Models/MyModel.udatasmith"));

// 在接收端检查数据
UDirectLinkTestLibrary::DumpReceivedScene();

// 清理
UDirectLinkTestLibrary::StopSender();
UDirectLinkTestLibrary::StopReceiver();
UDirectLinkTestLibrary::DeleteAllEndpoint();
```

## Demo 示例

以下是一个最小化的 Actor 类，用于在关卡中测试 DirectLink 的发送功能。

**DirectLinkTestActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DirectLinkTestActor.generated.h"

UCLASS()
class ADirectLinkTestActor : public AActor
{
    GENERATED_BODY()

public:
    ADirectLinkTestActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "DirectLink Test")
    FString SceneFilePath;

private:
    int32 EndpointId;
};
```

**DirectLinkTestActor.cpp**
```cpp
#include "DirectLinkTestActor.h"
#include "DirectLinkTestLibrary.h"

ADirectLinkTestActor::ADirectLinkTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
    EndpointId = INDEX_NONE;
}

void ADirectLinkTestActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建端点
    EndpointId = UDirectLinkTestLibrary::MakeEndpoint(GetName(), true);
    if (EndpointId != INDEX_NONE)
    {
        // 添加源并启动发送
        UDirectLinkTestLibrary::AddPublicSource(EndpointId, TEXT("ActorSource"));
        UDirectLinkTestLibrary::SetupSender();
        UDirectLinkTestLibrary::StartSender();

        // 如果指定了文件，则发送
        if (!SceneFilePath.IsEmpty())
        {
            UDirectLinkTestLibrary::SendScene(SceneFilePath);
            UE_LOG(LogTemp, Log, TEXT("DirectLinkTestActor: Sent scene from %s"), *SceneFilePath);
        }
    }
}

void ADirectLinkTestActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理资源
    if (EndpointId != INDEX_NONE)
    {
        UDirectLinkTestLibrary::StopSender();
        UDirectLinkTestLibrary::DeleteEndpoint(EndpointId);
        EndpointId = INDEX_NONE;
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

`DirectLinkTest` 模块依赖于 DirectLink 核心库来实现其测试功能。

| 模块 | 用途 |
|---|---|
| `DirectLink` | 提供 DirectLink 通信协议的核心实现，包括端点、源、目的地等概念。 |

## 维护状态

### 近期更新

```
- 4812f8eaf698 datasmith: cleanup directlink usage in element access #rb Jeanluc.Corenthin
- 68150e0be7d1 Merge UE5/Release-Engine-Staging to UE5/Main @ 14611496 This represents UE4/Main @ 14594913
- 4c1bb11c298a Merge UE5/Release-Engine-Staging to UE5/Main @ 14548662 This represents UE4/Main @ 14525125 + cherrypicked fixes #skipundocheck
```

*   `4812f8eaf698`：清理了元素访问中对 DirectLink 的使用。这表明该模块仍在被维护和优化，以保持代码整洁。
*   后两次提交均为分支合并操作，不包含针对 `DirectLinkTest` 模块本身的功能性修改。

### 维护评价

-   **创建时间**：该插件（及此模块）创建于 2019 年，已有约 6 年历史。
-   **更新频率**：从最近的提交记录看，该模块没有频繁的功能更新。最近的实质性改动是代码清理，而非新功能或重大修复。
-   **活跃度**：作为 Datasmith 生态系统的一部分，其核心功能（DirectLink）是稳定的。`DirectLinkTest` 作为测试工具，其更新通常跟随核心 DirectLink 模块的变化。目前看来处于**维护中但不活跃**的状态。
-   **已知问题**：作为测试模块，其稳定性依赖于底层 DirectLink 库。没有公开的已知重大问题。
-   **推荐使用**：**推荐**。如果你正在开发或调试基于 Datasmith DirectLink 的功能，这个模块提供的蓝图和 C++ 接口是进行连接测试和诊断的宝贵工具。尽管更新不频繁，但其核心功能稳定可靠。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (模块自身包含测试代码)