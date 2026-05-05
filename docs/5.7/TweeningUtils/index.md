# Tweening Utils

> Algorithms and widgets useful for inbetweening.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `TweeningUtils` (Runtime), `TweeningUtilsEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-12-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/TweeningUtils) | |

## 用途

TweeningUtils 是 UE5 曲线编辑器（Curve Editor）的补间（Tweening / Inbetweening）工具插件。它提供了一套混合算法和 Slate UI 控件，允许动画师在曲线编辑器中选中一组关键帧后，通过拖动滑块将关键帧值向相邻范围"推拉"变形，实现类似传统动画中间帧（inbetweening）的效果。

插件解决的核心问题是：在动画曲线编辑中，手动逐帧调整关键帧值既耗时又不直观。通过 TweeningUtils，动画师可以用一个滑块交互式地批量调整连续关键帧的 Y 值，支持 7 种不同的混合算法（经典补间、Push/Pull、邻居混合、Ease、相对偏移、平滑/粗糙、时间偏移），每种算法产生不同的中间帧效果。

插件采用 Model-View-Controller 架构设计，核心混合算法与 UI 完全解耦，方便扩展新的混合函数。

## 使用场景

- 你在做动画曲线精修，需要快速将一组选中的关键帧值向首尾关键帧线性插值 → 用 ControlsToTween 模式
- 你需要让曲线的中间帧更平滑或更夸张（类似 After Effects 的 Easy Ease） → 用 Ease 或 Push/Pull 模式
- 你在处理动捕数据，需要平滑掉曲线中的噪声 → 用 Smooth/Rough 模式
- 你需要将动画曲线在时间轴上整体偏移（phase shift）而不用移动关键帧位置 → 用 Time Offset 模式
- 你需要将选中的关键帧值相对首尾偏移 → 用 Relative 模式

## 蓝图用法

此插件**不暴露任何蓝图接口**。所有类均为纯 C++，没有 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。它是编辑器内部工具，通过曲线编辑器工具栏的滑块控件进行交互。

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块 - 混合算法
#include "Math/KeyBlendingFunctions.h"

// Editor 模块 - 曲线编辑器集成
#include "Math/Models/CurveTweenModel.h"
#include "Math/Models/EditorTweenModel.h"
#include "Math/ContiguousKeyMapping.h"
#include "Math/CurveBlending.h"
#include "Math/Abstraction/TweenRangeTemplates.h"
#include "Math/Abstraction/KeyBlendingAbstraction.h"
#include "Math/Abstraction/TweenModelArray.h"
#include "Widgets/MVC/TweenControllers.h"
#include "Widgets/MVC/TweenToolbarController.h"
```

### 基本用法：直接调用混合算法

混合算法位于 `UE::TweeningUtils` 命名空间（Runtime 模块），可独立于 UI 使用。

```cpp
// 来源: KeyBlendingFunctions.h / KeyBlendingFunctions.cpp

#include "Math/KeyBlendingFunctions.h"

using namespace UE::TweeningUtils;

// 所有混合函数的 blend value 范围为 [-1.0, 1.0]
double BlendValue = 0.5;

FVector2d BeforeRange(0.0, 10.0);    // 范围前的关键帧 (时间, 值)
FVector2d Current(0.5, 15.0);         // 当前要混合的关键帧
FVector2d AfterRange(1.0, 10.0);      // 范围后的关键帧

// 1. ControlsToTween: 经典补间，所有关键帧线性插值到首尾之间
double NewVal1 = Blend_ControlsToTween(BlendValue, BeforeRange, AfterRange);

// 2. Push/Pull: -1 压平谷峰，+1 夸张谷峰
double NewVal2 = Blend_PushPull(BlendValue, BeforeRange, Current, AfterRange);

// 3. Neighbor: 线性插值到相邻范围
double NewVal3 = Blend_Neighbor(BlendValue, BeforeRange, Current, AfterRange);

// 4. Ease: S 曲线平滑过渡
double NewVal4 = Blend_Ease(BlendValue, BeforeRange, Current, AfterRange);

// 5. Relative: 整体偏移关键帧
FVector2d FirstBlended(0.2, 12.0);
FVector2d LastBlended(0.8, 14.0);
double NewVal5 = Blend_Relative(BlendValue, BeforeRange, FirstBlended, Current, LastBlended, AfterRange);

// 6. Smooth/Rough: 平滑噪声或加剧跳变
FVector2d BeforeCurrent(0.3, 11.0);
FVector2d AfterCurrent(0.7, 13.0);
double NewVal6 = Blend_SmoothRough(BlendValue, BeforeCurrent, Current, AfterCurrent);

// 7. OffsetTime: 相位偏移（需要可求值的曲线函数）
auto EvaluateFunc = [](double X) -> double { return FMath::Sin(X * 3.14159); };
FVector2d FirstBlendedKey(0.0, 0.0);
FVector2d LastBlendedKey(1.0, 0.0);
double NewVal7 = Blend_OffsetTime(0.5, Current,
    FirstBlendedKey, LastBlendedKey, BeforeRange, AfterRange, EvaluateFunc);
```

