# DataflowVolumetric

> Adds volumetric support to Dataflow（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Dataflow |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `DataflowVolumeCore` (Editor), `DataflowVolumeNodes` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DataflowVolumetricPlugin) | |

## 用途

该插件扩展了 UE5 的 **Dataflow** 系统，为其增加了处理和操作**体积数据**（Volumetric Data）的能力。Dataflow 是一个基于节点的可视化数据流图系统，而此插件专门提供了用于创建、操作和渲染体积（如 SDF 有符号距离场）的节点。

它解决的核心问题是：**如何在 Dataflow 的节点图框架内，方便地构建和处理三维体积数据**。这使得开发者或技术美术可以通过连接节点的方式，程序化地生成和修改体积效果（如地形变形、体积雾、粒子效果等），而无需编写复杂的底层代码。

## 使用场景

- 你需要通过节点图程序化地生成一个球体或立方体的 SDF（有符号距离场）体积，用于后续的体积渲染或物理交互。
- 你正在使用 Dataflow 系统构建一个动态的、基于节点的效果管线，并希望将体积数据（如密度场、温度场）作为管线中的数据类型进行传递和处理。
- 你希望在编辑器中可视化调试体积数据，例如查看 SDF 的等值面或体素分布。

## 蓝图用法

该插件主要通过 Dataflow 节点图进行操作，其节点在蓝图中体现为可连接的 Dataflow 节点。核心功能通过 `USTRUCT` 定义的节点结构体暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeSDFSphere` | 生成一个球体形状的 SDF 浮点体积 | `FMakeSDFSphereDataflowNode` |
| `MakeSDFCube` | 生成一个立方体形状的 SDF 浮点体积 | `FMakeSDFCubeDataflowNode` |
| *(更多节点...)* | *根据头文件截断，应包含其他体积生成、操作节点* | |

### 使用示例（蓝图描述）

1.  在 Dataflow 编辑器中，从节点列表的 **“Volume|Generators”** 分类下找到 **“MakeSDFSphere”** 节点并添加到图中。
2.  在节点的细节面板中，设置 **VoxelSize**（体素大小）、**Radius**（半径）和 **Center**（中心点）等参数。这些参数也可以通过输入引脚连接其他节点的输出来动态控制。
3.  该节点的输出引脚 **“FloatVolume”** 会生成一个 `FDataflowFloatVolume` 类型的数据，代表生成的 SDF 体积。
4.  将此输出连接到其他体积处理节点（如布尔运算、变换）或最终的体积渲染节点，以完成整个效果管线。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowVolumeNodes.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建并使用一个 `MakeSDFSphere` 节点来生成体积数据。

```cpp
// 假设在一个 Dataflow 图的评估函数或自定义工具中
#include "Dataflow/DataflowVolumeNodes.h"
#include "Dataflow/DataflowEngine.h"

void GenerateSphereVolume()
{
    // 1. 创建节点实例
    FMakeSDFSphereDataflowNode SphereNode(UE::Dataflow::FNodeParameters());
    
    // 2. 设置节点参数（通过 FProperty 或直接访问成员）
    // 注意：在实际 Dataflow 图中，参数通常通过连接或细节面板设置。
    // 这里直接设置成员变量仅为演示。
    SphereNode.VoxelSize = 0.5f;
    SphereNode.Radius = 10.0f;
    SphereNode.Center = FVector(0, 0, 0);
    
    // 3. 创建上下文并评估节点
    UE::Dataflow::FContext Context;
    // 评估节点，结果将存储在 SphereNode.FloatVolume 中
    SphereNode.Evaluate(Context, nullptr);
    
    // 4. 使用生成的体积数据
    FDataflowFloatVolume& GeneratedVolume = SphereNode.FloatVolume;
    // ... 对 GeneratedVolume 进行后续操作，例如传递给渲染器或其他节点
}
```

### 进阶用法

结合多个节点构建一个简单的体积处理管线。

```cpp
// 伪代码，展示节点连接思想
void BuildVolumePipeline()
{
    // 创建生成器节点
    FMakeSDFSphereDataflowNode SphereNode(...);
    FMakeSDFCubeDataflowNode CubeNode(...);
    
    // 创建一个假设的布尔运算节点（需根据实际插件API）
    // FDataflowVolumeBooleanNode BooleanNode(...);
    
    // 在 Dataflow 图中，通过 FDataflowConnection 将 SphereNode 的输出
    // 连接到 BooleanNode 的一个输入，将 CubeNode 的输出连接到另一个输入。
    // 然后评估 BooleanNode，即可得到两个体积的布尔运算结果。
}
```

## Demo 示例

以下是一个最小化的 Actor 示例，演示如何在运行时通过代码触发 Dataflow 体积节点的评估。

```cpp
// MyVolumetricActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVolumetricActor.generated.h"

UCLASS()
class AMyVolumetricActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyVolumetricActor();

protected:
    virtual void BeginPlay() override;

public:
    // 用于存储生成的体积数据
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Volume")
    FDataflowFloatVolume CurrentVolume;
};
```

```cpp
// MyVolumetricActor.cpp
#include "MyVolumetricActor.h"
#include "Dataflow/DataflowVolumeNodes.h"
#include "Dataflow/DataflowEngine.h"

AMyVolumetricActor::AMyVolumetricActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyVolumetricActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个球体 SDF 节点
    FMakeSDFSphereDataflowNode SphereNode(UE::Dataflow::FNodeParameters());
    SphereNode.VoxelSize = 1.0f;
    SphereNode.Radius = 50.0f;
    SphereNode.Center = GetActorLocation();

    // 评估节点
    UE::Dataflow::FContext Context;
    SphereNode.Evaluate(Context, nullptr);

    // 将结果保存到成员变量
    CurrentVolume = SphereNode.FloatVolume;

    UE_LOG(LogTemp, Log, TEXT("Generated SDF Sphere Volume with %d voxels."), CurrentVolume.GetNumVoxels());
    // 此时，CurrentVolume 包含了球体 SDF 数据，可用于后续的体积渲染或计算。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 核心依赖，提供 Dataflow 节点图、上下文和基础类型 |
| `DataflowRendering` | 用于体积数据的可视化渲染设置（如 `UDataflowVolumeRenderSettings`） |

## 维护状态

### 近期更新

*（由于未提供 git log 信息，无法列出具体 commit。基于创建时间推断）*
- 2026-01-24 插件初始创建，包含基础体积生成节点和渲染设置。

### 维护评价

- **创建时间**：2026 年 1 月，非常新的插件。
- **实验性状态**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`Installed: false`)。这表明该插件仍处于早期实验阶段，API 和功能可能会发生重大变化。
- **维护活跃度**：作为实验性新插件，预计仍在积极开发中，但稳定性未经验证。
- **已知限制**：作为实验性功能，可能存在性能问题、功能缺失或与未来引擎版本不兼容的风险。
- **推荐使用**：**仅推荐用于学习、研究或原型开发**。不建议在正式生产项目中依赖此插件，除非你愿意承担其可能带来的不稳定性和维护成本。请密切关注 Epic Games 的官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DataflowVolumetricPlugin)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现）