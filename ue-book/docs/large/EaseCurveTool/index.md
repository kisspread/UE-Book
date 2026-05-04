# Ease Curve Tool

> Sequencer / Curve Editor tool to ease tangents between keyframes using custom preset libraries

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预设库数据资产） |
| 模块 | `EaseCurveTool` (Editor) |
| 实验性 | ⚠️ 是（IsBetaVersion=true） |
| 创建时间 | 2025-09-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/EaseCurveTool) | |

## 用途

EaseCurveTool 是 UE5 Sequencer 的关键帧缓动曲线编辑工具。它解决的核心问题是：在 Sequencer 或 Curve Editor 中手动调整关键帧之间的切线（tangent）来实现缓入缓出效果非常繁琐。该工具提供了一个可视化曲线编辑器，配合预设库（Preset Library）系统，让用户可以快速选择、创建和应用各种缓动曲线预设，并将这些预设的切线数据应用到选中的关键帧上。

该插件最近（2025-09）从 Experimental 文件夹迁移到正式的 Animation 分类，但仍标记为 Beta 版本。

## 使用场景

- 你在 Sequencer 中为角色动画设置了关键帧，想快速给所有关键帧加上 ease-in/ease-out 效果 → 使用 EaseCurveTool 选择预设并一键应用
- 你需要自定义缓动曲线形状，保存为预设供团队复用 → 创建 EaseCurveLibrary 数据资产并添加自定义预设
- 你需要在 Curve Editor 中批量修改选中关键帧的切线 → 通过 Curve Editor 工具栏的 EaseCurveTool 按钮操作
- 你需要从外部导入 cubic bezier 缓动曲线（如 CSS ease 曲线）→ 使用 CubicBezierCurveSerializer 导入

## 蓝图用法

⚠️ 该插件是纯 Editor 工具，**没有暴露 BlueprintCallable 函数**。所有操作通过 Sequencer / Curve Editor 的 UI 交互完成，不可在蓝图中调用。

## C++ 用法

该插件的核心类不暴露为 Public API，主要通过编辑器 UI 操作。但可以通过以下方式在 C++ 中交互：

### 核心类概述

#### UEaseCurve

继承自 `UCurveFloat`，表示工具内部使用的缓动曲线。只有两个关键帧（起始和结束），通过修改切线来改变缓动形状。

```cpp
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Private/EaseCurve.h
UEaseCurve* EaseCurve = ...;
FEaseCurveTangents Tangents = EaseCurve->GetTangents();
EaseCurve->SetStartTangent(TangentValue, TangentWeight);
EaseCurve->SetEndTangent(TangentValue, TangentWeight);
```

#### FEaseCurveTangents

缓动曲线的核心数据结构，存储起点切线（Start/StartWeight）和终点切线（End/EndWeight）。支持从多种格式构造：

```cpp
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Private/EaseCurveTangents.h

// 从值直接构造
FEaseCurveTangents Tangents(0.5, 0.0, 0.5, 0.0);

// 从 RichCurveKey 构造
FEaseCurveTangents Tangents(RichCurveKey);

// 从 MovieSceneFloatChannel 的值构造
FEaseCurveTangents Tangents(MovieSceneFloatValue);

// 从 cubic bezier 字符串构造（CSS ease 曲线格式）
FEaseCurveTangents Tangents(TEXT("0.45, 0.34, 0.0, 1.00"));

// 转换为 cubic bezier 坐标
TStaticArray<double, 4> BezierPoints;
Tangents.ToCubicBezier(BezierPoints);

// 计算曲线长度（用于排序，越大越"硬"）
double Length = Tangents.CalculateCurveLength();
```

#### FEaseCurvePreset

预设结构体，包含分类名（Category）、名称（Name）和切线数据（Tangents）：

```cpp
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Private/EaseCurvePreset.h
FEaseCurvePreset Preset(
    FText::FromString("Ease In"),
    FText::FromString("Cubic"),
    FEaseCurveTangents(0.5, 0.0, 0.5, 0.0)
);
```

#### UEaseCurveLibrary

