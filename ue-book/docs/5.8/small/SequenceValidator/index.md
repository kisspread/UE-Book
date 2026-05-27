# Sequence Validator

> A tool that provides validation rules for detecting common errors in sequences（照抄，不翻译）

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

Sequence Validator 是一个编辑器工具，旨在自动化检测 Unreal Engine 中 Sequencer 序列（如关卡序列、电影序列）中的常见错误。它通过运行一系列可扩展的验证规则，帮助动画师和电影制作人在打包或提交资产前发现潜在问题，从而提升序列内容的质量和一致性。

该插件解决的问题是：手动检查复杂的、嵌套的 Sequencer 序列以发现对齐错误、关键帧问题、缺失引用等是非常耗时且容易出错的。此工具将这些检查自动化，提供结构化的结果（包括错误、警告和信息），并定位到序列中的具体位置。

## 使用场景

- 你正在为游戏或过场动画创建复杂的关卡序列，并希望在编辑器内快速验证其内容是否符合团队规范。
- 你的序列包含多个子序列（Sub-Sections），需要确保所有部分的起止时间对齐且没有重叠。
- 在提交序列资产到版本控制或打包构建之前，进行自动化的质量检查。
- 你希望自定义验证规则来检测项目特有的序列问题。

## 蓝图用法

该插件主要为编辑器扩展和C++代码提供服务，未发现直接暴露给蓝图的 `BlueprintCallable` 函数。其核心功能通过编辑器UI（一个专门的面板）和模块接口（`ISequenceValidatorModule`）访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 该插件的API主要为C++编辑器模块设计 | - |

### 使用示例（蓝图描述）

在蓝图中，主要通过编辑器子系统或直接调用C++函数（通过插件或项目模块）来交互。典型的流程是：
1.  获取 `ISequenceValidatorModule` 模块实例。
2.  创建 `FSequenceValidator` 对象。
3.  使用 `Queue` 函数将目标 `UMovieSceneSequence` 资产加入验证队列。
4.  调用 `StartValidation` 开始异步验证。
5.  监听 `GetOnValidationFinished` 事件，验证完成后从 `GetResults` 获取 `FSequenceValidationResults` 进行处理。
6.  使用 `SSequenceValidator` 等Slate控件在编辑器中展示结果。

## C++ 用法

### 头文件引入

```cpp
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"
```

### 基本用法

以下示例展示了如何注册一个自定义验证规则并运行一次同步验证。

```cpp
// 引入序列验证器模块
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"

// 假设你在一个编辑器模块中
void RegisterCustomRuleAndValidate()
{
    // 1. 获取序列验证器模块
    UE::Sequencer::ISequenceValidatorModule& ValidatorModule = FModuleManager::Get().LoadModuleChecked<UE::Sequencer::ISequenceValidatorModule>(TEXT("SequenceValidator"));
    
    // 2. 创建一个自定义的验证规则信息
    UE::Sequencer::FSequenceValidationRuleInfo MyRuleInfo;
    MyRuleInfo.RuleName = FText::FromString(TEXT("My Custom Rule"));
    MyRuleInfo.RuleDescription = FText::FromString(TEXT("Checks for something custom."));
    MyRuleInfo.RuleFactory = []() -> TSharedRef<UE::Sequencer::FSequenceValidationRule>
    {
        // 返回你的自定义规则实例
        return MakeShared<FMyCustomValidationRule>();
    };
    
    // 3. 注册该规则
    UE::Sequencer::FSequenceValidationRuleID MyRuleID = ValidatorModule.RegisterValidationRule(MoveTemp(MyRuleInfo));
    
    // 4. 创建一个验证器实例（它会自动收集当前所有已注册的规则）
    UE::Sequencer::FSequenceValidator Validator;
    
    // 5. 将要验证的序列加入队列
    UMovieSceneSequence* SequenceToValidate = /* 获取你的序列资产 */;
    Validator.Queue(SequenceToValidate);
    
    // 6. 运行同步验证
    Validator.Validate(SequenceToValidate); // 或者调用 Validate(Queue)
    
    // 7. 获取结果
    const UE::Sequencer::FSequenceValidationResults& Results = Validator.GetResults();
    for (const TSharedPtr<UE::Sequencer::FSequenceValidationResult>& Result : Results.GetResults())
    {
        UE_LOG(LogTemp, Warning, TEXT("[%s] %s: %s"),
            *Result->GetSeverityString(),
            *Result->GetRuleInfo().RuleName.ToString(),
            *Result->GetUserMessage().ToString());
    }
    
    // 8. （可选）用完后注销规则
    ValidatorModule.UnregisterValidationRule(MyRuleID);
}
```

### 进阶用法

使用 `FSequenceValidator` 的异步验证功能，并利用 `FSequenceValidationResult` 的详细定位能力。

