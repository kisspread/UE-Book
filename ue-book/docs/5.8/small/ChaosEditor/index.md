# ChaosEditor

> Destruction Tools

| 属性 | 值 |
|---|---|
| 中文名 | 破碎编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、资产模板） |
| 模块 | `FractureEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor) | |

## 用途

ChaosEditor 是 UE5 中用于在编辑器内创建和编辑 **几何集合 (Geometry Collection)** 的完整工具集。几何集合是 Chaos 物理系统用于实现可破坏物体（如建筑物、车辆、环境物体）的核心资产。此插件并非直接提供物理破碎模拟，而是为美术师和开发者提供了一个 **破碎工作流编辑器模式**，用于在内容创作阶段定义物体的破碎层次结构、破碎模式、物理属性（如碰撞、材质）等，从而在运行时由 Chaos 物理系统驱动破碎效果。它解决了如何在编辑器内可视化、编辑和验证复杂可破坏几何体的问题。

## 使用场景

- 你需要为一个建筑物、雕像或任何静态网格体创建可破坏的碎片效果，并定义它们在被击中时如何断裂。
- 你正在编辑一个几何集合资产，需要调整其层次结构（聚类）、凸包碰撞、材质分配或物理属性（如初始动态状态、移除条件）。
- 你需要通过多种模式（如 Voronoi、平面切割、砖块模式等）对网格体进行破碎，并实时预览破碎结果。
- 你需要可视化几何集合的层次结构、属性（如损坏值、体积大小）并选择特定骨骼进行编辑。

## 蓝图用法

此插件主要通过编辑器模式和工具套件暴露蓝图接口，用于控制破碎编辑器的视图和交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetExplodedViewValue` | 获取当前爆炸视图的缩放比例（0-1）。 | `FFractureEditorModeToolkit` |
| `OnSetExplodedViewValue` | 设置爆炸视图的缩放比例，用于分开查看碎片。 | `FFractureEditorModeToolkit` |
| `GetLevelViewValue` | 获取当前层级视图的层级数。 | `FFractureEditorModeToolkit` |
| `OnSetLevelViewValue` | 设置要在编辑器中显示的几何集合层级。 | `FFractureEditorModeToolkit` |
| `GetHideUnselectedValue` | 获取是否隐藏未选中骨骼的设置。 | `FFractureEditorModeToolkit` |
| `OnHideUnselectedChanged` | 当“隐藏未选中”设置改变时调用。 | `FFractureEditorModeToolkit` |
| `SetBoneSelection` | 设置几何集合组件中骨骼的选择状态。 | `FFractureEditorModeToolkit` |
| `ExecuteAction` | 执行一个 `UFractureActionTool` 定义的操作（如选择、删除、合并）。 | `FFractureEditorModeToolkit` |
| `CanExecuteAction` | 检查当前状态下是否可以执行指定的操作工具。 | `FFractureEditorModeToolkit` |
| `SetActiveTool` | 设置当前活动的模态工具（如 Voronoi 破碎、平面切割等）。 | `FFractureEditorModeToolkit` |
| `GetActiveTool` | 获取当前活动的模态工具。 | `FFractureEditorModeToolkit` |
| `ShutdownActiveTool` | 关闭并重置当前活动的模态工具。 | `FFractureEditorModeToolkit` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过获取破碎编辑器模式的工具套件来访问这些功能。例如，要控制视图：
1. 从编辑器工具上下文（Editor Tool Context）获取 `FFractureEditorModeToolkit` 实例。
2. 使用 `GetExplodedViewValue` 和 `OnSetExplodedViewValue` 节点连接到滑块控件，动态调整破碎物体的爆炸视图。
3. 使用 `SetBoneSelection` 节点，配合从 UI 事件（如列表选择）传入的骨骼索引数组，来在视口中高亮显示特定的破碎片段。

## C++ 用法

