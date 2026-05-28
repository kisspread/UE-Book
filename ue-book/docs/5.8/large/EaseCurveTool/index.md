# Ease Curve Tool

> Sequencer / Curve Editor tool to ease tangents between keyframes using custom preset libraries

| 属性 | 值 |
|---|---|
| 中文名 | 缓动曲线工具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `EaseCurveTool` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/EaseCurveTool) | |

## 用途

EaseCurveTool 是一个集成在 Sequencer 和曲线编辑器中的动画缓动工具。它解决了动画师在调整关键帧之间过渡时，需要手动、反复调整切线参数（如权重、斜率）以获得期望缓动效果（如 EaseIn、EaseOut、EaseInOut）的繁琐问题。该工具提供了一个可视化的曲线编辑器，允许用户直接拖拽预览和编辑切线，并内置了一个预设库系统，支持保存、加载、导入和导出缓动预设，从而实现缓动效果的快速应用和团队共享。它将常用的缓动曲线样式（如三次贝塞尔）抽象为可管理的预设，极大地提高了动画曲线的编辑效率和一致性。

## 使用场景

- **动画师调整缓动**：在 Sequencer 中为角色动画或 UI 动画的关键帧应用平滑的缓入缓出效果时，无需手动计算切线值，可以从预设库中选择或直观地拖拽曲线。
- **快速应用预设**：需要为大量相似的关键帧序列应用统一的缓动风格时，可以使用自定义预设库进行快速应用。
- **曲线编辑器增强**：在动画蓝图或任何使用 RichCurve 的地方，通过曲线编辑器的集成，获得更强大的切线编辑功能。
- **缓动效果共享**：项目团队可以创建、导出并共享一套标准的缓动曲线预设库，确保动画风格的一致性。

## 蓝图用法

该插件主要为编辑器扩展，直接暴露给蓝图的公开接口有限，主要集中在曲线资产的创建和预设的应用上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateExternalCurveAsset` | 根据当前工具中的缓动曲线创建一个新的外部浮点曲线资产 (`UCurveBase`)。 | `UE::EaseCurveTool::FEaseCurveTool` |
| `ApplyQuickEaseToSequencerKeySelections` | 将工具中设置的缓动切线（或快速缓动预设）应用到当前 Sequencer 中选中的关键帧。 | `UE::EaseCurveTool::FEaseCurveTool` |
| `SetSequencerKeySelectionTangents` | 直接将一组 `FEaseCurveTangents` 应用到当前 Sequencer 选中的关键帧上。 | `UE::EaseCurveTool::FEaseCurveTool` |

### 使用示例（蓝图描述）

由于该工具主要通过编辑器UI交互，蓝图直接使用的场景不多。典型用法是：
1.  在动画蓝图编辑器的 Sequencer 窗口中，确保“Ease Curve Tool”侧边栏或工具栏可见。
2.  选中一段动画轨道上的多个关键帧。
3.  在工具界面中，从下拉列表选择一个预设，或者手动拖拽曲线编辑器中的切线手柄来调整缓动形状。
4.  点击“Apply”或使用快捷键，将调整后的缓动效果应用到选中的关键帧上。
5.  或者，可以使用 `CreateExternalCurveAsset` 节点，将当前编辑的缓动曲线保存为项目中的独立曲线资产，供其他系统（如 Niagara、动画通知）使用。

## C++ 用法

### 头文件引入

```cpp
#include "EaseCurveToolModule.h"
#include "EaseCurveTool.h"
#include "EaseCurveLibrary.h"
#include "EaseCurveTangents.h"
```

### 基本用法

从测试用例中可以了解到，该工具主要与 `ISequencer` 和 `FCurveEditor` 交互。以下是一个简化的示例，展示如何获取与当前 Sequencer 实例关联的工具实例：

**来源文件**: `Private/EaseCurveTool.h`, `Private/EaseCurveToolExtender.h`
```cpp
// 假设你已经有一个有效的 ISequencer 实例指针 TSharedPtr<ISequencer> MySequencer
using namespace UE::EaseCurveTool;

// 通过扩展器查找或创建与特定 Sequencer 关联的工具实例
TSharedPtr<FEaseCurveTool> EaseTool = FEaseCurveToolExtender::FindToolInstance(MySequencer.ToSharedRef());

if (EaseTool.IsValid())
{
    // 工具已就绪，可以进行查询或操作
    // 例如，获取当前缓动曲线的切线数据
    FEaseCurveTangents CurrentTangents = EaseTool->GetEaseCurveTangents();
    UE_LOG(LogTemp, Log, TEXT("Current Tangents: %s"), *CurrentTangents.ToString());

    // 将一组自定义切线应用到 Sequencer 选中的关键帧
    FEaseCurveTangents NewTangents(0.5f, 0.2f, -0.5f, 0.8f); // Start, StartWeight, End, EndWeight
    EaseTool->SetSequencerKeySelectionTangents(NewTangents, EEaseCurveToolOperation::InOut);
}
```

### 进阶用法

结合 `UEaseCurveLibrary` 管理预设，并快速应用一个预设：

**来源文件**: `Public/EaseCurveLibrary.h`, `Private/EaseCurveTool.h`
```cpp
using namespace UE::EaseCurveTool;

