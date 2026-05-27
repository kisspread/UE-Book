# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 亚音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途
Subsonic 是一个实验性的、高级别的音频创作和播放系统。它旨在为开发者提供更强大、更灵活的音频控制能力，可能用于构建复杂的交互式音乐系统、环境音景或先进的音频事件处理流程。由于其处于实验阶段，API 和功能可能会在未来的版本中发生变化，不保证向后兼容性。

## 使用场景
-   当你需要构建一个动态的、响应游戏状态变化的交互式音乐系统时。
-   当你需要更精细地控制音频波形的生成、处理与混合，而传统 Sound Cue 或 MetaSounds 不足以满足需求时。
-   当你希望为音频设计师提供一套更高层次的创作工具，并与引擎运行时紧密结合时。

## 蓝图用法
*由于 `SubsonicEngineTest` 是一个测试模块，其中的公开蓝图 API 可能非常有限。以下内容基于插件现有公开接口的推测，实际使用需参考更核心的 `SubsonicCore` 和 `SubsonicEngine` 模块。*

### 核心节点
该插件主要用于扩展引擎的音频子系统，其核心 API 可能通过 C++ 服务接口暴露。当前测试模块未发现可直接用于游戏逻辑的 `BlueprintCallable` 节点。

### 使用示例（蓝图描述）
目前，Subsonic 插件更多地被设计为引擎内部的底层音频服务，而非直接提供一系列可在蓝图中连接的可视化节点。它的使用通常涉及在 C++ 中集成其提供的服务接口。

## C++ 用法
用法主要基于插件自身的测试用例和模块构建逻辑。

### 头文件引入
```cpp
#include "SubsonicModule.h" // 根据核心模块名推测
```

### 基本用法
测试用例通常用于验证模块的基础功能。一个典型的测试文件结构如下（基于常见的 UE 自动化测试模式）：
```cpp
// 来源: Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest/Private/SubsonicEngineTest.cpp
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSubsonicBasicTest, "Subsonic.Engine.Basic", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FSubsonicBasicTest::RunTest(const FString& Parameters)
{
    // 这里是测试 Subsonic 基础引擎功能的代码
    // 例如，测试音频节点的创建、处理链的构建等
    // 由于是内部系统，具体 API 调用取决于 SubsonicEngine 模块的实现
    return true;
}
```

### 进阶用法
更复杂的用法可能涉及使用 Subsonic 系统来处理实时音频流。这通常需要将 Subsonic 的处理节点集成到音频混合图中，具体的接口和流程需要查看 `SubsonicCore` 和 `SubsonicEngine` 模块中的公开类，例如继承自某个处理基类，并重写其音频处理函数。

## Demo 示例
由于 Subsonic 是一个底层音频引擎系统，一个最小可编译示例将展示如何创建一个自定义的 Subsonic 处理节点。

**SubsonicCustomNode.h**
```cpp
#pragma once
#include "SubsonicNodeBase.h" // 假设存在一个基础节点类

UCLASS()
class UMySubsonicNode : public USubsonicNodeBase
{
    GENERATED_BODY()
public:
    virtual void ProcessAudio(const FSubsonicAudioBuffer& InBuffer, FSubsonicAudioBuffer& OutBuffer) override;
    // 其他必要的属性和函数...
};
```

**SubsonicCustomNode.cpp**
```cpp
#include "SubsonicCustomNode.h"

void UMySubsonicNode::ProcessAudio(const FSubsonicAudioBuffer& InBuffer, FSubsonicAudioBuffer& OutBuffer)
{
    // 在此处实现自定义的音频处理逻辑
    // 例如，对音频数据进行滤波、增益调整等
    // 最终将处理结果写入 OutBuffer
    OutBuffer = InBuffer; // 简单的直通示例
}
```

## 模块依赖
从 Build.cs 文件的依赖关系可以推断出该插件的核心依赖。对于使用者来说，要集成 Subsonic，你的模块可能需要链接到它的核心库。

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 系统的基础类型定义和核心框架 |
| `SubsonicEngine` | Subsonic 在引擎中的运行时实现和集成 |
| `AudioMixer` | UE 底层音频混音器，Subsonic 可能深度依赖或扩展此模块 |
| `SignalProcessing` | 音频信号处理库，Subsonic 可能用于实现其音频处理算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了一个错误的合并提交，回退了部分破坏性的修改。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静音了一些 PVS（静态代码分析）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 可能是在内容浏览器中为 Subsonic 添加了新的音频资产创建菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到更现代的 UE_LOGF。 |

### 维护评价
-   **年龄**：插件于 2026 年初创建，非常年轻。
-   **更新频率**：最近一个月内有多次更新，包括功能添加、合并冲突解决和代码质量改进，表明处于 **活跃开发** 阶段。
-   **维护状态**：**活跃维护中**。由 Epic Games 团队直接开发。
-   **已知问题/限制**：作为实验性插件，API 不稳定是主要限制。目前主要由 `SubsonicEngineTest` 模块表明其仍在内部测试和验证阶段。
-   **推荐使用**：由于其高度的实验性和 API 的不稳定性，**不建议在需要长期稳定的生产项目中直接使用**。但非常适合进行技术预研、内部工具开发或愿意承担 API 变更风险的先行者探索。

## 相关链接
-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
-   [测试用例 (SubsonicEngineTest)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)