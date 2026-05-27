# Chaos Cloth Asset USD Dataflow Nodes

> Dataflow nodes for importing USD Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料USD导入节点 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetUsdDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-12-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes) | |

## 用途

该插件为 Chaos 布料资产系统提供 USD 格式布料文件的导入能力。它将 USD 文件中的布料数据（包括模拟网格和渲染网格）转换为 UE5 的 `FManagedArrayCollection` 布料数据格式，供 Chaos 布料模拟系统使用。

这个插件从 `ChaosClothAssetDataflowNodes` 中独立拆分出来，专门处理 USD 格式的布料资产导入，支持从 Marvelous Designer、CLO3D 等第三方服装构造软件导出的 USD 布料文件。它处理了 USD 坐标轴转换（Z-up/Y-up）、布料 Schema 解析、以及将 USD 原始数据转换为引擎可用的静态网格资产等复杂逻辑。

## 使用场景

- 你在使用 Marvelous Designer 或 CLO3D 等服装设计软件，需要将布料模拟数据导入 UE5 → 用此插件的 USD Import 节点
- 你需要在 Dataflow 图中构建布料资产导入流水线 → 拖入 `USDImport` 节点
- 你需要分别控制模拟网格和渲染网格的导入（是否包含透明度等）→ 通过节点属性分别设置

## 蓝图用法

该插件提供的是 Dataflow 节点，而非传统蓝图节点。Dataflow 节点在 Dataflow 编辑器（Chaos Cloth 编辑器）中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `USDImport` | 从 USD 文件导入布料资产（模拟网格 + 渲染网格），位于 "Cloth" 分类下 | `FChaosClothAssetUSDImportNode_v3` |

### 节点属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `bImportSimMesh` | bool | 是否导入模拟网格数据（默认 true） |
| `bImportRenderMesh` | bool | 是否导入渲染网格数据（默认 true） |
| `bImportWithOpacity` | bool | 导入渲染网格时是否包含透明度信息（需要项目设置中启用半透明） |
| `UsdFile` | FChaosClothAssetImportFilePath | USD 文件路径 |
| `ReimportUsdFile` | Button | 点击重新导入 USD 文件并重新生成中间资产 |
| `ReloadSimStaticMesh` | Button | 点击仅重新加载模拟静态网格（不重新导入 USD） |
| `ReloadRenderStaticMesh` | Button | 点击仅重新加载渲染静态网格（不重新导入 USD） |

### 输出

| 输出 | 类型 | 说明 |
|---|---|---|
| `Collection` | FManagedArrayCollection | 导入后的布料数据集合，可连接到下游 Dataflow 节点 |

### 使用示例

1. 在 Chaos Cloth 编辑器中打开 Dataflow 图
2. 从节点列表中拖入 **Cloth → Cloth USD Import** 节点
3. 设置 **USD File** 属性指向你的 `.usd`/`.usda`/`.usdc` 文件
4. 根据需要勾选 **Import Sim Mesh**（模拟网格）和 **Import Render Mesh**（渲染网格）
5. 如需透明度效果，勾选 **Import With Opacity**（需先在项目设置中启用半透明）
6. 将节点的 **Collection** 输出连接到下游布料处理节点（如 Set Cloth Config 等）
7. 使用 **Reimport USD File** 按钮可重新导入整个 USD 文件

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/USDImportNode_v3.h"
#include "ChaosClothAsset/UsdPrimAttributeAccessor.h"
```

### USD Prim 属性访问器

`FUsdPrimAttributeAccessor` 提供了类型安全的 USD Prim 属性读取，自动处理 USD 到 UE 的类型转换和坐标轴重排：

```cpp
// 来源: Source/ChaosClothAssetUsdDataflowNodes/Private/ChaosClothAsset/UsdPrimAttributeAccessor.h

#if USE_USD_SDK
using namespace UE::Chaos::ClothAsset;

// 创建属性访问器，指定 USD 的上轴方向
FUsdPrimAttributeAccessor Accessor(UsdPrim, EUsdUpAxis::ZAxis);

// 读取单个浮点值
float Value = Accessor.GetValue<float>(TEXT("myFloatAttribute"), 0.0f);

