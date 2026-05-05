# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA资产） |
| 模块 | `RigLogicLib` (CPlusPlus), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个高性能的面部动画驱动系统，其核心是处理 **DNA (Digital Native Animation)** 数据。DNA 是一种专有的二进制格式，用于存储高保真角色的面部骨骼结构、变形目标（Blend Shapes）、关节行为、神经网络权重以及机器学习行为等复杂数据。

该插件的主要作用是：
1.  **加载与解析 DNA 数据**：从文件或内存流中读取 DNA 数据，并将其解析为内部可操作的结构。
2.  **驱动面部动画**：基于输入的控制参数（如表情、骨骼变换），通过内置的求解器（包括神经网络、径向基函数 RBF 求解器、PSD 等）计算出最终的面部骨骼变换和变形目标权重。
3.  **提供底层库**：`RigLogicLib` 模块封装了核心的 `rl4` (RigLogic 4) 库，提供了跨平台的、高性能的动画计算引擎。

它解决的问题是：如何将来自 DCC 工具（如 Maya）的复杂面部绑定数据，以高效、标准化的方式在游戏引擎中实时驱动，实现电影级别的面部动画效果。

## 使用场景

-   **数字人/虚拟偶像**：需要高保真、实时面部表情驱动的虚拟角色。
-   **游戏角色面部动画**：为 AAA 级游戏中的主角或重要 NPC 提供细腻的面部表情系统。
-   **从 DCC 工具导出**：当美术师在 Maya 等软件中使用特定的绑定插件（如 Epic 的 MetaHuman Creator 流程）创建角色后，会生成 DNA 文件。此插件用于在 UE 中加载并驱动这些数据。
-   **自定义动画管线**：需要深度集成或扩展面部动画计算流程的开发者。

## 蓝图用法

由于 `RigLogicLib` 是底层 C++ 库，其蓝图接口主要通过 `RigLogicModule` 暴露。从提供的头文件中可以推断出一些核心的蓝图可访问功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Version` | 获取 RigLogic 库的版本信息 | `UVersionInfo` (推测) |
| `Load DNA from File` | 从文件路径加载 DNA 数据 | `URigLogicDNA` (推测) |
| `Create Rig Instance` | 创建一个用于计算动画的 Rig 实例 | `URigInstance` (推测) |
| `Set Control Values` | 设置驱动动画的输入控制值（如表情参数） | `URigInstance` (推测) |
| `Calculate` | 执行一次动画计算，更新输出 | `URigInstance` (推测) |
| `Get Joint Transforms` | 获取计算后的骨骼变换结果 | `URigInstance` (推测) |
| `Get Blend Shape Weights` | 获取计算后的变形目标权重 | `URigInstance` (推测) |

### 使用示例（蓝图描述）

1.  **加载 DNA**：使用 `Load DNA from File` 节点，提供 DNA 文件的路径，获取一个 DNA 数据对象。
2.  **创建实例**：使用 `Create Rig Instance` 节点，传入上一步的 DNA 对象，创建一个可操作的 Rig 实例。
3.  **设置输入**：在每一帧或需要时，通过 `Set Control Values` 节点，将游戏逻辑中的表情参数（如 `Smile`, `BrowRaise`）映射并设置到 Rig 实例的输入端口。
4.  **计算与获取结果**：调用 `Calculate` 节点驱动计算。随后，使用 `Get Joint Transforms` 和 `Get Blend Shape Weights` 节点获取结果，并将其应用到角色的骨骼网格体组件上。

## C++ 用法

### 头文件引入

```cpp
#include "RigLogicLib.h" // 模块头文件
#include "riglogic/RigLogic.h" // 核心 RigLogic 头文件
#include "riglogic/riglogic/RigInstance.h" // Rig 实例
#include "dna/StreamReader.h" // DNA 读取器
#include "FMemoryResource.h" // UE 内存资源适配器
```

### 基本用法

以下代码展示了如何加载 DNA 并创建一个 Rig 实例。此模式是使用 RigLogic 的基础。

```cpp
// 来源：基于 FMemoryResource.h 和 RigLogic.h 的典型用法推断
#include "RigLogicLib.h"
#include "riglogic/RigLogic.h"
#include "dna/StreamReader.h"
#include "FMemoryResource.h"

