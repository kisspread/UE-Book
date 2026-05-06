# GeometryFlow

> Geometry DataFlow Graph

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流图 |
| 分类 | Geometry |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryFlowCore` (Runtime), `GeometryFlowMeshProcessing` (Runtime), `GeometryFlowMeshProcessingEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow) | |

## 用途

GeometryFlow 是 UE5 中基于数据流图（DataFlow）的几何处理框架。它将几何处理任务（如 UV 自动生成、网格简化、重拓扑等）抽象为有向无环图中的节点，用户或系统可以通过连接节点构建处理管线，实现灵活、可复用的几何计算流程。

该插件主要面向程序化几何处理、编辑器工具和自动化管线场景，利用 UE5 自带的 GeometryProcessing 库和 ModelingToolset 提供底层算法。

| 模块 | 说明 |
|---|---|
| `GeometryFlowCore` | 数据流框架核心，定义图、节点、数据类型的基类 |
| `GeometryFlowMeshProcessing` | 网格处理节点实现，如 UV 生成、重网格等 |
| `GeometryFlowMeshProcessingEditor` | 编辑器集成，提供节点注册、序列化支持、编辑器 UI 联动 |

当前模块文档基于 **`GeometryFlowMeshProcessingEditor`**（编辑器模块），提供 UV 自动生成节点的编辑器支持。

## 使用场景

- 你正在开发一个程序化建模工具，需要自动生成或优化模型的 UV 布局。
- 你需要将多个几何处理步骤（如重拓扑→UV 生成→材质分配）组合成一个可配置的管线。
- 你在编辑器内需要直观调整 UV 生成参数，并实时预览效果（需搭配 ModelingTools 编辑器基础设施）。

## 蓝图用法

以下 API 来自 `GeometryFlowMeshProcessingEditor` 模块，主要用于配置 UV 自动生成节点。

### 核心枚举与结构体

| 类型 | 说明 | 所在文件 |
|---|---|---|
| `EGeometryFlow_AutoUVMethod` | UV 展开方法：`PatchBuilder`、`UVAtlas`、`XAtlas` | `MeshAutoGenerateUVsNode.h` |
| `FMeshAutoGenerateUVsSettings` | UV 生成参数结构体，所有属性均可蓝图读写 | `MeshAutoGenerateUVsNode.h` |

### 设置属性

`FMeshAutoGenerateUVsSettings` 中所有 `UPROPERTY(EditAnywhere, Category = "Geometry Flow")` 属性均可通过蓝图进行读写和显示。

| 属性 | 类型 | 说明 |
|---|---|---|
| `Method` | `EGeometryFlow_AutoUVMethod` | UV 展开算法 |
| `UVAtlasStretch` | `double` | UVAtlas 拉伸容忍度，值越大允许越少拉伸 |
| `UVAtlasNumCharts` | `int` | UVAtlas 最大图表数（0 表示自动） |
| `XAtlasMaxIterations` | `int` | XAtlas 最大迭代次数 |
| `NumInitialPatches` | `int` | PatchBuilder 初始 Patch 数 |
| `CurvatureAlignment` | `double` | PatchBuilder 曲率对齐权重 |
| `MergingThreshold` | `double` | PatchBuilder 合并阈值 |
| `MaxAngleDeviationDeg` | `double` | PatchBuilder 最大角度偏差（度） |
| `SmoothingSteps` | `int` | PatchBuilder 平滑步数 |
| `SmoothingAlpha` | `double` | PatchBuilder 平滑 alpha |
| `bAutoPack` | `bool` | 是否自动打包 UV |
| `PackingTargetWidth` | `int` | 打包目标宽度（像素） |

### 使用示例（蓝图描述）

1. 创建一个自定义用户数据/类型（例如将 `FMeshAutoGenerateUVsSettings` 作为行结构体）。
2. 在构建数据流图时，创建一个 `FMeshAutoGenerateUVsNode`（对应蓝图节点为 `Mesh Auto Generate UVs`，需要配合 GeometryFlow 图编辑界面）。
3. 将设置结构体作为输入连接到节点，该节点会输出处理后的网格数据。
4. 节点执行由内部图引擎驱动，蓝图只需配置参数即可。

> 注意：GeometryFlow 节点通常不直接暴露为独立蓝图函数，而是作为数据流图的一部分在编辑器工具 UI 中配置。当前模块主要提供编辑器中的节点注册与序列化支持。

## C++ 用法

### 头文件引入

```cpp
#include "MeshProcessingNodes/MeshAutoGenerateUVsNode.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建和配置 UV 自动生成节点。

```cpp
// 来源：Engine/Plugins/Experimental/GeometryFlow/Source/GeometryFlowMeshProcessingEditor/Public/MeshProcessingNodes/MeshAutoGenerateUVsNode.h

