# Curve Editor Tools

> This provides a default set of editing tools for the Curve Editor.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CurveEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-05-24 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/CurveEditorTools) | |

## 用途

Curve Editor Tools 是 UE5 曲线编辑器（Curve Editor）的核心工具插件，为动画曲线的编辑提供了一套完整的交互工具集。它解决了"如何高效地批量操作动画关键帧"的问题——没有这个插件，曲线编辑器只是一个查看器；有了它，你可以对关键帧进行变换、缩放、重定时和晶格变形等高级操作。

该插件注册了 **4 个工具扩展**（Transform、Retime、MultiScale、Lattice）、**2 个编辑器扩展**（Focus、Tween）和 **1 个滤镜**（FFT），并通过扩展 Curve Editor 工具栏菜单使这些工具在 UI 中可用。

## 使用场景

- 你需要对选中的动画关键帧进行框选式平移/缩放，支持软选择衰减 → 用 **Transform Tool**
- 你需要调整动画的时间节奏（加速/减速），而不改变曲线形状 → 用 **Retime Tool**
- 你需要在 X 或 Y 轴上独立缩放关键帧，支持自定义缩放中心 → 用 **MultiScale Tool**
- 你需要像 Photoshop 液化工具一样，通过拖拽晶格控制点来变形曲线 → 用 **Lattice Tool**
- 你需要对曲线进行 FFT 低通/高通滤波来平滑噪声数据 → 用 **FFT Filter**
- 你需要在曲线编辑器中使用 Tweening（缓动）功能来调整关键帧插值 → 用 **Tween Extension**

## 工具详解

### Transform Tool（变换工具）

`FCurveEditorTransformTool` — 最基础也最常用的工具。在选中的关键帧周围绘制一个边界框（marquee widget），用户可以：

- **拖拽边框边缘**：在 X 或 Y 方向上平移关键帧
- **拖拽角点**：同时缩放 X 和 Y
- **拖拽 Falloff 区域**（按住 Ctrl）：软选择模式，距离拖拽点越远的关键帧受影响越小
- **自定义缩放中心**：可通过 UI 拖拽缩放原点

支持的衰减插值类型（`EToolTransformInterpType`）：
- Linear（线性）
- Sinusoidal（正弦）
- Cubic（三次）
- CircularIn / CircularOut（圆弧入/出）
- ExpIn / ExpOut（指数入/出）

工具选项通过 `FTransformToolOptions` 暴露，可在 Details 面板中编辑。

### Retime Tool（重定时工具）

`FCurveEditorRetimeTool` — 用于调整动画的时间节奏。核心概念是 **Anchor（锚点）**：

- 在时间轴上放置锚点（`FCurveEditorRetimeAnchor`），每个锚点分为 **Move-Only Bar**（窄区域，仅移动锚点）和 **Retime Bar**（宽区域，拖拽会重映射关键帧时间）
- 拖拽 Retime Bar 时，锚点两侧的关键帧时间会被重新映射——相当于对动画做局部加速/减速
- 支持锚点的添加、删除、选中和高亮
- 使用 `UCurveEditorRetimeToolData`（UObject）存储锚点数据以支持 Undo/Redo

### MultiScale Tool（多轴缩放工具）

`FCurveEditorMultiScaleTool` — 专为独立 X/Y 缩放设计。与 Transform Tool 不同，它提供了：

- **X/Y 独立滑块**：分别控制水平和垂直缩放
- **X/Y 侧边栏**：拖拽缩放手柄
- **缩放中心选择**（`EMultiScalePivotType`）：
  - Average（关键帧平均位置）
  - BoundCenter（边界中心）
  - FirstKey（第一个关键帧）
  - LastKey（最后一个关键帧）

工具选项通过 `FMultiScaleToolOptions` 暴露，包含 `XScale`、`YScale` 和 `PivotType`。

### Lattice Tool（晶格变形工具）

`FCurveEditorLatticeTool` — 最复杂的工具，实现了 2D 晶格变形器（Lattice Deformer）。它在选中的关键帧上方放置一个可编辑的网格：

- **拖拽控制点**：移动单个网格顶点，影响周围关键帧
- **拖拽边**：移动整条边，同时翻转/镜像切线
- **拖拽单元格**：移动整个网格单元
- **双击边**：将该边移动到对边位置（展平曲线段）
- **双击网格中心**：镜像整个网格

核心组件：
- `FLatticeDeformer2D` / `TLatticeDeformer2D<T>`：2D 晶格变形器，基于双线性插值
- `FPerCurveLatticeData`：每条曲线独立的变形数据，支持不同视图模式（Absolute/Normalized）
- `FLatticeEdgeTangentsMirrorOp` / `FLatticePointTangentsMirrorOp`：切线镜像操作
- `UCurveEditorTools_LatticeUndoObject`：Undo 对象，保存晶格形状快照

