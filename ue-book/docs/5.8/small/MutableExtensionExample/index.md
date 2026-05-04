# Mutable Extension Example

> Example plugin which adds new external operations to Mutable.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableExtensionExample` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableExtensionExample) | |

## 用途

此插件并非一个通用工具，而是作为 **Mutable 外部操作（External Operations）** 的官方示例。它演示了如何通过继承 `UE::Mutable::FExternalOperation` 基类，为 Mutable 可定制对象系统添加自定义的网格处理节点。插件本身提供了三个具体的网格操作示例：裁剪、恒等变换和添加噪声，旨在帮助开发者学习如何扩展 Mutable 的功能。

## 使用场景

- 你需要为 Mutable 可定制对象系统添加一个自定义的网格处理步骤（例如，特殊的裁剪、变形或生成效果）。
- 你正在学习如何开发 Mutable 的外部操作，并希望参考官方示例代码。
- 你需要一个简单的网格噪声生成或基于球体的裁剪功能，并希望将其集成到 Mutable 工作流中。

## 蓝图用法

此插件中的操作以 `USTRUCT` 形式定义，并在 **Mutable 可定制对象编辑器** 中作为节点使用，而非在普通蓝图图表中直接调用。

### 核心节点（在 Mutable 编辑器中）

| 节点 | 说明 | 所在结构体 |
|---|---|---|
| `Mesh Clip With Sphere` | 使用一个球体裁剪输入网格。 | `FMeshClipSphere` |
| `Mesh Identity` | 恒等操作，直接返回输入网格（用于测试或流程占位）。 | `FMeshIdentity` |
| `Mesh Noise` | 为输入网格的顶点添加基于种子的噪声位移。 | `FMeshNoise` |

### 使用示例（在 Mutable 编辑器中）

1.  在你的 **Customizable Object** 蓝图中，右键点击并搜索 “Mesh Clip With Sphere”、“Mesh Identity” 或 “Mesh Noise” 节点。
2.  将一个网格输出引脚连接到该节点的 `Input Mesh` 输入引脚。
3.  对于 `Mesh Clip With Sphere`，还需要提供一个 `Sphere` 参数（类型为 `FPrimitiveSphere`）。
4.  对于 `Mesh Noise`，可以在节点的细节面板中设置 `Seed` 常量值。
5.  将该节点的输出连接到后续的网格处理节点或最终输出。

## C++ 用法

### 头文件引入

```cpp
#include "MeshClipSphere.h"
#include "MeshIdentity.h"
#include "MeshNoise.h"
#include "PrimitiveSphere.h"
```

### 基本用法

定义一个自定义的外部操作，需要继承 `UE::Mutable::FExternalOperation` 并实现其虚函数。以下是一个简化示例，展示了 `FMeshNoise` 的核心结构。

```cpp
// 来自 Source/MutableExtensionExample/Public/MeshNoise.h
USTRUCT(DisplayName = "Mesh Noise")
struct FMeshNoise : public UE::Mutable::FExternalOperation
{
    GENERATED_BODY()

    // 声明输入和输出
    virtual TArray<TPair<FText, const UScriptStruct*>> GetInputs() const override;
    virtual TPair<FText, const UScriptStruct*> GetOutput() const override;

    // 实现评估逻辑
    virtual void Evaluate(UE::Mutable::FContext& Context) const override;

    // 输入引脚的标识文本
    const static FText TextInputMesh;
    const static FText TextInputFactor;