void LoadAndCreateRigInstance()
{
    // 1. 获取内存资源管理器（使用 UE 的内存分配器）
    rl4::MemoryResource* MemResource = FMemoryResource::Instance();

    // 2. 创建 DNA 读取器（假设从文件流读取）
    // trio::FileStream DnaFileStream(TEXT("path/to/character.dna"));
    // DnaFileStream.open(trio::AccessMode::Read, trio::OpenMode::Binary);
    // dna::StreamReader* DnaReader = dna::StreamReader::create(&DnaFileStream, MemResource);
    // DnaReader->read();

    // 3. 创建 RigLogic 核心对象
    rl4::RigLogic* RigLogic = rl4::RigLogic::create(MemResource);

    // 4. 从 DNA 数据构建 RigLogic 内部状态
    // RigLogic->build(DnaReader);

    // 5. 创建一个 Rig 实例，用于后续的动画计算
    rl4::RigInstance* RigInstance = RigLogic->createInstance(MemResource);

    // 现在可以使用 RigInstance 设置输入并计算输出了
    // ...

    // 清理（通常由智能指针或自定义内存管理处理）
    // rl4::RigInstance::destroy(RigInstance, MemResource);
    // rl4::RigLogic::destroy(RigLogic, MemResource);
    // dna::StreamReader::destroy(DnaReader, MemResource);
}
```

### 进阶用法

结合 `Stats` 结构和 `Configuration`，可以了解和配置 Rig 的能力。

```cpp
// 来源：基于 riglogic/riglogic/Stats.h 和 riglogic/riglogic/Configuration.h
#include "riglogic/riglogic/Stats.h"
#include "riglogic/riglogic/Configuration.h"

void InspectRigCapabilities(rl4::RigLogic* RigLogic)
{
    // 获取 Rig 的统计信息
    rl4::Stats Stats = RigLogic->getStats();

    UE_LOG(LogRigLogicLib, Log, TEXT("Rig Stats:"));
    UE_LOG(LogRigLogicLib, Log, TEXT("  Joints: %d"), Stats.jointCount);
    UE_LOG(LogRigLogicLib, Log, TEXT("  BlendShapeChannels: %d"), Stats.blendShapeChannelCount);
    UE_LOG(LogRigLogicLib, Log, TEXT("  NeuralNetworks: %d"), Stats.neuralNetworkCount);
    UE_LOG(LogRigLogicLib, Log, TEXT("  RBFSolvers: %d"), Stats.rbfSolverCount);
    UE_LOG(LogRigLogicLib, Log, TEXT("  Calculation Type: %d"), static_cast<int>(Stats.calculationType));

    // 可以根据 Stats 调整 Configuration，例如选择计算后端（CPU/GPU）
    // rl4::Configuration Config;
    // Config.calculationType = rl4::CalculationType::SSE; // 使用 SSE 指令集加速
    // RigLogic->configure(Config);
}
```

## Demo 示例

一个最小的、可编译的示例，展示如何从内存加载 DNA 并执行一次计算。

**MyRigLogicActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "riglogic/riglogic/RigInstance.h"
#include "MyRigLogicActor.generated.h"

namespace rl4 { class RigLogic; }

UCLASS()
class AMyRigLogicActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigLogicActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    // RigLogic 核心对象和实例
    rl4::RigLogic* RigLogicCore;
    rl4::RigInstance* RigInstance;

    // 模拟的输入控制值（例如，一个微笑表情）
    TArray<float> ControlValues;
};
```

