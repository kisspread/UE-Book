# Sequence Validator

> A tool that provides validation rules for detecting common errors in sequences

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SequenceValidator` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/SequenceValidator) | |

## 用途

Sequence Validator 是一个 Sequencer 编辑器扩展插件，用于自动检测 Level Sequence 中的常见错误。在虚拟制片和大型影视项目中，Sequence 中往往包含大量轨道、关键帧和子序列引用，手动检查这些数据中的问题非常耗时且容易遗漏。该插件通过可扩展的规则引擎，异步遍历整个序列层级结构，自动报告重复关键帧、Section 边界偏移、未赋值的绑定/资产、以及非整帧边界等问题。

插件采用 Visitor 模式遍历 `UMovieSceneSequence` 的完整层级（包括根轨道、Object Binding、子序列、Section 和 Channel），并支持自定义验证规则的注册与扩展。

## 使用场景

- 你在做虚拟制片项目，Sequence 中有几十个子序列和上百个 Section → 用 Sequence Validator 批量检查
- 你发现 Sequencer 中某些关键帧行为异常，怀疑有重复关键帧 → 用 Duplicate Keys 规则排查
- 你的 Sequence 播放时某些动画或音频没有播放 → 用 Unassigned Bindings/Assets 规则检查引用是否丢失
- 你需要确保所有 Section 的起止时间精确对齐到整帧 → 用 Whole Section Ranges 规则
- 你的 Section 边界和 Camera Cut 时间差了 1-2 帧 → 用 Section Alignments 规则检测

## 蓝图用法

该插件是纯编辑器工具，没有公开的蓝图接口。所有功能通过编辑器 UI 窗口操作。

## 编辑器用法

### 打开 Sequence Validator 窗口

通过菜单 **Window → Cinematics → Sequence Validator** 打开验证器窗口（注册为 Nomad Tab，在 Cinematics 类别下）。

### 窗口布局

窗口分为三个区域：

- **左侧上方** — Queue（验证队列）：通过拖放或资产选择器添加要验证的 Level Sequence
- **左侧下方** — Rules（验证规则）：显示所有已注册的验证规则及其启用状态
- **右侧** — Results（验证结果）：以树形结构显示验证结果，按 Sequence 分组

### 工作流程

1. 将一个或多个 `ULevelSequence` 资产拖放到 Queue 面板
2. 在 Rules 面板中确认需要启用的规则
3. 点击底部 **Start Validation** 按钮
4. 在 Results 面板中查看验证结果，双击可定位到问题对象

### 内置验证规则

| 规则 | 说明 | 检测的问题 |
|---|---|---|
| **Section Alignments** | Section 对齐检查 | Section 的起止时间在 Camera Cut 边界或播放范围边界附近（2 帧以内）但未精确对齐 |
| **Unassigned Bindings/Assets** | 绑定和资产引用检查 | 音频 Section 缺少 Sound 引用、Camera Cut Section 缺少有效 Camera Binding、约束 Section 缺少有效 Binding、子序列 Section 缺少 Sequence 引用、骨骼动画 Section 缺少 Animation 引用 |
| **Whole Section Ranges** | 整帧边界检查 | Section 的起止时间不在整帧上（骨骼动画 Section 的上界除外） |
| **Duplicate Keys** | 重复关键帧检查 | 同一 Channel 上同一时间存在多个关键帧 |

### 验证结果说明

每个验证结果包含：
- **严重级别**：Info / Warning / Error
- **目标对象**：指向产生问题的 UMovieSceneSection
- **时间信息**：问题发生的帧时间
- **子序列路径**：如果问题在子序列中，会记录从根序列到问题位置的 SubSection 路径
- **关键帧句柄**（Duplicate Keys 规则）：可直接选中重复的关键帧

## C++ 用法

### 头文件引入

```cpp
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"
```

### 基本用法 — 同步验证单个序列

```cpp
// 来源: Validation/SequenceValidator.cpp (Validate 方法)
#include "Validation/SequenceValidator.h"

using namespace UE::Sequencer;

// 创建验证器实例（自动加载所有已注册的规则）
FSequenceValidator Validator;

// 同步验证单个序列
Validator.Validate(MyLevelSequence);

// 查看结果
const FSequenceValidationResults& Results = Validator.GetResults();
for (const TSharedPtr<FSequenceValidationResult>& Result : Results.GetResults())
{
    // 根节点是序列本身，子节点是具体的问题
    if (Result->HasChildren())
    {
        for (const TSharedPtr<FSequenceValidationResult>& Child : Result->GetChildren())
        {
            UE_LOG(LogTemp, Warning, TEXT("%s"), *Child->GetUserMessage().ToString());
        }
    }
}
```

### 进阶用法 — 异步批量验证

```cpp
// 来源: Validation/SequenceValidator.cpp (StartValidation 方法)
#include "Validation/SequenceValidator.h"

using namespace UE::Sequencer;

FSequenceValidator Validator;

// 添加多个序列到队列
Validator.Queue(SequenceArray);

// 监听验证完成事件
Validator.GetOnValidationFinished().AddLambda([&Validator]()
{
    const FSequenceValidationResults& Results = Validator.GetResults();
    // 处理结果...
});

// 异步启动验证（使用 UE::Tasks 并行执行规则）
Validator.StartValidation();

// 检查是否正在验证
if (Validator.IsValidating())
{
    // 等待 Tick 中的 OnValidationFinished 回调
}
```

### 自定义验证规则

```cpp
// 来源: ISequenceValidatorModule.h, Validation/SequenceValidationRule.h
#include "ISequenceValidatorModule.h"
#include "Validation/SequenceValidationRule.h"
#include "Validation/SequenceValidationResult.h"

using namespace UE::Sequencer;

