# Mesh Partition Editor UI

> Large-scale mesh authoring system through spatial partitioning, non-destructive modifier editing, and platform-adaptive runtime representations.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartition` (Runtime), `MeshPartitionCompute` (Runtime), `MeshPartitionEditor` (Runtime), `MeshPartitionEditorUI` (Runtime), `MeshPartitionModelingToolset` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition) | |

## 用途

MeshPartitionEditorUI 是 Mesh Partition 插件的编辑器界面层，负责为大规模网格空间分区系统提供完整的编辑器 UI 支撑。该模块基于 UE5 的 Typed Element Data Storage (TEDS) 框架构建，提供：

1. **层级浏览器（Outliner）集成**：通过 TEDS 注册自定义表格、查询和层级结构，在编辑器中以树状结构展示 Mesh Partition 的层级关系（父 Actor、图层、修改器）
2. **自定义 Slate 控件**：包括构建成本统计、可见性切换、图层构建状态指示器、层级名称显示、父 Actor 引用等专用 Widget
3. **属性面板定制**：为 Mesh Partition 特有的属性类型（如可切换约束名称、样条修改器、纹理贴图等）提供自定义的 Details 面板编辑体验
4. **可扩展性设置**：提供预览简化、边缘长度、最小顶点数等可扩展性选项的 UI 控件

该模块解决的核心问题是：当场景中存在大量通过空间分区管理的网格体时，如何在编辑器中高效地浏览、编辑和监控这些网格体的层级结构、修改器状态和构建性能。

## 使用场景

- 你正在使用 Mesh Partition 系统创建大规模地形或环境网格 → 需要此模块提供的编辑器 UI 来管理图层和修改器
- 你需要在编辑器中查看网格分区的构建耗时统计 → 使用 Build Cost Widget
- 你需要控制各个图层/修改器的可见性和构建状态 → 使用 Visibility 和 Layer Build Widget
- 你需要自定义属性面板中 Mesh Partition 相关属性的显示方式 → 使用本模块的 Detail Customization

## 蓝图用法

本模块主要提供编辑器 UI 组件，不暴露 BlueprintCallable 函数。以下为可扩展的 Slate Widget 和 TEDS Widget Constructor。

### 核心 Widget

| Widget | 说明 | 所在类 |
|---|---|---|
| `SMegaMeshBuildCostWidget` | 显示网格分区的构建耗时统计信息 | `SMegaMeshBuildCostWidget` |
| `SHierarchyWidget` | 以列表形式展示 Mesh Partition 的子项层级 | `SHierarchyWidget` |
| `SMegaMeshLayerBuildWidget` | 图层/修改器的构建状态指示器（未构建/目标构建/自动构建） | `SMegaMeshLayerBuildWidget` |
| `SMegaMeshVisibilityWidget` | 单个图层/修改器的可见性切换控件 | `SMegaMeshVisibilityWidget` |
| `SMegaMeshSettingsWidget` | Mesh Partition 全局设置面板，包含过滤器和可扩展性选项 | `SMegaMeshSettingsWidget` |
| `SParentActorWidget` | 显示修改器所属的父 Actor 引用 | `SParentActorWidget` |

### TEDS Widget Constructor

| Constructor | 说明 | 所在类 |
|---|---|---|
| `FMegaMeshBuildCostWidgetHeaderConstructor` | 构建成本 Widget 的表头构造器 | `FMegaMeshBuildCostWidgetHeaderConstructor` |
| `FMegaMeshBuildCostWidgetConstructor` | 构建成本 Widget 的数据列构造器 | `FMegaMeshBuildCostWidgetConstructor` |
| `FMegaMeshLayerBuildWidgetHeaderConstructor` | 图层构建状态表头构造器 | `FMegaMeshLayerBuildWidgetHeaderConstructor` |
| `FMegaMeshLayerBuildWidget` | 图层构建状态数据列构造器 | `FMegaMeshLayerBuildWidget` |
| `FMegaMeshVisibilityWidgetHeaderConstructor` | 可见性表头构造器 | `FMegaMeshVisibilityWidgetHeaderConstructor` |
| `FMegaMeshVisibilityFlagWidget` | 可见性标志数据列构造器 | `FMegaMeshVisibilityFlagWidget` |
| `FNameWidgetHeaderConstructor` | 名称表头构造器（支持排序） | `FNameWidgetHeaderConstructor` |
| `FMegaMeshLayerNameWidgetConstructor` | 图层名称数据列构造器 | `FMegaMeshLayerNameWidgetConstructor` |
| `FMegaMeshModifierNameWidgetConstructor` | 修改器名称数据列构造器 | `FMegaMeshModifierNameWidgetConstructor` |
| `FHierarchyWidget` | 层级 Widget 构造器 | `FHierarchyWidget` |
| `FParentActorWidgetHeaderConstructor` | 父 Actor 表头构造器 | `FParentActorWidgetHeaderConstructor` |
| `FParentActorWidgetConstructor` | 父 Actor 数据列构造器 | `FParentActorWidgetConstructor` |

### TEDS 数据列（Columns）

| 列 | 说明 | 所在结构体 |
|---|---|---|
| `FMegaMeshRowParentColumn` | 存储父子层级关系（Parent + Children） | `FMegaMeshRowParentColumn` |
| `FUnresolvedMegaMeshLayer` | 未解析的修改器图层引用 | `FUnresolvedMegaMeshLayer` |
| `FParentActorRefColumn` | 父 Actor 的行引用 | `FParentActorRefColumn` |
| `FMegaMeshTimingStatistics` | 构建耗时统计（均值和标准差） | `FMegaMeshTimingStatistics` |
| `FMegaMeshModifierTiming` | 单个修改器的耗时信息 | `FMegaMeshModifierTiming` |

### TEDS 标签（Tags）

| 标签 | 说明 |
|---|---|
| `FMegaMeshBoundsFilterSourceTag` | 标记为 Mesh Partition 边界过滤源 |
| `FIsMegaMeshObjectTag` | 标记对象为 AMeshPartition |
| `FIsMegaMeshModifierTag` | 标记对象为 Mega Mesh 修改器 |
| `FMegaMeshLayerUpdatedTag` | 标记图层标签需要更新 |
| `FMegaMeshAffectsFilterBounds` | 标记修改器影响选中的基础区段 |
| `FIsMegaMeshModifierAssignedTag` | 标记修改器已分配给 Mega Mesh |
| `FMegaMeshNotHiddenInOutlinerTag` | 标记在 Outliner 中未隐藏 |

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionEditorUIModule.h"
#include "MeshPartitionTedsFactory.h"
#include "Columns/LayerOutlinerColumns.h"
#include "SculptLayersModifierController.h"
#include "MeshPartitionModifiersCustomizations.h"
```

