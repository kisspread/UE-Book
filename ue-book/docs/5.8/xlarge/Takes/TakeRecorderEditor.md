# Take Recorder

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 中文名 | 录制管理器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderEditor` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime), `TakesCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-11 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

Take Recorder 是 UE5 虚拟制片流程中的核心录制工具。它解决的问题是：**在虚拟制片环境中，如何将演员表演、摄像机运动、动画数据、音频等实时捕获并关联到时间码，以 Sequencer Level Sequence 的格式存储，供后期回放和审查**。

该插件不仅仅是简单的"录制功能"，而是一套完整的录制-审查-回放工作流套件，包含：

- **多来源录制**：支持同时从多种数据源（Actor 变换、动画、音频、Live Link 等）捕获数据
- **时间码管理与卡顿保护**：录制过程中监控引擎帧率，当引擎卡顿导致时间码跳跃时，通过线性回归估算正确的后续时间码，避免录制数据时间线断裂
- **Take 元数据系统**：管理 Slate 名称、Take 编号、用户描述等影视制作元数据
- **命名令牌集成**：支持命名令牌（Naming Tokens）动态生成录制输出路径
- **Sequencer 卡顿可视化**：录制完成后在 Sequencer 中标记时间码跳跃/重复/追赶区域，方便审查录制完整性
- **预设系统**：可保存和加载录制配置作为 TakePreset 资产

## 使用场景

- 你在做虚拟制片项目，需要录制演员的表演数据（动作捕捉、面部动画等）→ 用 Take Recorder
- 你需要在 Unreal 中录制带有时间码同步的多通道数据（视频、动画、音频）→ 用 Take Recorder
- 你需要录制多个 Take 并对比选择最佳表现 → 用 Take Recorder 的 Take 元数据和预设系统
- 你的引擎录制过程中出现卡顿，担心录制数据不完整 → 用 Take Recorder 的卡顿保护功能
- 你需要将录制输出路径自动化（按场景名、日期等动态生成）→ 用 Take Recorder 的命名令牌功能

## 蓝图用法

Take Recorder Editor 模块主要提供编辑器 UI 和配置，运行时 API 集中在 `TakeRecorder`、`TakesCore` 等其他模块中。本模块侧重于编辑器面板和属性自定义。

### 核心节点

由于 TakeRecorderEditor 是一个 Runtime 模块但主要服务于编辑器，其对外暴露的蓝图 API 较少。核心交互通过 Take Recorder 的编辑器面板完成：

| 功能 | 说明 | 所在类 |
|---|---|---|
| 录制面板 | 设置录制元数据、启动/停止录制的主 UI | `STakeRecorderPanel` |
| 驾驶舱控件 | 管理 Slate、Take 编号、帧率等录制参数 | `STakeRecorderCockpit` |
| 来源管理 | 添加、删除、拖拽排列录制数据源 | `STakeRecorderSources` |
| 预设编辑 | 编辑和保存 TakePreset 资产 | `STakePresetAssetEditor` |

### 使用示例

1. **打开 Take Recorder 面板**：通过菜单栏 `Window > Cinematics > Take Recorder` 打开
2. **配置录制来源**：在 Sources 面板中点击 "+" 添加录制源（如 Actor、动画、音频等）
3. **设置元数据**：在驾驶舱区域填写 Slate 名称（场景号）、Take 编号、描述等
4. **设置帧率**：可手动指定帧率或从 Timecode Provider 同步
5. **启动录制**：点击录制按钮开始捕获
6. **审查录制**：录制完成后 Sequencer 中会显示卡顿标记（红色：时间码跳跃，黄色：追赶区域）

## C++ 用法

### 头文件引入

```cpp
#include "TakeRecorderEditorModule.h"
```

### 基本用法

TakeRecorderEditor 模块通过注册编辑器扩展和自定义实现工作流。以下是关键的模块初始化模式：

```cpp
// TakeRecorderEditorModule.h - 模块生命周期管理
// 来源：Private/TakeRecorderEditorModule.h

class FTakeRecorderEditorModule : public IModuleInterface, public FGCObject
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    // 注册编辑器扩展：菜单、工具栏、面板等
    void RegisterLevelEditorExtensions();
    void UnregisterLevelEditorExtensions() const;
    
    // 注册属性面板自定义
    void RegisterDetailCustomizations();
    void UnregisterDetailCustomizations();
    
    // 录制事件回调
    void OnRecordingInitialized(UTakeRecorder* InRecorder);
    void OnRecordingFinished(UTakeRecorder* InRecorder);
};
```

### 进阶用法：卡顿保护系统

录制过程中的时间码保护是该插件的核心高级功能：

```cpp
// TimecodeRegressionRecordSetup.h - 设置卡顿保护的录制环境
// 来源：Private/Timecode/Regression/TimecodeRegressionRecordSetup.h

#include "Timecode/Regression/TimecodeRegressionRecordSetup.h"

// 设置引擎环境以进行卡顿保护录制
UE::TakeRecorder::FTimecodeRegressionRecordSetup TimecodeSetup;
FTakeRecorderHitchProtectionParameters Params;
// ... 配置参数

auto Result = TimecodeSetup.SetupEngineEnvironmentForRecording(Params);
if (Result.IsSuccess())
{
    UTimecodeRegressionProvider* Estimator = Result.Estimator;
    // Estimator 将通过线性回归估算正确的时间码
    // 即使引擎出现 1 秒卡顿，后续帧仍会获得连续的时间码
}

// 录制完成后清理
TimecodeSetup.CleanupRecording();
```

