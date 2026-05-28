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

Sequence Validator 是一个集成在 Sequencer 编辑器中的静态分析工具，用于在资产打包或发布前自动检测关卡序列（Level Sequence）中常见的、可能导致问题的错误。它通过运行一系列可扩展的验证规则来实现这一目标，帮助动画师、关卡设计师和技术美术等人员提升序列资产的质量。

它解决的核心问题是：序列资产中的错误（如关键帧重复、节范围非整数帧、资产引用丢失等）往往在运行时才会暴露，排查困难。该工具将问题前置，在编辑器阶段就提供清晰的警告和错误报告。

## 使用场景

- 你在制作过场动画序列，并希望确保所有动画节（Section）的起止时间都对齐在整帧上，以避免渲染或同步问题。
- 你的序列包含许多绑定（Bindings）和外部资产引用（如材质、音效），需要快速检查是否有任何绑定丢失或资产无效。
- 你正在管理一个包含大量子序列（Sub-sequences）的复杂项目，需要验证不同层级的序列节是否正确对齐。
- 你是一个团队的技术负责人，希望为项目制定序列资产的规范，并通过自定义规则来确保规范被遵守。

## 蓝图用法

该插件主要通过编辑器 UI（Sequencer 面板）进行操作，不暴露通用的蓝图节点。其核心功能通过 C++ API 调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 无 | 无 |

### 使用示例（蓝图描述）

此插件无面向蓝图的公共节点。主要功能通过 Sequencer 编辑器内的专用面板进行操作。

## C++ 用法

核心 C++ API 用于注册自定义验证规则、以及以编程方式触发验证。

### 头文件引入

```cpp
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"
```

### 基本用法

1. **注册自定义验证规则**
   来自测试用例 `SequenceValidatorTest.cpp` 和 `ISequenceValidatorModule.h`。
   ```cpp
   // 获取验证器模块接口
   ISequenceValidatorModule& ValidatorModule = FModuleManager::LoadModuleChecked<ISequenceValidatorModule>("SequenceValidator");

   // 定义验证规则工厂
   FSequenceValidationRuleInfo RuleInfo;
   RuleInfo.RuleName = LOCTEXT("MyRuleName", "My Custom Rule");
   RuleInfo.RuleDescription = LOCTEXT("MyRuleDesc", "Checks for something specific.");
   RuleInfo.RuleFactory = FOnCreateSequenceValidationRule::CreateLambda([]() -> TSharedRef<FSequenceValidationRule>
   {
       return MakeShared<FMyCustomValidationRule>();
   });

   // 注册规则
   FSequenceValidationRuleID RuleID = ValidatorModule.RegisterValidationRule(MoveTemp(RuleInfo));
   ```

2. **运行同步验证**
   来自测试用例 `SequenceValidatorTest.cpp` 和 `SequenceValidator.h`。
   ```cpp
   // 创建一个验证器实例
   UE::Sequencer::FSequenceValidator Validator;

   // 将序列添加到验证队列
   Validator.Queue(MyLevelSequence);

   // 同步执行验证
   Validator.Validate(MyLevelSequence);

   // 获取结果
   const UE::Sequencer::FSequenceValidationResults& Results = Validator.GetResults();
   for (const auto& ResultPtr : Results.GetResults())
   {
       if (ResultPtr.IsValid())
       {
           UE_LOG(LogTemp, Warning, TEXT("Validation Result: %s - %s"),
               *ResultPtr->GetUserMessage().ToString(),
               *UEnum::GetValueAsString(ResultPtr->GetSeverity()));
       }
   }
   ```

### 进阶用法

1. **使用内置的验证规则**
   该插件内置了多个规则，可直接用于测试或参考。
   ```cpp
   #include "Validation/Rules/SequenceValidationRule_DuplicateKeys.h"
   #include "Validation/Rules/SequenceValidationRule_WholeSectionRanges.h"

   // 手动创建并使用某个内置规则
   auto DuplicateKeysRule = MakeShared<UE::Sequencer::FSequenceValidationRule_DuplicateKeys>();
   UE::Sequencer::FSequenceValidationResults LocalResults;
   DuplicateKeysRule->Run(MyLevelSequence, LocalResults);
   ```