### 基本用法：注册 TEDS 工厂

TEDS 工厂是本模块与编辑器数据存储系统交互的核心入口。通过继承 `UEditorDataStorageFactory`，在 `RegisterTables`、`RegisterQueries`、`RegisterHierarchies` 和 `RegisterWidgetConstructors` 中注册自定义数据结构和 UI 组件。

```cpp
// MeshPartitionTedsFactory.h - TEDS 工厂注册示例
// 来源: Public/MeshPartitionTedsFactory.h

// 工厂在 PreRegister 中初始化查询句柄
void UMegaMeshTedsFactory::PreRegister(Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册前的准备工作，如创建查询句柄
}

// 注册自定义表格
void UMegaMeshTedsFactory::RegisterTables(
    Editor::DataStorage::ICoreProvider& DataStorage,
    Editor::DataStorage::ICompatibilityProvider& CompatibilityDataStorage)
{
    // 注册 MegaMeshTable, MegaMeshDefinitionTable, 
    // MegaMeshDefinitionLayerTable, MegaMeshModifierTable
}

// 注册查询
void UMegaMeshTedsFactory::RegisterQueries(Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册 MegaMeshQuery, DefinitionLayerQueryRO, ActiveLayerQuery,
    // MegaMeshModifierQueryRW 等查询
}

// 注册层级结构
void UMegaMeshTedsFactory::RegisterHierarchies(UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 注册 MegaMeshHierarchy 层级句柄
}

// 注册 Widget 构造器
void UMegaMeshTedsFactory::RegisterWidgetConstructors(
    Editor::DataStorage::ICoreProvider& DataStorage,
    Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    // 注册所有 Widget Constructor（名称、可见性、构建状态、层级等）
}
```

