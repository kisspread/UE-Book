# Music Environment

> A Project-Wide source of musical information (musically synchronized clocks, events, etc.)

| 属性 | 值 |
|---|---|
| 中文名 | 音乐环境 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MusicEnvironment` (Runtime), `MusicEnvironmentEditor` (Runtime), `MusicEnvironmentTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment) | |

## 用途

MusicEnvironment 是一个由 Harmonix GenTech 团队开发的项目级音乐信息中枢插件，旨在为整个项目提供统一的音乐同步基础设施。它解决了以下核心问题：

- **音乐同步时钟**：提供项目范围内的音乐同步时钟，让多个系统（音频、动画、视觉效果、游戏逻辑）能够基于同一个音乐节拍时间轴运行，避免各系统各自维护时钟导致的同步漂移。
- **帧精确时间签名**：引入基于帧的时间签名（Frame-Based Time Signature）概念，将传统的音乐节拍（如 4/4 拍）映射到引擎帧率上，确保在非实时播放场景（如时间轴编辑、离线渲染）中也能保持音乐结构的精确性。
- **音乐事件广播**：作为项目范围内音乐事件的中央发布源，其他系统可以订阅节拍、小节、音乐段落等事件，实现高度协调的视听体验。

该插件最初是引擎内核的"始终启用"模块，后迁移为可选的 Runtime 插件，表明 Epic 希望将其作为可选功能提供给需要音乐同步能力的项目（如音乐游戏、节奏游戏、互动音乐体验等）。

## 使用场景

- 你在开发一款音乐/节奏游戏（如 Guitar Hero、Rock Band 风格）→ 用 MusicEnvironment 确保所有视觉反馈与音乐节拍严格同步
- 你需要让粒子特效、灯光、动画在特定节拍点触发 → 用 MusicEnvironment 提供的音乐事件系统
- 你在做互动音乐系统（如自适应配乐），需要项目级别的音乐状态管理 → 用 MusicEnvironment 作为中央协调器
- 你在编辑器中需要可视化和编辑基于帧的音乐时间签名 → 启用 MusicEnvironmentEditor 模块

## 蓝图用法

基于源码分析，MusicEnvironment 核心模块主要提供底层 C++ 接口，蓝图暴露功能有限。编辑器模块提供了可视化控件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 时间签名输入控件 | Slate 控件，用于输入基于帧的音乐时间签名（分子/分母） | `SFrameBasedTimeSignatureInput` |

> **注意**：由于该插件仍处于 Beta/实验阶段，蓝图 API 可能在后续版本中大幅变更。

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "MusicEnvironmentModule.h"

// 编辑器模块（仅在编辑器中使用）
#include "MusicEnvironmentEditorModule.h"
```

### 基本用法 — 基于帧的时间签名

该插件引入了 `FFrameBasedTimeSignature` 结构体，用于表示与引擎帧率关联的时间签名：

```cpp
// 创建一个 4/4 拍的时间签名（基于帧）
FFrameBasedTimeSignature TimeSignature;
// 具体字段需参考 FFrameBasedTimeSignature 定义
```

*来源：`Engine/Plugins/Runtime/MusicEnvironment/` 相关头文件*

### 进阶用法 — 自定义属性面板

在编辑器中为 `FFrameBasedTimeSignature` 类型属性注册自定义面板展示：

```cpp
// 通常在模块 StartupModule 中注册
PropertyModule.RegisterCustomPropertyTypeLayout(
    FFrameBasedTimeSignature::StaticStruct()->GetFName(),
    FOnGetPropertyTypeCustomizationInstance::CreateStatic(
        &FFrameBasedTimeSignatureCustomization::MakeInstance
    )
);
```

*来源：`Source/MusicEnvironmentEditor/Private/Customization/`*

## Demo 示例

以下示例展示如何在自定义 Slate 界面中嵌入时间签名输入控件：

```cpp
// MyMusicPanel.h
#pragma once

#include "Widgets/SCompoundWidget.h"

class SMyMusicPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMusicPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OnTimeSignatureChanged(const FFrameBasedTimeSignature& NewSignature, ETextCommit::Type CommitType);
};
```

```cpp
// MyMusicPanel.cpp
#include "MyMusicPanel.h"
#include "Widgets/Input/SFrameBasedTimeSignatureInput.h"

void SMyMusicPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("时间签名")))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            SNew(SFrameBasedTimeSignatureInput)
            .Value(FFrameBasedTimeSignature()) // 默认值
            .MaxNumerator(32)
            .MaxDenominator(32)
            .OnValueCommitted_Raw(this, &SMyMusicPanel::OnTimeSignatureChanged)
        ]
    ];
}

void SMyMusicPanel::OnTimeSignatureChanged(
    const FFrameBasedTimeSignature& NewSignature,
    ETextCommit::Type CommitType)
{
    // 处理时间签名变更
    UE_LOG(LogTemp, Log, TEXT("Time signature updated"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | 编辑器模块中注册自定义属性面板（FFrameBasedTimeSignatureCustomization） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等及 PropertyEditor）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 UE_LOGF |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 修复非 Unity 编译的头文件缺失问题 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏优化编译 |
| 2025-06-23 | `d42c028c` | Music Map Song Length Data | 新增音乐映射歌曲长度数据功能 |
| 2025-06-11 | `e0d87df8` | Replace some usages of FORCEINLINE with inline in Audio modules. | 替换 FORCEINLINE 为 inline 以改善编译兼容性 |

### 维护评价

- **创建时间**：2024 年 12 月，属于较新的插件
- **更新频率**：2025-2026 年间有多次实质性更新，包括功能新增（Music Map Song Length Data）和构建系统优化
- **实验状态**：`IsBetaVersion=true` 且 `IsExperimentalVersion=true`，表明 API 尚未稳定
- **手动启用**：`EnabledByDefault=false`，需要在项目设置中手动启用
- **团队背景**：由 Harmonix GenTech 团队（知名音乐游戏开发商）开发，具有专业背景

**综合评价**：该插件处于**积极开发中**的实验阶段。近期更新频繁，包括实质性功能新增。建议仅在音乐/节奏游戏等强需求场景中使用，并做好 API 变更的准备。不建议用于需要长期稳定的生产项目，除非愿意跟踪上游变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment)