# Groom

> Rendering and simulation of grooms

| 属性 | 值 |
|---|---|
| 中文名 | 毛发束插件 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `HairCardGeneratorFramework` (Runtime), `HairStrandsCore` (Runtime), `HairStrandsDataflow` (Runtime), `HairStrandsDeformer` (Runtime), `HairStrandsEditor` (Runtime), `HairStrandsRuntime` (Runtime), `HairStrandsSolver` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-24 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands) | |

## 用途

HairStrands 插件（在编辑器中显示为 “Groom”）是 Unreal Engine 用于处理高密度、基于束（strand-based）毛发和毛发系统（Groom）的完整解决方案。它解决的核心问题是：如何在 UE 中高效地导入、渲染、模拟和编辑来自专业 DCC 工具（如 Maya、Houdini、Blender）的复杂毛发资产。插件不仅仅是一个渲染器，它提供了一个完整的工作流，包括资产导入、物理模拟、LOD 管理、材质绑定、动画缓存（Groom Cache）以及与 Sequencer 的深度集成，使其成为影视和高端游戏角色制作的强大工具。

## 使用场景

-   你正在为角色制作逼真的毛发、胡须或毛皮，并使用 DCC 工具生成了基于束的 Groom 数据 → 使用 HairStrands 插件导入、编辑和渲染。
-   你需要在引擎中实时模拟角色的毛发在风、重力、碰撞下的动态效果 → 使用插件内置的物理模拟功能。
-   你的动画需要角色毛发有特定的动态表现（如奔跑时的飘动），并希望在引擎中精确控制 → 创建 Groom Cache 资产并将其与 Sequencer 配合使用。
-   你需要将 Groom 绑定到不同骨骼的 Skeletal Mesh 上，并确保绑定效果正确 → 使用 Groom Binding 资产。

## 蓝图用法

HairStrands 插件的蓝图功能主要集中在运行时组件控制和资产操作上，用于驱动预览和控制模拟。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetGroomComponent` | 设置要预览的 Groom 组件。 | `SGroomEditorViewport` |
| `SetSkeletalMeshComponent` | 设置预览 Groom 所绑定的骨骼网格体组件。 | `SGroomEditorViewport` |
| `PlaySimulation` | 开始播放 Groom 的物理模拟。 | `FGroomCustomAssetEditorToolkit` |
| `PauseSimulation` | 暂停当前的物理模拟。 | `FGroomCustomAssetEditorToolkit` |
| `ResetSimulation` | 将模拟重置到初始状态。 | `FGroomCustomAssetEditorToolkit` |
| `PlayAnimation` | 播放用于预览的动画资产。 | `FGroomCustomAssetEditorToolkit` |
| `StopAnimation` | 停止播放动画。 | `FGroomCustomAssetEditorToolkit` |
| `PreviewBinding` | 预览指定的 Groom Binding 资产效果。 | `FGroomCustomAssetEditorToolkit` |

### 使用示例（蓝图描述）

假设你有一个角色蓝图，其中包含一个 Groom Component：
1.  在角色蓝图中，添加一个 `Groom Component` 并赋予其 Groom 资产。
2.  在关卡蓝图或 UI 蓝图中，你可以获取到该角色的引用。
3.  使用一个“事件”节点（如按键事件）作为触发。
4.  从触发事件连出执行线，连接到一个“获取 Groom Component”节点（通过角色引用）。
5.  再连接到一个“播放模拟”或“重置模拟”等函数节点，即可在运行时通过蓝图控制毛发行为。

## C++ 用法

HairStrands 的 C++ API 主要服务于编辑器工具的开发和自定义导入器的创建。

### 头文件引入

```cpp
#include "HairStrandsEditor.h"
#include "GroomAsset.h"
#include "GroomComponent.h"
#include "HairStrandsImporter.h"
```

### 基本用法

以下代码片段展示了如何通过 C++ 代码创建一个基础的 Groom 编辑器工具包，并加载一个 Groom 资产进行编辑。（来源：`Public/GroomCustomAssetEditorToolkit.h`）

```cpp
// 创建编辑器工具包实例
TSharedRef<FGroomCustomAssetEditorToolkit> EditorToolkit = MakeShareable(new FGroomCustomAssetEditorToolkit());
// 初始化编辑器，传入模式、宿主和要编辑的 Groom 资产
EditorToolkit->InitCustomAssetEditor(
    EToolkitMode::Standalone,
    TSharedPtr<IToolkitHost>(),
    MyGroomAsset
);
// 预览第一个绑定资产
EditorToolkit->PreviewBinding(0);
```

### 进阶用法

你可以实现自定义的 `IDetailCustomization` 来扩展 Groom 资产在属性面板中的显示。例如，自定义材质面板。（来源：`Private/GroomMaterialDetails.h`, `Private/GroomAssetDetails.h`）

```cpp
// 继承 IDetailCustomization
class FMyCustomGroomDetails : public IDetailCustomization
{
public:
    // 工厂方法，用于注册
    static TSharedRef<IDetailCustomization> MakeInstance(IGroomCustomAssetEditorToolkit* InToolkit)
    {
        return MakeShareable(new FMyCustomGroomDetails(InToolkit));
    }

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailLayout) override
    {
        // 在这里定制你的属性布局，例如添加自定义材质槽控件
        // 参考 FGroomMaterialDetails 的实现
    }

