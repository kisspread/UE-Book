# Tweening Utils

> Algorithms and widgets useful for inbetweening.

| 属性 | 值 |
|---|---|
| 中文名 | 补间工具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `TweeningUtils` (Runtime), `TweeningUtilsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-12-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils) | |

## 用途

TweeningUtils 是一个面向动画关键帧补间（inbetweening）的工具插件，为曲线编辑器提供了一套完整的补间操作框架。它解决的核心问题是：动画师需要在已有的关键帧之间快速平滑过渡，而不是手动逐帧调整每个关键帧的值。

插件从 CurveEditor 的原有逻辑中重构而来，采用 **Model-View-Controller (MVC)** 架构设计，提供：

- **7 种内置补间算法**：BlendNeighbor（相邻混合）、PushPull（推拉）、BlendEase（缓动混合）、ControlsToTween（控制点补间）、BlendRelative（相对混合）、SmoothRough（平滑粗糙）、TimeOffset（时间偏移）
- **STweenSlider 控件**：一个从 -1 到 1 的交互式滑块，支持拖拽、点击选取、过冲模式等
- **工具栏集成能力**：通过 FTweenToolbarController 将补间功能无缝集成到任何 CurveEditor 的工具栏中
- **鼠标滑动控制**：支持快捷键 + 鼠标移动的间接操作方式（类似 3D 视口中的快捷操作）
- **用户偏好持久化**：通过 UTweeningToolsUserSettings 记住每个功能区域上次使用的补间函数

## 使用场景

- 你在动画编辑器的曲线编辑器中选中了几个关键帧，想快速在它们之间做平滑过渡 → 使用任意补间算法拖拽滑块
- 你想把一段动画的关键帧整体向左/右"推移"，保持曲线形状不变 → 使用 TimeOffset 补间模式
- 你想在不过冲的前提下精确控制混合程度（0-100%）→ 使用 Normalized 缩放模式
- 你想体验更强的控制力，允许混合到 200% 产生夸张效果 → 启用 Overshoot 模式
- 你正在开发自己的编辑器插件，需要在工具栏中嵌入补间滑块 → 使用 FTweenToolbarController 和 FTweenControllers

## 蓝图用法

本插件主要面向 C++ 编辑器扩展，**不暴露 BlueprintCallable 节点**。所有功能通过 C++ API 和 Slate 控件使用。

但插件提供了可配置的 Slate 控件，可在自定义编辑器面板中使用。

### 核心控件

| 控件 | 说明 |
|---|---|
| `STweenSlider` | 交互式补间滑块，范围 [-1, 1]，支持拖拽和点击 |
| `STweenView` | 将 STweenSlider 与 FTweenModel 桥接的 MVC 视图组件 |

### 核心控制器

| 控制器 | 说明 |
|---|---|
| `FTweenToolbarController` | 管理工具栏上的组合框 + 滑块 + 过冲按钮 |
| `FTweenControllers` | 一站式封装，包含所有控制器的便利结构体 |
| `FCycleFunctionController` | 快捷键循环切换补间函数 |
| `FTweenMouseSlidingController` | 鼠标滑动驱动补间值 |
| `FMoveSliderByHotkeyController` | 快捷键直接设置滑块位置（25%/50%/100%） |

## C++ 用法

### 头文件引入

```cpp
// 补间模型基类和曲线补间模型
#include "Math/Models/TweenModel.h"
#include "Math/Models/CurveTweenModel.h"
#include "Math/Models/EditorTweenModel.h"

// 工具栏集成
#include "Widgets/MVC/TweenControllers.h"
#include "Widgets/MVC/TweenToolbarController.h"

// 命令注册
#include "TweeningUtilsCommands.h"

// 补间函数抽象
#include "Math/Abstraction/KeyBlendingAbstraction.h"
#include "Math/Abstraction/TweenRangeTemplates.h"

// 曲线混合核心算法
#include "Math/CurveBlending.h"
```

### 基本用法

从源码中提取的补间操作核心流程：

```cpp
// 1. 创建补间模型（以 PushPull 算法为例）
// 使用 TEditorTweenModel 包装，自动获得撤销/重做和切线展平功能
using FPushPullModel = TEditorTweenModel<TCurveTweenModel<EBlendFunction::PushPull>>;

const TSharedRef<FCurveEditor> CurveEditor = /* 获取曲线编辑器 */ ;
TSharedRef<FPushPullModel> TweenModel = MakeShared<FPushPullModel>(
    CurveEditor,  // TTangentFlatteningTweenProxy 参数
    TWeakPtr<FCurveEditor>(CurveEditor)  // TCurveTweenModel 参数
);

