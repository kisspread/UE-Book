# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（缩略图渲染器、编辑器资产） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件为 **Dataflow 驱动的 Chaos 布料资产** 提供完整的编辑器工作流。它从旧版 `ChaosClothEditor` 插件拆分而来，将 USD 相关代码移出编辑器模块，同时保留全部功能。

插件解决的核心问题：**如何在编辑器中可视化地创建、编辑和调试基于 Dataflow 节点图的布料资产**。这包括：

- **双视口编辑**：2D 构建空间（裁片编辑）+ 3D 预览空间（模拟预览），支持在两种视角之间无缝切换
- **Dataflow 节点图集成**：直接在编辑器内操作节点图，选中节点自动启动对应的编辑工具（如重网格化、权重绘制、网格选择等）
- **布料模拟控制**：软重置、硬重置、暂停/恢复、LOD 切换，实时观察模拟效果
- **调试可视化**：线框、接缝、法线、权重贴图、形态目标、气动力、风速等多种可视化叠加
- **遗留资产转换**：将旧版 `UClothingAssetCommon` 转换为新的 `UChaosClothAsset`（实验性功能）
- **缩略图渲染**：为布料资产生成编辑器中的缩略图预览

## 使用场景

- 你在使用 Chaos 物理引擎制作布料模拟，需要可视化编辑布料裁片 → 使用本插件的编辑器模式
- 你有一个基于 Dataflow 的布料资产工作流，需要在节点图中添加/连接/删除节点 → 使用本插件的 Dataflow 集成功能
- 你有旧版 `UClothingAssetCommon` 布料资产需要迁移到新的 Chaos 布料系统 → 使用 `FLegacyClothingConverter` 转换
- 你需要调试布料模拟的权重贴图、接缝、法线、气动力等参数 → 使用本插件的模拟可视化面板
- 你需要在 2D 平面视图中编辑布料裁片拓扑，在 3D 视图中实时预览模拟效果 → 使用双视口模式

## 蓝图用法

本插件主要是编辑器内部 C++ 模块，不暴露 `BlueprintCallable` 节点。但以下可编辑属性可通过 **设置面板 / 详情面板** 在编辑器中调整：

### 预览场景设置（UChaosClothPreviewSceneDescription）

在编辑器的预览场景详情面板中可编辑：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bPauseWhilePlayingInEditor` | `bool` | PIE/SIE 期间是否暂停动画和模拟 |
| `SkeletalMeshAsset` | `USkeletalMesh*` | 用于预览的骨骼网格体 |
| `AnimationAsset` | `UAnimationAsset*` | 用于预览的动画资产 |
| `SolverGeometryScale` | `float` | 求解器几何缩放（0-10） |
| `TeleportDistanceThreshold` | `float` | 位移瞬移阈值（超过此值触发传送） |
| `TeleportRotationThreshold` | `float` | 旋转瞬移阈值（0-180度） |

### 编辑器用户设置（UChaosClothEditorOptions）

在 **项目设置 → 编辑器 → Chaos Cloth Editor** 中可配置：

| 属性 | 类型 | 说明 |
|---|---|---|
| `bClothAssetsOpenInDataflowEditor` | `bool` | 布料资产是否在 Dataflow 编辑器中打开（而非旧版 Cloth 编辑器） |
| `ConstructionViewportMousePanButton` | `EConstructionViewportMousePanButton` | 2D 模式下的平移鼠标按键（右键/中键/任意） |

## C++ 用法

### 遗留布料资产转换（公共 API）

这是本插件对外暴露的主要公共 C++ API，用于将旧版布料资产转换为 Chaos 布料资产。

### 头文件引入

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
```

### 基本用法

将遗留布料资产转换为新的 Chaos 布料资产文件：

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"

// 假设 SourceAsset 是一个 UClothingAssetCommon 遗留资产
const UClothingAssetCommon* SourceAsset = /* ... */;

// 转换并创建新资产
UE::Chaos::ClothAsset::FLegacyClothingConverterResult Result = 
    UE::Chaos::ClothAsset::FLegacyClothingConverter::Convert(
        SourceAsset,
        TEXT("/Game/ClothAssets"),   // 输出包路径
        TEXT("ConvertedClothAsset") // 资产名称
    );

if (Result.CreatedAsset)
{
    // 转换成功
    UE_LOG(LogTemp, Log, TEXT("Created asset at: %s"), *Result.CreatedAssetPath);
}
else
{
    // 转换失败
    UE_LOG(LogTemp, Error, TEXT("Conversion failed: %s"), *Result.ErrorText.ToString());
}
```

### 进阶用法

将遗留布料资产转换到已存在的 Chaos 布料资产上（就地修改）：

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"

const UClothingAssetCommon* SourceAsset = /* ... */;
UChaosClothAsset* TargetAsset = /* 已存在的目标资产 */;

// 就地转换（会重置目标资产的 Dataflow 图）
UE::Chaos::ClothAsset::FLegacyClothingConverterResult Result = 
    UE::Chaos::ClothAsset::FLegacyClothingConverter::ConvertInto(
        SourceAsset,
        TargetAsset
    );
```

