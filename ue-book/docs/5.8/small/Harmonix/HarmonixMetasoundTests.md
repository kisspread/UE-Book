# Harmonix Metasound Tests

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 和声MetaSound测试模块 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests) | |

## 用途

本插件是一个专为 Unreal Engine 5 设计的、基于 MetaSound 的音乐和音频处理功能集，由 Epic Games 的 Harmonix GenTech 团队开发。它旨在扩展 UE 原生音频系统，为开发者提供专业的音乐制作、分析和交互式音频功能，特别是与 MIDI 和 MetaSound 系统的深度集成。

## 使用场景

- 你需要在 MetaSound 节点图中执行复杂的音乐理论运算、节奏同步或 MIDI 处理。
- 你在制作音乐节奏游戏，需要精确的时钟同步和音频事件分析。
- 你需要为游戏创建能够实时响应玩家输入或游戏状态变化的交互式音乐系统。
- 你需要对 MetaSound 生成器或音频输出进行自动化功能测试，确保其行为符合预期。

## 蓝图用法

本模块主要用于测试，但也提供了一些可用于测试的蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Finish` | 标记当前测试动作完成，并决定是否继续下一个动作。 | `UHarmonixFunctionalTestAction` |
| `IsFinished` | 检查当前测试动作是否已完成。 | `UHarmonixFunctionalTestAction` |
| `AddOutputLogger` | 为指定的 MetaSound 生成器输出添加一个音频参数记录器。 | `UHarmonixMetasoundFunctionalTestLibrary` |
| `AddMidiStreamLogger` | 为指定的 MetaSound 生成器输出添加一个 MIDI 流记录器。 | `UHarmonixMetasoundFunctionalTestLibrary` |

### 使用示例（蓝图描述）

在 `AHarmonixMetasoundFunctionalTest` Actor 中，你可以通过 `FunctionalTestActions` 数组配置一系列测试步骤（`UHarmonixFunctionalTestActionSequence`）。例如：
1. 添加一个 `Set Audio Parameter` 动作来触发 MetaSound 中的特定音效。
2. 添加一个 `Record Clock Output` 动作来记录音乐时钟的输出数据。
3. 添加一个 `Wait For Audio Finished` 动作来等待音频播放完毕。
4. 最后添加一个 `Finish Test` 动作来结束测试并报告结果。

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixFunctionalTestAction.h"
#include "HarmonixMetasoundFunctionalTest.h"
```

### 基本用法

创建自定义的测试动作。来源：`Private/HarmonixFunctionalTestAction.h`

```cpp
// 继承 UHarmonixFunctionalTestAction 创建自定义测试步骤
UCLASS(NotBlueprintable, Meta=(DisplayName="My Custom Action"))
class UMyCustomTestAction : public UHarmonixFunctionalTestAction
{
	GENERATED_BODY()

public:
	// 当测试步骤开始时被调用
	virtual void OnStart_Implementation(AFunctionalTest* Test) override
	{
		// 执行一些自定义逻辑，例如播放一个音效
		// ...
		// 逻辑完成后，调用 Finish 来结束此步骤
		Finish(true); // true 表示继续执行下一个步骤
	}
};
```

### 进阶用法

组合使用库函数进行测试结果验证。来源：`Private/HarmonixMetasoundFunctionalTest.h`

```cpp
void AHarmonixMetasoundFunctionalTest::StartTest()
{
	// ... 其他初始化代码 ...

	// 获取 MetaSound 生成器句柄
	GeneratorHandle = UMetasoundGeneratorHandle::Create(/* ... */);

	// 使用测试库函数添加记录器
	if (GeneratorHandle)
	{
		// 记录一个名为“AudioOut”的音频输出
		UHarmonixMetasoundFunctionalTestLibrary::AddOutputLogger(GeneratorHandle, TEXT("AudioOut"), EAudioParameterType::Float);

		// 记录一个名为“MidiOut”的MIDI流
		UHarmonixMetasoundFunctionalTestLibrary::AddMidiStreamLogger(GeneratorHandle, TEXT("MidiOut"));
	}

	// 开始执行预定义的动作序列
	ActionSequence->OnStart(this);
}
```

## Demo 示例

一个简单的、用于记录音频时钟数据的自定义测试动作。

```cpp
// MyTestAction.h
#pragma once

#include "CoreMinimal.h"
#include "HarmonixFunctionalTestAction.h"
#include "MyTestAction.generated.h"

UCLASS(NotBlueprintable, Meta=(DisplayName="Log Clock State"))
class UMyTestActionLogClockState : public UHarmonixFunctionalTestAction
{
	GENERATED_BODY()

public:
	virtual void OnStart_Implementation(AFunctionalTest* Test) override
	{
		UE_LOG(LogTemp, Log, TEXT("Test Action Started: Log Clock State"));
		// 假设这里有一些获取时钟状态的逻辑
		// FMidiSongPos CurrentPos = ...;
		// UE_LOG(LogTemp, Log, TEXT("Current Song Position: Bar %d, Beat %d"), CurrentPos.Bar, CurrentPos.Beat);
	}

	virtual void Tick_Implementation(AFunctionalTest* Test, float DeltaSeconds) override
	{
		TotalTime += DeltaSeconds;
		if (TotalTime >= 2.0f) // 持续2秒后完成
		{
			Finish(true);
		}
	}

private:
	float TotalTime = 0.0f;
};
```

## 模块依赖

从各模块的 Build.cs 分析，以下为独特或关键的依赖（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | Harmonix 核心的数字信号处理模块。 |
| `HarmonixMidi` | Harmonix 的 MIDI 解析与处理模块。 |
| `HarmonixMetasound` | 将 Harmonix 功能集成到 MetaSound 系统中的核心模块。 |
| `AssetRegistry` | 用于资产依赖分析和扫描。 |
| `UnrealEd` | 用于编辑器工具集成和功能测试框架。 |
| `MetasoundFrontend` | MetaSound 的前端框架，用于访问和分析 MetaSound 图表。 |
| `FunctionalTesting` | UE 的功能测试框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复了 Fusion 语音系统中键区排序问题，并增加了空值防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃修复相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下将 double 常量截断为 float 时产生的警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 FusionPatch 代理添加了用户对象，可用于关联活动跟踪。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符与参数位数不匹配的问题（32位/64位）。 |

### 维护评价

- **状态**：**活跃维护**。插件于2024年1月创建，至今年龄约1年。近期（2026年5月）仍有频繁的代码提交，包含功能改进、错误修复和代码质量优化，表明项目处于积极开发和维护中。
- **实验性**：插件被标记为 `IsExperimentalVersion: true`，且默认未启用。这意味着其 API 和功能可能尚未完全稳定，未来版本中可能会有重大变更。使用者需注意版本兼容性风险。
- **推荐度**：对于需要在 UE5 中实现复杂、专业音频和音乐功能（特别是基于 MetaSound 和 MIDI）的项目，此插件是官方提供的强大工具。鉴于其活跃维护状态，可以谨慎地在新项目中进行评估和使用，但需做好应对 API 变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)