// 定义自定义规则
class FMyCustomValidationRule : public FSequenceValidationRule
{
protected:
    virtual void OnRun(const UMovieSceneSequence* InSequence,
                       FSequenceValidationResults& OutResults) const override
    {
        UMovieScene* MovieScene = InSequence->GetMovieScene();
        // 遍历 MovieScene，检查你需要的条件
        // 如果发现问题：
        auto Result = MakeShared<FSequenceValidationResult>(
            EMessageSeverity::Warning, ProblemSection, RuleInfo);
        Result->SetUserMessage(LOCTEXT("MyWarning", "发现自定义问题"));
        OutResults.AddResult(Result);
    }
};

// 注册规则（通常在模块 StartupModule 中）
ISequenceValidatorModule& Module = FModuleManager::LoadModuleChecked<ISequenceValidatorModule>("SequenceValidator");

FSequenceValidationRuleInfo RuleInfo;
RuleInfo.RuleName = LOCTEXT("MyRule", "My Custom Rule");
RuleInfo.RuleDescription = LOCTEXT("MyRuleDesc", "Checks for custom issues.");
RuleInfo.RuleFactory = FOnCreateSequenceValidationRule::CreateLambda(
    []() { return MakeShared<FMyCustomValidationRule>(); });

FSequenceValidationRuleID RuleID = Module.RegisterValidationRule(MoveTemp(RuleInfo));

// 不再需要时注销
Module.UnregisterValidationRule(RuleID);
```

### 控制并发任务数

```cpp
// 来源: Validation/SequenceValidator.cpp
// 控制台变量，控制异步验证的最大并发任务数
// SequenceValidation.MaxConcurrentTasks
// 默认值: -1（使用 CPU 核心数）
// 可在控制台中设置:
//   SequenceValidation.MaxConcurrentTasks 4
```

## Demo 示例

### 最小验证示例

```cpp
// MySequenceValidator.h
#pragma once

#include "CoreMinimal.h"

class ULevelSequence;

class FMySequenceValidator
{
public:
    static void ValidateSequence(ULevelSequence* InSequence);
};
```

```cpp
// MySequenceValidator.cpp
#include "MySequenceValidator.h"
#include "Validation/SequenceValidator.h"
#include "Validation/SequenceValidationResult.h"

void FMySequenceValidator::ValidateSequence(ULevelSequence* InSequence)
{
    using namespace UE::Sequencer;

    FSequenceValidator Validator;
    Validator.Validate(InSequence);

    int32 WarningCount = 0;
    const FSequenceValidationResults& Results = Validator.GetResults();
    for (const TSharedPtr<FSequenceValidationResult>& RootResult : Results.GetResults())
    {
        for (const TSharedPtr<FSequenceValidationResult>& Child : RootResult->GetChildren())
        {
            if (Child->GetSeverity() == EMessageSeverity::Warning)
            {
                ++WarningCount;
                UE_LOG(LogTemp, Warning, TEXT("[SeqValidator] %s"),
                    *Child->GetUserMessage().ToString());
            }
        }
    }
    UE_LOG(LogTemp, Display, TEXT("[SeqValidator] Found %d warnings."), WarningCount);
}
```

**Build.cs 依赖**：

```csharp
// 注意: SequenceValidator 是 Editor 模块，只能在 Editor 模块中使用
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "MovieScene",
    "LevelSequence",
    "SequenceValidator",
});
```

## 模块依赖

以下模块在 Build.cs 的 PrivateDependencyModuleNames 中声明，使用该插件时通常不需要额外依赖（因为 SequenceValidator 本身是 Editor 插件）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MovieScene` | MovieScene 序列化框架、Channel、Section |
| `MovieSceneTracks` | Camera Cut Track、Sub Track 等具体轨道类型 |
| `LevelSequence` | LevelSequence 资产类型 |
| `LevelSequenceEditor` | Sequencer 编辑器集成 |
| `Sequencer` | Sequencer 编辑器核心 |
| `SequencerCore` | Sequencer 核心工具 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器基础框架 |
| `ToolMenus` | 菜单注册系统 |
| `ContentBrowser` | 内容浏览器集成（拖放支持） |
| `AssetRegistry` | 资产查询 |
| `ToolWidgets` | 编辑器通用控件 |
| `InputCore` | 输入系统 |
| `Projects` | 插件系统 |
| `ApplicationCore` | 应用核心 |
| `WorkspaceMenuStructure` | 工作区菜单分类 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-24 | `3a9929b` | Fix uninitialized — 修复未初始化变量问题 |
| 2025-09-24 | `176072a` | Added duplicate keys validator — 新增重复关键帧检测规则 |
| 2025-09-24 | `60b472b` | Add support for selecting keys on validation — 验证结果可直接选中关键帧 |

### 维护评价

Sequence Validator 是一个非常新的插件（2025 年 7 月创建，约 1 年），目前处于 **实验性** 阶段（`IsExperimentalVersion=true`）。

- **活跃程度**：2025 年 9 月有密集的功能开发（同一天内连续 3 次提交），表明当时正在快速迭代
- **功能完整性**：已具备 4 个内置验证规则，支持异步并行验证、自定义规则注册、拖放添加序列等核心功能
- **架构质量**：设计良好，采用 Visitor 模式遍历序列层级，规则通过模块接口注册/注销，支持扩展
- **风险提示**：标记为实验性，API 可能在后续版本中发生变化。由于创建时间较短，使用时需关注后续版本的兼容性

**推荐使用**：如果你的项目中有复杂的 Level Sequence 需要质量检查，可以启用此插件。但由于实验性标记，建议不要在生产构建中深度绑定其 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MovieScene/SequenceValidator)
- 官方文档：无