```cpp
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationResult.h"
#include "MovieSceneSubSection.h"

void AsyncValidationExample()
{
    UE::Sequencer::FSequenceValidator Validator;
    
    // 绑定验证完成事件
    Validator.GetOnValidationFinished().AddLambda([&Validator]()
    {
        UE_LOG(LogTemp, Log, TEXT("Async validation finished!"));
        
        // 处理结果
        const auto& Results = Validator.GetResults().GetResults();
        for (const auto& ResultPtr : Results)
        {
            const UE::Sequencer::FSequenceValidationResult& Result = *ResultPtr;
            
            // 检查是否有子序列路径信息
            TArray<UMovieSceneSubSection*> SubSectionTrail;
            if (Result.GetSubSectionTrail(SubSectionTrail))
            {
                UE_LOG(LogTemp, Log, TEXT("  Located in sub-section trail: %d sections deep."), SubSectionTrail.Num());
            }
            
            // 检查是否有定位到特定关键帧
            if (Result.HasLocalTime())
            {
                FFrameTime Time = Result.GetLocalTime();
                UE_LOG(LogTemp, Log, TEXT("  Occurs at frame time: %d"), Time.GetFrame().Value);
            }
            
            // 获取关联的目标对象（如 UMovieSceneSection）
            if (UObject* Target = Result.GetTarget())
            {
                UE_LOG(LogTemp, Log, TEXT("  Target object: %s"), *Target->GetName());
            }
        }
    });
    
    // 添加序列到队列
    Validator.Queue(MySequence1);
    Validator.Queue(MySequence2);
    
    // 开始异步验证
    Validator.StartValidation();
    
    // 在 Tick 中可以检查 Validator.IsValidating() 状态
}
```

## Demo 示例

一个最小的编辑器工具面板，用于验证当前打开的关卡序列。

**SequenceValidatorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "SequenceValidatorTool.generated.h"

class UMovieSceneSequence;

UCLASS()
class USequenceValidatorTool : public UEditorUtilityWidget
{
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable, Category = "Sequence Validator")
    void ValidateCurrentLevelSequence();
    
    UFUNCTION(BlueprintCallable, Category = "Sequence Validator")
    void ClearResults();
    
private:
    TSharedPtr<UE::Sequencer::FSequenceValidator> Validator;
};
```

**SequenceValidatorTool.cpp**
```cpp
#include "SequenceValidatorTool.h"
#include "ISequenceValidatorModule.h"
#include "LevelSequence.h"
#include "LevelSequenceEditorBlueprintLibrary.h"
#include "Widgets/Notifications/SNotificationList.h"

void USequenceValidatorTool::ValidateCurrentLevelSequence()
{
    // 确保模块已加载
    if (!FModuleManager::Get().IsModuleLoaded("SequenceValidator"))
    {
        FModuleManager::Get().LoadModule("SequenceValidator");
    }
    
    UE::Sequencer::ISequenceValidatorModule& ValidatorModule = FModuleManager::Get().GetModuleChecked<UE::Sequencer::ISequenceValidatorModule>(TEXT("SequenceValidator"));
    
    // 创建或复用验证器
    if (!Validator.IsValid())
    {
        Validator = MakeShared<UE::Sequencer::FSequenceValidator>();
    }
    
    // 清除旧队列和结果
    Validator->ClearQueue();
    Validator->GetResults().Reset();
    
    // 获取当前在Sequencer中打开的关卡序列
    ULevelSequence* CurrentLS = ULevelSequenceEditorBlueprintLibrary::GetCurrentLevelSequence();
    if (!CurrentLS)
    {
        UE_LOG(LogTemp, Warning, TEXT("No level sequence currently open in Sequencer."));
        return;
    }
    
    // 加入验证队列并运行
    Validator->Queue(CurrentLS);
    Validator->Validate(CurrentLS);
    
    // 显示一个简单通知
    const int32 ErrorCount = /* 从 Results 中统计 Error 和 Warning 的数量 */;
    FText NotificationText = FText::Format(
        NSLOCTEXT("SequenceValidator", "ValidationDone", "Validation finished. Found {0} issues."),
        FText::AsNumber(ErrorCount));
    
    FNotificationInfo Info(NotificationText);
    Info.ExpireDuration = 5.0f;
    FSlateNotificationManager::Get().AddNotification(Info);
}

void USequenceValidatorTool::ClearResults()
{
    if (Validator.IsValid())
    {
        Validator->GetResults().Reset();
    }
}
```

## 模块依赖

从 `Build.cs` 文件分析，该插件有以下特定依赖：

| 模块 | 用途 |
|---|---|
| `MovieScene` | 核心序列框架，提供 `UMovieSceneSequence`, `UMovieSceneSection` 等基础类型 |
| `LevelSequenceEditor` | 提供在编辑器中操作关卡序列的蓝图库和上下文，用于获取当前打开的序列 |
| `Slate`, `SlateCore` | 用于构建验证器UI控件（SSequenceValidator, SSequenceValidatorResults等） |
| `EditorStyle` | 用于UI控件的样式和主题 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移至UE_LOGF格式，统一日志记录。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换后进行的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了变更列表51314860的修改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing registration | 修复因委托访问方式变更导致的初始化缺失问题。 |
| 2025-12-08 | `34716c37` | PR #14125: SequenceValidator: Fix WholeSectionRanges rule reporting incorrect results | 修复了“完整章节范围”规则报告错误结果的问题。 |

### 维护评价

**活跃维护**。插件创建于约一年前（2025年7月），且自创建以来一直有持续的更新。最近的提交（2026年4月）是UE5内部大规模API调整（UE_LOG到UE_LOGF迁移）的一部分，表明该插件仍在主开发分支中被维护和兼容。历史上还有针对性的bug修复（如`WholeSectionRanges`规则修复）。

该插件仍标记为 **实验性 (IsExperimentalVersion=true)**，这意味着其API和功能在未来版本中可能会发生变化。尽管如此，从提交历史看，它正随着引擎的其他部分一起被积极维护。对于希望提升序列内容质量的团队，它是一个推荐使用的工具，但需注意其“实验性”状态可能带来的未来兼容性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator)