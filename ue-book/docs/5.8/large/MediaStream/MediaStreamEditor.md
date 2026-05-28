# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流代理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器自定义UI） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream) | |

## 用途

MediaStream 插件为 UE 的媒体框架提供了一个**内容无关、类型无关的可链式媒体代理层**（Media Proxy）。它在 UE 原生的 `UMediaPlayer` / `UMediaTexture` 之上封装了 `UMediaStream` 抽象，实现以下目标：

1. **统一媒体管理**：将媒体源（Source）、播放器（Player）、纹理（Texture）、缓存（Cache）等松散组件整合为一个 `UMediaStream` 对象，简化引用关系
2. **方案化媒体源**（Scheme-based Source）：通过 `IMediaStreamSchemeHandler` 接口支持多种媒体源方案，每种方案可在详情面板中独立配置
3. **可链式代理**：支持代理链模式，可在媒体流路径中插入中间处理节点
4. **编辑器深度集成**：提供详情面板自定义、可拖拽时间轴（Scrub Track）、播放控制按钮、关卡序列集成等编辑器功能

简单来说，原生媒体框架需要手动管理 Player ↔ Texture ↔ Source 之间的绑定关系，MediaStream 将这一切封装为一个对象，降低使用复杂度。

## 使用场景

- 你在关卡中放置了大量媒体展示屏幕 → 用 MediaStream 统一管理每个屏幕的媒体播放
- 你需要在 Sequencer 时间轴中精确控制视频播放的时间点 → MediaStream 提供 Sequencer 轨道集成
- 你的项目需要支持不同类型的媒体源（文件、流媒体、资产引用等）→ MediaStream 的 Scheme 机制支持多种源类型切换
- 你需要在编辑器中快速预览和调试媒体播放 → MediaStreamEditor 提供播放控制面板和详细信息显示

## 蓝图用法

### 核心节点

MediaStreamEditor 模块提供了 UI 组件工厂方法，可在蓝图中嵌入媒体控制界面：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateSourceSchemeRows` | 生成媒体源方案选择控件 | `FMediaStreamWidgets` |
| `CreateTextureDetailsWidget` | 创建媒体纹理详情展示控件 | `FMediaStreamWidgets` |
| `CreateTrackWidget` | 创建可拖拽播放进度条控件 | `FMediaStreamWidgets` |
| `CreateControlsWidget` | 创建播放控制按钮组（播放/暂停/倒放等） | `FMediaStreamWidgets` |

> ⚠️ 注意：上述 API 均为 C++ 层的 Slate 控件工厂方法，主要供编辑器扩展使用。运行时蓝图操作 UMediaStream 对象的 API 位于 `MediaStream` 运行时模块中（本文档未包含其源码分析）。

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "MediaStream.h"

// 编辑器模块
#include "MediaStreamWidgets.h"
```

### 基本用法 — 创建媒体控件（编辑器扩展）

`FMediaStreamWidgets` 提供了一组静态工厂方法，用于在自定义编辑器面板中嵌入媒体控制 UI。

**来源**: `Public/MediaStreamWidgets.h`

```cpp
#include "MediaStreamWidgets.h"

// 为单个 MediaStream 创建媒体纹理详情面板
TSharedRef<SWidget> TextureDetails = 
    UE::MediaStreamEditor::FMediaStreamWidgets::CreateTextureDetailsWidget(MyMediaStream);

// 为多个 MediaStream 创建可拖拽时间轴
TArray<UMediaStream*> MediaStreams = { MediaStream1, MediaStream2 };
TSharedRef<SWidget> Track = 
    UE::MediaStreamEditor::FMediaStreamWidgets::CreateTrackWidget(MediaStreams);

// 创建播放控制按钮组（播放、暂停、倒放、快进等）
TSharedRef<SWidget> Controls = 
    UE::MediaStreamEditor::FMediaStreamWidgets::CreateControlsWidget(MediaStreams);

// 生成媒体源方案选择行（如文件源、流媒体源等）
IMediaStreamSchemeHandler::FCustomWidgets SourceWidgets = 
    UE::MediaStreamEditor::FMediaStreamWidgets::GenerateSourceSchemeRows(MyMediaStream);
```

### 进阶用法 — Sequencer 集成

`FMediaStreamEditorSequencerLibrary` 提供了关卡序列（Level Sequence）集成的工具方法。

**来源**: `Private/MediaStreamEditorSequencerLibrary.h`

```cpp
#include "MediaStreamEditorSequencerLibrary.h"

// 获取当前打开的关卡序列
ULevelSequence* LevelSequence = FMediaStreamEditorSequencerLibrary::GetLevelSequence();

// 检查 MediaStream 是否已有关联的 Sequencer 轨道
if (FMediaStreamEditorSequencerLibrary::HasTrack(MyMediaStream))
{
    UE_LOG(LogTemp, Log, TEXT("MediaStream already has a sequencer track"));
}

// 检查是否可以添加轨道（依赖 LevelSequenceEditor 插件）
if (FMediaStreamEditorSequencerLibrary::CanAddTrack(MyMediaStream))
{
    // 将 MediaStream 添加为 Sequencer 轨道
    FMediaStreamEditorSequencerLibrary::AddTrack(MyMediaStream);
}
```

