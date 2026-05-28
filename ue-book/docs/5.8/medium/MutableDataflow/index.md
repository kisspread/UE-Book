# Mutable Dataflow Extensions

> Adds Mutable functionality to work with Dataflow objects from the Dataflow plugin. WARNING: All nodes in this plugin are experimental and will be changed/deprecated in the future. The Dataflow system does not yet fully support mutable so the functionality of these nodes is currently quite limited and manual.

| 属性 | 值 |
|---|---|
| 中文名 | 可变数据流扩展 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MutableDataflowEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableDataflow) | |

## 用途

这个插件解决的核心问题是：**如何在 Unreal Engine 的 Dataflow（数据流）图形化编程系统中驱动 Mutable（可变形对象）系统**。

Mutable 是 Unreal Engine 中用于实时生成复杂、可定制化资产（如带换装系统的角色）的强大系统。Dataflow 是一种基于节点的可视化编程框架。`MutableDataflow` 插件充当了两者之间的桥梁，它提供了一套专用的 Dataflow 节点，允许用户通过连接节点的方式，将各种参数（如网格体、材质、布尔值等）组合起来，最终驱动一个 `CustomizableObjectInstance` 生成包含指定组件的 `SkeletalMesh` 资源。

简而言之，它为 Mutable 系统提供了一个图形化、节点化的工作流，使其能更直观地集成到需要复杂数据流逻辑的项目中。

## 使用场景

- **角色定制/换装系统的可视化逻辑搭建**：当你需要通过一个可视化的节点图来决定角色身上的不同部件（头、身体、武器）和材质时，可以使用此插件中的参数节点来组合各种输入，然后连接到生成器节点来生成最终的角色网格体。
- **程序化内容生成 (PCG) 中的资产驱动**：在 Dataflow 或 PCG 图中，根据环境或游戏逻辑动态生成并组装可定制化资产。
- **编辑器工具开发**：需要为设计师提供一个节点界面，让他们无需编写代码就能预览和测试不同参数组合下生成的角色外观。

## 蓝图用法

**注意**：此插件的节点主要作为 Dataflow 图中的节点使用，而非传统意义上的蓝图节点。它们在 Dataflow 编辑器中被使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCustomizableObjectInstance` | **核心生成器节点**。作为 Mutable 在 Dataflow 图中的入口点，负责配置可定制化对象实例 (COI)、接收所有参数、触发资源编译与更新，并输出生成的网格体资源。 | `FCOInstanceGeneratorNode` |
| `GetComponentMesh` | 从生成器输出的资源数组中，根据组件名称提取特定的骨架网格体。 | `FCOInstanceGetComponentMesh` |
| `Mutable<类型>Parameter` | **参数创建节点家族**（如 `MutableSkeletalMeshParameter`, `MutableBoolParameter`）。用于将单个输入值（网格体、布尔值、浮点数等）与一个参数名打包，创建一个可传递给生成器节点的参数结构体。 | `FMutable<类型>ParameterNode` |
| `MakeMutable<类型>ParametersArray` | **参数数组组合节点家族**（如 `MakeMutableSkeletalMeshParametersArray`）。接受多个参数结构体输入，将它们组合成一个数组，以便一次性传递给生成器节点的对应输入引脚。支持动态添加/移除输入引脚。 | `FMakeMutable<类型>ParametersArrayNode` |

### 使用示例（蓝图描述）

1.  **创建参数**：在 Dataflow 图中，添加一个 `MutableSkeletalMeshParameter` 节点。在它的输入引脚设置 `ParameterName` (例如 “Head”)，并从资产浏览器拖入一个 `SkeletalMesh` 连接到它的 `SkeletalMesh` 输入引脚。该节点的输出引脚 `SkeletalMeshParameter` 会输出一个包含名称和网格体引用的结构体。
2.  **组合参数**：添加一个 `MakeMutableSkeletalMeshParametersArray` 节点。将步骤1中参数节点的输出连接到它的第一个输入引脚。你可以右键点击该数组节点添加更多引脚，连接其他参数节点（如身体、手臂等），从而创建一个网格体参数数组。
3.  **设置生成器**：添加 `GenerateCustomizableObjectInstance` 节点。
    - 将 `CustomizableObject` 引用连接到它的对应输入引脚。
    - 将步骤2中创建的参数数组连接到它的 `SkeletalMeshParameters` 输入引脚。
    - 可以类似地连接其他类型的参数数组（`BoolParameters`, `TextureParameters` 等）。
4.  **生成与输出**：在 `GenerateCustomizableObjectInstance` 节点的细节面板中，点击 **Generate Resources** 按钮。节点将编译关联的可定制化对象并更新实例。完成后，其 `GeneratedResources` 或 `GeneratedSkeletalMeshes` 输出引脚将提供生成的资产。
5.  **提取资源**：将生成器的 `GeneratedResources` 输出连接到 `GetComponentMesh` 节点的输入，并在该节点上设置要提取的 `ComponentName`，即可得到最终的 `SkeletalMesh`。

## C++ 用法

此插件主要提供 Dataflow 节点，通常在编辑器模块内使用。其 API 以结构体 (USTRUCT) 和参数类型为主。

### 头文件引入

```cpp
#include "MutableDataflowParameters.h" // 包含所有参数结构体定义
#include "Nodes/COInstanceGeneratorNode.h" // 包含核心生成器节点
```

### 基本用法（定义参数）

你需要了解插件提供的参数结构体，以便在 C++ 中构建 Dataflow 节点的输入数据。

**文件路径**: `Source/MutableDataflowEditor/Public/MutableDataflowParameters.h`

```cpp
// 示例：创建一个布尔参数
FMutableBoolParameter MyBoolParam;
MyBoolParam.Name = “EnableHat”; // 参数名，需要与可定制化对象中的参数名对应
MyBoolParam.Bool = true; // 参数值