### 基本用法：自定义属性面板

```cpp
// MeshPartitionModifiersCustomizations.h - 属性面板定制
// 来源: Public/MeshPartitionModifiersCustomizations.h

// 注册自定义 Detail Customization
class FMegaMeshTexturePatchDetails : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance();
    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override;
    
private:
    // 重排高度位移属性
    void ReparentHeightDisplacement(IDetailLayoutBuilder& DetailBuilder);
    // 添加权重通道复制按钮
    void AddWeightChannelCopyButtons(IDetailLayoutBuilder& DetailBuilder);
    // 添加细分复选框
    void AddTessellationCheckbox(IDetailLayoutBuilder& DetailBuilder);
};
```

### 进阶用法：Sculpt Layers 控制器

```cpp
// SculptLayersModifierController.h - 雕刻图层控制器
// 来源: Public/SculptLayersModifierController.h

// 创建控制器实例
FSculptLayersModifiersController Controller;

// 设置要控制的修改器属性
Controller.SetProperties(MyProjectMeshLayersModifier);

// 查询图层数量
int32 NumLayers = Controller.GetNumMeshLayers();

// 获取/设置图层名称
FName LayerName = Controller.GetLayerName(0);
Controller.SetLayerName(0, FName("MyLayer"));

// 获取/设置图层权重
double Weight = Controller.GetLayerWeight(0);
Controller.SetLayerWeight(0, 0.5, EPropertyChangeType::ValueSet);

// 刷新图层堆栈视图
Controller.RefreshLayersStackView();
```

### 进阶用法：可切换约束名称定制

```cpp
// MeshPartitionToggleableConstraintNameCustomization.h
// 来源: Private/MeshPartitionToggleableConstraintNameCustomization.h

// 注册为属性类型定制
// 在模块启动时注册：
PropertyModule.RegisterCustomPropertyTypeLayout(
    "ToggleableConstraintName",
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(
        &FToggleableConstraintNameCustomization::MakeInstance));

// 该定制器提供一个带开关的下拉框：
// - 开关打开时：使用 GetOptions 元数据函数约束可选项
// - 开关关闭时：允许自由文本输入
```

## Demo 示例

### 自定义 TEDS Widget Constructor

```cpp
// MyCustomWidget.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "Elements/Interfaces/TypedElementDataStorageInterface.h"
#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "Elements/Interfaces/TypedElementDataStorageUiInterface.h"

USTRUCT()
struct FMyCustomWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    FMyCustomWidgetConstructor();
    ~FMyCustomWidgetConstructor() override = default;

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};

class SMyCustomWidget : public SCompoundWidget
{
    using RowHandle = UE::Editor::DataStorage::RowHandle;

public:
    SLATE_BEGIN_ARGS(SMyCustomWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, const RowHandle& InTargetRow, const RowHandle& InWidgetRow);

protected:
    RowHandle TargetRow;
    RowHandle WidgetRow;
};
```

```cpp
// MyCustomWidget.cpp
#include "MyCustomWidget.h"

FMyCustomWidgetConstructor::FMyCustomWidgetConstructor()
{
}

TSharedPtr<SWidget> FMyCustomWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    return SNew(SMyCustomWidget)
        .TargetRow(TargetRow)
        .WidgetRow(WidgetRow);
}

void SMyCustomWidget::Construct(const FArguments& InArgs, 
    const RowHandle& InTargetRow, const RowHandle& InWidgetRow)
{
    TargetRow = InTargetRow;
    WidgetRow = InWidgetRow;

    ChildSlot
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("Custom Mesh Partition Widget")))
    ];
}
```

