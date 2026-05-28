# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名Token |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

`NamingTokens` 插件提供了一套强大的框架，用于在字符串中定义、识别和替换动态的“命名Token”。其核心目的是在不使用复杂格式化字符串或硬编码逻辑的情况下，构建灵活、可维护且用户友好的模板系统。它解决了在资产命名、路径生成、UI显示等场景下，需要将动态数据（如日期、项目名、资产类型、自定义参数）嵌入到静态字符串模板中的问题。通过这个插件，开发者可以将“`{ProjectName}_{AssetType}_{Date}`”这样的模板字符串，自动求值为“MyGame_StaticMesh_20250514”这样的最终结果。

## 使用场景

-   **资产命名规范化**：你正在开发一个资产导入或重命名工具，需要按照公司或项目的特定规则（如`{Department}_{AssetName}_{Version}`）来自动生成或验证资产命名。
-   **动态路径生成**：你需要为项目生成动态的文件路径或目录结构，例如基于当前日期、分支名称或用户信息来组织构建输出或日志文件。
-   **模板系统**：你在编辑器中构建一个文本模板功能，允许用户输入包含可替换变量的文本，然后在运行时或特定操作时将其填充为实际值。
-   **蓝图中的字符串构建**：你在蓝图中需要动态生成复杂的字符串，但使用“格式化文本”节点或拼接字符串节点过于繁琐且难以维护，希望使用更声明式的Token方式。

## 蓝图用法

核心API主要通过 `UNamingTokensEngineSubsystem` 访问，它是一个引擎子系统，负责Token的全局管理、查找和求值。

### 核心节点

#### Token求值与查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateTokenText` | 对包含Token的 `FText` 字符串进行解析和求值，返回包含原始文本、求值结果及各Token详情的结构体。 | `UNamingTokensEngineSubsystem` |
| `EvaluateTokenString` | 与 `EvaluateTokenText` 功能相同，但输入和输出均为 `FString`。 | `UNamingTokensEngineSubsystem` |
| `EvaluateTokenList` | 对一个包含原始Token键（不含花括号）的列表进行求值，返回每个Token及其求值结果。 | `UNamingTokensEngineSubsystem` |
| `GetNamingTokens` | 根据命名空间名称获取对应的 `UNamingTokens` 对象实例。 | `UNamingTokensEngineSubsystem` |

#### 命名空间与全局Token管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterGlobalNamespace` | 将指定命名空间注册为全局。全局命名空间的Token在求值时无需前缀命名空间名。 | `UNamingTokensEngineSubsystem` |
| `UnregisterGlobalNamespace` | 将命名空间从全局注册中移除。 | `UNamingTokensEngineSubsystem` |
| `GetAllNamespaces` | 获取当前项目中发现的所有命名空间列表。 | `UNamingTokensEngineSubsystem` |
| `ClearCachedNamingTokens` | 清除已加载的Token对象缓存。当蓝图资产中的命名空间被修改后，调用此方法可以强制重新加载，无需重启编辑器。 | `UNamingTokensEngineSubsystem` |

#### 求值控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FNamingTokenFilterArgs` | 求值时的过滤器参数结构体，用于控制哪些命名空间参与求值、是否强制大小写敏感、是否仅限原生Token等。 | 结构体 |

### 使用示例（蓝图描述）