卡顿分析可以在 Sequencer 中查看：

```cpp
// HitchAnalysis.h - 分析录制后的时间码卡顿
// 来源：Private/Timecode/Visualization/HitchAnalysis.h

#include "Timecode/Visualization/HitchAnalysis.h"

// 分析 Sequencer 中的时间码卡顿
auto AnalysisResult = UE::TakeRecorder::AnalyseHitches(*Sequencer);
if (AnalysisResult.HasValue())
{
    const FTimecodeHitchData& HitchData = AnalysisResult.GetValue();
    
    // 检查时间码跳跃
    for (const auto& SkipMarker : HitchData.SkippedTimecodeMarkers)
    {
        UE_LOG(LogTemp, Warning, TEXT("Frame %d: Timecode skipped from %s to %s"),
            SkipMarker.Frame.Value,
            *SkipMarker.ExpectedFrame.ToString(),
            *SkipMarker.ActualTimecode.ToString());
    }
    
    // 检查追赶区域
    for (const auto& Catchup : HitchData.CatchupTimes)
    {
        UE_LOG(LogTemp, Warning, TEXT("Engine fell behind from frame %d to %d"),
            Catchup.StartTime.Value, Catchup.EndTime.Value);
    }
}
```

### 进阶用法：属性自定义系统

该模块为录制设置提供了丰富的属性自定义：

```cpp
// TakeRecorderNamingTokenCustomizationUtilities.h - 命名令牌属性自定义
// 来源：Private/Customization/TakeRecorderNamingTokenCustomizationUtilities.h

#include "Customization/TakeRecorderNamingTokenCustomizationUtilities.h"

// 为属性行创建命名令牌文本框
void HandleNamingTokensPropertyRow(IDetailPropertyRow& InPropertyRow)
{
    // 自动为标记了 UseNamingTokens 的属性创建令牌编辑控件
    UE::TakeRecorder::NamingTokens::HandleNamingTokensRow(InPropertyRow);
}
```

## Demo 示例

以下演示如何创建一个最小的录制状态监控扩展：

```cpp
// MyTakeRecorderExtension.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyTakeRecorderExtension : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    FDelegateHandle OnRecordingInitHandle;
    FDelegateHandle OnRecordingFinishHandle;
    
    void HandleRecordingInitialized(UTakeRecorder* InRecorder);
    void HandleRecordingFinished(UTakeRecorder* InRecorder);
};
```

```cpp
// MyTakeRecorderExtension.cpp
#include "MyTakeRecorderExtension.h"

void FMyTakeRecorderExtension::StartupModule()
{
    // 注册录制事件监听
    // UTakeRecorderSubsystem 提供录制生命周期事件
    UE_LOG(LogTemp, Log, TEXT("Take Recorder Extension loaded"));
}

void FMyTakeRecorderExtension::ShutdownModule()
{
    // 清理事件绑定
}

void FMyTakeRecorderExtension::HandleRecordingInitialized(UTakeRecorder* InRecorder)
{
    UE_LOG(LogTemp, Log, TEXT("Recording started"));
    // 可在此处初始化自定义录制逻辑
}

void FMyTakeRecorderExtension::HandleRecordingFinished(UTakeRecorder* InRecorder)
{
    UE_LOG(LogTemp, Log, TEXT("Recording finished"));
    // 可在此处执行录制后处理
}

IMPLEMENT_MODULE(FMyTakeRecorderExtension, MyTakeRecorderExtension)
```

## 模块依赖

从模块结构和头文件引用推断：

| 模块 | 用途 |
|---|---|
| `TakesCore` | 核心录制数据结构和接口 |
| `TakeRecorder` | 录制器运行时核心 |
| `TakeRecorderSources` | 录制数据源管理 |
| `TakeMovieScene` | 录制数据的 MovieScene 集成 |
| `TakeSequencer` | Sequencer 扩展 |
| `NamingTokens` | 命名令牌系统集成 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `AudioMixer` | 音频设备和输入管理 |
| `AudioInputDevice` | 音频输入设备枚举 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee6722f8` | Take Recorder: Correcting regression where the Attach Track Recorder does not correctly record attac | 修复 Attach Track Recorder 未正确录制附加数据的回归问题 |
| 2026-05-14 | `d17111f0` | Take Recorder: Protecting against crashing on a null sub section sequence. | 防止子序列为空时导致崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `0c5ab24a` | Take Recorder: Adding missing WITH_EDITOR guard on log. | 补充日志代码缺失的 WITH_EDITOR 预编译守卫 |
| 2026-05-13 | `6aee158b` | Take Recorder: Fixing possible crash where a weak pointer could trigger an assertion due to a CastCh | 修复弱指针因 Cast 检查触发断言的潜在崩溃 |

### 维护评价

- **活跃维护** ✅：最近 1 个月内有实质性 bug 修复和稳定性改进
- **创建于 2019 年**，作为虚拟制片工具套件已运行约 7 年，代码成熟稳定
- **9 个模块的大型架构**，包含完整的录制-审查-回放工作流
- **卡顿保护系统**是相对较新的高级功能，说明仍在积极开发新特性
- 近期更新集中在**稳定性修复**（崩溃防护、回归修复），表明该插件处于成熟期的维护阶段
- **推荐使用**：作为 UE5 虚拟制片的核心录制工具，该插件经过长期验证，功能完善，且 Epic Games 仍在持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Takes)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/take-recorder-in-unreal-engine/)