// 2. 检查是否有可混合的关键帧
if (TweenModel->HasAnythingToBlend())
{
    // 3. 执行单次混合操作（内部自动管理 StartBlendOperation/StopBlendOperation）
    TweenModel->BlendOneOff(0.5f);  // 向正方向混合 50%
}

// 4. 或者手动控制混合操作的生命周期
TweenModel->StartBlendOperation();
TweenModel->BlendValues(0.3f);   // 30%
TweenModel->BlendValues(0.7f);   // 70%
TweenModel->StopBlendOperation();
```

**来源**：`Public/Math/Models/CurveTweenModel.h`、`Public/Math/Models/EditorTweenModel.h`

### 工具栏集成

```cpp
// 将补间控件集成到你的编辑器工具栏
void FMyEditorModule::SetupToolbar(FToolBarBuilder& ToolbarBuilder)
{
    const TSharedRef<FUICommandList> CommandList = MakeShared<FUICommandList>();
    
    // 创建包含所有内置补间函数的容器
    TArray<FTweenModelUIEntry> Models;
    ForEachBlendFunction([&Models](EBlendFunction Func)
    {
        auto Model = MakeUnique<TEditorTweenModel<TCurveTweenModel<Func>>>(
            WeakCurveEditor, TWeakPtr<FCurveEditor>(WeakCurveEditor)
        );
        Models.Emplace(MoveTemp(Model), FTweenModelDisplayInfo(Func));
    });
    const TSharedRef<ITweenModelContainer> TweenModels = MakeShared<FTweenModelArray>(MoveTemp(Models));
    
    // 创建一站式控制器
    auto Controllers = MakeShared<FTweenControllers>(CommandList, TweenModels);
    
    // 将控件添加到工具栏
    Controllers->ToolbarController.AddToToolbar(ToolbarBuilder);
}
```

**来源**：`Public/Widgets/MVC/TweenControllers.h`、`Public/Math/Abstraction/TweenModelArray.h`

### 进阶用法

直接使用底层混合算法 API，不依赖 MVC 框架：

```cpp
#include "Math/ContiguousKeyMapping.h"
#include "Math/CurveBlending.h"
#include "Math/Abstraction/TweenRangeTemplates.h"

// 构建关键帧选择映射
FContiguousKeyMapping KeyMapping(CurveEditor);

// 逐键混合
BlendCurves_BySingleKey(CurveEditor, KeyMapping,
    [](const FCurveModelID& CurveId,
       const FContiguousKeyMapping::FContiguousKeysArray& AllBlendedKeys,
       const FContiguousKeys& CurrentBlendRange,
       int32 Index) -> double
    {
        // 使用预定义的 PushPull 算法
        return TweenRange<EBlendFunction::PushPull>(
            0.5f, AllBlendedKeys, CurrentBlendRange, Index
        );
    });

// 或者按范围批量混合
BlendCurve_ByKeyRange(CurveEditor, KeyMapping,
    [](const FCurveModelID& CurveId,
       const FContiguousKeyMapping::FContiguousKeysArray& AllBlendedKeys,
       const FContiguousKeys& CurrentBlendRange,
       TArray<FKeyHandle>& OutHandles,
       TArray<FKeyPosition>& OutPositions)
    {
        for (int32 i = 0; i < CurrentBlendRange.Indices.Num(); ++i)
        {
            OutHandles[i] = AllBlendedKeys.AllKeyHandles[CurrentBlendRange.Indices[i]];
            const FVector2D& Key = AllBlendedKeys.GetCurrent(CurrentBlendRange, i);
            OutPositions[i] = FKeyPosition(Key.X, Key.Y * 0.5f);  // 自定义混合逻辑
        }
    });
```

**来源**：`Public/Math/CurveBlending.h`、`Public/Math/Abstraction/TweenRangeTemplates.h`

## Demo 示例

### 自定义编辑器面板中的补间滑块集成

```cpp
// MyAnimEditorModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyAnimEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FUICommandList> CommandList;
    TSharedPtr<struct FTweenControllers> TweenControllers;
};
```

```cpp
// MyAnimEditorModule.cpp
#include "MyAnimEditorModule.h"
#include "Widgets/MVC/TweenControllers.h"
#include "Widgets/MVC/TweenToolbarController.h"
#include "Math/Abstraction/TweenModelArray.h"
#include "Math/Models/EditorTweenModel.h"
#include "Math/Models/CurveTweenModel.h"
#include "Math/Abstraction/KeyBlendingAbstraction.h"
#include "Framework/Commands/UICommandList.h"
#include "ToolMenus.h"

