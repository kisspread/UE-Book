# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个处于实验阶段的引擎级音频创作和播放框架。它旨在提供一套高于 `UAudioComponent` 和 `USoundWave` 层次的高级工具，用于处理复杂的声音设计场景、动态音频混合以及实时音频处理。其目标是简化大型开放世界游戏或对音频交互性要求极高的项目中的音频系统实现。

## 使用场景

- 你需要构建一个具有复杂环境音效（如动态天气、昼夜循环影响声音传播）的开放世界游戏。
- 你的项目需要音乐系统能够根据玩家行为或游戏状态（如紧张、平静）进行实时、平滑的过渡和混合。
- 你需要自定义音效的实时处理逻辑（如动态混响、滤波器、失真），并且希望以数据驱动或可视化的方式进行编辑，而不是纯代码。
- 作为引擎开发者或音频中间件集成者，正在试验下一代音频架构。

## 蓝图用法

> **注意**：此插件为实验性，蓝图 API 可能不完整或发生变化。当前文档基于已公开的模块和源码结构推断。

### 核心节点

> ⚠️ 待补充：由于插件处于早期实验阶段，尚未在公开的插件头文件中找到明确的 `UFUNCTION(BlueprintCallable)` 定义。蓝图功能可能主要集中在编辑器工具（如 SubsonicEditor）和基于资产的工作流中。

## C++ 用法

> ⚠️ 待补充：当前可访问的源码模块 `SubsonicEngineTest` 主要为测试代码。核心的 `SubsonicEngine` 和 `SubsonicCore` 模块的公共 API 尚未完全清晰。以下为基于模块结构的推测性说明。

### 头文件引入

```cpp
#include "SubsonicCore.h" // 核心类型和接口
#include "SubsonicEngine.h" // 引擎集成和主要运行时类
```

### 基本用法

插件的使用可能涉及创建和管理 `Subsonic` 专用的音频资产（如声音场景、音频图），并通过引擎服务进行播放和更新。具体 API 需要查看 `SubsonicEngine` 模块的公共头文件。

### 进阶用法

预计支持自定义音频处理节点、动态参数绑定以及与游戏逻辑（如 Gameplay Ability System）的集成。这些功能需要查看 `SubsonicCore` 模块中定义的接口和 `SubsonicEngine` 中的具体实现。

## Demo 示例

由于插件处于实验初期，公开可用的稳定示例代码较少。建议参考引擎测试套件（`SubsonicEngineTest`）中的用例来了解设计意图和使用方式。

## 模块依赖

从各模块的 `.Build.cs` 文件推断，使用者通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 使用 Subsonic 系统的核心类型、接口和数据资产。 |
| `SubsonicEngine` | 引擎运行时集成，用于播放、混合和处理 Subsonic 音频。 |
| `AudioMixer` | 底层音频混音和硬件抽象层。 |
| `SignalProcessing` | 用于实现音频 DSP 节点和效果器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复错误的合并：回退 Subsonic Subscriber 的改动，采用最小化处理而非弃用。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 弃用修复相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复/静默 PVS 代码分析警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | （内容浏览器相关）新增音频菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |

### 维护评价

- **创建时间**：约 1 年前创建。
- **近期更新频率**：最近一个月内有多次提交，但主要是合并冲突修复、编译警告清理和与其它模块（如 Content Browser）的接口调整，未发现显著的新功能开发。
- **活跃度**：仍在进行维护性更新，但缺乏面向用户的功能性提交。
- **状态**：**实验性**。`.uplugin` 明确标记 `IsExperimentalVersion: true`，且 `EnabledByDefault` 未设置（默认应为 `false`）。
- **建议**：**谨慎使用**。适合用于技术调研、原型开发或引擎音频系统的深入学习。由于缺乏向后兼容性保证，且功能可能不完整，不建议在需要长期稳定维护的正式项目中作为核心依赖。持续关注其 API 变动和成熟度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)