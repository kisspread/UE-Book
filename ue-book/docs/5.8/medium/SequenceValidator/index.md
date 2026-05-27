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
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator) | |

## 用途

SequenceValidator 是一个编辑器工具，专门用于对 Unreal Engine 中的 Sequencer 序列（如关卡序列、动画序列）进行自动化验证。它的核心作用是帮助用户在创建和编辑序列时，预先发现常见的错误和潜在问题，避免在运行时或后期制作中出现意外情况。

**为什么存在？** Sequencer 是 UE5 中强大的非线性动画和过场动画工具，但其内容（如关键帧、轨道、绑定关系）容易在复杂操作中产生不易察觉的错误（例如关键帧重复、节范围不对齐、资源引用丢失等）。手动检查这些错误耗时且容易遗漏。此插件提供了一个系统化的框架和一组内置规则，能够批量、异步地检查序列，显著提升内容创作的质量和效率。

## 使用场景

-   **过场动画制作**：在复杂的过场动画序列中，验证所有摄像机剪辑点是否对齐，确保动画段在整帧开始和结束。
-   **动画资源管理**：检查动画蒙太奇或动画序列中是否存在未绑定的资源或无效的轨道绑定。
-   **协作与代码审查**：在团队中，作为集成检查工具，确保提交的序列资产符合项目规范，减少集成错误。
-   **自动化构建流程**：将序列验证集成到构建或打包脚本中，作为质量门禁（Quality Gate）的一部分。

## 蓝图用法

此插件主要面向编辑器扩展和自动化，未暴露可供蓝图直接调用的核心验证节点。其用户界面集成在 Sequencer 编辑器内。

### 核心 UI 功能

插件通过以下 Slate Widget 提供可视化操作界面，这些 Widget 被集成到 Sequencer 编辑器中：

| 界面组件 | 说明 | 所在类 |
|---|---|---|
| 验证器主面板 | 集成在 Sequencer 编辑器内的核心面板，包含队列、规则列表和结果展示。 | `SSequenceValidator` |
| 验证队列视图 | 显示待验证的序列资产列表，支持拖放添加。 | `SSequenceValidatorQueue` |
| 验证规则视图 | 列出所有已注册的验证规则及其启用状态。 | `SSequenceValidatorRules` |
| 验证结果树视图 | 以树状结构展示所有验证问题，按严重性分类。 | `SSequenceValidatorResults` |

**使用方式**：在 Sequencer 编辑器中，通过菜单或命令（`FSequenceValidatorCommands::StartValidation`）打开验证器面板。在队列中添加一个或多个序列资产，选择要运行的验证规则，然后启动验证。结果将以树状结构展示，并可直接定位到问题所在的帧或对象。

## C++ 用法

### 头文件引入

```cpp
#include "SequenceValidator/Public/ISequenceValidatorModule.h"
```

### 基本用法

**1. 获取模块接口**
```cpp
// 获取 SequenceValidator 模块接口
ISequenceValidatorModule& ValidatorModule = FModuleManager::Get().LoadModuleChecked<ISequenceValidatorModule>(TEXT("SequenceValidator"));
```
*来源：通过 `ISequenceValidatorModule` 的公开接口使用。*

**2. 注册自定义验证规则**
```cpp
// 定义你的验证规则工厂函数
TSharedRef<FSequenceValidationRule> CreateMyRule()
{
    // 返回你自定义规则的实例
    return MakeShared<FSequenceValidationRule_MyCustomRule>();
}

// 构造规则信息
FSequenceValidationRuleInfo MyRuleInfo;
MyRuleInfo.RuleName = NSLOCTEXT("MyPlugin", "MyRuleName", "My Custom Rule");
MyRuleInfo.RuleDescription = NSLOCTEXT("MyPlugin", "MyRuleDesc", "Checks for custom conditions.");
MyRuleInfo.RuleFactory = FOnCreateSequenceValidationRule::CreateStatic(&CreateMyRule);
MyRuleInfo.bIsEnabled = true;

// 注册规则
UE::Sequencer::FSequenceValidationRuleID MyRuleID = ValidatorModule.RegisterValidationRule(MoveTemp(MyRuleInfo));

// ... 在插件卸载时记得注销
ValidatorModule.UnregisterValidationRule(MyRuleID);
```
*来源：`ISequenceValidatorModule` 接口及 `FSequenceValidationRuleInfo` 结构体。*

### 进阶用法

**创建并使用序列验证器**
```cpp
// 创建一个验证器实例
UE::Sequencer::FSequenceValidator Validator;

// 获取所有可用的验证规则（由模块注册）
TArray<TSharedPtr<UE::Sequencer::FSequenceValidationRuleInfo>> Rules = Validator.GetRules();

// 将序列加入验证队列
UMovieSceneSequence* MySequence = GetMySequenceAsset(); // 假设你有一个序列
Validator.Queue(MySequence);

// 绑定验证完成事件
FSimpleDelegate OnDone;
OnDone.BindLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Validation finished!"));
});
Validator.GetOnValidationFinished().Add(OnDone);

// 启动异步验证
Validator.StartValidation();

// ... 稍后检查是否完成
if (!Validator.IsValidating())
{
    // 获取验证结果
    const UE::Sequencer::FSequenceValidationResults& Results = Validator.GetResults();
    for (const TSharedPtr<UE::Sequencer::FSequenceValidationResult>& Result : Results.GetResults())
    {
        if (Result->GetSeverity() == EMessageSeverity::Error)
        {
            UE_LOG(LogTemp, Error, TEXT("Validation Error: %s"), *Result->GetUserMessage().ToString());
            // 可以进一步获取目标对象、时间等信息
            UObject* Target = Result->GetTarget();
            if (Result->HasLocalTime())
            {
                FFrameTime Time = Result->GetLocalTime();
            }
        }
    }
}
```
*来源：`FSequenceValidator` 类、`FSequenceValidationResult` 类及 `ISequenceValidatorModule` 的典型使用模式。*

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 核心依赖，插件作为 Sequencer 编辑器的扩展，深度集成了关卡序列的编辑和验证功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于代码格式更新。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作后的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL51314860 提交的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复引擎初始化委托注册问题，确保插件正确初始化。 |
| 2025-12-08 | `34716c37` | PR #14125: SequenceValidator: Fix WholeSectionRanges rule reporting incorrect results | 修复了“整个节范围”规则报告错误结果的问题。 |

### 维护评价

**实验性插件，处于早期开发阶段**。该插件于 2025 年 7 月创建，历史很短。从提交记录看，2025 年 12 月有一次针对内置规则的重要修复，2026 年 2-4 月有多次与底层引擎初始化相关的调整和回退，表明其代码仍在与引擎核心进行适配和稳定化。

**优点**：
1.  目标明确，功能实用，能有效解决序列资产验证的痛点。
2.  架构设计良好，采用规则工厂模式，易于扩展自定义验证规则。
3.  拥有异步验证和事件回调，可集成到自动化流程。

**注意**：
1.  **标记为实验性**（`IsExperimentalVersion = true`），接口和功能未来可能发生较大变化。
2.  **开发活跃但不稳定**：近期提交多与底层修复和回退相关，说明功能层和底层交互仍在磨合。
3.  **尚无官方文档**（`DocsURL` 为空）。

**建议**：如果你正在制作大量过场动画或需要严格的质量控制，可以尝试启用此插件以获得早期反馈。但由于其处于实验阶段，不建议在需要高度稳定的生产管线中作为唯一依赖。可用于辅助性检查，并关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/SequenceValidator)
- [官方文档]()（暂无）