using namespace UE::TweeningUtilsEditor;

void FMyAnimEditorModule::StartupModule()
{
    CommandList = MakeShared<FUICommandList>();

    // 构建包含所有内置补间函数的容器
    TArray<FTweenModelUIEntry> ModelEntries;
    TWeakPtr<FCurveEditor> WeakCurveEditor; // 实际使用时从你的编辑器获取

    ForEachBlendFunction([&](EBlendFunction Func)
    {
        TUniquePtr<FTweenModel> Model;

        // 使用 TEditorTweenModel 包装，获得撤销/重做和切线展平
        switch (Func)
        {
        case EBlendFunction::BlendNeighbor:
            Model = MakeUnique<TEditorTweenModel<TCurveTweenModel<EBlendFunction::BlendNeighbor>>>(
                WeakCurveEditor, WeakCurveEditor);
            break;
        case EBlendFunction::PushPull:
            Model = MakeUnique<TEditorTweenModel<TCurveTweenModel<EBlendFunction::PushPull>>>(
                WeakCurveEditor, WeakCurveEditor);
            break;
        case EBlendFunction::BlendEase:
            Model = MakeUnique<TEditorTweenModel<TCurveTweenModel<EBlendFunction::BlendEase>>>(
                WeakCurveEditor, WeakCurveEditor);
            break;
        // ... 其他函数类似
        default:
            break;
        }

        if (Model)
        {
            ModelEntries.Emplace(MoveTemp(Model), FTweenModelDisplayInfo(Func));
        }
    });

    const TSharedRef<ITweenModelContainer> TweenModels =
        MakeShared<FTweenModelArray>(MoveTemp(ModelEntries));

    // 创建一站式控制器，自动绑定所有快捷键
    TweenControllers = MakeShared<FTweenControllers>(
        CommandList.ToSharedRef(),
        TweenModels,
        FName("MyAnimEditor") // 用户偏好保存键
    );

    // 注册工具栏扩展
    UToolMenus::RegisterStartupCallback(
        FSimpleMulticastDelegate::FDelegate::CreateLambda([this]()
        {
            UToolMenu* Menu = UToolMenus::Get()->ExtendMenu(
                "LevelEditor.LevelEditorToolBar.PlayToolBar");
            FToolMenuSection& Section = Menu->AddSection("MyAnimTweening");

            FToolBarBuilder Builder(CommandList, FMultiBoxCustomization::None);
            TweenControllers->ToolbarController.AddToToolbar(Builder);
            Section.AddEntry(FToolMenuEntry::InitToolBarBuilder(
                FName("MyAnimTweening"), Builder));
        })
    );
}

void FMyAnimEditorModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CurveEditor` | FCurveEditor、FCurveModelID、FCurveModel 等曲线编辑器核心类型 |
| `CurveEditorTools` | 曲线编辑器工具基础设施（如 FCurvesSnapshotBuilder、FScopedCurveChange） |
| `EditorFramework` | FUICommandInfo、FUICommandList 等编辑器命令系统 |

标准依赖（Core、CoreUObject、Engine、Slate、SlateCore、InputCore 等）已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `fe0c9ae2` | AIE: Time offset now handles pre and post infinity extrapolation | 时间偏移模式现在支持曲线无穷外推处理 |
| 2026-04-13 | `08a29230` | Tweening Utils: Improve parameters for easing tween function based on animator feedback. | 根据动画师反馈改进缓动补间函数的参数 |
| 2026-04-13 | `d90a7355` | Curve Editor: Fix tweening not flattening user tangents when tweening exactly 1 key. | 修复仅选择单个关键帧时切线未展平的问题 |
| 2026-04-09 | `eae4d14e` | Curve Editor: Add Tweening.Ease.SlopeExponent and Tweening.Ease.SlopeMultiplier CVars to better cont | 新增缓动函数的 CVar 控制参数，提供更精细的控制 |

### 维护评价

- **活跃维护**：最近 1 个月内有多次实质性更新（2026-04 ~ 2026-05）
- **持续改进**：频繁根据动画师用户反馈优化参数和行为，说明该插件已被实际生产使用
- **质量较高**：commit 中包含 bug 修复、功能增强和编译警告修复，维护态度认真
- **从创建至今**：约 1.4 年，属于较新的插件，正在快速迭代完善中

**推荐使用**。该插件处于活跃维护状态，且为官方 CurveEditor 的核心补间基础设施，后续会持续获得更新支持。从 commit 历史可以看到它已从实验性阶段进入正式生产使用，正在根据实际动画师反馈不断优化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/TweeningUtils)
- 官方文档：无（暂未发布独立文档）