该插件主要为编辑器扩展，其 API 用于自定义或扩展破碎编辑器模式和工具。

### 头文件引入

```cpp
#include "FractureEditor.h" // 模块主头文件
#include "FractureEditorMode.h" // 编辑器模式
#include "FractureEditorModeToolkit.h" // 工具套件，用于UI交互
#include "FractureTool.h" // 所有破碎工具的基类
#include "FractureContext.h" // 操作上下文
```

### 基本用法

**1. 获取破碎编辑器模式的工具套件（用于视图控制）**
```cpp
// 来源：Source/FractureEditor/Public/FractureEditorModeToolkit.h
// 通常通过模式访问工具套件
if (GEditor)
{
    UEdMode* ActiveMode = GEditor->GetActiveMode(FractureEditorModeID);
    if (UFractureEditorMode* FractureMode = Cast<UFractureEditorMode>(ActiveMode))
    {
        // 获取工具套件
        TSharedPtr<FFractureEditorModeToolkit> Toolkit = FractureMode->GetToolkit();
        if (Toolkit.IsValid())
        {
            // 控制视图
            Toolkit->OnSetExplodedViewValue(0.5f); // 设置50%爆炸视图
            Toolkit->OnSetLevelViewValue(2); // 查看层级2
            Toolkit->OnHideUnselectedChanged(); // 应用“隐藏未选中”更改
        }
    }
}
```

**2. 理解并使用操作工具 (Action Tool)**
```cpp
// 来源：Source/FractureEditor/Public/FractureTool.h
// 创建一个工具上下文，包含当前选择
UGeometryCollectionComponent* SelectedComponent = ...; // 从场景获取
FFractureToolContext Context(SelectedComponent);
Context.Sanitize(); // 清理选择（例如，移除无效索引）

// 获取工具套件并执行一个操作工具
if (TSharedPtr<FFractureEditorModeToolkit> Toolkit = ...)
{
    // 实例化一个具体的操作工具（例如选择叶子节点）
    UFractureToolSelectLeaf* SelectLeafTool = NewObject<UFractureToolSelectLeaf>();
    // 执行它
    Toolkit->ExecuteAction(SelectLeafTool);
}
```

### 进阶用法

**创建和执行一个模态工具（Modal Tool）流程**
模态工具（如 `UFractureToolUniformVoronoi`）需要用户设置参数后执行。
```cpp
// 来源：Source/FractureEditor/Public/FractureTool.h, Source/FractureEditor/Private/FractureToolContext.h
// 1. 准备操作上下文
UGeometryCollectionComponent* Component = ...;
FFractureToolContext Context(Component);
Context.ConvertSelectionToLeafNodes(); // 例如，只选择叶子节点进行破碎

// 2. 创建模态工具并设置参数
UFractureToolUniformVoronoi* VoronoiTool = NewObject<UFractureToolUniformVoronoi>();
// 工具的参数通常暴露为 UPROPERTY，可以通过工具的 GetSettingsObjects() 获取设置对象
TArray<UObject*> SettingsObjects = VoronoiTool->GetSettingsObjects();
// 假设第一个对象是 UFractureUniformVoronoiSettings
if (UFractureUniformVoronoiSettings* VoronoiSettings = Cast<UFractureUniformVoronoiSettings>(SettingsObjects[0]))
{
    VoronoiSettings->NumberVoronoiSites = 50; // 设置50个Voronoi点
}

// 3. 通过工具套件执行
// 在实际插件中，工具套件会管理模态状态的进入、退出和执行
// 以下是其内部逻辑的简化模拟
if (Toolkit->CanSetModalTool(VoronoiTool))
{
    Toolkit->SetActiveTool(VoronoiTool);
    // 模态工具通常通过“Apply”按钮或命令触发执行
    // VoronoiTool->Execute(Toolkit);
}
```

## Demo 示例