// 1. 创建设置结构体
FMeshAutoGenerateUVsSettings UVSettings;
UVSettings.Method = EGeometryFlow_AutoUVMethod::PatchBuilder;
UVSettings.NumInitialPatches = 100;
UVSettings.CurvatureAlignment = 1.0;

// 2. 创建 UV 自动生成节点
FMeshAutoGenerateUVsNode UVNode;

// 3. 设置节点参数
UVNode.SetSettings(UVSettings);

// 4. 节点注册（必需，用于序列化）
FMeshProcessingEditorNodeRegistration::RegisterNodes();
```

### 进阶用法

将 UV 自动生成节点集成到更大的数据流图中：

```cpp
// 来源：Engine/Plugins/Experimental/GeometryFlow/Source/GeometryFlowMeshProcessingEditor/Private/...（假设示例）

// 1. 创建数据流图
TUniquePtr<FDataFlowGraph> Graph = MakeUnique<FDataFlowGraph>();

// 2. 添加源节点（如网格输入）和 UV 生成节点
auto SourceNode = Graph->AddNode<FMeshSourceNode>(...);
auto UVNode = Graph->AddNode<FMeshAutoGenerateUVsNode>(...);

// 3. 连接节点
Graph->Connect(SourceNode, 0, UVNode, 0);

// 4. 设置 UV 参数
UVNode->SetSettings(FMeshAutoGenerateUVsSettings());

// 5. 执行图
Graph->Evaluate();
```

## Demo 示例

一个最小化 C++ 示例，展示如何注册并使用 UV 自动生成节点。

**MyGeometryFlowActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MeshProcessingNodes/MeshAutoGenerateUVsNode.h"
#include "MyGeometryFlowActor.generated.h"

UCLASS()
class AMyGeometryFlowActor : public AActor
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "GeometryFlow")
	void GenerateUV(const FMeshAutoGenerateUVsSettings& Settings);
};
```

**MyGeometryFlowActor.cpp**
```cpp
#include "MyGeometryFlowActor.h"
#include "MeshProcessingNodes/MeshAutoGenerateUVsNode.h"
#include "MeshProcessingEditorNodeRegistration.h"

void AMyGeometryFlowActor::GenerateUV(const FMeshAutoGenerateUVsSettings& Settings)
{
	// 注册节点（仅需执行一次）
	static bool bRegistered = false;
	if (!bRegistered)
	{
		UE::GeometryFlow::FMeshProcessingEditorNodeRegistration::RegisterNodes();
		bRegistered = true;
	}

	// 创建设置并传递给节点
	FMeshAutoGenerateUVsNode UVNode;
	UVNode.SetSettings(Settings);

	// 示例：此处应由真正的数据流图驱动，节点还需连接输入网格
	UE_LOG(LogTemp, Log, TEXT("UV生成参数已设置：Method=%d"), (int)Settings.Method);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 底层几何算法库（网格数据结构、UV 展开算法、重拓扑等） |
| `MeshModelingToolsetExp` | 建模工具集实验模块，提供编辑器交互和序列化基础设施 |
| `GeometryFlowCore` | 数据流图核心框架 |
| `GeometryFlowMeshProcessing` | 网格处理节点基类和通用节点 |
| `GeometryFlowMeshProcessingEditor` | 当前模块自身，依赖上述模块 |

> 常见依赖（Core, Engine, Slate 等）未列出。

## 维护状态

### 近期更新

- 2025-07-10 `9803c443` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files.
- 2025-05-31 `52e3dac1` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types.
- 2024-12-16 `dbb51bc5` GeometryFlow: clean-up node registration.
- 2024-12-13 `1d69cf7b` Geometry Processing Unit Tests: eliminate warnings and other problems in preparation for enabling them.
- 2024-11-10 `66e9bb39` Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base.

### 维护评价

- **创建时间**：2024-11-10，距今约 8 个月（不足一年）。
- **更新频率**：最近 7 个月内共有 4 次提交，涉及代码清理、模块注册优化、单元测试修复等，但**无功能性新增**。
- **活跃度**：维护频率中等，主要跟随 UE 主仓库的编译和 API 变化进行适配。由于该插件标记为 `Experimental` 且 `Hidden`，目前并非核心功能，可能存在 API 不稳定、文档不全等问题。
- **推荐使用**：适合对数据流图框架有深度需求的团队，但建议仅在编辑器工具中使用，并做好版本锁定。如果只是简单的 UV 生成，可考虑使用更成熟的 `MeshModelingToolsetExp` 中的直接算法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryFlow)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/)（目前无独立页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/GeometryFlow)（可能存在，待确认）