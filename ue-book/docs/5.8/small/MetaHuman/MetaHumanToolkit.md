# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、模型等） |
| 模块 | `MetaHumanToolkit` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSpeech2Face` (Runtime), ... 等28个模块 |
| 实验性 | 否 |
| 创建时间 | 2022-04-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 推出的官方 MetaHuman 工具集，旨在解决从真实世界捕捉数据（如 iPhone、深度摄像头）到高质量、可驱动的虚拟数字人（MetaHuman）之间的全链路流程问题。它并非一个单一功能模块，而是一个庞大的插件集合，其核心目的包括：

1.  **数据捕获与导入**：支持多种捕获源（如 Live Link Face, HMC），并提供数据清理和格式转换工具。
2.  **面部求解与拟合**：将捕获的面部动画数据（2D 特征点、深度图）转换为 MetaHuman 骨骼的控制数据，并进行高质量拟合。
3.  **动画创作与编辑**：提供集成在 Sequencer 中的专用工具，用于预览、编辑和驱动面部动画。
4.  **资产创建与管理**：管理 MetaHuman 身份（Identity）和表演（Performance）资产，并集成到 Unreal Engine 的资产编辑体系中。
5.  **工具框架**：`MetaHumanToolkit` 模块提供了构建上述所有编辑器工具的基础框架，统一了视口、时间轴、AB 对比等交互体验。

简单来说，它是一个“从面部视频/照片到可驱动虚拟角色”的端到端解决方案和开发工具包。

## 使用场景

*   **你是一位虚拟制片或游戏开发者**，希望将演员的面部表演快速、高质量地转化为游戏或影视中的数字角色。
*   **你正在开发 MetaHuman 相关的插件或扩展工具**，需要一个强大、一致的编辑器框架来构建 UI，包括带有 AB 对比、深度可视化、轨迹叠加的高级视口。
*   **你需要批量处理面部动画数据**，或者需要将来自不同捕获设备的数据统一转换为引擎可用的格式。
*   **你希望深度定制 MetaHuman 的面部动画流程**，例如集成自定义的求解器或修改动画数据的导入管线。

## 蓝图用法

**注意**：`MetaHumanToolkit` 主要是一个 **编辑器端（Editor-side）的 C++ 框架模块**，其核心类（如 `FMetaHumanToolkitBase`）并非 `UObject`，因此无法直接在蓝图中使用。蓝图可调用的功能主要分布于其他模块，如 `MetaHumanPerformance`、`MetaHumanPipeline` 等。`MetaHumanToolkitCommands` 定义了与蓝图或 UI 交互的命令。

### 核心节点（来自其他模块，非 `MetaHumanToolkit` 本身）

| 节点 | 说明 | 所在类 |
|---|---|---|
| (其他模块提供的节点) | 例如：加载表演资产、应用动画蓝图、触发求解器等 | `UMetaHumanPerformance`, `UMetaHumanPipeline` 等 |

### 使用示例（UI 命令描述）

`MetaHumanToolkitCommands` 定义了基础视口操作命令。这些命令通常在 C++ 中绑定到编辑器 UI 按钮或菜单项。例如，以下命令控制视口的显示模式：
*   `ViewMixToSingle`: 切换到单视图模式。
*   `ViewMixToWipe`: 切换到擦除对比模式。
*   `ViewMixToDual`: 切换到双视图模式。
*   `ToggleCurves`: 切换显示面部曲线覆盖。
*   `ToggleControlVertices`: 切换显示控制顶点。
*   `ToggleDepthMesh`: 切换深度网格可视化。

## C++ 用法

`MetaHumanToolkit` 模块提供了构建 MetaHuman 资产编辑器的核心基类。

### 头文件引入

```cpp
#include "MetaHumanToolkitBase.h"
#include "MetaHumanEditorViewportClient.h"
```

### 基本用法

以下是一个自定义资产编辑器工具的示例框架，继承自 `FMetaHumanToolkitBase`。
```cpp
// MyMetaHumanAssetEditor.h
#pragma once
#include "MetaHumanToolkitBase.h"

class FMyMetaHumanAssetEditor : public FMetaHumanToolkitBase
{
public:
    FMyMetaHumanAssetEditor(UAssetEditor* InOwningAssetEditor);

    // 可以重写 CreateWidgets 来添加自定义 UI 面板
    virtual void CreateWidgets() override;

    // 重写此函数来绑定自定义命令
    virtual void BindCommands() override;

