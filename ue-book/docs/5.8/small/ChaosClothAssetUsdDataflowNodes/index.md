# Chaos Cloth Asset USD Dataflow Nodes

> Dataflow nodes for importing USD Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | Chaos布料USD数据流节点 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetUsdDataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) | |

## 用途

该插件提供了一组 **Dataflow 节点**，用于将第三方服装制作软件（如 CLO3D、Marvelous Designer 等）导出的 **USD 布料资产**导入到 UE5 的 Chaos 布料系统中。

核心功能是将 USD 文件中的模拟网格（Simulation Mesh）和渲染网格（Render Mesh）数据转换为 `FManagedArrayCollection` 格式的布料集合，供 Chaos Cloth Asset Dataflow 图使用。它作为 `ChaosClothAssetDataflowNodes` 的扩展，专注于 USD 格式的导入流程，支持两种 USD 布料 Schema：旧版无 Schema 格式和新版有效布料 Schema 格式。

## 使用场景

- 你在使用 CLO3D 或 Marvelous Designer 制作服装，需要将布料资产以 USD 格式导入 UE5
- 你正在使用 Chaos Cloth Asset 的 Dataflow 图进行布料资产制作，需要从外部 USD 文件读取网格数据
- 你需要分别导入模拟网格和渲染网格，并控制透明度等高级选项
- 你希望在 Dataflow 图中实现 USD 布料资产的自动化导入流程

## 蓝图用法

该插件的核心是一个 Dataflow 结构体节点，通过 Unreal 的 Dataflow 框架在蓝图/数据流图编辑器中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USDImport` | 从 USD 文件导入布料数据，输出布料集合 | `FChaosClothAssetUSDImportNode_v3` |
| `Reimport` | 重新导入指定的 USD 文件并重新生成中间资产 | `FChaosClothAssetUSDImportNode_v3` |
| `ReloadSimMesh` | 仅重新加载模拟网格，不重新导入 USD 文件 | `FChaosClothAssetUSDImportNode_v3` |
| `ReloadRenderMesh` | 仅重新加载渲染网格，不重新导入 USD 文件 | `FChaosClothAssetUSDImportNode_v3` |

### 节点属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `bImportSimMesh` | `bool` | 是否导入模拟网格数据（默认开启） |
| `bImportRenderMesh` | `bool` | 是否导入渲染网格数据（默认开启） |
| `bImportWithOpacity` | `bool` | 是否带透明度导入渲染网格（需项目设置中启用半透明） |
| `UsdFile` | `FChaosClothAssetImportFilePath` | 要导入的 USD 文件路径 |

### 使用示例（蓝图描述）

1. 在 **Dataflow Graph Editor** 中创建一个 **Cloth USD Import** 节点（搜索 "USDImport"）
2. 在节点的 **USD File** 属性中选择你的 `.usd` / `.usda` / `.usdc` 文件路径
3. 根据需要勾选 **Import Sim Mesh**（模拟网格）和 **Import Render Mesh**（渲染网格）
4. 如果需要透明度支持（如透明纱质面料），勾选 **Import With Opacity**
5. 点击 **Reimport USD File** 按钮执行导入
6. 节点的 **Collection** 输出端口会输出 `FClothCollection` 数据，连接到后续的布料处理节点

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/USDImportNode_v3.h"
```

### 基本用法

通过 Dataflow 框架直接使用导入节点结构体：

```cpp
#include "ChaosClothAsset/USDImportNode_v3.h"
#include "Dataflow/DataflowContext.h"

// 获取 Dataflow 图中的 USD Import 节点并配置属性
// FChaosClothAssetUSDImportNode_v3 是 Dataflow 节点，通常在 Dataflow Graph Editor 中使用
// 以下展示程序化设置节点属性的方式

// 创建节点参数
UE::Dataflow::FNodeParameters Params;
FChaosClothAssetUSDImportNode_v3 ImportNode(Params);

// 设置 USD 文件路径
ImportNode.UsdFile = FChaosClothAssetImportFilePath{TEXT("/Game/ClothAssets/MyGarment.usd")};

// 配置导入选项
ImportNode.bImportSimMesh = true;   // 导入模拟网格
ImportNode.bImportRenderMesh = true; // 导入渲染网格
ImportNode.bImportWithOpacity = false; // 不导入透明度数据
```

### 使用 UsdPrimAttributeAccessor 辅助类

当需要直接访问 USD Prim 属性数据时：