数据资产类，管理一组预设。插件附带 `Content/DefaultPresetLibrary.uasset` 作为默认预设库。

```cpp
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Public/EaseCurveLibrary.h
UEaseCurveLibrary* Library = ...;
TArray<FEaseCurvePreset> AllPresets = Library->GetPresets();
TArray<FText> Categories = Library->GetCategories();
TArray<FEaseCurvePreset> EaseInPresets = Library->GetCategoryPresets(FText::FromString("Ease In"));

// 添加新预设
FEaseCurvePreset NewPreset;
Library->AddPresetToNewCategory(
    FText::FromString("Custom"),
    FEaseCurveTangents(0.25, 0.1, 0.25, 1.0),
    NewPreset
);
```

### Serializer 扩展

可以通过继承 `UEaseCurveSerializer` 实现自定义导入导出格式：

```cpp
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Public/EaseCurveSerializer.h

// 内置的 UCubicBezierCurveSerializer 已实现 cubic bezier 格式的导入导出
// Engine/Plugins/Animation/EaseCurveTool/Source/EaseCurveTool/Private/Serializers/CubicBezierCurveSerializer.h
```

### 工具设置

`UEaseCurveToolSettings`（继承 `UDeveloperSettings`）存储用户配置，可在编辑器设置中找到：

| 设置 | 说明 | 默认值 |
|---|---|---|
| ShowInSidebar | 在 Sequencer 侧边栏显示工具 | `true` |
| ShowCurveEditorToolbarButton | 在 Curve Editor 工具栏显示按钮 | `false` |
| DefaultPresetLibrary | 默认预设库资产 | （内置默认库） |
| NewPresetCategory | 新预设的默认分类名 | （空） |
| QuickEaseTangents | 快速缓动的切线值（cubic bezier 格式） | （空） |
| GraphSize | 曲线图高度（64-256） | `140` |
| GridSnap | 切线吸附到网格 | `false` |
| GridSize | 网格大小（4-24） | `8` |
| AutoZoomToFit | 修改切线后自动缩放适配 | `false` |
| AutoFlipTangents | 当关键帧值递减时自动翻转切线 | `true` |

### 工具操作模式

```cpp
// EEaseCurveToolMode（引擎内部）
enum class EEaseCurveToolMode : uint8
{
    DualKeyEdit,   // 编辑选中关键帧的 LeaveTangent + 下一个关键帧的 ArriveTangent
    SingleKeyEdit  // 仅编辑选中的单个关键帧
};

// EEaseCurveToolOperation
enum class EEaseCurveToolOperation : uint8
{
    InOut,  // 同时修改入和出切线
    In,     // 仅修改入切线
    Out     // 仅修改出切线
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `CurveEditor` | 曲线编辑器框架 |
| `Sequencer` / `SequencerCore` | Sequencer 编辑器集成 |
| `MovieScene` / `MovieSceneTools` | 关键帧通道数据操作 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 工具栏/菜单扩展 |
| `UnrealEd` | 编辑器基础功能 |
| `PropertyEditor` | 属性面板集成 |
| `Json` | JSON 序列化支持 |
| `DeveloperSettings` | 设置系统基类 |
| `EditorSubsystem` | 编辑器子系统生命周期 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-14 | `ec8831fb` | 修复 PostUndo/PostRedo 处理，确保撤销/重做时正确调用 `UpdateEaseCurveFromKeySelections()` |
| 2025-09-26 | `af27afdd` | 将插件从 Experimental 文件夹迁移到 Animation 分类 |

### 维护评价

- **状态**: Beta（IsBetaVersion=true），刚从 Experimental 毕业
- **最近更新**: 2025-10-14，仅 2 次 commit 记录
- **评价**: 该插件非常新（约 1 年），刚完成从 Experimental 到正式分类的迁移。目前仍标记为 Beta，API 和功能可能还有变动。代码结构清晰，功能完整（预设管理、多种序列化格式、Curve Editor 集成、Sequencer 侧边栏集成），但因为是 Beta 状态，建议关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/EaseCurveTool)