以下是一个最小的编辑器模块示例，展示如何初始化破碎编辑器模式（如果作为独立插件扩展，而不是使用原生 ChaosEditor）。

```cpp
// MyFractureEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyFractureEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 可以持有对破碎模式或工具套件的引用用于扩展
    // TWeakObjectPtr<UFractureEditorMode> FractureMode;
};
```

```cpp
// MyFractureEditorModule.cpp
#include "MyFractureEditorModule.h"
#include "FractureEditorMode.h" // 来自 ChaosEditor 插件
#include "EditorModeRegistry.h"

void FMyFractureEditorModule::StartupModule()
{
    // 破碎编辑器模式由 ChaosEditor 插件自身注册。
    // 此处可以执行自定义逻辑，例如在模式注册后添加自定义工具。
    FEditorModeRegistry& EditorModeRegistry = FEditorModeRegistry::Get();
    if (EditorModeRegistry.IsModeActive(UFractureEditorMode::EM_FractureEditorModeId))
    {
        // 破碎模式已激活，可以访问其工具套件进行扩展
        UE_LOG(LogTemp, Log, TEXT("Fracture Editor Mode is active and ready for extension."));
    }
}

void FMyFractureEditorModule::ShutdownModule()
{
    // 清理资源
}

IMPLEMENT_MODULE(FMyFractureEditorModule, MyFractureEditor)
```

## 模块依赖

要使用此插件的功能，你的项目或模块需要依赖以下插件和模块：

| 模块/插件 | 用途 |
|---|---|
| `GeometryCollectionPlugin` | 几何集合资产的基础运行时支持。 |
| `Fracture` | Chaos 物理系统的破碎模拟运行时库。 |
| `PlanarCut` | 提供平面切割几何体的底层算法。 |
| `MeshModelingToolsetExp` | 提供网格体建模工具（如自动UV、凸包生成）的实验性集合。 |
| `EditorScriptingUtilities` | 提供编辑器脚本实用程序。 |

你的 `Build.cs` 文件可能需要如下依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Slate",
    "SlateCore",
    "UnrealEd",
    "GeometryCollectionPlugin",
    "Fracture",
    "MeshModelingToolsetExp"
});
PrivateDependencyModuleNames.AddRange(new string[] {
    "PlanarCut",
    "EditorScriptingUtilities",
    // ... 其他可能的依赖如 InputCore, PropertyEditor
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数时产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中的说明符，确保当参数为64位时使用正确的说明符，反之亦然。 |
| 2026-04-14 | `eaf81cf6` | Add new fracture mode utility to split islands | 在破碎编辑器模式中添加了用于分割独立几何岛屿的新工具。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将代码中的日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-04-06 | `3e98cc7e` | TLazyObjectPtr Deprecation pt 3: | 处理 `TLazyObjectPtr` 类型的弃用警告的第三部分工作。 |

### 维护评价

ChaosEditor 插件创建于 **2019 年**，至今约 7 年历史，属于 **老古董** 级别。尽管 `.uplugin` 标记为 `IsBetaVersion: true`，表明它仍被认为是实验性功能，但从 git 历史看，它**仍在持续维护中**。
- **近期更新频繁**：最近几次更新集中在 2026 年 4 月和 5 月，主要是编译修复、警告清理和工具功能添加（如“分割岛屿”工具）。
- **核心功能稳定**：作为 UE5 Chaos 物理系统的关键编辑器组件，其基础架构和核心破碎工具已趋于稳定。
- **限制与风险**：由于标记为实验性，API 和行为在未来的引擎版本中可能发生变化。它深度依赖 `GeometryCollectionPlugin` 和 `Fracture` 模块。
- **推荐**：对于需要创建可破坏物体的项目，**强烈推荐使用**此插件。它是 UE5 官方提供的最完整的破碎工作流解决方案。开发者应关注引擎更新日志中关于 Chaos 和几何集合的变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosEditor/Tests) (如果存在)