### 进阶用法：在曲线编辑器中驱动 Tween Model

Editor 模块提供了将混合算法集成到曲线编辑器的完整 MVC 框架。

```cpp
// 来源: CurveTweenModel.h, EditorTweenModel.h

#include "CurveEditor.h"
#include "Math/Models/EditorTweenModel.h"
#include "Math/Models/CurveTweenModel.h"
#include "Math/Abstraction/TweenRangeTemplates.h"

using namespace UE::TweeningUtilsEditor;

// 创建一个曲线补间模型，使用 PushPull 混合函数
// TEditorTweenModel 包装了 TCurveTweenModel，自动添加:
//   - Undo/Redo 事务支持 (TTransactionalTweenModelProxy)
//   - 切线自动压平 (TTangentFlatteningTweenProxy)
using FPushPullModel = TCurveTweenModel<EBlendFunction::PushPull>;
using FEditorModel = TEditorTweenModel<FPushPullModel>;

TSharedPtr<FCurveEditor> CurveEditor = /* 获取曲线编辑器 */;

TSharedRef<FEditorModel> Model = MakeShared<FEditorModel>(
    CurveEditor.ToWeakPtr()  // TTangentFlatteningTweenProxy 参数
    // FPushPullModel 无需额外参数
);

// 执行一次性混合
if (Model->HasAnythingToBlend())
{
    Model->BlendOneOff(0.5f);  // blend value = 0.5
}
```

### 进阶用法：使用 TweenModelContainer 管理多种混合函数

```cpp
// 来源: TweenModelArray.h, TweenModelDisplayInfo.h

#include "Math/Abstraction/TweenModelArray.h"
#include "Math/Abstraction/TweenModelDisplayInfo.h"

using namespace UE::TweeningUtilsEditor;

// 构建混合函数数组
TArray<FTweenModelUIEntry> Entries;

// 为每种混合函数创建模型和显示信息
auto AddModel = [&]<EBlendFunction Func>()
{
    using ModelType = TEditorTweenModel<TCurveTweenModel<Func>>;
    Entries.Add(FTweenModelUIEntry(
        MakeUnique<ModelType>(CurveEditor.ToWeakPtr()),
        FTweenModelDisplayInfo(Func)  // 自动从 EBlendFunction 获取 UI 信息
    ));
};
ForEachCurveTweenable(AddModel);

TSharedRef<FTweenModelArray> Container = MakeShared<FTweenModelArray>(MoveTemp(Entries));
```

### 进阶用法：将 Tween 控件添加到工具栏

```cpp
// 来源: TweenControllers.h, TweenToolbarController.h

#include "Widgets/MVC/TweenControllers.h"

using namespace UE::TweeningUtilsEditor;

// FTweenControllers 封装了所有 MVC 控件
TSharedRef<FUICommandList> CommandList = /* 命令列表 */;
TSharedRef<ITweenModelContainer> TweenModels = /* 上面创建的 Container */;

// 创建控制器集合（工具栏 + 快捷键切换 + 鼠标滑动）
FTweenControllers Controllers(CommandList, TweenModels, "MyAnimEditor");

// 添加到工具栏
FToolBarBuilder ToolbarBuilder(CommandList, FMultiBoxCustomization::None);
Controllers.ToolbarController.AddToToolbar(ToolbarBuilder);

// 用户交互:
// - 工具栏上的 Combo 按钮选择混合函数
// - 滑块拖动产生 [-1, 1] 的 blend value
// - Shift+U 快捷键循环切换混合函数
// - U + 鼠标移动 间接控制滑块
```

### 进阶用法：自定义 Tween Model

你可以继承 `FTweenModel` 来实现自定义混合逻辑（如 Control Rig 模型的混合）：