2. **异步验证与完成回调**
   来自 `SequenceValidator.h` 的 API 设计。
   ```cpp
   UE::Sequencer::FSequenceValidator Validator;
   Validator.Queue(MyLevelSequence1);
   Validator.Queue(MyLevelSequence2);

   // 绑定验证完成后的回调
   Validator.GetOnValidationFinished().AddLambda([&Validator]()
   {
       // 验证完成，安全地获取结果
       const auto& Results = Validator.GetResults();
       // ... 处理结果 ...
   });

   // 开始异步验证
   Validator.StartValidation();

   // 检查是否仍在验证中
   if (Validator.IsValidating())
   {
       // ... 可以做其他事情 ...
   }
   ```

## Demo 示例

一个完整的、可编译的最小示例，展示如何定义并注册一个自定义验证规则。

**MyCustomRule.h**
```cpp
#pragma once

#include "Validation/SequenceValidationRule.h"

namespace UE::Sequencer
{

class FMyCustomValidationRule : public FSequenceValidationRule
{
public:
    static FSequenceValidationRuleInfo MakeRuleInfo();

protected:
    virtual void OnRun(const UMovieSceneSequence* InSequence, FSequenceValidationResults& OutResults) const override;
};

}
```

**MyCustomRule.cpp**
```cpp
#include "MyCustomRule.h"

#define LOCTEXT_NAMESPACE "MyCustomValidationRule"

namespace UE::Sequencer
{

FSequenceValidationRuleInfo FMyCustomValidationRule::MakeRuleInfo()
{
    FSequenceValidationRuleInfo Info;
    Info.RuleName = LOCTEXT("RuleName", "My Custom Rule");
    Info.RuleDescription = LOCTEXT("RuleDesc", "Checks for a custom condition.");
    Info.RuleFactory = FOnCreateSequenceValidationRule::CreateStatic([]() -> TSharedRef<FSequenceValidationRule>
    {
        return MakeShared<FMyCustomValidationRule>();
    });
    Info.RuleColor = FLinearColor(1.0f, 0.5f, 0.0f); // 橙色
    return Info;
}

void FMyCustomValidationRule::OnRun(const UMovieSceneSequence* InSequence, FSequenceValidationResults& OutResults) const
{
    // 在此处实现你的验证逻辑
    // 例如：遍历序列中的所有节，检查某个条件
    if (SomeConditionIsTrue)
    {
        // 创建一个警告结果
        auto WarningResult = MakeShared<FSequenceValidationResult>(
            EMessageSeverity::Warning,
            InSequence, // 关联的对象
            LOCTEXT("WarningMsg", "Found a custom issue in the sequence!"),
            GetRuleInfo()
        );
        // 可选：设置时间点和子节路径
        // WarningResult->SetLocalTime(FFrameTime(100));
        // WarningResult->SetSubSectionTrail(...);
        OutResults.AddResult(WarningResult);
    }
}

} // namespace UE::Sequencer

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心的序列和轨道数据结构 |
| `SequencerCore` | Sequencer 编辑器的核心功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，适配引擎日志系统更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作，重新提交代码。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL 51314860 的改动，可能因其引入问题。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复因委托接口变更导致的引擎初始化后注册失败的问题。 |
| 2025-12-08 | `34716c37` | PR #14125: SequenceValidator: Fix WholeSectionRanges rule reporting incorrect results | 修复了“整帧范围”验证规则错误报告结果的问题。 |

### 维护评价

**SequenceValidator** 是一个相对较新的插件（创建于 2025 年 7 月），目前仍处于实验阶段（`IsExperimentalVersion=true`）。从提交历史看，近半年内的更新主要集中在**引擎兼容性适配**（如日志宏迁移、委托接口变更）和**已有规则的 Bug 修复**，尚未看到大量新功能的添加。

插件的架构清晰（规则注册、验证器、结果容器），并内置了四个实用的验证规则。作为编辑器工具，其价值在于提升序列资产质量，但实验性标签意味着其 API 和功能未来可能会发生变化。

**结论**：**维护中，但谨慎使用**。适合希望在项目中提前引入序列质量控制的技术团队，建议关注后续版本的稳定性和 API 变化。目前没有发现超过一年的更新停滞。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator)
- 官方文档：无