晶格控制点索引方式：
```
 0---1---2---3
 |   |   |   |
 4---5---6---7
 |   |   |   |
 8---9--10--11
```

### FFT Filter（傅里叶变换滤镜）

`UCurveEditorFFTFilter` — 对曲线数据应用频域滤波。在 Curve Editor 的 Filter 菜单中可用。

参数：
- `CutoffFrequency`（0-1）：归一化截止频率。低通时值越低越平滑，高通时值越高越平滑
- `Type`：Lowpass（低通，去除高频噪声）或 Highpass（高通，去除低频趋势）
- `Response`：Butterworth 或 Chebyshev 滤波器实现
- `Order`（1-8）：滤波器阶数，越高衰减越陡峭

实现流程：先用 Bake Filter 将曲线重采样为等间距数据，再应用 `Audio::Filter` 进行频域滤波，最后在原始关键帧位置重新采样。

### Tween Extension（缓动扩展）

`FTweenEditorExtension` — 在曲线编辑器工具栏中集成 Tweening 工具，允许用户以交互方式调整关键帧的缓动模型。通过 `FCurveEditorTweenModels` 管理可用的缓动模型数组。

### Focus Extension（聚焦扩展）

`FCurveEditorFocusExtension` — 在 Curve Editor 工具栏的 Framing 菜单中添加两个命令：
- **Focus Playback Time**：聚焦到当前播放时间
- **Focus Playback Range**：聚焦到播放范围

## 蓝图用法

本插件 **没有公开的蓝图 API**。所有源码都在 `Private/` 目录下，不暴露 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。这是一个纯编辑器工具插件，通过 Curve Editor UI 交互使用。

`UCurveEditorFFTFilter` 的属性（`CutoffFrequency`、`Type`、`Response`、`Order`）标记了 `BlueprintReadWrite`，但这是为了 Details 面板编辑，而非蓝图图使用。

## C++ 用法

本插件不暴露 Public 头文件，所有类均为 Editor 模块内部实现。如果需要以编程方式与 Curve Editor 工具交互，应通过 `ICurveEditorModule` 接口注册自定义工具扩展。

### 头文件引入

由于没有 Public API，不能直接 include。要扩展 Curve Editor 工具，使用：

```cpp
#include "ICurveEditorModule.h"
#include "ICurveEditorToolExtension.h"
```

### 注册自定义工具扩展

参考本插件的 `FCurveEditorToolsModule::StartupModule()` 实现模式：

```cpp
// 从 CurveEditorToolsModule.cpp 提取的模式
ICurveEditorModule& CurveEditorModule = 
    FModuleManager::Get().LoadModuleChecked<ICurveEditorModule>("CurveEditor");

// 注册工具扩展
auto CreateMyTool = [](TWeakPtr<FCurveEditor> InCurveEditor) -> TUniquePtr<ICurveEditorToolExtension>
{
    return MakeUnique<FMyCustomTool>(InCurveEditor);
};
FDelegateHandle Handle = CurveEditorModule.RegisterToolExtension(
    FOnCreateCurveEditorToolExtension::CreateLambda(CreateMyTool)
);

// 注册编辑器扩展
auto CreateMyExtension = [](TWeakPtr<FCurveEditor> InCurveEditor) -> TSharedRef<ICurveEditorExtension>
{
    return MakeShared<FMyEditorExtension>(InCurveEditor);
};
FDelegateHandle ExtHandle = CurveEditorModule.RegisterEditorExtension(
    FOnCreateCurveEditorExtension::CreateStatic(&CreateMyExtension)
);
```

### ICurveEditorToolExtension 接口

实现自定义工具需要重写以下关键方法：

```cpp
class FMyTool : public ICurveEditorToolExtension
{
    // 绘制工具 UI（边框、手柄等）
    virtual void OnPaint(const FPaintArgs& Args, const FGeometry& AllottedGeometry,
        const FSlateRect& MyCullingRect, FSlateWindowElementList& OutDrawElements,
        int32 PaintOnLayerId, const FWidgetStyle& InWidgetStyle, bool bParentEnabled) const override;
    
    // 每帧更新
    virtual void Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, 
        const float InDeltaTime) override;
    
    // 鼠标事件
    virtual FReply OnMouseButtonDown(TSharedRef<SWidget> OwningWidget, 
        const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FReply OnMouseMove(TSharedRef<SWidget> OwningWidget, 
        const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    virtual FReply OnMouseButtonUp(TSharedRef<SWidget> OwningWidget, 
        const FGeometry& MyGeometry, const FPointerEvent& MouseEvent) override;
    
    // 工具激活/停用
    virtual void OnToolActivated() override;
    virtual void OnToolDeactivated() override;
    
    // 绑定快捷键
    virtual void BindCommands(TSharedRef<FUICommandList> CommandBindings) override;
    
    // 工具元数据
    virtual FText GetLabel() const override;
    virtual FText GetDescription() const override;
    virtual FSlateIcon GetIcon() const override;
};
```