> ⚠️ **实验性 API**：`FLegacyClothingConverter` 被标记为 `UE_EXPERIMENTAL(5.8, ...)`，使用时需注意风险。
> 
> **已知限制**：目前仅导入 LOD 0，多 LOD 遗留资产的其他 LOD 级别会在转换时丢失。

### 转换细节

转换过程会执行以下操作：
1. 从遗留的 `FClothPhysicalMeshData` 构建布料集合作为 `ImportedSimClothCollection` Dataflow 变量覆盖
2. 每个遗留权重贴图附加一个 `WeightMapNode`，值缩放至 `[0,1]`
3. 当遗留资产有 `TetherEndsMask` 时，启用自定义系绳生成模式
4. 标量配置值通过 `UProperty` 反射写入现有的 `Simulation*` 配置节点

## Demo 示例

以下示例展示如何在编辑器工具中批量转换遗留布料资产：

### LegacyClothBatchConverter.h

```cpp
#pragma once

#include "CoreMinimal.h"

class UClothingAssetCommon;

/**
 * 批量遗留布料资产转换器示例
 */
class FLegacyClothBatchConverter
{
public:
    /**
     * 将指定骨骼网格体上的所有遗留布料资产转换为 Chaos 布料资产
     * @param SkeletalMesh 源骨骼网格体
     * @param OutputPath 输出路径
     * @return 成功转换的数量
     */
    static int32 ConvertAllClothingAssets(
        USkeletalMesh* SkeletalMesh,
        const FString& OutputPath);
};
```

### LegacyClothBatchConverter.cpp

```cpp
#include "LegacyClothBatchConverter.h"

#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "Engine/SkeletalMesh.h"
#include "ClothingAsset.h"

int32 FLegacyClothBatchConverter::ConvertAllClothingAssets(
    USkeletalMesh* SkeletalMesh,
    const FString& OutputPath)
{
    if (!SkeletalMesh)
    {
        return 0;
    }

    int32 ConvertedCount = 0;

    // 获取骨骼网格体上的所有布料资产
    TArray<UClothingAssetCommon*> ClothingAssets = SkeletalMesh->GetMeshClothingAssets();

    for (UClothingAssetCommon* ClothingAsset : ClothingAssets)
    {
        if (!ClothingAsset)
        {
            continue;
        }

        // 构造输出资产名称
        FString AssetName = FString::Printf(
            TEXT("Chaos_%s"), *ClothingAsset->GetName());

        // 执行转换
        UE::Chaos::ClothAsset::FLegacyClothingConverterResult Result =
            UE::Chaos::ClothAsset::FLegacyClothingConverter::Convert(
                ClothingAsset,
                OutputPath,
                AssetName
            );

        if (Result.CreatedAsset)
        {
            ++ConvertedCount;
        }
    }

    return ConvertedCount;
}
```

## 模块依赖

> 以下仅列出非标准依赖。公共 API 模块 (`ChaosClothAssetEditor`) 的隐含依赖不需额外配置。

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | Chaos 布料资产运行时类型（UChaosClothAsset、UChaosClothComponent） |
| `Dataflow` | Dataflow 节点图编辑器和执行引擎 |
| `BaseCharacterFXEditor` | 角色特效编辑器基类（编辑模式、工具集框架） |
| `InteractiveToolsFramework` | 交互式工具框架（拖拽、选择、Gizmo） |
| `GeometryFramework` | 动态网格体组件（UDynamicMeshComponent）用于 2D 构建视图 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Daaflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 在布料和 Dataflow 选择工具视口中添加 HUD 选中信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp, ChaosClothAssetEdit | 修复编辑器模块的编译警告 |

### 维护评价

- **状态**：🟢 **活跃维护中**
- **创建时间**：2026-01-27（约 4 个月前），是从旧版 `ChaosClothEditor` 插件拆分而来
- **更新频率**：近 1 个月内有 5 次提交，包括功能增强（重新导入、HUD 信息）、bug 修复和代码清理
- **API 稳定性**：旧版 Cloth Panel Editor 已标记为 `UE_DEPRECATED(5.8)`，正在向 Dataflow 编辑器迁移
- **实验性部分**：`FLegacyClothingConverter` 标记为实验性，仅支持 LOD 0 转换
- **推荐程度**：如果你使用 Chaos 布料系统，本插件是必需的编辑器支持组件。作为新插件，API 可能还在演进中，但核心功能已可使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档（暂无）