```cpp
#include "ChaosClothAsset/UsdPrimAttributeAccessor.h"

// 创建属性访问器，指定 USD 坐标系（Z 轴或 Y 轴向上）
UE::Chaos::ClothAsset::FUsdPrimAttributeAccessor Accessor(UsdPrim, EUsdUpAxis::ZAxis);

// 获取单个属性值
uint32 VertexCount = Accessor.GetValue<uint32>(TEXT("vertexCount"), 0);
float Density = Accessor.GetValue<float>(TEXT("density"), 1.0f);
FVector3f Gravity = Accessor.GetValue<FVector3f>(TEXT("gravity"), FVector3f(0.f, 0.f, -980.f));

// 获取数组属性
TArray<float> RestLengths = Accessor.GetArray<float>(TEXT("restLengths"));

// 通过索引获取数组中的特定值
float FirstLength = Accessor.GetArrayValue<float>(TEXT("restLengths"), 0.0f, 0);
```

## Demo 示例

以下展示如何创建一个自定义 Dataflow 节点来处理导入的布料数据：

**CustomClothProcessor.h**
```cpp
#pragma once

#include "Dataflow/DataflowNode.h"
#include "ManagedArrayCollection/ManagedArrayCollection.h"

// 自定义节点：处理导入的 USD 布料数据
USTRUCT(Meta = (DataflowCloth))
struct FCustomClothProcessorNode : public FDataflowNode
{
	GENERATED_USTRUCT_BODY()
	DATAFLOW_NODE_DEFINE_INTERNAL(FCustomClothProcessorNode, "ProcessClothData", "Cloth", "Process Imported Cloth")
	DATAFLOW_NODE_RENDER_TYPE("SurfaceRender", FName("FClothCollection"), "Collection")

public:
	/** 输入的布料集合（来自 USD Import 节点） */
	UPROPERTY(meta = (DataflowInput))
	FManagedArrayCollection Collection;

	/** 处理后的布料集合 */
	UPROPERTY(meta = (DataflowOutput))
	FManagedArrayCollection OutCollection;

	/** 质量缩放因子 */
	UPROPERTY(EditAnywhere, Category = "Processing")
	float MassScale = 1.0f;

	FCustomClothProcessorNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
	virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

**CustomClothProcessor.cpp**
```cpp
#include "CustomClothProcessor.h"
#include "Dataflow/DataflowContext.h"

FCustomClothProcessorNode::FCustomClothProcessorNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
	: FDataflowNode(InParam, InGuid)
{
	RegisterInputConnection(&Collection);
	RegisterOutputConnection(&OutCollection, &Collection);
}

void FCustomClothProcessorNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
	// 从输入获取布料集合
	const FManagedArrayCollection& InCollection = GetValue(Context, &Collection);
	FManagedArrayCollection& Result = Context.GetOutputValue(&OutCollection);
	Result = InCollection;

	// 应用质量缩放等处理逻辑
	// ...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | UE5 Dataflow 框架，提供节点图执行引擎 |
| `ChaosClothAsset` | Chaos 布料资产核心模块 |
| `ChaosClothAssetDataflowNodes` | Chaos 布料 Dataflow 节点基础库 |

插件级依赖：
| 插件 | 用途 |
|---|---|
| `USDImporter` | USD 文件导入基础设施 |
| `ChaosClothAsset` | Chaos 布料资产主插件 |
| `ChaosClothAssetDataflowNodes` | 布料 Dataflow 节点插件 |
| `Dataflow` | Dataflow 框架插件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | USD Interchange 添加对 ChaosCloth 资产的支持 |
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产模块正式脱离 Beta 阶段 |
| 2026-04-17 | `49f946b4` | [Dataflow] | Dataflow 框架相关更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移：从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复重复符号链接错误 |

### 维护评价

- **创建时间**：2025-12-05，插件较新（约 1 年历史）
- **更新频率**：活跃维护中，近 3 个月内有多次功能性更新
- **关键节点**：2026-04-21 布料资产模块正式脱离 Beta，说明该插件已趋于稳定
- **状态**：该插件从 `ChaosClothAssetDataflowNodes` 中独立拆分而来，专注于 USD 导入功能，近期仍在持续改进
- **推荐**：✅ 推荐使用。插件处于活跃维护状态，依赖的布料资产系统已脱离 Beta，适合生产环境使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)
- [官方文档]()（暂无）
- [测试用例]()（暂无独立测试）