### 使用 Sculpt Layers 控制器

```cpp
// MySculptTool.h
#pragma once

#include "CoreMinimal.h"
#include "SculptLayersModifierController.h"

class FMySculptTool
{
public:
    void Initialize(MeshPartition::UProjectMeshLayersModifier* Modifier)
    {
        Controller.SetProperties(Modifier);
    }

    void AdjustLayerWeight(int32 LayerIndex, double Delta)
    {
        double CurrentWeight = Controller.GetLayerWeight(LayerIndex);
        double NewWeight = FMath::Clamp(CurrentWeight + Delta, 0.0, 1.0);
        Controller.SetLayerWeight(LayerIndex, NewWeight, EPropertyChangeType::ValueSet);
    }

    void PrintLayerInfo()
    {
        int32 NumLayers = Controller.GetNumMeshLayers();
        for (int32 i = 0; i < NumLayers; ++i)
        {
            FName Name = Controller.GetLayerName(i);
            double Weight = Controller.GetLayerWeight(i);
            UE_LOG(LogTemp, Log, TEXT("Layer %d: %s (Weight: %.2f)"), 
                i, *Name.ToString(), Weight);
        }
    }

private:
    UE::MeshPartition::FSculptLayersModifiersController Controller;
};
```

## 模块依赖

从 Build.cs 分析，本模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | Typed Element Data Storage 框架，提供 TEDS 表格、查询、层级和 UI 接口 |
| `TypedElementRuntime` | Typed Element 运行时支持 |
| `ModelingWidgets` | 提供 `IMeshLayersController` 基类和建模相关 Widget |
| `MeshPartition` | Mesh Partition 核心运行时模块，提供 `AMeshPartition`、`UMeshPartitionDefinition` 等核心类型 |
| `MeshPartitionEditor` | Mesh Partition 编辑器模块，提供 `UMeshPartitionEditorComponent` 等编辑器组件 |
| `SceneOutliner` | 场景大纲集成，提供 `ISceneOutliner` 和 Outliner 初始化选项 |
| `WorkspaceMenuStructure` | 工作区菜单结构，用于注册自定义编辑器标签页 |
| `DataStorage` | 数据存储句柄和接口 |

## 维护状态

### 近期更新

- 2026-04-24 `44085aba` Mesh Partition: avoid passing hard-coded SM6 argument to GenerateMips. Fixes a crash on projects wit
- 2026-04-24 `473e05b1` Mesh Terrain sculpt layer tools:
- 2026-04-24 `bb6e1b38` Guard against empty UV-Layers and unset element triangles
- 2026-04-23 `2a27739c` Add a path where the for-all-modifiers iteration allows null modifiers to be silently skipped, to av
- 2026-04-23 `dbed6742` Fix broken handling of UV seams at mesh skirt vertices -- take care to copy the UVs from the vertice

### 维护评价

- **创建时间**：2026-04-23，全新插件
- **实验性标记**：位于 `Engine/Plugins/Experimental/` 目录下，属于实验性功能
- **模块类型异常**：所有 5 个模块均标记为 `Runtime` 类型，但 `MeshPartitionEditorUI`、`MeshPartitionEditor` 和 `MeshPartitionModelingToolset` 从代码内容看明显是编辑器专用模块（包含 `IDetailCustomization`、`ISlateStyle`、TEDS Widget 等编辑器 API），这可能是构建配置的临时状态
- **架构成熟度**：基于 TEDS 框架构建，采用了 UE5 最新的编辑器数据存储架构，表明这是面向未来的设计
- **推荐程度**：作为实验性插件，适合用于原型开发和功能评估，不建议在生产环境中直接依赖。关注 Epic 官方的后续更新和从 Experimental 目录的迁移

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain)