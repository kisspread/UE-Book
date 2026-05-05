# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具资源） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件为基于 Dataflow 的 Chaos 布料资产提供核心编辑工具集。它解决的核心问题是：在 UE5 的 Dataflow 编辑器中，如何直观高效地创建和编辑布料模拟所需的各类数据。

插件包含三个核心编辑工具：

1. **布料网格选择工具**（`UClothMeshSelectionTool`）：在布料网格上进行顶点/边/面选择，支持扩展、收缩、泛填充和清除等选择操作，用于精确指定布料操作的目标区域。
2. **权重图绘制工具**（`UClothWeightMapPaintTool`）：在布料网格上绘制权重图（Weight Map），用于控制布料模拟参数（如刚度、阻尼等）在网格表面的空间分布。支持绘制、平滑、擦除笔刷以及填充、多边形套索、渐变等交互模式。
3. **蒙皮权重转移工具**（`UClothTransferSkinWeightsTool`）：将源骨骼网格体（Skeletal Mesh）的蒙皮权重转移到布料资产上，使布料能够正确跟随角色骨骼运动。支持通过 Transform Gizmo 实时调整源网格的位置、旋转和缩放。

此外，插件还提供了编辑器上下文对象（`UClothEditorContextObject`，已废弃，推荐使用 `UDataflowContextObject`）来管理 Dataflow 图编辑器状态、选中节点和布料集合，以及工具热键绑定系统（`FClothToolActionCommandBindings`）。

## 使用场景

- **角色布料模拟设置** → 你正在为角色制作披风、裙子等布料部件 → 使用蒙皮权重转移工具将角色骨骼的蒙皮权重转移到布料网格，确保布料跟随骨骼正确变形
- **布料行为精细调优** → 你需要让布料在某些区域更硬、某些区域更软 → 使用权重图绘制工具绘制权重图，精确控制模拟参数的空间分布
- **布料网格区域选择** → 你需要对布料网格的特定顶点/面进行约束或操作 → 使用网格选择工具精确选择目标区域
- **Dataflow 布料资产工作流** → 你正在使用 Dataflow 节点图构建布料资产 → 本插件提供 Dataflow 编辑器中所需的全部布料编辑工具

## 蓝图用法

本模块为编辑器工具模块，不包含 `BlueprintCallable` 运行时 API。以下是在编辑器工具面板中可用的属性和操作。

### 核心节点

#### 网格选择工具操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GrowSelection` | 扩展当前选择区域（向外生长一圈） | `UClothMeshSelectionToolActions` |
| `ShrinkSelection` | 收缩当前选择区域（向内缩减一圈） | `UClothMeshSelectionToolActions` |
| `FloodSelection` | 泛填充选择整个连通区域 | `UClothMeshSelectionToolActions` |
| `ClearSelection` | 清除所有选择 | `UClothMeshSelectionToolActions` |

#### 网格选择工具属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Name` | `FString` | 选择集名称 | `UClothMeshSelectionToolProperties` |
| `SelectionOverrideType` | `EChaosClothAssetSelectionOverrideType` | 选择覆盖类型 | `UClothMeshSelectionToolProperties` |
| `bShowVertices` | `bool` | 是否在视口中显示顶点 | `UClothMeshSelectionToolProperties` |

#### 蒙皮权重转移工具属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `SourceMesh` | `USkeletalMesh*` | 源骨骼网格体资产 | `UClothTransferSkinWeightsToolProperties` |
| `SourceMeshTranslation` | `FVector3d` | 源网格位置偏移 | `UClothTransferSkinWeightsToolProperties` |
| `SourceMeshRotation` | `FVector3d` | 源网格旋转 | `UClothTransferSkinWeightsToolProperties` |
| `SourceMeshScale` | `FVector3d` | 源网格缩放（支持等比缩放） | `UClothTransferSkinWeightsToolProperties` |
| `bHideSourceMesh` | `bool` | 是否隐藏源网格预览 | `UClothTransferSkinWeightsToolProperties` |

#### 权重图绘制工具笔刷类型

| 枚举值 | 说明 |
|---|---|
| `Paint` | 绘制权重值 |
| `Smooth` | 平滑已有权重 |
| `Erase` | 擦除权重（设为 0） |

#### 权重图绘制工具交互模式

| 枚举值 | 说明 |
|---|---|
| `Brush` | 笔刷模式 |
| `Fill` | 填充模式 |
| `PolyLasso` | 多边形套索模式 |
| `Gradient` | 渐变模式 |
| `HideTriangles` | 隐藏三角面模式 |

### 使用示例（编辑器操作描述）

**网格选择操作流程：**
1. 在 Dataflow 编辑器中打开布料资产，进入构造视图
2. 激活"网格选择工具"
3. 在布料网格上点击或框选顶点/边/面
4. 点击"GrowSelection"按钮扩展选择范围，或"ShrinkSelection"收缩
5. 点击"FloodSelection"选择整个连通区域
6. 点击"ClearSelection"重置所有选择

**蒙皮权重转移操作流程：**
1. 激活"蒙皮权重转移工具"
2. 在属性面板中指定源骨骼网格体（`SourceMesh`）
3. 使用 Transform Gizmo 调整源网格的位置/旋转/缩放，使其与布料网格对齐
4. 确认后执行权重转移

## C++ 用法

### 头文件引入

```cpp
#include "ClothEditorToolBuilders.h"
#include "ClothEditorContextObject.h"
#include "ClothWeightMapPaintTool.h"
#include "ClothMeshSelectionTool.h"
#include "ClothTransferSkinWeightsTool.h"
```

