# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools.
Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 是一套完整的 **Tiled Mipmap Video (TMV)** 播放与转码框架。TMV 是一种基于分块 Mipmap 结构的视频格式，底层使用 Epic 自研的 **Advanced Professional Video (APV)** 编解码器。

该插件解决的核心问题是：**如何在 UE5 中高效播放超高分辨率视频**。传统视频格式在播放 4K/8K 等高分辨率内容时面临带宽和解码瓶颈，TMV 通过将视频分割为 tile 并生成 mipmap 层级，使得播放器可以根据视口大小和距离动态加载不同精度的 tile，实现类似纹理流送的按需加载策略。

插件包含以下子模块：
- **ApvMedia** — APV 编解码器的媒体层封装，依赖 `UEOpenAPV` 库
- **TmvMedia** — TMV 格式的核心运行时播放逻辑
- **TmvMediaEditor** — 编辑器转码工具 UI（转码面板、作业管理、属性自定义）
- **TmvMediaMp4Utils** — MP4 容器解析/写入工具
- **TmvMediaShaders** — TMV 播放所需的 GPU 着色器

## 使用场景

- 你需要在虚拟制片（Virtual Production）场景中播放超高分辨率（8K+）视频背景板 → 用 TmvMedia 转码为 TMV 格式后流式播放
- 你需要将现有视频素材转换为支持 tile 级别 mipmap 的格式，以实现按需加载 → 用 TmvMediaEditor 的转码工具
- 你需要在运行时根据摄像机距离动态调整视频播放精度 → TMV 的 mipmap 层级机制天然支持此场景
- 你需要集成 APV 编解码器到自定义媒体管线 → 用 ApvMedia 模块

## 蓝图用法

TmvMediaEditor 模块主要是编辑器工具，不直接暴露蓝图 API。运行时蓝图接口位于 TmvMedia 和 ApvMedia 模块中（不在本文档范围内）。

本模块提供的编辑器功能通过 **转码面板（Transcoder Panel）** 操作，无需蓝图节点。

## C++ 用法

TmvMediaEditor 模块主要提供编辑器 UI 组件和属性自定义，以下是从源码中提取的关键扩展点。

### 头文件引入

```cpp
#include "TmvMediaEditorLog.h"
#include "Widgets/TmvMediaTranscodeListHandle.h"
#include "Widgets/TmvMediaTranscodeNotification.h"
#include "Widgets/TmvMediaTranscodeTaskMakeMediaSource.h"
```

### 属性自定义注册

TmvMediaEditor 注册了三个属性类型自定义，用于转码器的细节面板：

```cpp
// 文件路径选择器 - 用于选择源视频文件
// FTmvMediaFilePathCustomization : IPropertyTypeCustomization

// 目录路径选择器 - 用于选择输出目录
// FTmvMediaDirectoryPathCustomization : IPropertyTypeCustomization

// Muxer 设置选择器 - 用下拉框展示已注册的 ITmvMediaMuxerFactory
// FTmvMediaMuxerSettingsCustomization : IPropertyTypeCustomization
```

### 转码列表句柄（Controller 层）

`FTmvMediaTranscodeListHandle` 是转码列表编辑器的核心控制器，采用间接引用模式管理 `UTmvMediaTranscodeList`：

```cpp
#include "Widgets/TmvMediaTranscodeListHandle.h"

// 创建句柄并绑定转码列表
TSharedPtr<FTmvMediaTranscodeListHandle> ListHandle = MakeShared<FTmvMediaTranscodeListHandle>();

// 设置转码列表（会广播 OnListChanged 事件）
ListHandle->SetTranscodeList(MyTranscodeList);

// 监听列表变更
ListHandle->GetOnTranscodeListChanged().AddLambda(
    [](UTmvMediaTranscodeList* PreviousList, UTmvMediaTranscodeList* NewList)
    {
        // 处理列表切换
    }
);

// 监听选择变更
ListHandle->GetOnSelectionChanged().AddLambda(
    [](const UTmvMediaTranscodeList* InList, TConstArrayView<int32> SelectedItems)
    {
        // 处理选择变化
    }
);

// 获取当前选择
TArray<int32> Selection = ListHandle->GetCurrentSelection();
```

### 转码通知系统

使用 `FTmvMediaTranscodeNotification` 在转码过程中显示编辑器通知：