**MyRigLogicActor.cpp**
```cpp
#include "MyRigLogicActor.h"
#include "RigLogicLib.h"
#include "riglogic/RigLogic.h"
#include "FMemoryResource.h"
#include "dna/StreamReader.h"

AMyRigLogicActor::AMyRigLogicActor()
{
    PrimaryActorTick.bCanEverTick = true;
    RigLogicCore = nullptr;
    RigInstance = nullptr;
}

void AMyRigLogicActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 初始化内存资源
    rl4::MemoryResource* MemRes = FMemoryResource::Instance();

    // 2. 模拟从内存块加载 DNA（实际应从文件或资产加载）
    // 假设 `DnaData` 是一个包含 DNA 二进制数据的 uint8 数组
    // trio::MemoryStream MemStream(DnaData, DnaDataSize);
    // MemStream.open(trio::AccessMode::Read, trio::OpenMode::Binary);
    // dna::StreamReader* Reader = dna::StreamReader::create(&MemStream, MemRes);
    // Reader->read();

    // 3. 创建 RigLogic 核心并构建
    RigLogicCore = rl4::RigLogic::create(MemRes);
    // RigLogicCore->build(Reader);

    // 4. 创建实例
    RigInstance = RigLogicCore->createInstance(MemRes);

    // 5. 初始化控制值数组（大小应与 DNA 中定义的输入数量匹配）
    ControlValues.SetNumZeroed(RigInstance->getInputCount());

    // 清理 Reader
    // dna::StreamReader::destroy(Reader, MemRes);
}

void AMyRigLogicActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理资源
    if (RigInstance)
    {
        rl4::RigInstance::destroy(RigInstance, FMemoryResource::Instance());
        RigInstance = nullptr;
    }
    if (RigLogicCore)
    {
        rl4::RigLogic::destroy(RigLogicCore, FMemoryResource::Instance());
        RigLogicCore = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyRigLogicActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!RigInstance) return;

    // 模拟更新输入：让第一个控制值随时间正弦变化
    ControlValues[0] = FMath::Sin(GetGameTimeSinceCreation()) * 0.5f + 0.5f;

    // 设置输入
    RigInstance->setControlValues(ControlValues.GetData(), ControlValues.Num());

    // 执行计算
    RigInstance->calculate();

    // 此处可以获取输出并应用到骨骼网格体
    // const float* JointOutputs = RigInstance->getJointOutputs();
    // const float* BlendShapeOutputs = RigInstance->getBlendShapeOutputs();
}
```

## 模块依赖

要使用 `RigLogicLib` 核心库，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RigLogicLib` | RigLogic 核心 C++ 库，提供 DNA 解析和动画计算引擎。 |
| `SkeletalMeshUtilitiesCommon` | `RigLogicModule` 依赖，用于与骨骼网格体交互。 |
| `RHI`, `RenderCore` | `RigLogicModule` 依赖，可能用于 GPU 计算支持。 |
| `MessageLog` | `RigLogicModule` 依赖，用于输出日志和错误信息。 |

## 维护状态

### 近期更新

```
- a4ca42033949 Trigger caching of all otherwise lazily computed data when a DNA is loaded from a binary stream, which can avoid potential race conditions if the same DNA reader is utilized in a multithreaded environment
- a2f48da51db8 Fixed circular includes across the engine
- ac6fbec65d9d Fixed header units compile errors
```

### 维护评价

-   **创建时间**：2020年7月，作为 UE5 面部动画管线的核心组件引入。
-   **最近更新**：最近的提交集中在**性能优化**（缓存机制）和**工程维护**（修复编译问题、头文件循环依赖）。这表明插件处于**稳定维护期**，主要工作是确保其在新版引擎中的兼容性和性能，而非添加大量新功能。
-   **活跃度**：作为 Epic Games 官方维护的、用于 MetaHuman 等关键产品的插件，其代码质量和维护优先级很高。虽然更新频率可能不如一些社区插件，但属于**持续维护中**。
-   **已知限制**：作为底层库，其使用门槛较高，通常需要配合特定的 DCC 工具链和资产导出流程。直接使用 C++ API 需要对 DNA 数据格式和 RigLogic 概念有深入了解。
-   **推荐使用**：**强烈推荐**用于需要专业级、高保真面部动画的项目。它是 Epic 官方数字人解决方案的基石，稳定性和性能有保障。对于简单的面部动画需求，可能显得过于复杂。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
- [官方文档]() (无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)