### 进阶用法 — 自定义详情面板

你可以继承或使用 `FMediaStreamCustomization` 来自定义 `UMediaStream` 对象在属性面板中的显示方式。

**来源**: `Private/DetailsPanel/MediaStreamCustomization.h`

```cpp
#include "MediaStreamCustomization.h"

// FMediaStreamCustomization 自动为 UMediaStream 对象添加以下分类：
// - 控制分类（Control）：可拖拽轨道 + 播放控制按钮
// - 源分类（Source）：媒体源方案选择与配置
// - 详情分类（Details）：媒体和播放器详细信息
// - 纹理分类（Texture）：媒体纹理对象与选项
// - 缓存分类（Cache）：媒体缓存设置
// - 播放器分类（Player）：播放器配置选项
```

## Demo 示例

以下示例展示了如何创建一个自定义编辑器面板，嵌入 MediaStream 的媒体控制界面：

### MediaStreamPanel.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class UMediaStream;

class SMediaStreamPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMediaStreamPanel) {}
        SLATE_ARGUMENT(UMediaStream*, MediaStream)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TWeakObjectPtr<UMediaStream> MediaStreamWeak;
};
```

### MediaStreamPanel.cpp

```cpp
#include "MediaStreamPanel.h"
#include "MediaStreamWidgets.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"

void SMediaStreamPanel::Construct(const FArguments& InArgs)
{
    MediaStreamWeak = InArgs._MediaStream;
    UMediaStream* MediaStream = InArgs._MediaStream;

    if (!MediaStream)
    {
        ChildSlot
        [
            SNew(SBox)
            .Padding(10.0f)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("No Media Stream assigned.")))
            ]
        ];
        return;
    }

    TArray<UMediaStream*> MediaStreams = { MediaStream };

    ChildSlot
    [
        SNew(SVerticalBox)

        // 播放控制按钮
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            UE::MediaStreamEditor::FMediaStreamWidgets::CreateControlsWidget(MediaStreams)
        ]

        // 可拖拽播放进度条
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            UE::MediaStreamEditor::FMediaStreamWidgets::CreateTrackWidget(MediaStreams)
        ]

        // 媒体纹理详情
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(4.0f)
        [
            UE::MediaStreamEditor::FMediaStreamWidgets::CreateTextureDetailsWidget(MediaStream)
        ]
    ];
}
```

## 模块依赖

本插件声明了以下插件级依赖：

| 插件 | 用途 |
|---|---|
| `LevelSequenceEditor` | Sequencer 时间轴集成，支持 MediaStream 轨道 |
| `MediaCompositing` | 媒体合成功能，支持媒体在场景中的渲染合成 |
| `MediaPlayerEditor` | 媒体播放器编辑器，提供基础媒体编辑能力 |

模块级依赖（从代码结构推断，Build.cs 未完整提供）：

| 模块 | 用途 |
|---|---|
| `Sequencer` | IObjectSchema 接口、Sequencer 扩展支持 |
| `MediaAssets` | UMediaPlayer、UMediaTexture、UMediaSource 等媒体资产 |
| `MediaFrameworkUtils` | 媒体框架工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `6ba34f64` | [MediaStream] Revert Sample Queue approach; bind MediaTexture directly to player before opening | 回退采样队列方案，改为在打开前直接绑定 MediaTexture 到播放器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-12 | `4fc7c47c` | [MediaViewer] Fix drop-target image identification | 修复 MediaViewer 拖放目标图片识别问题 |
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us... | 新增缓存设置覆盖（类似 MediaPlate），支持使用本地缓存 |
| 2026-05-12 | `aa0f454d` | [MediaViewer] Implementing a Tile visibility provider for media viewer that support zooming, panning | 实现 MediaViewer 的 Tile 可见性提供器，支持缩放和平移 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025-01-10，至今约 1 年，属于较新的实验性插件
- **更新频率**：近期（2026 年 5 月）有密集的功能性更新，包括架构调整（回退采样队列方案）、新功能（缓存覆盖、Tile 可见性）和 bug 修复
- **开发状态**：作为实验性插件，仍在积极迭代中。代码中可见 Jira 关联（UE-213178），表明有 Epic 内部项目驱动
- **已知限制**：`IsExperimentalVersion=true`，API 可能在未来版本中发生破坏性变更；`EnabledByDefault=false` 需手动启用
- **推荐程度**：如果你的项目需要高级媒体管理功能，可以尝试使用，但需关注后续版本的 API 变更。不建议在生产环境的关键路径中依赖此插件的 API

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream)
- 测试用例：未发现独立测试文件（插件内无 Tests 目录）