1.  **获取子系统**：在任何蓝图图表中，使用“Get Engine Subsystem”节点，类选择 `UNamingTokensEngineSubsystem`。
2.  **调用求值**：将子系统输出引脚连接到 `Evaluate Token Text` 节点的“Target”输入。
3.  **输入模板**：在“InTokenText”输入中，键入模板字符串，例如：`"Folder: {global:Date}_Prefix"`。其中 `{global:Date}` 表示调用 `global` 命名空间下的 `Date` Token。
4.  **设置过滤器（可选）**：创建一个 `FNamingTokenFilterArgs` 结构体变量，可以设置其“Additional Namespaces to Include”属性为包含 “MyCustomTools” 等字符串，这样在求值时就不需要写全名 `{MyCustomTools:SomeToken}`，直接写 `{SomeToken}` 即可。
5.  **获取结果**：`Evaluate Token Text` 节点会返回一个 `FNamingTokenResultData` 结构体。其“Evaluated Text”属性即为最终求值后的字符串（如 `"Folder: 20250514_Prefix"`）。“Token Values”数组则包含了每个被替换的Token的详细信息（键、值、是否成功等）。

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens/NamingTokenData.h"
#include "NamingTokens/NamingTokensEngineSubsystem.h"
```

### 基本用法

以下示例展示如何创建自定义Token类，并注册一个原生处理函数。这是扩展插件功能的主要方式。

```cpp
// MyGameNamingTokens.h
#pragma once
#include "NamingTokens/NamingTokens.h"
#include "MyGameNamingTokens.generated.h"

UCLASS()
class UMyGameNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyGameNamingTokens();

protected:
    // 重写此函数来添加默认Token
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override;

    // 一个原生的Token处理函数
    static FText GetCurrentMapName();
};
```

```cpp
// MyGameNamingTokens.cpp
#include "MyGameNamingTokens.h"

UMyGameNamingTokens::UMyGameNamingTokens()
{
    // 设置命名空间名称，必须唯一
    Namespace = TEXT("MyGame");
    NamespaceDisplayName = NSLOCTEXT("MyGameNamingTokens", "Namespace", "My Game");
}

void UMyGameNamingTokens::OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens)
{
    // 定义一个名为“MapName”的Token
    FNamingTokenData MapNameToken;
    MapNameToken.TokenKey = TEXT("MapName");
    MapNameToken.DisplayName = NSLOCTEXT("MyGameNamingTokens", "MapNameToken", "Current Map Name");
    MapNameToken.Description = NSLOCTEXT("MyGameNamingTokens", "MapNameTokenDesc", "The name of the currently loaded map.");
    // 绑定到一个静态函数作为处理器
    MapNameToken.TokenProcessorNative = FTokenProcessorDelegateNative::CreateStatic(&UMyGameNamingTokens::GetCurrentMapName);
    Tokens.Add(MapNameToken);

    // 可以添加更多Token...
}

FText UMyGameNamingTokens::GetCurrentMapName()
{
    UWorld* World = GEditor ? GEditor->GetEditorWorldContext().World() : nullptr;
    if (World)
    {
        FText MapName = FText::FromString(FPackageName::GetShortName(World->GetMapName()));
        return MapName;
    }
    return FText::FromString(TEXT("None"));
}
```

**来源文件**：概念与结构参考 `Public/GlobalNamingTokens.h` 和 `Public/NamingTokens.h`。

### 进阶用法

使用引擎子系统在运行时或工具代码中求值字符串。

```cpp
// 在某个工具函数中
void UMyAssetTool::ProcessTemplateString(const FString& TemplateString)
{
    // 获取子系统
    UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();
    if (!Subsystem) return;

    // 配置过滤器
    FNamingTokenFilterArgs FilterArgs;
    FilterArgs.AdditionalNamespacesToInclude.Add(TEXT("MyGame")); // 让 “MyGame” 命名空间的Token可以被直接访问
    FilterArgs.bIncludeGlobal = true;

    // 调用求值
    FNamingTokenResultData Result = Subsystem->EvaluateTokenString(TemplateString, FilterArgs);

    // 使用结果
    UE_LOG(LogTemp, Log, TEXT("Evaluated Path: %s"), *Result.EvaluatedText.ToString());

    // 检查某个Token是否求值失败
    for (const FNamingTokenValueData& Value : Result.TokenValues)
    {
        if (!Value.bWasEvaluated)
        {
            UE_LOG(LogTemp, Warning, TEXT("Token '%s' failed to evaluate."), *Value.TokenKey);
        }
    }
}
```

**来源文件**：用法逻辑参考 `Public/NamingTokensEngineSubsystem.h` 中函数的注释。

## Demo 示例

一个最小的、可运行的自定义Token类实现。

```cpp
// SimpleDateTimeTokens.h
#pragma once
#include "NamingTokens/NamingTokens.h"
#include "SimpleDateTimeTokens.generated.h"