// 示例：创建一个骨骼网格体参数
FMutableSkeletalMeshParameter MeshParam;
MeshParam.Name = “SwordMesh”;
MeshParam.Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT(“/Game/Meshes/Sword_Skel”));

// 示例：创建一个浮点参数
FMutableFloatParameter FloatParam;
FloatParam.Name = “SkinBrightness”;
FloatParam.Float = 0.75f;

// 这些参数结构体通常被组合成数组（TArray），并传递给 FCOInstanceGeneratorNode 的输入属性。
```

### 进阶用法（理解生成器节点流程）

虽然直接实例化 `FCOInstanceGeneratorNode` 不常见（它通常由 Dataflow 框架管理），但理解其内部流程有助于调试。

**文件路径**: `Source/MutableDataflowEditor/Public/Nodes/COInstanceGeneratorNode.h`

其核心流程（`Evaluate` 方法内部或按钮回调中）大致为：
1.  **`CacheNodeInputs`**: 从连接的输入引脚读取所有参数数组到本地缓存。
2.  **`RequestCompilation`**: 确保关联的 `UCustomizableObject` 已编译。
3.  **`ApplyInstanceParameters`**: 将缓存的参数应用到一个 `UCustomizableObjectInstance` 上。
4.  **`RequestUpdate`**: 触发该实例的异步更新，生成新资源。
5.  **`GetInstanceGeneratedMeshes`**: 更新完成后，从实例中提取各组件的网格体作为输出。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义参数结构体并模拟为生成器节点准备数据。

**.h 文件 (示例)**
```cpp
// MutableDataflowDemoNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "MutableDataflowParameters.h" // 引入参数类型

USTRUCT()
struct FMutableDataflowDemoNode : public FDataflowNode
{
	GENERATED_USTRUCT_BODY()

	// 模拟一些输入参数
	UPROPERTY()
	TArray<FMutableBoolParameter> BoolParams;
	
	UPROPERTY()
	TArray<FMutableFloatParameter> FloatParams;

	// 模拟输出（这里简化，实际生成器输出的是网格体资源）
	UPROPERTY(meta=(DataflowOutput))
	FString StatusMessage;

	virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

**.cpp 文件 (示例)**
```cpp
// MutableDataflowDemoNode.cpp
#include “MutableDataflowDemoNode.h”

void FMutableDataflowDemoNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
	// 模拟从输入引脚获取参数值
	const TArray<FMutableBoolParameter>& Bools = GetValue(Context, &BoolParams);
	const TArray<FMutableFloatParameter>& Floats = GetValue(Context, &FloatParams);
	
	// 构建一个简单的状态信息
	FString Result = FString::Printf(TEXT(“Received %d bool and %d float parameters.”), Bools.Num(), Floats.Num());
	
	for (const FMutableBoolParameter& BParam : Bools)
	{
		Result += FString::Printf(TEXT(“\n  %s: %s”), *BParam.Name, BParam.Bool ? TEXT(“True”) : TEXT(“False”));
	}
	
	// 设置输出
	SetValue(Context, Result, &StatusMessage);
}
```

## 模块依赖

你的项目模块如果需要以编程方式使用此插件定义的类型（如参数结构体），需要在 `.Build.cs` 文件中添加依赖。

| 模块 | 用途 |
|---|---|
| `MutableDataflowEditor` | 插件自身模块，包含所有节点和参数定义。 |
| `Mutable` | 核心的 Mutable 可变形对象系统。 |
| `Dataflow` | 核心的 Dataflow 数据流图形系统。 |
| `CustomizableObject` | Mutable 系统中可定制化对象的核心模块（由 `Mutable` 模块依赖，但理解其类型如 `UCustomizableObjectInstance` 很重要）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-17 | `49f946b4` | [Dataflow] | 涉及 Dataflow 系统的整体性更新。 |
| 2025-10-28 | `e16635d0` | [mutable] Added support for FInstanecdStructs as parameters of the COI | 新增了对实例化结构体 (FInstancedStruct) 作为可定制化对象参数的支持。 |
| 2025-10-24 | `241b362c` | [mutable] Dataflow Instanced Struct Parameters. | 在 Dataflow 中实现了实例化结构体参数的节点支持。 |
| 2025-10-16 | `fd81a6c0` | [mutable] Added multiple mutable parameter type supporting nodes to be used within Dataflow graphs | 添加了多种 Mutable 参数类型的支持节点，用于在 Dataflow 图中使用。 |
| 2025-09-04 | `364681cb` | [mutable-Dataflow] Set the MutableDataflow plugin disabled by default | 将 MutableDataflow 插件的默认启用状态设为禁用。 |

### 维护评价

- **创建时间**: 该插件非常新，创建于 2025 年 8 月底。
- **活跃度**: 从提交记录看，在创建后的几个月内（至 2025 年 10 月）有持续的功能添加和调整，表明其处于早期活跃开发阶段。2026 年的更新可能关联到底层系统的变动。
- **状态**: **实验性 (Experimental)**。插件描述和代码元数据都明确标记为实验性，且默认禁用。这意味着其 API、节点行为和功能范围在未来版本中可能发生重大变化、被重构或废弃。
- **推荐**: 目前不建议在需要长期稳定性的正式项目中依赖此插件。它更适合用于原型验证、技术预研或内部工具开发，以便提前探索 Mutable 与 Dataflow 结合的工作流。使用时需做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MutableDataflow)
- [官方文档](https://docs.unrealengine.com/)（暂无专用文档）
- 测试用例：未在提供的信息中发现专用测试文件。