### 基本用法

#### 查询工具支持的构造视图模式

每个工具构建器都实现了 `IChaosClothAssetEditorToolBuilder` 接口，可以查询工具支持的视图模式：

```cpp
// 来源: Public/ChaosClothAsset/ClothEditorToolBuilders.h

// 获取工具支持的构造视图模式
UClothMeshSelectionToolBuilder* Builder = GetDefault<UClothMeshSelectionToolBuilder>();
TArray<UE::Chaos::ClothAsset::EClothPatternVertexType> SupportedModes;
Builder->GetSupportedViewModes(*ContextObject, SupportedModes);

// 第一个元素是首选视图模式
if (SupportedModes.Num() > 0)
{
    UE::Chaos::ClothAsset::EClothPatternVertexType PreferredMode = SupportedModes[0];
}
```

#### 使用上下文对象获取选中的布料集合

```cpp
// 来源: Public/ChaosClothAsset/ClothEditorContextObject.h
// 注意: UClothEditorContextObject 已废弃(5.6)，请使用 UDataflowContextObject

UDataflowContextObject* ContextObject = /* 从编辑器获取 */;

// 获取当前选中的布料集合
TWeakPtr<const FManagedArrayCollection> ClothCollection = ContextObject->GetSelectedClothCollection();

// 获取当前构造视图模式
EClothPatternVertexType ViewMode = ContextObject->GetConstructionViewMode();

// 检查是否使用输入集合
bool bUsingInput = ContextObject->IsUsingInputCollection();
```

#### 获取 Dataflow 图编辑器中选中的特定类型节点

```cpp
// 来源: Public/ChaosClothAsset/ClothEditorContextObject.h
// UClothEditorContextObject 中的模板方法（已废弃但仍可用）

// 获取单个选中的指定类型节点，如果没有选中或选中多个则返回 nullptr
template<typename NodeType>
NodeType* GetSingleSelectedNodeOfType() const;
```

### 进阶用法

#### 注册和管理工具热键绑定

```cpp
// 来源: Private/ChaosClothAsset/ClothToolActionCommandBindings.h

// 创建工具操作命令绑定实例
FClothToolActionCommandBindings Bindings;

// 当工具激活时绑定命令
TSharedPtr<FUICommandList> UICommandList = MakeShared<FUICommandList>();
UInteractiveTool* ActiveTool = /* 当前激活的工具 */;
Bindings.BindCommandsForCurrentTool(UICommandList, ActiveTool);

// 当工具停用时解绑命令
Bindings.UnbindActiveCommands(UICommandList);
```

#### 自定义权重图绘制笔刷操作

```cpp
// 来源: Private/ChaosClothAsset/ClothWeightMapPaintBrushOps.h

// 绘制笔刷属性
UWeightMapPaintBrushOpProps* PaintProps = GetDefault<UWeightMapPaintBrushOpProps>();
PaintProps->AttributeValue = 1.0;  // 绘制的权重值
PaintProps->Strength = 0.5f;       // 笔刷强度 (0-10)

// 擦除笔刷属性
UWeightMapEraseBrushOpProps* EraseProps = GetDefault<UWeightMapEraseBrushOpProps>();
EraseProps->AttributeValue = 0.0;  // 擦除后的值
```

#### 自定义网格选择机制

```cpp
// 来源: Private/ChaosClothAsset/ClothMeshSelectionTool.h

// UClothMeshSelectionMechanic 继承自 UPolygonSelectionMechanic
// 可以重写 UpdateSelection 来自定义选择行为
class UClothMeshSelectionMechanic : public UPolygonSelectionMechanic
{
    virtual bool UpdateSelection(
        const FRay& WorldRay,
        FVector3d& LocalHitPositionOut,
        FVector3d& LocalHitNormalOut) override;
};
```

## Demo 示例

以下是一个最小的编辑器工具扩展示例，展示如何基于本插件的工具构建器创建自定义布料编辑工具：

```cpp
// MyCustomClothToolBuilder.h
#pragma once

#include "ClothEditorToolBuilders.h"
#include "MyCustomClothToolBuilder.generated.h"

/**
 * 自定义布料网格选择工具构建器
 * 继承 UClothMeshSelectionToolBuilder 以扩展默认行为
 */
UCLASS()
class UMyCustomClothToolBuilder : public UClothMeshSelectionToolBuilder
{
    GENERATED_BODY()

public:
    // 重写支持的视图模式
    virtual void GetSupportedViewModes(
        const UDataflowContextObject& ContextObject,
        TArray<UE::Chaos::ClothAsset::EClothPatternVertexType>& Modes) const override
    {
        // 只支持特定的视图模式
        Modes.Add(UE::Chaos::ClothAsset::EClothPatternVertexType::Position);
    }

    // 重写工具构建逻辑
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override
    {
        UInteractiveTool* Tool = Super::BuildTool(SceneState);
        // 在此处添加自定义工具配置
        return Tool;
    }
};
```

```cpp
// MyCustomClothToolBuilder.cpp
#include "MyCustomClothToolBuilder.h"

// 工
### 近期更新

- 2026-04-21 `600f5cce` [Chaos Cloth Asset] Moved Cloth Asset modules out of beta.
- 2026-04-14 `0d40a411` [ContentBrowser] New Add Menu Physics Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `0be5748b` Dataflow : Move all assets to use the new way to bind dataflow menu commends in the asset context me
- 2026-04-07 `30afa955` Cloth : Use the new template user experience