// 读取 3D 向量（自动处理坐标轴转换）
FVector3f UpVector = Accessor.GetValue<FVector3f>(TEXT("upAxis"), FVector3f::UpVector);

// 读取无符号整数
uint32 Version = Accessor.GetValue<uint32>(TEXT("schemaVersion"), 0);

// 读取浮点数组
TArray<float> FloatArray = Accessor.GetArray<float>(TEXT("myArrayAttribute"));

// 按索引读取数组中的值
float FirstElement = Accessor.GetArrayValue<float>(TEXT("myArrayAttribute"), 0.0f, 0);
#endif
```

### 内部导入流程

USD Import 节点在内部执行以下步骤：

```cpp
// 简化流程（来源于节点的私有方法）

// 1. 根据 USD 文件是否有布料 Schema 选择导入路径
if (bHasClothSchema)
{
    ImportUsdFile(UsdPath, AssetPath, OutErrorText);      // 带 Schema 的标准导入
}
else
{
    ImportUsdFile_Schemaless(UsdPath, AssetPath, OutErrorText);  // 兼容旧格式
}

// 2. 将生成的静态网格转换为布料集合
ImportSimStaticMesh(ClothCollection, OutErrorText);   // 模拟网格
ImportRenderStaticMesh(ClothCollection, OutErrorText); // 渲染网格

// 3. 查找并关联生成的中间资产
UpdateImportedAssets(SimMeshName, RenderMeshName);
```

## Demo 示例

以下示例展示了如何在 C++ 中创建一个自定义的 Dataflow 节点来使用 USD 布料导入功能：

```cpp
// MyClothImportProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "ManagedArrayCollection.h"

class FMyClothImportProcessor
{
public:
    // 处理导入后的布料数据
    static void ProcessImportedClothData(const TSharedRef<FManagedArrayCollection>& ClothCollection);
};
```

```cpp
// MyClothImportProcessor.cpp
#include "MyClothImportProcessor.h"

void FMyClothImportProcessor::ProcessImportedClothData(
    const TSharedRef<FManagedArrayCollection>& ClothCollection)
{
    // 检查布料集合是否包含模拟网格数据
    if (ClothCollection->HasGroup(TEXT("SimPatterns2D")))
    {
        // 处理 2D 图案数据
        const int32 NumPatterns = ClothCollection->NumElements(TEXT("SimPatterns2D"));
        UE_LOG(LogTemp, Log, TEXT("Imported %d simulation patterns"), NumPatterns);
    }

    // 检查渲染网格数据
    if (ClothCollection->HasGroup(TEXT("RenderVertices")))
    {
        const int32 NumRenderVerts = ClothCollection->NumElements(TEXT("RenderVertices"));
        UE_LOG(LogTemp, Log, TEXT("Imported %d render vertices"), NumRenderVerts);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | Chaos 布料资产核心模块 |
| `ChaosClothAssetDataflowNodes` | 布料资产的 Dataflow 节点基础模块 |
| `Dataflow` | Dataflow 图编辑器框架 |
| `USDImporter` | USD 文件导入核心模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | USD 互换功能新增 ChaosCloth 资产支持 |
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产模块正式移除 Beta 标记 |
| 2026-04-17 | `49f946b4` | [Dataflow] | Dataflow 框架相关更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF 格式 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复重复符号链接错误 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次功能性更新，开发活跃
- 2026 年 4 月密集更新，包括布料模块正式脱离 Beta、USD 互换支持增强等
- 作为 Chaos 布料资产生态的一部分，跟随主布料系统同步维护
- 插件仍在快速迭代中，API 可能会有变化（如 `USDImportNode_v3` 中的 v3 后缀所示，已经历多次迭代）

**推荐使用**：该插件正在活跃开发且已脱离 Beta 状态，适合需要从第三方服装软件导入 USD 布料数据的项目使用。注意 API 仍在迭代中，需关注版本兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)
- [USD Import 节点头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes/Private/ChaosClothAsset/USDImportNode_v3.h)
- [USD Prim 属性访问器](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes/Private/ChaosClothAsset/UsdPrimAttributeAccessor.h)
- [Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes/Source/ChaosClothAssetUsdDataflowNodes/ChaosClothAssetUsdDataflowNodes.Build.cs)