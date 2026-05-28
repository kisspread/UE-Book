# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-07-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作全套工具链。它不是一个单一功能插件，而是一个庞大的**动画制作生态系统**，涵盖了从面部和身体捕捉数据的获取（MetaHumanCaptureSource）、处理（MetaHumanPipeline）、面部动画解算（MetaHumanFaceAnimationSolver）、性能优化（MetaHumanPerformance）到最终在 Sequencer 中进行高级编辑（MetaHumanSequencer）的完整工作流。该插件旨在将高保真、电影级的 MetaHuman 角色动画制作能力直接集成到 Unreal Engine 内部，替代或补充传统的外部 DCC（数字内容创建）工具流程。

## 使用场景

- **影视级虚拟人表演捕捉**：你使用 iPhone、专业头盔或其他设备进行了面部捕捉，需要将原始数据（视频、深度图）转化为驱动 MetaHuman 模型的高质量面部动画。
- **对话驱动的面部动画**：你有一段音频，希望为其自动生成自然的面部表情动画（Speech2Face）。
- **批量处理与自动化**：你需要对大量 MetaHuman 模型进行统一的配置应用、动画重定向或资产处理（MetaHumanBatchProcessor）。
- **基于深度的重建与匹配**：你拥有多角度或深度相机拍摄的面部数据，需要重建出高精度的 3D 面部网格（MetaHumanDepthGenerator, MetaHumanFaceFittingSolver）。
- **集成自定义设备**：你的动捕设备使用了自定义的网络协议，需要通过插件进行接入（MetaHumanCaptureProtocolStack）。
- **高级动画编辑与合成**：你已经在 Sequencer 中制作了基础动画，需要精细调整控制器、混合动画或应用物理效果（MetaHumanSequencer, MetaHumanToolkit）。

## 蓝图用法

*注意：由于该插件主要包含底层 C++ 模块和编辑器工具，其公共 API 主要通过 C++ 暴露，核心工作流通常在编辑器面板中以可视化方式完成，而非通过蓝图节点直接调用。*

### 核心节点 (示例)

大部分高级功能封装在编辑器自定义面板中。少量可用于运行时的 `BlueprintCallable` 函数可能存在于 `MetaHumanCore` 或 `MetaHumanPerformance` 等模块中，需要具体分析。`MetaHumanConfigEditor` 模块本身不暴露蓝图 API。

## C++ 用法

该插件主要为**编辑器扩展**和**底层库**，其 C++ API 主要供引擎内部或其他高级插件调用。

### 头文件引入 (MetaHumanConfigEditor 模块示例)

```cpp
#include "MetaHumanConfigEditor/Private/Customizations/MetaHumanConfigCustomizations.h"
```

### 基本用法

MetaHumanConfigEditor 模块的核心作用是提供 `UMetaHumanConfig` 资产在编辑器中的自定义界面。在其他模块中注册 `UMetaHumanConfig` 资产的详细信息自定义。

```cpp
// 来自 MetaHumanConfigEditor/Private/Customizations/MetaHumanConfigCustomizations.h
// 在某个编辑器模块的 StartupModule 中注册自定义
FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
PropertyModule.RegisterCustomClassLayout(
    UMetaHumanConfig::StaticClass()->GetFName(),
    FOnGetDetailCustomizationInstance::CreateStatic(&FMetaHumanConfigCustomization::MakeInstance)
);
```

### 进阶用法

在自定义详情面板中，使用 `SMetaHumanConfigCombo` 控件为特定属性提供便捷的配置资产选择下拉框。

```cpp
// 来自 MetaHumanConfigEditor/Private/SMetaHumanConfigCombo.h
// 在 IDetailCustomization::CustomizeDetails 的实现中
TSharedRef<SWidget> ConfigComboWidget =
    SNew(SMetaHumanConfigCombo)
    .MetaHumanConfigType(EMetaHumanConfigType::Face) // 指定配置类型
    .PropertyOwner(PropertyOwnerObject) // 持有属性的对象
    .Property(PropertyHandle); // 要编辑的属性句柄
DetailBuilder.AddCustomRowToCategory(CategoryName)
    .NameContent()
    [ PropertyHandle->CreatePropertyNameWidget() ]
    .ValueContent()
    [ ConfigComboWidget ];
```

