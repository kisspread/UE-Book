# Sequence Validator

> A tool that provides validation rules for detecting common errors in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列验证器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequenceValidator` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator) | |

## 用途

SequenceValidator 是一个面向 **Sequencer (关卡序列)** 的编辑器工具，其核心功能是提供一个可扩展的框架，用于自动检测序列资产中的潜在问题和错误。它解决了在复杂或大型关卡序列中，人工检查难以发现技术性错误（如关键帧对齐、资产绑定、时间范围等问题）的痛点。

插件本身并不直接包含最终用户界面，而是提供了：
1.  一个验证规则的 **注册与管理模块** (`ISequenceValidatorModule`)。
2.  一个能够异步执行验证任务的 **验证引擎** (`FSequenceValidator`)。
3.  一套用于展示验证结果（错误、警告）的 **Slate 控件**。
4.  几个 **内置的验证规则示例**，如检查段落对齐、整帧范围、未绑定资产和重复关键帧。

其设计目标是作为“序列的质量检查（QA）工具”，帮助艺术家和开发者在打包或发布前发现并修复序列中的潜在问题。

## 使用场景

-   你正在制作电影或过场动画，并拥有一个结构复杂、包含大量嵌套子序列的关卡序列。
-   你需要确保所有动画段落（Sections）的开始/结束时间都精确对齐到整帧，以避免播放时的抖动或同步问题。
-   你希望快速找出序列中引用了无效或已删除资产的绑定（Bindings）。
-   你的团队需要一套标准化的检查流程，并希望自定义扩展检查规则以满足项目特定需求。
-   你需要批量验证多个序列资产，以确保它们符合项目的技术规范。

## 蓝图用法

该插件主要为 C++ 模块设计，提供的蓝图接口有限，核心在于通过 C++ 注册自定义验证规则。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterValidationRule` | 向模块注册一个新的验证规则工厂 | `ISequenceValidatorModule` |
| `UnregisterValidationRule` | 反注册一个验证规则 | `ISequenceValidatorModule` |
| `GetValidationRules` | 获取所有已注册的验证规则信息 | `ISequenceValidatorModule` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `Get Sequence Validator Module` 节点获取 `ISequenceValidatorModule` 的实例，然后调用上述方法来管理验证规则。然而，实际的验证执行（`Queue`, `StartValidation`）和结果处理主要在 C++ 中完成，或通过插件内建的编辑器界面触发。

## C++ 用法

### 头文件引入

```cpp
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"
```

### 基本用法

以下是一个简单的同步验证序列的示例。

```cpp
// 假设在某个编辑器工具或自定义编辑器模式中
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "MovieSceneSequence.h"

void ValidateMySequence(UMovieSceneSequence* MySequence)
{
    // 1. 创建一个验证器实例，它会自动加载当前所有已注册的规则
    UE::Sequencer::FSequenceValidator Validator;

    // 2. 将待验证的序列加入队列
    Validator.Queue(MySequence);

    // 3. 同步执行验证（阻塞当前线程）
    Validator.Validate(MySequence);

    // 4. 获取并处理验证结果
    const UE::Sequencer::FSequenceValidationResults& Results = Validator.GetResults();
    for (const TSharedPtr<UE::Sequencer::FSequenceValidationResult>& Result : Results.GetResults())
    {
        // 根据严重等级进行处理
        if (Result->GetSeverity() == EMessageSeverity::Error)
        {
            UE_LOG(LogTemp, Error, TEXT("Validation Error: %s"), *Result->GetUserMessage().ToString());
        }
        else if (Result->GetSeverity() == EMessageSeverity::Warning)
        {
            UE_LOG(LogTemp, Warning, TEXT("Validation Warning: %s"), *Result->GetUserMessage().ToString());
        }
        // 可以获取更多信息，如出错的对象、时间等
        // UObject* Target = Result->GetTarget();
        // FFrameTime Time = Result->GetLocalTime();
    }
}
```

### 进阶用法：注册自定义验证规则

你可以创建自己的验证规则并注册到模块中。

```cpp
// MyCustomValidationRule.h
#pragma once
#include "Validation/SequenceValidationRule.h"

class FMyCustomValidationRule : public UE::Sequencer::FSequenceValidationRule
{
public:
    static UE::Sequencer::FSequenceValidationRuleInfo MakeRuleInfo()
    {
        UE::Sequencer::FSequenceValidationRuleInfo Info;
        Info.RuleName = FText::FromString(TEXT("Custom Project Rule"));
        Info.RuleDescription = FText::FromString(TEXT("Checks for project-specific constraints."));
        Info.RuleFactory = FOnCreateSequenceValidationRule::CreateStatic([]() -> TSharedRef<FSequenceValidationRule>
        {
            return MakeShareable(new FMyCustomValidationRule());
        });
        return Info;
    }

protected:
    virtual void OnRun(const UMovieSceneSequence* InSequence, UE::Sequencer::FSequenceValidationResults& OutResults) const override
    {
        // 在这里实现你的验证逻辑
        // 例如：检查序列名称是否符合命名规范
        FString Name = InSequence->GetName();
        if (!Name.StartsWith(TEXT("SEQ_")))
        {
            auto Result = MakeShared<UE::Sequencer::FSequenceValidationResult>(
                EMessageSeverity::Warning,
                InSequence,
                FText::Format(NSLOCTEXT("MyValidator", "BadName", "Sequence name '{0}' should start with 'SEQ_'."), FText::FromString(Name)),
                *CurrentRuleInfo // 需要保存对当前规则信息的引用
            );
            OutResults.AddResult(Result.ToSharedRef());
        }
    }
};

// 在模块启动时注册规则
void MyEditorModule::StartupModule()
{
    if (ISequenceValidatorModule* ValidatorModule = FModuleManager::GetModulePtr<ISequenceValidatorModule>(TEXT("SequenceValidator")))
    {
        ValidatorModule->RegisterValidationRule(FMyCustomValidationRule::MakeRuleInfo());
    }
}
```