// 获取默认预设库或加载一个自定义预设库资产
TObjectPtr<UEaseCurveLibrary> MyLibrary = NewObject<UEaseCurveLibrary>();
// 或者从磁盘加载： MyLibrary = LoadObject<UEaseCurveLibrary>(nullptr, TEXT("/Game/Path/MyCurveLibrary"));

if (MyLibrary)
{
    // 假设我们要应用名为 "QuickEase" 的预设
    FEaseCurvePresetHandle PresetToApply(FText::FromString(“Custom”), FText::FromString(“QuickEase”));
    FEaseCurvePreset FoundPreset;

    if (MyLibrary->FindPreset(PresetToApply, FoundPreset))
    {
        // 获取工具实例（假设 MySequencer 有效）
        TSharedPtr<FEaseCurveTool> EaseTool = FEaseCurveToolExtender::FindToolInstance(MySequencer.ToSharedRef());
        if (EaseTool.IsValid())
        {
            // 将找到的预设切线应用到选中的关键帧
            EaseTool->SetSequencerKeySelectionTangents(FoundPreset.Tangents);
        }
    }
}
```

## Demo 示例

以下是一个最小示例，演示如何在自定义编辑器模块中通过命令打开或关闭 EaseCurveTool 的侧边栏标签页。

**MyEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FUICommandList> PluginCommands;
    void RegisterMenus();
    void OnToggleEaseCurveToolTab();
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "EaseCurveToolExtender.h"
#include "EaseCurveToolCommands.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 注册自定义命令（如果需要）
    RegisterMenus();
}

void FMyEditorModule::ShutdownModule()
{
    // 清理命令
}

void FMyEditorModule::RegisterMenus()
{
    // 通常在此注册菜单项，但这里我们直接通过函数调用
}

void FMyEditorModule::OnToggleEaseCurveToolTab()
{
    using namespace UE::EaseCurveTool;
    // 查找第一个可用的工具实例（简化示例，实际中可能需要更具体的获取逻辑）
    // 这里假设通过模块全局的FEaseCurveToolExtender来获取或切换可见性
    // 具体实现依赖于插件的内部管理，以下为概念性代码
    // FEaseCurveToolExtender::Get().GetToolInstance(...)
    // 然后调用 ToggleToolTabVisible()
    UE_LOG(LogTemp, Log, TEXT("Toggling EaseCurveTool visibility. (Demo action)"));
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditorModule)
```

## 模块依赖

从 `EaseCurveTool.Build.cs` 分析，要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SequencerCore` | Sequencer 核心框架，用于访问 ISequencer 接口 |
| `CurveEditor` | 曲线编辑器框架，用于集成和扩展曲线编辑器功能 |
| `MovieScene` | MovieScene 核心数据类型（如 `UMovieSceneSection`, `FMovieSceneChannelHandle`） |
| `ToolWidgets` | 用于构建编辑器工具栏和菜单的 Slate 控件 |
| `EditorWidgets` | 编辑器通用 Slate 控件 |

*注：已省略 Core, CoreUObject, Engine, Slate, SlateCore, UnrealEd, DeveloperSettings 等通用依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `37380749` | [EaseCurveTool] Update content browser extension to use UToolMenu system | 更新内容浏览器扩展，改用 UToolMenu 系统 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 配合内容浏览器“添加”菜单数据化改造 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移至新格式 UE_LOGF |
| 2026-04-10 | `f8c80d19` | Curve Editor: Fix ease curve tool pop up menu location, otherwise it can go offscreen when invoking | 修复缓动曲线工具弹出菜单定位问题，防止调用时菜单超出屏幕 |
| 2026-01-23 | `49664505` | Ease Curve Selection improvement | 改进缓动曲线的选择逻辑 |

### 维护评价

**维护状态：活跃维护中**

EaseCurveTool 是一个较新的插件（2025年9月创建），自创建以来持续有更新，最近一次更新在2026年4月。从提交记录看，维护内容涵盖了功能迁移（如将插件从实验目录移出）、UI/UX 改进（菜单定位、选择优化）、代码维护（日志宏迁移）以及与引擎其他系统（如内容浏览器）的适配。这表明 Epic 团队仍在积极维护和改进此插件。

**注意事项**：
1.  **实验性状态**：插件的 `.uplugin` 文件中 `IsBetaVersion` 为 `true`，表明它仍处于 Beta 测试阶段。API 和功能可能会发生变化。
2.  **依赖关系**：作为编辑器工具，它深度集成于 Sequencer 和曲线编辑器，因此对这些核心动画系统的更新可能会产生影响。

**推荐**：对于需要高效编辑动画缓动曲线的项目，尤其是使用 Sequencer 进行影视动画或过场动画制作的团队，推荐尝试使用此工具。尽管是 Beta 版，但其功能完整且得到官方维护。在使用前，建议在非生产环境中测试其稳定性和与项目工作流的契合度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/EaseCurveTool)
- [官方文档]() (暂无)