```cpp
// 来源: TweenModel.h

#include "Math/Models/TweenModel.h"

using namespace UE::TweeningUtilsEditor;

class FMyCustomTweenModel : public FTweenModel
{
public:
    virtual void StartBlendOperation() override
    {
        // 保存混合前的状态
    }

    virtual void StopBlendOperation() override
    {
        // 清理混合状态
    }

    virtual void BlendValues(float InNormalizedValue) override
    {
        // InNormalizedValue 范围 [-1, 1]
        const float ScaledValue = ScaleBlendValue(InNormalizedValue);
        // 应用自定义混合逻辑...
    }
};
```

### 进阶用法：使用 ContiguousKeyMapping 手动管理关键帧

```cpp
// 来源: ContiguousKeyMapping.h, KeyBlendingAbstraction.h

#include "Math/ContiguousKeyMapping.h"
#include "Math/Abstraction/KeyBlendingAbstraction.h"

using namespace UE::TweeningUtilsEditor;

// 从曲线编辑器构建关键帧映射
FContiguousKeyMapping KeyMapping(*CurveEditor);

// 或手动添加特定曲线的关键帧
TArray<FKeyHandle> SelectedKeys = /* 获取选中的关键帧句柄 */;
KeyMapping.Append(*CurveEditor, CurveModelId, SelectedKeys);

// 使用 BlendCurves_BySingleKey 逐帧混合
BlendCurves_BySingleKey(*CurveEditor, KeyMapping,
    [](const FCurveModelID& CurveId,
       const FContiguousKeyMapping::FContiguousKeysArray& AllBlendedKeys,
       const FContiguousKeys& CurrentBlendRange,
       int32 KeyIndex) -> double
    {
        double BlendValue = 0.5;
        return TweenRange<EBlendFunction::PushPull>(
            BlendValue, AllBlendedKeys, CurrentBlendRange, KeyIndex);
    });

// 或使用 BlendCurve_ByKeyRange 按范围混合
BlendCurve_ByKeyRange(*CurveEditor, KeyMapping,
    [](const FCurveModelID& CurveId,
       const FContiguousKeyMapping::FContiguousKeysArray& AllBlendedKeys,
       const FContiguousKeys& CurrentBlendRange,
       TArray<FKeyHandle>& OutHandles,
       TArray<FKeyPosition>& OutPositions)
    {
        // 自定义逻辑填充 OutHandles 和 OutPositions
    });
```

## 添加新的混合函数

插件设计了完善的扩展机制。源码中的注释（`KeyBlendingAbstraction.h`）给出了清晰的步骤：

1. 在 `KeyBlendingFunctions.h/cpp` 中添加新的混合函数
2. 扩展 `EBlendFunction` 枚举
3. 在 `FTweeningUtilsCommands` 中添加对应命令
4. 在 `FTweeningUtilsStyle` 中添加颜色、图标和样式
5. 更新 `KeyBlendingAbstraction.cpp` 中的 `GetFunctionData`
6. 如果是"简单"函数，还需在 `TweenRangeTemplates.h` 中特化 `TweenRange<>`

整个流程由 `static_assert` 保护——如果遗漏步骤，编译会失败并给出明确提示。

## Demo 示例

### 最小可编译示例：调用 Runtime 混合算法

**Build.cs** 依赖：

```csharp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "TweeningUtils",
});
```

**MyBlendExample.h**：

```cpp
#pragma once
#include "CoreMinimal.h"

class FMyBlendExample
{
public:
    static void RunBlendExample();
};
```

**MyBlendExample.cpp**：

```cpp
#include "MyBlendExample.h"
#include "Math/KeyBlendingFunctions.h"
#include "Math/Vector2D.h"

void FMyBlendExample::RunBlendExample()
{
    using namespace UE::TweeningUtils;
    
    // 模拟一组关键帧: 时间 0~1, 值 10~30~10 (山峰形状)
    FVector2d Before(0.0, 10.0);
    FVector2d Peak(0.5, 30.0);
    FVector2d After(1.0, 10.0);
    
    // Push/Pull: -1 将峰值压向线性插值
    double FlatValue = Blend_PushPull(-1.0, Before, Peak, After);
    // FlatValue ≈ 10.0 + 0.5 * (10.0 - 10.0) = 10.0 (完全压平)
    
    // Ease: 使用 S 曲线平滑过渡
    double EaseValue = Blend_Ease(0.5, Before, Peak, After);
    
    // Smooth/Rough: 平滑噪声
    FVector2d BeforePeak(0.3, 25.0);
    FVector2d AfterPeak(0.7, 22.0);
    double SmoothValue = Blend_SmoothRough(-1.0, BeforePeak, Peak, AfterPeak);
    // -1 趋向加权平均: 0.25*25 + 0.5*30 + 0.25*22 = 26.75
}
```

