# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（工具资产） |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights) | |

## 用途

Audio Insights 插件为 Unreal Engine 提供了一套专门的音频分析、调试和监控工具集。它解决了在复杂项目中缺乏深入音频系统运行状况洞察的问题，允许开发者和音频设计师实时分析音频性能、追踪音频资产使用情况、调试音频播放问题，并监控音频线程和资源消耗，从而优化游戏音频体验和性能。

## 使用场景

- 你需要分析游戏运行时的音频性能瓶颈（如 CPU 占用、内存分配）。
- 你需要调试特定音频事件为何没有播放、播放错误或延迟。
- 你需要监控音频线程的负载，确保其不会成为性能瓶颈。
- 你需要查看哪些音频资产正在被加载和使用，以优化内存。
- 你正在使用 Unreal Insights 工具，并希望集成专门的音频分析通道。

## 模块列表

本插件包含以下模块，详细 API 与用法请参阅对应文档：

| 模块 | 一句话总结 | 文档链接 |
|---|---|---|
| **AudioInsights** | 核心分析引擎与数据收集器，为 Unreal Insights 提供音频分析通道。 | [AudioInsights.md](AudioInsights.md) |
| **AudioInsightsEditor** | 编辑器集成模块，提供用于启动和查看音频分析工具的编辑器界面与菜单。 | [AudioInsightsEditor.md](AudioInsightsEditor.md) |

## 蓝图用法

本插件主要作为编辑器和分析工具使用，其核心功能通过 Unreal Insights 应用程序和编辑器菜单访问，而非直接在游戏运行时蓝图中调用。主要的用户交互发生在编辑器界面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图可调用节点） | 主要功能通过编辑器菜单和 Unreal Insights 界面提供。 | N/A |

### 使用示例（蓝图描述）

1.  在编辑器中，通过菜单 `Tools -> Audio Insights` 或 `Window -> Developer Tools -> Audio Insights` 打开分析工具窗口。
2.  启动游戏会话（PIE 或独立进程），分析工具将自动开始收集数据。
3.  在 Unreal Insights 应用程序中，连接到你的游戏会话，并导航到 “Audio” 通道查看详细的音频分析数据。

## C++ 用法

本插件的 C++ 接口主要面向需要扩展或集成音频分析功能的开发者。

### 头文件引入

```cpp
#include "AudioInsightsModule.h"
```

### 基本用法

获取音频分析模块的单例并注册自定义的分析提供者（Provider）。

```cpp
// 来自 AudioInsights 模块的公共接口
IAudioInsightsModule& AudioInsightsModule = IAudioInsightsModule::Get();
if (AudioInsightsModule.IsAvailable())
{
    // 注册一个自定义的音频分析数据提供者
    AudioInsightsModule.RegisterAudioAnalysisProvider(MyCustomProvider);
}
```

### 进阶用法

创建自定义的音频分析视图（View），以在 Unreal Insights 中显示特定类型的数据。这通常需要继承自 `FAudioAnalyzer` 或相关基类，并实现数据收集和序列化逻辑。

## Demo 示例

一个最小的示例，展示如何在 C++ 模块中检查 Audio Insights 插件是否可用。

```cpp
// MyGameModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyGameModule.cpp
#include "MyGameModule.h"
#include "AudioInsightsModule.h"

void FMyGameModule::StartupModule()
{
    // 检查 Audio Insights 模块是否已加载并可用
    if (IAudioInsightsModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Audio Insights module is available. Audio profiling tools are ready."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Audio Insights module is not available. Audio profiling features may be limited."));
    }
}

void FMyGameModule::ShutdownModule()
{
    // 清理工作
}

IMPLEMENT_MODULE(FMyGameModule, MyGame)
```

## 模块依赖

要使用本插件的功能，你的项目模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AudioInsights` | 访问核心音频分析数据和接口。 |
| `AudioInsightsEditor` | （仅编辑器模块）集成编辑器菜单和窗口。 |
| `AudioWidgets` | 提供音频分析界面中使用的自定义 UI 控件。 |

## 维护状态

### 近期更新

（注：以下为基于插件创建时间的推断，实际 commit 信息需从仓库获取）
- 2023-12-01 初始提交，创建插件基础结构。
- （后续更新信息需查询 git log）

### 维护评价

- **创建时间**：约 2 年前（2023-12-01）。
- **实验性状态**：插件标记为 `IsBetaVersion: true`，表明其仍处于测试阶段，API 和功能可能发生变化。
- **维护状态**：作为 Epic Games 官方维护的工具插件，预计会随引擎版本更新而维护，但因其 Beta 状态，稳定性可能不如正式版插件。
- **推荐使用**：推荐用于开发和调试阶段，以分析和优化音频性能。不建议在最终发布版本中依赖其非稳定的 API。对于生产环境，应关注其正式发布状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioInsights)
- [官方文档]() （暂无）
- [测试用例]() （暂无）