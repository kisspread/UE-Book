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

`SequenceValidator` 插件不仅仅是一个简单的错误检测工具，它为 Unreal Engine 的 Sequencer（序列器）构建了一个**可扩展的、异步的资产验证框架**。其核心目的是帮助动画师、技术美术和关卡设计师在大型项目中维护序列资产（如关卡序列、动画序列）的质量和规范性，避免常见的配置错误、资源引用错误或对齐问题，从而在项目后期（如打包或表演录制前）减少潜在的崩溃和视觉错误。

**解决的问题：**
1.  **人工检查繁琐且易错**：手动检查一个复杂序列的每个子段、每个绑定是否有效、关键帧是否重复、段落范围是否对齐整帧等，耗时且容易遗漏。
2.  **缺乏标准化的验证流程**：团队中不同成员可能遵循不同的编辑规范，缺少统一的、可自动化的检查点。
3.  **错误发现太晚**：序列中的问题（如指向无效资产的绑定）可能在游戏运行时才暴露，此时修复成本高。

**工作原理：**
插件提供了一个模块化系统，允许注册自定义的“验证规则”。一个核心的 `FSequenceValidator` 类可以将一个或多个序列加入队列，并异步运行所有已注册的规则。规则的结果（错误、警告、信息）会被收集起来，并在一个专门的编辑器界面（工具窗口）中以树状结构清晰地展示给用户，帮助定位问题。

## 使用场景

- **大型项目多人协作**：当多个艺术家或设计师共同编辑一个主序列及其嵌套的子序列时，使用此工具进行提交前或定期验证，确保序列的结构完整性和一致性。
- **项目里程碑质量检查**：在关键的开发节点（如Alpha、Beta）前，对项目中的核心过场动画序列进行批量验证，确保没有遗漏的绑定、错误的资产引用或不规范的段落设置。
- **自动化CI/CD流程集成**：可以将 `FSequenceValidator` 的同步验证功能集成到构建服务器脚本中，实现序列资产的自动化质量检查，防止引入错误。
- **学习与教学**：用于向新团队成员展示序列编辑的最佳实践，通过预设的验证规则来指导他们避免常见错误。

## 蓝图用法

**注意：** `SequenceValidator` 主要是一个面向 C++ 开发者的编辑器工具扩展框架。它通过 `ISequenceValidatorModule` 接口暴露注册/注销验证规则的功能，但这些操作通常在 C++ 模块启动时完成，而非在运行时蓝图中动态调用。其 UI 控件 (`SSequenceValidator` 等) 是 Slate 控件，不可直接在 UMG 蓝图中使用。

该插件**没有**提供 `BlueprintCallable` 函数供蓝图直接调用以执行验证。验证流程的启动和自定义规则注册均在 C++ 层面进行。

## C++ 用法

该插件的核心功能通过 C++ 接口提供。

### 头文件引入

```cpp
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"
```

### 基本用法：注册一个自定义验证规则

这是扩展插件功能的主要方式。你需要创建一个继承自 `FSequenceValidationRule` 的类，并在模块启动时注册它的工厂信息。
(来源：`SequenceValidationRule.h`, `ISequenceValidatorModule.h`, 及内置规则示例)