UCLASS()
class USimpleDateTimeTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    USimpleDateTimeTokens();

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override;
    virtual void OnPreEvaluate_Implementation(const FNamingTokensEvaluationData& InEvaluationData) override;

private:
    FDateTime CachedEvaluationTime;
};
```

```cpp
// SimpleDateTimeTokens.cpp
#include "SimpleDateTimeTokens.h"

USimpleDateTimeTokens::USimpleDateTimeTokens()
{
    Namespace = TEXT("SimpleDateTime");
    NamespaceDisplayName = FText::FromString(TEXT("Simple DateTime"));
}

void USimpleDateTimeTokens::OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens)
{
    // 年
    FNamingTokenData YearToken(TEXT("Year"), FText::FromString(TEXT("Current Year")),
        FTokenProcessorDelegateNative::CreateLambda([this]() -> FText {
            return FText::AsNumber(CachedEvaluationTime.GetYear());
        }));
    Tokens.Add(YearToken);

    // 月日
    FNamingTokenData DateToken(TEXT("Date"), FText::FromString(TEXT("Current Date")),
        FTokenProcessorDelegateNative::CreateLambda([this]() -> FText {
            return FText::FromString(CachedEvaluationTime.ToString(TEXT("%Y%m%d")));
        }));
    Tokens.Add(DateToken);

    // 时间戳
    FNamingTokenData TimestampToken(TEXT("Timestamp"), FText::FromString(TEXT("High Resolution Timestamp")),
        FTokenProcessorDelegateNative::CreateLambda([this]() -> FText {
            return FText::AsNumber(CachedEvaluationTime.GetTicks()); // 获取高精度时间戳
        }));
    Tokens.Add(TimestampToken);
}

void USimpleDateTimeTokens::OnPreEvaluate_Implementation(const FNamingTokensEvaluationData& InEvaluationData)
{
    // 在求值开始前，捕获一次时间，确保同一次求值中所有时间Token使用相同的时间点
    CachedEvaluationTime = InEvaluationData.CurrentDateTime;
}
```

## 模块依赖

使用此插件的功能，你的模块通常只需依赖核心的 `NamingTokens` 模块。如果需要自定义Token类，则如上所示继承 `UNamingTokens`。

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 插件的核心运行时框架，包含Token定义、求值引擎和子系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 优化了警告提示，未解析的Token键现在会用花括号包裹显示，更清晰。 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复了自动完成菜单的交互，单击即可选择并确认Token。 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复了在包含Token的文本上右键单击会破坏文本结构的问题。 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i | 为编辑器实用工具添加了工厂和资产定义，使其能在内容浏览器中正确显示。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | （关联提交）将虚拟制片相关资产移至新的资产分类，并迁移至新插件，NamingTokens插件支持此类扩展。 |

### 维护评价

-   **状态**：**活跃维护**。插件于2025年初创建，属于较新的实验性功能（`IsExperimentalVersion=true`）。从提交历史看，截至2026年5月仍有持续的、高质量的开发活动，主要集中在修复UI/UX问题和增强编辑器集成。
-   **推荐度**：**推荐在工具链开发中使用**。作为Epic官方推出的实验性插件，其API设计成熟，旨在解决一个常见的编辑器工具开发痛点。虽然标记为实验性，但代码质量高，且近期的更新表明其正在走向稳定。非常适合用于构建需要动态字符串模板的自定义资产处理器、命名工具或工作流。需要注意其“实验性”状态，意味着API可能在未来版本中发生变化。
-   **注意事项**：目前标记为实验性，且默认未启用（`Installed: false`）。在生产项目中使用前，应充分测试其稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [官方文档]() （当前为空，可关注UE官方文档或Wiki的后续更新）