## Demo 示例

一个完整的最小验证示例，演示如何创建验证器、添加序列并同步执行。

```cpp
// SequenceValidatorDemo.h
#pragma once

#include "CoreMinimal.h"

class UMovieSceneSequence;

class FSequenceValidatorDemo
{
public:
    static void RunDemoValidation(UMovieSceneSequence* SequenceToValidate);
};
```

```cpp
// SequenceValidatorDemo.cpp
#include "SequenceValidatorDemo.h"

#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationResult.h"
#include "MovieSceneSequence.h"

void FSequenceValidatorDemo::RunDemoValidation(UMovieSceneSequence* SequenceToValidate)
{
    // 检查插件模块是否加载
    ISequenceValidatorModule* ValidatorModule = FModuleManager::GetModulePtr<ISequenceValidatorModule>(TEXT("SequenceValidator"));
    if (!ValidatorModule || !SequenceToValidate)
    {
        UE_LOG(LogTemp, Error, TEXT("SequenceValidator module not loaded or sequence is null."));
        return;
    }

    // 创建验证器
    UE::Sequencer::FSequenceValidator Validator;

    // 将序列加入验证队列
    Validator.Queue(SequenceToValidate);

    // 执行同步验证
    Validator.Validate(SequenceToValidate);

    // 输出结果
    const UE::Sequencer::FSequenceValidationResults& Results = Validator.GetResults();
    UE_LOG(LogTemp, Log, TEXT("Validation completed for sequence '%s'. Found %d results."),
        *SequenceToValidate->GetName(), Results.GetResults().Num());

    for (const auto& ResultPtr : Results.GetResults())
    {
        const UE::Sequencer::FSequenceValidationResult& Result = *ResultPtr;
        FString SeverityStr;
        switch (Result.GetSeverity())
        {
        case EMessageSeverity::Info:    SeverityStr = TEXT("Info");    break;
        case EMessageSeverity::Warning: SeverityStr = TEXT("Warning"); break;
        case EMessageSeverity::Error:   SeverityStr = TEXT("Error");   break;
        default:                        SeverityStr = TEXT("Unknown"); break;
        }
        UE_LOG(LogTemp, Log, TEXT("  [%s] %s"), *SeverityStr, *Result.GetUserMessage().ToString());
    }
}
```

## 模块依赖

要使用 `SequenceValidator` 插件的功能，你的模块需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 基础的关卡序列编辑器功能，是此插件的主要运行上下文。 |
| `SequencerCore` | Sequencer 的核心数据结构，用于访问 `UMovieSceneSequence` 等对象。 |
| `MovieScene` | Sequencer 的核心模块，包含 `UMovieSceneSubSection` 等关键类。 |

其他如 `Slate`, `UMG` 等 UI 模块被插件内部用于构建界面，但通常不作为用户模块的直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移为新的 UE_LOGF 格式。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了一次错误的查找替换操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 CL51314860 的改动。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist... | 调整引擎初始化委托的注册方式，以解决潜在的初始化顺序问题。 |
| 2025-12-08 | `34716c37` | PR #14125: SequenceValidator: Fix WholeSectionRanges rule reporting incorrect results | 修复了内置规则 `WholeSectionRanges` 报告错误结果的问题。 |

### 维护评价

-   **活跃状态**: 插件处于**实验性**阶段（`IsExperimentalVersion: true`），这意味着其 API 和行为可能在未来版本中发生变化。
-   **近期更新**: 最近的提交集中在**底层框架的维护和修复**上（如日志宏迁移、委托接口调整），以及修复一个内置规则的 bug。更新频率不高，但仍在维护中。
-   **推荐度**: 对于需要序列质量保证的**高级用户或技术美术/程序员**，此插件是一个有价值的工具框架。由于其**实验性**状态，不建议在生产关键路径上完全依赖它，除非你愿意承担未来 API 变更的风险。它非常适合用于开发自定义验证工具或集成到项目的 QA 流程中。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator)
-   [官方文档]() (暂无)
-   [测试用例]() (插件目录内未发现测试文件，可能位于引擎测试套件中)