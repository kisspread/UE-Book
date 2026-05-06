# Landmass

> 无描述。（.uplugin 中 Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | 地形蓝图刷子系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图类、材质资产） |
| 模块 | `Landmass` (Runtime), `LandmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass) | |

## 用途

Landmass 插件提供了一套基于蓝图的地形编辑刷子系统，允许开发者/美术师通过蓝图创建自定义地形画笔，并利用材质混合、四叉树优化、预览模式等高级功能。它解决了标准地形编辑工具无法灵活扩展的问题：你可以编写自己的地形刷子逻辑，而无需修改引擎 C++ 代码。

核心机制：
- 使用 `ALandmassActor`（继承自 `AActor`）作为单个刷子容器，支持自定义 `RenderLayer` 蓝图事件。
- 使用 `ALandmassManagerBase`（继承自 `ALandscapeBlueprintBrushBase`）管理多个刷子的四叉树排序与渲染。
- 提供蓝图函数库（`ULandmassBlueprintFunctionLibrary`）帮助获取光标射线、转换坐标、强制更新纹理等。
- 提供 `ALandmassErosionBrushBase` 作为侵蚀刷子的基础类。

该插件目前处于实验阶段，默认不启用，适合对地形系统有较高自定义需求的团队。

## 使用场景

- 制作程序化地形工具：例如根据曲线、噪声或玩家位置动态修改地形高度和权重。
- 自定义侵蚀/沉积刷子：基于物理规则模拟自然侵蚀过程。
- 关卡设计辅助：快速预览不同材质混合效果，并调整刷子层级顺序。
- 实现多刷子协作：同时应用多个画笔并控制它们的混合模式。

## 蓝图用法

以下是从头文件中提取的蓝图可调用 API，按功能分组。

### 核心节点

#### ALandmassActor（刷子 Actor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CustomTick` | 每帧调用的蓝图事件（原生/蓝图均可） | `ALandmassActor` |
| `RenderLayer` | 地形渲染时调用的蓝图事件，在此实现刷子逻辑 | `ALandmassActor` |
| `RenderLayer_Native` | 调用原生渲染逻辑（仅 C++），不覆盖蓝图版本 | `ALandmassActor` |
| `FastPreviewMode` | 进入快速预览模式（低质量快速渲染） | `ALandmassActor` |
| `RestoreLandscapeEditing` | 退出预览，恢复标准地形编辑状态 | `ALandmassActor` |
| `MoveBrushUp` / `MoveBrushDown` | 在管理器图层中上移/下移本刷子 | `ALandmassActor` |
| `MoveToTop` / `MoveToBottom` | 将本刷子移动至图层顶层/底层 | `ALandmassActor` |

#### 属性（蓝图可读写）

| 属性 | 类型 | 说明 |
|---|---|---|
| `BrushSize` | float | 刷子的世界单位大小 |
| `DrawToEntireLandscape` | bool | 若启用，刷子作用域覆盖整个地形 |
| `AffectsHeightmap` | bool | 是否影响高度图 |
| `AffectsWeightmaps` | bool | 是否影响权重图 |
| `AffectsVisibility` | bool | 是否影响地形可见性 |
| `HeightBlendMode` | `EBrushBlendMode` | 高度图的混合模式（AlphaBlend/Min/Max/Additive） |
| `HeightMaterial` | `UMaterialInterface*` | 用于高度图的材质 |
| `WeightMapBlendMode` | `EBrushBlendMode` | 权重图的混合模式 |
| `WeightmapMaterial` | `UMaterialInterface*` | 用于权重图的材质 |
| `WeightmapLayers` | `TArray<FName>` | 受影响的权重图层名称列表 |
| `BrushExtents` | `FVector4` | 刷子的世界范围（只读调试信息） |

#### ULandmassBlueprintFunctionLibrary

| 节点 | 说明 |
|---|---|
| `Get Cursor World Ray` | 获取当前鼠标光标在世界空间中的位置和射线方向（用于绘制交互） |
| `Get Overlapping World Extents` | 合并两个世界范围构成最小包围盒 |
| `World Extents to Landmass Coordinates` | 将世界范围转换为地形画布坐标（适合用于材质参数） |
| `Force Update Texture` | 强制刷新指定纹理（用于更新渲染结果） |

#### ALandmassManagerBase（刷子管理器）

| 节点 | 说明 |
|---|---|
| `PopulateNodeTree` | 根据当前刷子列表填充四叉树节点数据 |
| `GetActorsWithinModifiedNodes` | 获取所有位于已修改节点内的刷子 |
| `UpdateChildDataCounts` | 更新所有节点的子数据计数 |
| `ConsolidateNodes` | 合并四叉树中相邻的可合并节点 |
| `SetTargetLandscape` | 设置该管理器负责的地形 |

#### ALandmassErosionBrushBase

| 节点 | 说明 |
|---|---|
| `SetTargetLandscape` | 将刷子添加到指定地形 |
| `GetLandscape` | 获取当前关联的地形 |
| `ActorSelectionChanged` | 当 Actor 在编辑器中选中状态发生变化时调用的蓝图事件 |

### 使用示例（蓝图描述）

1. **创建自定义刷子蓝图**：新建蓝图继承自 `ALandmassActor`，在事件图表中实现 `RenderLayer` 事件。在该事件中读取地形参数 `InParameters`，计算出新高度/权重值，并使用 `AffectsHeightmap`、`HeightMaterial` 等属性来应用效果。