    // 重写此函数来控制视口底部的额外控件
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;

protected:
    // 当 Sequencer 时间轴改变时被调用
    virtual void HandleSequencerGlobalTimeChanged() override;

    // 处理撤销/重做事件
    virtual void HandleUndoOrRedoTransaction(const FTransaction* InTransaction) override;

private:
    // 你的自定义 Widget 成员
    TSharedPtr<SMyCustomPanel> CustomPanel;
};
```

### 进阶用法

`FMetaHumanEditorViewportClient` 提供了高度可定制的视口。你可以通过委托与它交互。
```cpp
// 在你的 Toolkit 构造函数中
ViewportClient = MakeShareable(new FMetaHumanEditorViewportClient(PreviewScene.Get(), ViewportSettings));
ViewportClient->OnCameraMovedDelegate.AddSP(this, &FMyToolkit::HandleCameraMoved);
ViewportClient->OnPrimitiveComponentClickedDelegate.BindSP(this, &FMyToolkit::HandleComponentClicked);

// 设置深度可视化
if (CameraCalibration)
{
    CreateDepthMeshComponent(CameraCalibration);
}
```

## Demo 示例

一个最小的自定义 MetaHuman 编辑器工具类实现。
```cpp
// MyMHAssetEditor.h
#pragma once
#include "MetaHumanToolkitBase.h"

class FMyMHAssetEditor : public FMetaHumanToolkitBase
{
public:
    FMyMHAssetEditor(UAssetEditor* InOwningAssetEditor);
    virtual ~FMyMHAssetEditor();

    // 实现 FGCObject 接口
    virtual void AddReferencedObjects(FReferenceCollector& Collector) override;
    virtual FString GetReferencerName() const override { return TEXT("FMyMHAssetEditor"); }

protected:
    // 添加自定义 Widget 到视口底部
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;

private:
    TSharedPtr<class STextBlock> StatusText;
};
```

```cpp
// MyMHAssetEditor.cpp
#include "MyMHAssetEditor.h"
#include "Widgets/Text/STextBlock.h"

FMyMHAssetEditor::FMyMHAssetEditor(UAssetEditor* InOwningAssetEditor)
    : FMetaHumanToolkitBase(InOwningAssetEditor)
{
    // 基类已经创建了预览场景、序列器、视口等
}

FMyMHAssetEditor::~FMyMHAssetEditor()
{
    // 基类析构函数负责清理
}

void FMyMHAssetEditor::AddReferencedObjects(FReferenceCollector& Collector)
{
    // 调用基类以引用其持有的 UObject（如 Sequence）
    FMetaHumanToolkitBase::AddReferencedObjects(Collector);
}

TSharedRef<SWidget> FMyMHAssetEditor::GetViewportExtraContentWidget()
{
    // 创建一个简单的状态文本显示在视口底部
    StatusText = SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Tool Status")));
    return SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.0f)
        [
            StatusText.ToSharedRef()
        ];
}
```

## 模块依赖

`MetaHumanToolkit` 模块自身的依赖相对基础。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 插件的核心类型、数据结构和工具函数 |
| `UnrealEd` | 编辑器基础功能（常见依赖） |

**说明**：虽然 `MetaHumanToolkit` 本身依赖简单，但要实现完整的 MetaHuman 编辑器功能，通常需要组合使用 `MetaHumanAnimator` 插件内的其他多个模块（如 `MetaHumanIdentity`, `MetaHumanPerformance`），这些模块可能有更复杂的依赖链（如 `ControlRig`, `SkeletalMeshUtilitiesCommon`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 身体追踪启用时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

*   **状态**：**活跃维护中**。
*   **依据**：
    1.  创建于 2022 年，属于较新的功能插件。
    2.  最近一次更新在 2026 年 5 月，且提交频率较高（连续多天有更新），表明 Epic Games 团队正在积极开发和修复问题。
    3.  近期提交涵盖了功能增强（如身体追踪集成）、Bug 修复（渲染、缓存）和核心功能改进（动画序列导出），维护质量高。
    4.  该插件是 Epic Games 官方 MetaHuman 产品线的重要组成部分，预计将持续更新以支持新的引擎版本和 MetaHuman 功能。
*   **推荐**：**强烈推荐**。对于涉及 MetaHuman 创建、动画和编辑的任何正式项目，此插件是必不可少的核心工具。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
*   [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-in-unreal-engine/) (基于引擎通用文档页，非特定URL)