```cpp
// MyValidationRule.h
#pragma once
#include "Validation/SequenceValidationRule.h"

class FMyValidationRule : public UE::Sequencer::FSequenceValidationRule
{
public:
    // 提供规则信息（名称、描述、工厂方法）的静态方法
    static UE::Sequencer::FSequenceValidationRuleInfo MakeRuleInfo()
    {
        UE::Sequencer::FSequenceValidationRuleInfo Info;
        Info.RuleName = NSLOCTEXT("MyValidator", "MyRuleName", "检查特定命名模式");
        Info.RuleDescription = NSLOCTEXT("MyValidator", "MyRuleDesc", "检查所有绑定名称是否符合项目规范。");
        Info.RuleFactory = FOnCreateSequenceValidationRule::CreateStatic(&FMyValidationRule::Create);
        Info.bIsEnabled = true;
        return Info;
    }

private:
    static TSharedRef<UE::Sequencer::FSequenceValidationRule> Create()
    {
        return MakeShared<FMyValidationRule>();
    }

    // 核心验证逻辑
    virtual void OnRun(const UMovieSceneSequence* InSequence, UE::Sequencer::FSequenceValidationResults& OutResults) const override
    {
        // 1. 遍历序列中的所有绑定对象（Tracks）
        // 2. 检查绑定名称是否符合规则（例如，不以特定前缀开头）
        // 3. 如果发现不符合规范的，创建一个验证结果
        /*
        UObject* FoundInvalidObject = ...;
        if (FoundInvalidObject)
        {
            auto Result = MakeShared<UE::Sequencer::FSequenceValidationResult>(
                EMessageSeverity::Warning,
                FoundInvalidObject,
                NSLOCTEXT("MyValidator", "InvalidName", "绑定名称不符合规范: XXX"),
                GetRuleInfo()
            );
            OutResults.AddResult(Result);
        }
        */
    }
};

// MyModule.cpp (假设在某个 Editor 模块的 StartupModule 中注册)
void FMyEditorModule::StartupModule()
{
    ISequenceValidatorModule& ValidatorModule = FModuleManager::Get().LoadModuleChecked<ISequenceValidatorModule>("SequenceValidator");
    // 注册我们的自定义规则
    RuleID = ValidatorModule.RegisterValidationRule(FMyValidationRule::MakeRuleInfo());
}

void FMyEditorModule::ShutdownModule()
{
    if (ISequenceValidatorModule* ValidatorModule = FModuleManager::GetModulePtr<ISequenceValidatorModule>("SequenceValidator"))
    {
        // 注销规则
        ValidatorModule->UnregisterValidationRule(RuleID);
    }
}
```

### 进阶用法：以编程方式执行验证

你可以创建一个 `FSequenceValidator` 实例，将序列加入队列，然后启动验证，并监听完成事件。
(来源：`SequenceValidator.h`, 及内部实现逻辑)

```cpp
#include "Validation/SequenceValidator.h"
#include "MovieSceneSequence.h"

// 假设在某个编辑器工具或命令中
void RunSequenceValidation(UMovieSceneSequence* SequenceToValidate)
{
    // 1. 创建验证器实例（此时会从 ISequenceValidatorModule 获取当前所有已注册的规则）
    auto Validator = MakeShared<UE::Sequencer::FSequenceValidator>();

    // 2. 将序列加入验证队列
    Validator->Queue(SequenceToValidate);

    // 3. （可选）监听验证完成事件
    FDelegateHandle Handle = Validator->GetOnValidationFinished().AddLambda([ValidatorWeak = TWeakPtr<UE::Sequencer::FSequenceValidator>(Validator)]()
    {
        if (auto ValidatorPtr = ValidatorWeak.Pin())
        {
            const auto& Results = ValidatorPtr->GetResults();
            UE_LOG(LogSequenceValidator, Display, TEXT("验证完成，共发现 %d 个结果。"), Results.GetResults().Num());
            // 在这里处理结果，例如显示通知或日志输出
        }
    });

    // 4. 启动异步验证
    Validator->StartValidation();
}
```

## Demo 示例

一个最小化的自定义验证规则实现，检查序列中所有命名以 “Camera_” 开头的绑定是否真实存在（避免未分配的轨道）。
(这是一个简化的概念示例，省略了完整的对象遍历细节)