### 使用 Lattice Deformer

`FLatticeDeformer2D` 是一个可复用的 2D 晶格变形器：

```cpp
using namespace UE::CurveEditorTools;

// 创建一个 2x1 的晶格（2 个单元格宽，1 个高）
FLatticeDeformer2D Deformer(2, 1, FVector2D(0.0, 0.0), FVector2D(10.0, 5.0));

// 添加关键帧到晶格（必须在移动控制点之前）
Deformer.AddPoints_BeforeLatticeMoved(KeyPositions, 
    [](int32 InputIndex, const FPointIndex& PointIndex) {
        // 记录每个点被分配到哪个单元格
    });

// 移动控制点，自动更新所有受影响的关键帧
TArray<int32> PointsToUpdate = { 1 }; // 移动索引 1 的控制点
TArray<FVector2D> NewPositions = { FVector2D(5.0, 8.0) };
Deformer.UpdateControlPoints(PointsToUpdate, NewPositions,
    [](const FPointIndex& PointIndex, const FVector2D& NewPosition) {
        // 处理每个关键帧的新位置
    });
```

使用模板版本附加元数据：

```cpp
// TLatticeDeformer2D 允许为每个关键帧附加自定义数据（如 FKeyHandle）
TLatticeDeformer2D<FKeyHandle> TypedDeformer(2, 1, BottomLeft, TopRight);
TArray<FKeyHandle> Handles = { Handle1, Handle2, Handle3 };
TArray<FVector2D> Positions = { Pos1, Pos2, Pos3 };
TypedDeformer.AddPoints_BeforeLatticeMoved(Handles, Positions);
```

## 模块依赖

从 `CurveEditorTools.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CurveEditor` | 曲线编辑器核心框架 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统（Private） |
| `SlateCore` | Slate UI 核心（Private） |
| `Slate` | Slate UI 框架（Private） |
| `SequencerWidgets` | Sequencer 控件（Private） |
| `EditorFramework` | 编辑器框架（Private） |
| `UnrealEd` | 编辑器工具（Private） |
| `CoreUObject` | UObject 系统（Private） |
| `AudioMixer` | 音频混合器，FFT 滤镜使用（Private） |
| `SignalProcessing` | 信号处理库，FFT 滤波算法（Private） |
| `EditorStyle` | 编辑器样式（Private） |
| `TweeningUtils` | Tweening 工具库（Private） |
| `TweeningUtilsEditor` | Tweening 编辑器扩展（Private） |

插件依赖：
- **TweeningUtils**（在 `.uplugin` 中声明）

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-10-09 | `e4eaeffd` | Fix lattice tool no longer working correctly | 修复晶格工具失效的 bug |
| 2025-10-03 | `19d4353e` | Fix performance issue when no keys selected by caching common curve info | 性能优化：缓存曲线公共信息，避免每帧重建。引入 `FSharedCurveInfoModel` |
| 2025-10-02 | `a733b818` | Fix retime tool freezing the editor when moving many keys | 性能优化：重定时工具批量移动关键帧时改用 `ParallelFor` 并行处理 |
| 2025-09-25 | `05421117` | Fix lattice tool resetting its shape when you cause key stacking to remove keys | 修复晶格在堆叠关键帧被移除时重置形状的问题 |
| 2025-09-25 | `f0835e99` | Lattice tool now restores shape when you undo | 晶格工具支持 Undo 时恢复形状 |

### 维护评价

- **创建时间**：2019 年 5 月，约 7 年历史
- **最近更新**：2025 年 10 月，非常活跃
- **更新内容**：近期集中在性能优化和 Bug 修复，表明工具已进入成熟稳定期
- **活跃度**：🟢 **活跃维护** — 最近 6 个月内有多次实质性更新
- **推荐使用**：✅ 强烈推荐。这是曲线编辑器的核心工具集，默认启用，是 UE5 动画工作流不可或缺的部分

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/CurveEditorTools)
- [官方文档]()（无）
- [Curve Editor 核心模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Editor/CurveEditor)
- [TweeningUtils 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/TweeningUtils)