2. **管理器配置**：在关卡中放置一个 `ALandmassManagerBase`，在细节面板中设置 `TargetLandscape`，然后通过 `AddBrushToLayer`（或蓝图调用 `SetTargetLandscape` 和手动添加刷子）将自定义刷子注册到管理器。

3. **预览与调试**：在编辑器中选中刷子，点击细节面板上的 `FastPreviewMode` 按钮快速查看效果，之后用 `RestoreLandscapeEditing` 恢复正常编辑状态。

## C++ 用法

### 头文件引入

```cpp
#include "LandmassActor.h"
#include "LandmassManagerBase.h"
#include "LandmassBPEditorExtension.h"
```

### 基本用法

以下示例展示如何在 C++ 中创建自定义刷子类（继承自 `ALandmassActor`）并实现 `RenderLayer`。

```cpp
// MyCustomBrush.h
#pragma once

#include "LandmassActor.h"
#include "MyCustomBrush.generated.h"

UCLASS(Blueprintable, Category = "Landmass")
class AMyCustomBrush : public ALandmassActor
{
    GENERATED_BODY()

public:
    virtual void RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters) override;
};

// MyCustomBrush.cpp
#include "MyCustomBrush.h"
#include "LandmassBPEditorExtension.h"

void AMyCustomBrush::RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters)
{
    // 示例：将刷子作用区域统一设置为 0.5 高度
    // 使用传入的材质参数或直接修改地形数据需要更复杂的实现
    // 此示例仅演示函数重载
    DrawToEntireLandscape = true;
    // 使用蓝图函数库刷新当前刷子所属管理器的渲染
    ULandmassBlueprintFunctionLibrary::ForceUpdateTexture(/* 需要有效的纹理指针 */);
}
```

### 进阶用法

利用 `ALandmassManagerBase` 管理多个刷子：

```cpp
// 获取场景中的 LandmassManager
ALandmassManagerBase* Manager = Cast<ALandmassManagerBase>(GetWorld()->SpawnActor<ALandmassManagerBase>());
if (Manager)
{
    // 设置目标地形
    ALandscape* MyLandscape = /* 获取有效地形 */;
    Manager->SetTargetLandscape(MyLandscape);

    // 添加自定义刷子
    AMyCustomBrush* Brush = GetWorld()->SpawnActor<AMyCustomBrush>();
    // 将刷子注册到管理器（需要手动将 Brush 添加到 Manager->LandmassBrushes 并调用 PopulateNodeTree）
    Manager->LandmassBrushes.Add(Brush);
    Manager->PopulateNodeTree();
}
```

## Demo 示例

以下是一个完整的 C++ 类，继承自 `ALandmassActor`，并在 `RenderLayer` 中设置基本属性，随后通过蓝图函数库强制更新纹理。

**MyCustomBrush.h**
```cpp
#pragma once

#include "LandmassActor.h"
#include "MyCustomBrush.generated.h"

UCLASS(Blueprintable, Category = "Landmass")
class AMyCustomBrush : public ALandmassActor
{
    GENERATED_BODY()

public:
    virtual void RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters) override;
};
```

**MyCustomBrush.cpp**
```cpp
#include "MyCustomBrush.h"
#include "LandmassBPEditorExtension.h"

void AMyCustomBrush::RenderLayer_Implementation(const FLandscapeBrushParameters& InParameters)
{
    // 设置刷子尺寸为 8192 世界单位，影响高程
    BrushSize = 8192.0f;
    AffectsHeightmap = true;
    HeightBlendMode = EBrushBlendMode::Additive;

    // 示例：强制更新关联纹理（注意需要有效纹理指针）
    if (HeightMaterial)
    {
        UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(HeightMaterial, this);
        // 设置材质参数...
        ULandmassBlueprintFunctionLibrary::ForceUpdateTexture(MID->GetTextureParameterValue());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Landscape` | 提供地形蓝图刷子基类及地形编辑接口 |
| `Landmass` (Runtime) | 包含公共数据结构和定义（被编辑器模块引用） |

> 其他如 Core, CoreUObject, Engine 为常见依赖，此处省略。

## 维护状态

### 近期更新

- 2025-08-27 `5ac9e159` Landscape - 废弃非编辑层地形（适配新地形系统）
- 2025-05-29 `8bd3e004` 修复 Landmass 编译时保证加载 blutility 模块
- 2025-05-01 `0faa16c2` 将蓝图刷子基类设为不可放置，仅从地形面板添加
- 2025-03-07 `1a599460` 移除已废弃的宏代码路径
- 2025-02-13 `ec3fb596` 用 `IsValid` 替换 `this` 检查

### 维护评价

- **创建时间**：2025-02-13（约 0.5 年）
- **近期更新频率**：每 1-3 个月有功能性或兼容性更新，修复关键问题。
- **活跃度**：处于积极维护中（最新更新 2025-08-27），适配引擎演化（如废弃非编辑层地形）。
- **已知问题**：实验性标志存在，可能 API 不稳定；部分功能依赖编辑器模块（`LandmassEditor`）。
- **推荐使用**：适合需要高级自定义地形编辑的项目。若仅是标准地形编辑，无需启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Landmass)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/landmass-plugin/)（如存在，根据 .uplugin 中 `DocsURL` 判断，目前为空，可留空）