```cpp
// CameraBindingRule.h
#pragma once
#include "Validation/SequenceValidationRule.h"

class FCameraBindingRule : public UE::Sequencer::FSequenceValidationRule
{
public:
    static UE::Sequencer::FSequenceValidationRuleInfo MakeRuleInfo()
    {
        UE::Sequencer::FSequenceValidationRuleInfo Info;
        Info.RuleName = NSLOCTEXT("SeqValidatorDemo", "CameraBindRule", "摄像机绑定检查");
        Info.RuleDescription = NSLOCTEXT("SeqValidatorDemo", "CameraBindRuleDesc", "确保名称以‘Camera_’开头的轨道存在有效的绑定对象。");
        Info.RuleFactory = UE::Sequencer::FOnCreateSequenceValidationRule::CreateStatic(&FCameraBindingRule::Create);
        return Info;
    }

private:
    static TSharedRef<UE::Sequencer::FSequenceValidationRule> Create()
    {
        return MakeShared<FCameraBindingRule>();
    }

    virtual void OnRun(const UMovieSceneSequence* InSequence, UE::Sequencer::FSequenceValidationResults& OutResults) const override
    {
        if (!InSequence) return;

        UMovieScene* MovieScene = InSequence->GetMovieScene();
        if (!MovieScene) return;

        // 简化示例：遍历所有 Master Tracks
        for (UMovieSceneTrack* Track : MovieScene->GetMasterTracks())
        {
            FString TrackName = Track->GetDisplayName().ToString();
            if (TrackName.StartsWith(TEXT("Camera_")))
            {
                // 检查该轨道是否有任何 Section 包含有效的绑定
                bool bHasValidBinding = false;
                for (UMovieSceneSection* Section : Track->GetAllSections())
                {
                    // 在实际实现中，这里需要检查 Section 是否通过 GetObjectBindingID() 绑定了有效的对象
                    // 例如，对于 CineCameraActor 的绑定。
                    // 此处简化，假设我们检查某个关键属性
                    // bHasValidBinding |= (Section->GetSupportedBlendTypes().Num() > 0);
                }

                if (!bHasValidBinding)
                {
                    // 创建一个警告级别的验证结果
                    auto Result = MakeShared<UE::Sequencer::FSequenceValidationResult>(
                        EMessageSeverity::Warning,
                        /* InTarget */ Track, // 关联的UObject
                        FText::Format(NSLOCTEXT("SeqValidatorDemo", "EmptyCamTrack", "轨道‘{0}’似乎没有有效的摄像机绑定。"), FText::FromString(TrackName)),
                        GetRuleInfo()
                    );
                    OutResults.AddResult(Result);
                }
            }
        }
    }
};
```

## 模块依赖

要使用 `SequenceValidator` 插件（尤其是注册自定义规则），你的编辑器模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `SequenceValidator` | 提供 `ISequenceValidatorModule` 接口，用于注册验证规则。 |
| `LevelSequenceEditor` | 插件声明依赖此模块，是与序列编辑器深度集成的基础。 |
| `MovieScene` | 提供 `UMovieSceneSequence`、`UMovieScene`、`UMovieSceneTrack`、`UMovieSceneSection` 等核心序列资产类。 |
| `MovieSceneTools` | 提供序列相关的工具类，通常用于更深入的序列数据操作。 |
| `Slate` / `SlateCore` | 用于构建自定义验证规则时可能涉及的 UI 部分（如自定义消息）。 |

（注意：常见的 `Core`, `CoreUObject`, `Engine`, `UMG` 等依赖已省略）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF`，属于日志系统现代化重构。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次错误的查找替换操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了之前的一个变更（CL51314860）。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将引擎初始化后委托的使用方式从直接成员访问改为通过 Get 函数，修复了注册丢失问题。 |
| 2025-12-08 | `34716c37` | PR #14125: SequenceValidator: Fix WholeSectionRanges rule reporting incorrect results | 修复了“整帧段范围”验证规则报告错误结果的问题。 |

### 维护评价

`SequenceValidator` 是一个由 **Epic Games, Inc.** 官方维护的较新插件（创建于2025年7月）。从 Git 历史看，它在创建后的半年内有多次重要的稳定性修复和代码库重构（如委托使用方式迁移、日志系统迁移），表明它正处于**积极维护和打磨阶段**。

尽管其 `.uplugin` 标记为 `IsExperimentalVersion: true`，但这更多是 Epic 对其功能完整性和稳定性的谨慎表态，并不代表质量低下。作为 Sequencer 工作流中的一个质量保证工具，它具有明确的实用价值。

**推荐使用吗？**
**推荐。** 对于需要严格把控序列资产质量的项目，尤其是中大型团队项目，强烈建议启用并使用此插件。你可以：
1.  直接使用其内置规则（如重复关键帧、段落对齐检查）。
2.  按照文档中的指南，为项目编写特有的自定义验证规则。

由于它是实验性功能且版本号较低（0.1），未来API或UI可能会有调整，但核心验证框架已经稳定可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator)
- [官方文档]() （目前无专属文档）
- [测试用例]() （源码中未发现独立测试文件，测试可能位于更广泛的 Sequencer 测试套件中）