private:
    IGroomCustomAssetEditorToolkit* Toolkit;
};

// 在插件启动时注册这个自定义（通常在模块 StartupModule 中）
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UGroomAsset::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMyCustomGroomDetails::MakeInstance, MyToolkitPtr)
);
```

## Demo 示例

一个最小的示例，展示如何创建一个简单的 Groom 资产处理器。

**MyGroomProcessor.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UGroomAsset;
class UGroomImportOptions;

class FMyGroomProcessor
{
public:
    /** 处理一个已加载的 Groom 资产 */
    void ProcessGroomAsset(UGroomAsset* InGroom, UGroomImportOptions* InOptions);

    /** 从 HairDescription 创建一个新资产（演示导入流程） */
    UGroomAsset* CreateAssetFromDescription(const FHairDescription& HairDescription, UObject* InParent, FName InName);
};
```

**MyGroomProcessor.cpp**
```cpp
#include "MyGroomProcessor.h"
#include "GroomAsset.h"
#include "HairStrandsImporter.h"
#include "GroomImportOptions.h"

void FMyGroomProcessor::ProcessGroomAsset(UGroomAsset* InGroom, UGroomImportOptions* InOptions)
{
    if (!InGroom || !InOptions) return;

    // 示例：遍历 Groom 的每个组，并修改一个属性
    for (int32 GroupIndex = 0; GroupIndex < InGroom->GetNumHairGroups(); ++GroupIndex)
    {
        FHairGroupInfo& GroupInfo = InGroom->GetHairGroupInfo(GroupIndex);
        // 在此处对 GroupInfo 进行自定义处理，例如修改插值设置等
        // GroupInfo.InterpolationSettings.XXX = ...;
    }

    // 标记资产已修改以便保存
    InGroom->MarkPackageDirty();
}

UGroomAsset* FMyGroomProcessor::CreateAssetFromDescription(const FHairDescription& HairDescription, UObject* InParent, FName InName)
{
    // 使用插件提供的导入上下文和导入器
    FHairImportContext ImportContext(nullptr, InParent, UGroomAsset::StaticClass(), InName, RF_Public | RF_Standalone);
    return FHairStrandsImporter::ImportHair(ImportContext, const_cast<FHairDescription&>(HairDescription));
}
```

## 模块依赖

要使用 HairStrands 的核心功能和编辑器扩展，你的模块（Build.cs）通常需要添加以下依赖。省略了通用的 Core，Engine，Slate 等。

| 模块 | 用途 |
|---|---|
| `HairStrandsCore` | Groom 资产 (`UGroomAsset`, `UGroomComponent`) 和核心数据结构的定义。 |
| `HairStrandsEditor` | 提供 Groom 编辑器工具、工厂、资产操作和 UI 自定义。仅在编辑器模块中依赖。 |
| `HairStrandsRuntime` | 提供运行时渲染和模拟支持。 |
| `GeometryCache` | 用于支持 Groom Cache（缓存的 Groom 动画）功能。 |
| `MaterialShaderQualitySettings` | 用于材质和着色器质量相关的设置，常用于头发着色器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `aa770ac7` | Remove crash in mobile renderer when using groom binding. | 修复移动端渲染器在使用 Groom 绑定时的崩溃问题。 |
| 2026-05-26 | `3da4e98e` | Fix crash when selecting the addSolverDeformer dataflow node | 修复在选择“addSolverDeformer”数据流节点时发生的崩溃。 |
| 2026-05-26 | `d2f5bcd4` | Fix crash when recompiling BP while playing groom in dataflow editor + fix bad number of vertices ca | 修复在数据流编辑器中播放 Groom 时重编译蓝图导致的崩溃，并修正顶点数计算错误。 |
| 2026-05-22 | `9ce84766` | Remove the CreateGroomDataflowAsset from the context menu | 从右键菜单中移除了“创建 Groom 数据流资产”选项。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口改进：通过通知客户端关联和解耦事件，重构了必要的样板代码。 |

### 维护评价

**积极维护**。HairStrands (Groom) 插件处于**非常活跃的维护状态**。
-   **最近更新**：在2026年5月内有多次提交，主要集中在修复崩溃、改进编辑器工作流（如数据流编辑器）和优化渲染路径上。
-   **功能迭代**：从提交信息可以看出，团队在持续完善 Dataflow（数据流）系统与 Groom 的集成，这是较新的功能模块。
-   **稳定性**：近期更新以 bug 修复为主，表明团队正在积极解决用户反馈的问题，提升系统稳定性。
-   **推荐使用**：作为 UE 官方支持的、功能全面的毛发解决方案，它非常适合需要影视级毛发质量的项目。虽然默认未启用，但文档和代码支持良好。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HairStrands/Tests) (路径示例，具体结构需确认)