## Demo 示例

以下示例展示了如何在自定义的编辑器面板中使用 `SMetaHumanConfigCombo` 控件来关联编辑一个 `UObject` 上的 `UMetaHumanConfig*` 属性。

```cpp
// MyConfigPanel.h
#pragma once
#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyConfigPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyConfigPanel) {}
    SLATE_ARGUMENT(TObjectPtr<UObject>, ConfigOwner)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 一个指向拥有配置属性的对象的指针
    TObjectPtr<UObject> ConfigOwnerObject;
};
```

```cpp
// MyConfigPanel.cpp
#include "MyConfigPanel.h"
#include "SMetaHumanConfigCombo.h" // MetaHumanConfigEditor 模块的头文件
#include "MetaHumanConfig.h"       // MetaHumanConfig 模块的头文件
#include "DetailLayoutBuilder.h"
#include "IDetailsView.h"

void SMyConfigPanel::Construct(const FArguments& InArgs)
{
    ConfigOwnerObject = InArgs._ConfigOwner;

    // 创建一个用于编辑 UMetaHumanConfig* 属性的属性句柄
    // 假设你的 ConfigOwnerObject 类有一个名为 'CurrentConfig' 的 UPROPERTY
    FPropertyEditorModule& PropertyModule = FModuleManager::GetModuleChecked<FPropertyEditorModule>("PropertyEditor");
    TSharedPtr<IPropertyHandle> ConfigPropertyHandle =
        PropertyModule.CreatePropertyHandle(ConfigOwnerObject, GET_MEMBER_NAME_CHECKED(YourClass, CurrentConfig));

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            // 实例化 MetaHuman 配置下拉选择框
            SNew(SMetaHumanConfigCombo)
            .MetaHumanConfigType(EMetaHumanConfigType::Face) // 例如，面部配置
            .PropertyOwner(ConfigOwnerObject)
            .Property(ConfigPropertyHandle)
        ]
    ];
}
```

## 模块依赖

*注意：MetaHumanConfigEditor 是大型插件 `MetaHumanAnimator` 中的一个子模块。其自身依赖相对简单，但完整使用插件功能需要整个插件。*

| 模块 | 用途 |
|---|---|
| `MetaHumanConfig` | 定义 `UMetaHumanConfig` 核心资产类型和枚举 |
| `SlateCore` | 构建 `SMetaHumanConfigCombo` 所需的 Slate UI 框架 |

## 维护状态

### 近期更新

从 `git log` 分析，整个 MetaHumanAnimator 插件处于活跃开发中，近期更新主要围绕功能完善和问题修复。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 优化工作流：当启用身体追踪时，禁用关卡序列导出选项，避免无效操作 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 改进身体追踪模式下的可视化，过滤掉不必要的物体，使视图更清晰 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 新增功能：支持为已有的 MetaHuman 网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题，提升动画编辑的稳定性和性能 |

### 维护评价

- **活跃维护**：根据 Git 历史，该插件在**最近一周内有多次功能性提交**，修复了关键问题（渲染、缓存）并添加了新功能（动画序列导出）。这表明 Epic Games 团队正在积极开发和维护该插件。
- **功能重要性**：作为 MetaHuman 官方工作流的核心组件，它受到 Epic 的长期支持。
- **实验性/稳定性**：`.uplugin` 中 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`，表明该插件已达到**正式发布**状态。
- **推荐**：**强烈推荐**。如果你正在使用 MetaHuman 并计划进行专业级的动画制作（尤其是基于捕捉的流程），这是必须启用的核心插件。它功能强大且维护积极。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-for-unreal-engine/) （MetaHuman 官方文档主站）