## 模块依赖

### TweeningUtils（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和数学库 |

### TweeningUtilsEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统（用于用户设置持久化） |
| `CurveEditor` | 曲线编辑器核心框架 |
| `Engine` | 引擎基础 |
| `InputCore` | 输入处理 |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate UI 框架 |
| `TweeningUtils` | Runtime 混合算法 |
| `UnrealEd` | 编辑器框架 |

## 维护状态

### 近期更新

1. `90498444` | 2025-07-23 | Curve editor: Rename FScopedKeyChange to FScopedCurveChange to better communicate that any changes are detected.
   - 重构：将 `FScopedKeyChange` 重命名为 `FScopedCurveChange`，更准确地表达其功能（不仅检测 key 变更，还能检测 FCurveAttributes 变更等）

2. `8f9de4b3` | 2025-07-21 | Curve Editor: Replaces obvious usages GetKeys with GetAllKeys.
   - API 重命名：将 `GetKeys` 替换为 `GetAllKeys`，提升代码可读性

3. `45fec60d` | 2025-07-21 | Curve Editor: Change transaction-based undo to new command-based undo.
   - 架构改进：将事务型 undo 改为命令型 undo，影响 `TTransactionalTweenModelProxy` 的实现

### 维护评价

- **创建时间**：2024-12-10，非常年轻的插件（约 1 年）
- **更新频率**：最近一次更新在 2025-07-23，距今不到 1 年，属活跃维护
- **维护状态**：**活跃维护中**。作为 UE5 曲线编辑器的核心工具，与 CurveEditor 模块紧密耦合，随 CurveEditor 一起演进
- **实验性**：否，`EnabledByDefault=true`
- **已知限制**：
  - 纯编辑器工具，不支持运行时或蓝图
  - 没有独立的自动化测试用例
  - `CanContainContent=true` 但实际无 Content 目录（.uplugin 声明可能为占位）
- **推荐度**：✅ 推荐使用。如果你在编辑器插件中需要集成曲线补间功能，这是官方提供的一站式解决方案，架构清晰、扩展性好

## 架构概览

```
TweeningUtils (Runtime)
└── Math/KeyBlendingFunctions.h          7 种纯数学混合算法

TweeningUtilsEditor (Editor)
├── Math/
│   ├── Models/
│   │   ├── TweenModel.h                 抽象基类 (MVC Model)
│   │   ├── CurveTweenModel.h            模板类，按 EBlendFunction 混合曲线
│   │   ├── EditorTweenModel.h           类型别名 = Transactional + TangentFlattening + CurveTween
│   │   ├── TransactionalTweenModelProxy.h  混合期间自动创建 Undo 事务
│   │   ├── TangentFlatteningTweenProxy.h   混合期间自动压平切线
│   │   └── CurveTimeOffsetTweenModel.h  TimeOffset 专用模型（非模板）
│   ├── ContiguousKeyMapping.h           连续关键帧范围映射
│   ├── CurveBlending.h                  曲线级混合操作
│   └── Abstraction/
│       ├── KeyBlendingAbstraction.h     EBlendFunction 枚举 + UI 工具函数
│       ├── TweenRangeTemplates.h        TweenRange<> 模板特化桥接
│       ├── TweenModelArray.h            模型数组容器
│       ├── TweenModelDisplayInfo.h      模型 UI 显示信息
│       └── ITweenModelContainer.h       模型容器接口
├── Widgets/
│   ├── STweenSlider.h                   滑块 Slate 控件 (View)
│   ├── TweenSliderStyle.h              滑块视觉样式
│   ├── ETweenScaleMode.h              Normalized/Overshoot 缩放模式
│   └── MVC/
│       ├── STweenView.h                 MVC View，桥接 Slider 和 Model
│       ├── TweenToolbarController.h     工具栏控制器 (Controller)
│       ├── TweenMouseSlidingController.h  U+鼠标滑动控制器
│       ├── MouseSlidingController.h     通用鼠标滑动基类
│       ├── CycleFunctionController.h    Shift+U 循环切换函数
│       └── TweenControllers.h          控制器集合（便捷封装）
├── TweeningUtilsCommands.h             编辑器命令注册
├── TweeningUtilsStyle.h                Slate 样式集
└── TweeningToolsUserSettings.h         用户偏好设置持久化
```

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/TweeningUtils)
- [Curve Editor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Editor/CurveEditor) — TweeningUtils 的主要依赖