```cpp
#include "Widgets/TmvMediaTranscodeNotification.h"

// 创建通知（自动在 Slate 通知管理器中注册）
TSharedPtr<FTmvMediaTranscodeNotification> Notification = MakeShared<FTmvMediaTranscodeNotification>();

// 更新通知文本
Notification->SetText(FText::FromString(TEXT("正在转码: video_001.tmv")));

// 转码成功完成
Notification->Close(/*bInSuccess*/ true);

// 转码失败
Notification->Close(/*bInSuccess*/ false);
```

### 转码完成后创建 MediaSource

```cpp
#include "Widgets/TmvMediaTranscodeTaskMakeMediaSource.h"

// 为转码作业添加完成后自动创建/更新 MediaSource 的任务
UE::TmvMediaEditor::TranscodeTask::AddMakeOrUpdateMediaSourceTask(MyTranscodeJob);
```

## Demo 示例

以下展示如何在自定义编辑器工具中集成转码列表句柄：

```cpp
// MyTranscodeTool.h
#pragma once

#include "Widgets/TmvMediaTranscodeListHandle.h"
#include "Widgets/TmvMediaTranscodeNotification.h"

class UMyTranscodeTool
{
public:
    void Initialize();
    void StartTranscode(UTmvMediaTranscodeJob* InJob);

private:
    TSharedPtr<FTmvMediaTranscodeListHandle> ListHandle;
    TSharedPtr<FTmvMediaTranscodeNotification> ActiveNotification;
};
```

```cpp
// MyTranscodeTool.cpp
#include "MyTranscodeTool.h"
#include "Transcoder/TmvMediaTranscodeList.h"
#include "Transcoder/TmvMediaTranscodeJob.h"
#include "Widgets/TmvMediaTranscodeTaskMakeMediaSource.h"

void UMyTranscodeTool::Initialize()
{
    ListHandle = MakeShared<FTmvMediaTranscodeListHandle>();

    // 监听列表变更以更新 UI
    ListHandle->GetOnTranscodeListChanged().AddLambda(
        [this](UTmvMediaTranscodeList* Prev, UTmvMediaTranscodeList* Next)
        {
            UE_LOG(LogTmvMediaEditor, Log, TEXT("Transcode list changed: %s"),
                Next ? *Next->GetName() : TEXT("None"));
        }
    );
}

void UMyTranscodeTool::StartTranscode(UTmvMediaTranscodeJob* InJob)
{
    // 创建进度通知
    ActiveNotification = MakeShared<FTmvMediaTranscodeNotification>();
    ActiveNotification->SetText(FText::FromString(TEXT("Transcoding...")));

    // 添加完成后创建 MediaSource 的任务
    UE::TmvMediaEditor::TranscodeTask::AddMakeOrUpdateMediaSourceTask(InJob);

    // ... 启动转码作业 ...

    // 完成后关闭通知
    // ActiveNotification->Close(/*bInSuccess*/ true);
}
```

## 模块依赖

TmvMediaEditor 模块的 Build.cs 依赖信息未完整提供，但根据源码分析：

| 模块 | 用途 |
|---|---|
| `TmvMedia` | TMV 核心运行时（转码列表、作业对象等） |
| `ApvMedia` | APV 编解码器媒体层 |
| `UEOpenAPV` | APV 编解码器底层库（通过 ApvMedia 间接依赖） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

由于该插件创建时间为 2026-04-18，属于全新插件，暂无 git 历史记录可供分析。

### 维护评价

- **创建时间**：2026-04-18，全新插件
- **实验性**：`EnabledByDefault=false`，需要手动启用
- **模块类型异常**：TmvMediaEditor 标记为 Runtime 类型，但代码内容完全是编辑器功能（属性自定义、Slate Widget、编辑器命令），这可能是有意为之（允许在 Development 构建中使用）或配置疏忽
- **代码成熟度**：代码结构完整，包含完整的 MVC 架构（Handle/Controller 模式）、通知系统、命令绑定，表明经过充分设计
- **推荐使用**：作为实验性新插件，适合在虚拟制片等需要高分辨率视频播放的场景中试用，但不建议在生产环境中依赖

⚠️ 该插件标记为实验性且默认禁用，API 可能在后续版本中发生重大变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia)
- [官方文档]()（暂无）