    // 编辑器中可配置的常量参数
    UPROPERTY(EditAnywhere, Category = "Mesh Noise")
    int32 Seed = 0;
};
```

### 进阶用法

在 `Evaluate` 函数中，你需要从 `Context` 获取输入数据，进行处理，然后将结果设置回 `Context`。以下是一个概念性的实现框架：

```cpp
void FMeshNoise::Evaluate(UE::Mutable::FContext& Context) const
{
    // 1. 从上下文中获取输入网格
    //    (具体API需参考Mutable SDK文档)
    //    const FMesh* InputMesh = Context.GetInputMesh(TextInputMesh);

    // 2. 获取其他输入（如因子）
    //    const float* Factor = Context.GetInputScalar(TextInputFactor);

    // 3. 执行你的自定义网格处理逻辑
    //    FMesh* ResultMesh = ApplyNoiseToMesh(InputMesh, Seed, Factor);

    // 4. 将结果设置回上下文
    //    Context.SetOutputMesh(ResultMesh);
}
```

## Demo 示例

以下是一个最小的自定义外部操作示例，它简单地将输入网格的顶点位置乘以一个缩放因子。

**MyScaleMeshOperation.h**
```cpp
#pragma once

#include "MuR/External/Operation.h"
#include "MyScaleMeshOperation.generated.h"

USTRUCT(DisplayName = "Scale Mesh")
struct FMyScaleMeshOperation : public UE::Mutable::FExternalOperation
{
    GENERATED_BODY()

    virtual TArray<TPair<FText, const UScriptStruct*>> GetInputs() const override;
    virtual TPair<FText, const UScriptStruct*> GetOutput() const override;
    virtual void Evaluate(UE::Mutable::FContext& Context) const override;

    const static FText TextInputMesh;
    const static FText TextInputScaleFactor;

    UPROPERTY(EditAnywhere, Category = "Scale")
    FVector Scale = FVector(1.0f, 1.0f, 1.0f);
};
```

**MyScaleMeshOperation.cpp**
```cpp
#include "MyScaleMeshOperation.h"

const FText FMyScaleMeshOperation::TextInputMesh = NSLOCTEXT("MyOps", "InMesh", "Input Mesh");
const FText FMyScaleMeshOperation::TextInputScaleFactor = NSLOCTEXT("MyOps", "InScale", "Scale Factor");

TArray<TPair<FText, const UScriptStruct*>> FMyScaleMeshOperation::GetInputs() const
{
    return { {TextInputMesh, FMesh::StaticStruct()} };
}

TPair<FText, const UScriptStruct*> FMyScaleMeshOperation::GetOutput() const
{
    return { TextInputMesh, FMesh::StaticStruct() };
}

void FMyScaleMeshOperation::Evaluate(UE::Mutable::FContext& Context) const
{
    // 此处为示意代码，具体API需查阅Mutable SDK
    // const FMesh* InMesh = Context.GetInputMesh(TextInputMesh);
    // if (InMesh)
    // {
    //     FMesh* OutMesh = DuplicateMesh(InMesh);
    //     for (FVector& Vertex : OutMesh->Vertices)
    //     {
    //         Vertex *= Scale;
    //     }
    //     Context.SetOutputMesh(OutMesh);
    // }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mutable` | 核心依赖，提供 `FExternalOperation` 基类和 Mutable 运行时/编辑器框架。 |

## 维护状态

### 近期更新

- 2026-03-06 71ad860d [Mutable] Added AssetUserData type and nodes.
- 2025-10-15 270279df [Mutable] InstancedStruct Parameter.
- 2025-09-24 207bf71b [Mutable] Fix multiple issues with External Operations.

### 维护评价

- **创建时间**：2025年9月，非常新的插件。
- **更新频率**：创建后一个月内有多次提交，包括功能添加和问题修复，近期（2026年3月）仍有更新，表明其作为Mutable系统扩展示例在持续维护。
- **活跃状态**：**活跃维护中**。作为Mutable系统的官方示例，其更新与Mutable核心功能的演进保持同步。
- **已知限制**：这是一个**示例插件**，其代码主要用于教学和演示目的，不建议直接用于生产环境。生产环境应基于此示例开发自己的、经过充分测试的外部操作。
- **推荐使用**：**强烈推荐**给所有需要学习或开发Mutable外部操作的开发者。它是理解该扩展机制的最佳起点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableExtensionExample)
- [官方文档]() （无）
- [测试用例]() （无）