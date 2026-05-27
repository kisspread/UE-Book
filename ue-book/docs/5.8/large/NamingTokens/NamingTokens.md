# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名标记 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 是一个模板字符串求值系统，允许开发者定义可被识别和替换的"标记"（Token）。类似于模板引擎中的变量替换机制：你定义标记如 `{project}`、`{date}`、`{level}`，系统在求值字符串时会将这些标记替换为实际值。

该插件解决了以下问题：

1. **文件路径命名自动化**：在资产导入、批量重命名等场景中，通过标记动态生成文件路径
2. **项目级命名规范**：为项目定义统一的命名标记，供工具和工作流使用
3. **扩展性**：支持原生 C++ 和蓝图两种方式定义标记处理器，便于项目和工具各自扩展
4. **命名空间隔离**：不同工具/模块可以注册各自的命名空间，避免标记冲突

## 使用场景

- 你在做一个大型项目，需要统一的文件命名规范（如 `Map_{project}_{level}_{date}`） → 用 NamingTokens 定义项目级标记，所有工具统一调用求值
- 你在开发资产导入管线，需要根据上下文动态生成文件路径 → 注册自定义命名空间，用 `EvaluateTokenString` 替换路径中的标记
- 你需要一个可扩展的模板系统，让设计师在蓝图中自定义标记 → 继承 `UNamingTokens`，在蓝图中定义 CustomTokens
- 你希望标记不需要命名空间前缀就能直接使用 → 用 `RegisterGlobalNamespace` 注册为全局命名空间

## 蓝图用法

### 核心节点

#### 引擎子系统（UNamingTokensEngineSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNamingTokens` | 按命名空间查找标记对象（含缓存和蓝图查找） | `UNamingTokensEngineSubsystem` |
| `GetNamingTokensNative` | 按命名空间查找原生标记对象（仅 C++ 类） | `UNamingTokensEngineSubsystem` |
| `GetMultipleNamingTokens` | 批量查找多个命名空间的标记对象 | `UNamingTokensEngineSubsystem` |
| `EvaluateTokenText` | 求值包含标记的 FText 字符串 | `UNamingTokensEngineSubsystem` |
| `EvaluateTokenString` | 求值包含标记的 FString 字符串 | `UNamingTokensEngineSubsystem` |
| `EvaluateTokenList` | 求值一组标记键列表，返回各自的值 | `UNamingTokensEngineSubsystem` |
| `RegisterGlobalNamespace` | 注册为全局命名空间（标记无需命名空间前缀） | `UNamingTokensEngineSubsystem` |
| `UnregisterGlobalNamespace` | 取消全局命名空间注册 | `UNamingTokensEngineSubsystem` |
| `IsGlobalNamespaceRegistered` | 检查命名空间是否已注册为全局 | `UNamingTokensEngineSubsystem` |
| `GetGlobalNamespaces` | 获取所有全局命名空间 | `UNamingTokensEngineSubsystem` |
| `GetAllNamespaces` | 获取所有已发现的命名空间 | `UNamingTokensEngineSubsystem` |
| `ClearCachedNamingTokens` | 清除标记缓存，强制重新加载 | `UNamingTokensEngineSubsystem` |

#### 标记对象（UNamingTokens）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateTokenText` | 对当前命名空间的标记文本求值 | `UNamingTokens` |
| `GetFormattedTokensStringForDisplay` | 获取所有标记的友好显示字符串 | `UNamingTokens` |
| `GetCurrentDateTime` | 获取当前日期时间（可重写以自定义） | `UNamingTokens` |
| `IsPrivateNamespace` | 检查是否为私有命名空间 | `UNamingTokens` |

#### 过滤参数（FNamingTokenFilterArgs）

| 属性 | 说明 |
|---|---|
| `AdditionalNamespacesToInclude` | 额外包含的命名空间，无需前缀即可使用 |
| `bIncludeGlobal` | 是否包含全局命名空间（默认 true） |
| `bForceCaseSensitive` | 是否强制区分大小写（默认 false，不区分） |
| `bNativeOnly` | 是否仅查找原生 C++ 标记（默认 false） |
| `bNormalizeInput` | 是否预处理输入（移除标记内空格，默认 true） |

#### 结果数据（FNamingTokenResultData）

| 属性 | 说明 |
|---|---|
| `OriginalText` | 原始文本 |
| `EvaluatedText` | 求值后的文本（标记已替换） |
| `TokenValues` | 每个标记的求值结果数组（按出现顺序） |

### 使用示例

**求值标记字符串：**

1. 获取引擎子系统 → 调用 `EvaluateTokenString`
2. 输入：`"Map_{gameproject:project}_{date:year}"`
3. 设置 Filter：`bIncludeGlobal = true`，`AdditionalNamespacesToInclude` 包含 `"gameproject"` 和 `"date"`
4. 输出 ResultData 中 `EvaluatedText` 为 `"Map_MyProject_2025"`

**注册全局命名空间后简化调用：**

1. 调用 `RegisterGlobalNamespace("gameproject")`
2. 之后可以直接写 `"Map_{project}"` 而无需 `gameproject:` 前缀
3. 求值时 `bIncludeGlobal = true` 即可自动匹配

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens.h"
#include "NamingTokenData.h"
#include "NamingTokensEngineSubsystem.h"
```

### 基本用法：定义自定义命名空间

创建一个子类继承 `UNamingTokens`，在构造函数或 `OnCreateDefaultTokens` 中注册标记。

**来源**: `Public/NamingTokens.h`, `Public/NamingTokenData.h`

```cpp
// MyProjectNamingTokens.h
#pragma once

#include "NamingTokens.h"
#include "MyProjectNamingTokens.generated.h"

UCLASS()
class UMyProjectNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyProjectNamingTokens()
    {
        // 命名空间只允许字母数字和下划线
        Namespace = TEXT("myproject");
        NamespaceDisplayName = NSLOCTEXT("MyProject", "NS", "My Project");
    }

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override
    {
        // 添加一个原生标记：返回当前项目的名称
        Tokens.Emplace(
            TEXT("project"),                                          // TokenKey
            NSLOCTEXT("MyProject", "ProjectToken", "Project Name"),  // DisplayName
            FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::FromString(FApp::GetProjectName());
            })
        );

        // 添加一个带描述的标记
        Tokens.Emplace(
            TEXT("build"),
            NSLOCTEXT("MyProject", "BuildToken", "Build Version"),
            NSLOCTEXT("MyProject", "BuildDesc", "The current build version"),
            FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::FromString(TEXT("1.0.0"));
            })
        );
    }
};
```

### 基本用法：求值字符串

**来源**: `Public/NamingTokensEngineSubsystem.h`

```cpp
// 在任意运行时代码中使用
UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();

// 注册为全局命名空间（可选，这样标记无需前缀）
Subsystem->RegisterGlobalNamespace(TEXT("myproject"));

// 定义求值过滤参数
FNamingTokenFilterArgs Filter;
Filter.bIncludeGlobal = true;
Filter.bNormalizeInput = true;

// 求值包含标记的字符串
FString Input = TEXT("Map_{project}_{build}");
FNamingTokenResultData Result = Subsystem->EvaluateTokenString(Input, Filter);

// Result.EvaluatedText → "Map_MyProject_1.0.0"
// Result.TokenValues 包含每个标记的求值详情
UE_LOG(LogTemp, Log, TEXT("Evaluated: %s"), *Result.EvaluatedText.ToString());
```

### 基本用法：求值带命名空间前缀的标记

**来源**: `Public/NamingTokensEngineSubsystem.h`, `Public/Utils/NamingTokenUtils.h`

```cpp
UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();

// 不注册全局命名空间，使用 namespace:token 语法
FNamingTokenFilterArgs Filter;
Filter.bIncludeGlobal = false;

FString Input = TEXT("Assets/{myproject:project}/Maps/{myproject:build}.umap");
FNamingTokenResultData Result = Subsystem->EvaluateTokenString(Input, Filter);

// Result.EvaluatedText → "Assets/MyProject/Maps/1.0.0.umap"
```

### 进阶用法：外部标记注册

外部标记允许工具临时注册标记，无需修改 `UNamingTokens` 子类。

**来源**: `Public/NamingTokens.h`

```cpp
// 获取已存在的命名空间标记对象
UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();
UNamingTokens* TokenObj = Subsystem->GetNamingTokens(TEXT("myproject"));

if (TokenObj)
{
    // 注册外部标记，获取 Guid
    FGuid ExternalGuid;
    TArray<FNamingTokenData>& ExternalTokens = TokenObj->RegisterExternalTokens(ExternalGuid);

    // 添加临时标记
    ExternalTokens.Emplace(
        TEXT("temp_counter"),
        NSLOCTEXT("", "Counter", "Counter"),
        FTokenProcessorDelegateNative::CreateLambda([]() -> FText
        {
            static int32 Counter = 0;
            return FText::AsNumber(++Counter);
        })
    );

    // 现在求值可以使用该标记
    FNamingTokenResultData Result = TokenObj->EvaluateTokenText(
        FText::FromString(TEXT("{temp_counter}"))
    );

    // 清理
    TokenObj->UnregisterExternalTokens(ExternalGuid);
}
```

### 进阶用法：批量求值标记列表

**来源**: `Public/NamingTokensEngineSubsystem.h`

```cpp
UNamingTokensEngineSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();

TArray<FString> TokenList = {
    TEXT("project"),
    TEXT("build"),
    TEXT("date:year"),
    TEXT("date:month")
};

FNamingTokenFilterArgs Filter;
Filter.bIncludeGlobal = true;

TArray<FNamingTokenValueData> Values = Subsystem->EvaluateTokenList(TokenList, Filter);

for (const FNamingTokenValueData& Value : Values)
{
    UE_LOG(LogTemp, Log, TEXT("[%s:%s] = %s (bSuccess: %s)"),
        *Value.TokenNamespace, *Value.TokenKey,
        *Value.TokenValue.ToString(),
        Value.bWasEvaluated ? TEXT("true") : TEXT("false"));
}
```

## Demo 示例

完整的最小示例：定义一个自定义命名空间，包含两个标记，然后在代码中求值。

**MyProjectNamingTokens.h**

```cpp
#pragma once

#include "NamingTokens.h"
#include "MyProjectNamingTokens.generated.h"

/**
 * 项目级命名标记定义。
 * 注册为全局命名空间后，标记可直接写为 {project} 而非 {myproject:project}。
 */
UCLASS(Blueprintable)
class UMyProjectNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyProjectNamingTokens()
    {
        Namespace = TEXT("myproject");
        NamespaceDisplayName = NSLOCTEXT("MyProject", "NS", "My Project");
    }

protected:
    virtual void OnCreateDefaultTokens(TArray<FNamingTokenData>& Tokens) override
    {
        // 标记1：项目名称
        Tokens.Emplace(
            TEXT("project"),
            NSLOCTEXT("MyProject", "Project", "Project Name"),
            NSLOCTEXT("MyProject", "ProjectDesc", "The name of the project"),
            FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::FromString(FApp::GetProjectName());
            })
        );

        // 标记2：当前年份
        Tokens.Emplace(
            TEXT("year"),
            NSLOCTEXT("MyProject", "Year", "Year"),
            NSLOCTEXT("MyProject", "YearDesc", "Current year"),
            FTokenProcessorDelegateNative::CreateLambda([]() -> FText
            {
                return FText::AsDateTime(FDateTime::Now(), EDateTimeStyle::Custom, TEXT("yyyy"));
            })
        );
    }
};
```

**MyProjectNamingTokens.cpp**

```cpp
#include "MyProjectNamingTokens.h"
```

**NamingTokenDemoSubsystem.h**

```cpp
#pragma once

#include "Subsystems/EngineSubsystem.h"
#include "NamingTokenDemoSubsystem.generated.h"

UCLASS()
class UNamingTokenDemoSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
};
```

**NamingTokenDemoSubsystem.cpp**

```cpp
#include "NamingTokenDemoSubsystem.h"
#include "NamingTokensEngineSubsystem.h"
#include "NamingTokenData.h"

void UNamingTokenDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    // 获取命名标记子系统
    UNamingTokensEngineSubsystem* TokenSystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();
    if (!TokenSystem)
    {
        return;
    }

    // 注册为全局命名空间（标记可省略 "myproject:" 前缀）
    TokenSystem->RegisterGlobalNamespace(TEXT("myproject"));

    // 求值示例1：使用命名空间前缀
    {
        FNamingTokenFilterArgs Filter;
        Filter.bIncludeGlobal = false;

        FString Template = TEXT("Project/{myproject:project}/{myproject:year}_assets");
        FNamingTokenResultData Result = TokenSystem->EvaluateTokenString(Template, Filter);

        UE_LOG(LogTemp, Log, TEXT("Result: %s"), *Result.EvaluatedText.ToString());
        // 输出: Project/MyProjectName/2025_assets
    }

    // 求值示例2：全局命名空间（无需前缀）
    {
        FNamingTokenFilterArgs Filter;
        Filter.bIncludeGlobal = true;

        FString Template = TEXT("{project}_{year}_export");
        FNamingTokenResultData Result = TokenSystem->EvaluateTokenString(Template, Filter);

        UE_LOG(LogTemp, Log, TEXT("Result: %s"), *Result.EvaluatedText.ToString());
        // 输出: MyProjectName_2025_export

        // 查看每个标记的详细求值结果
        for (const FNamingTokenValueData& TokenValue : Result.TokenValues)
        {
            UE_LOG(LogTemp, Log, TEXT("  Token [%s] = %s"),
                *TokenValue.TokenKey, *TokenValue.TokenValue.ToString());
        }
    }

    // 求值示例3：批量求值标记列表
    {
        TArray<FString> TokenList = { TEXT("project"), TEXT("year") };
        FNamingTokenFilterArgs Filter;
        Filter.bIncludeGlobal = true;

        TArray<FNamingTokenValueData> Values = TokenSystem->EvaluateTokenList(TokenList, Filter);
        for (const auto& V : Values)
        {
            UE_LOG(LogTemp, Log, TEXT("  [%s] = %s"), *V.TokenKey, *V.TokenValue.ToString());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 查找蓝图命名标记资产 |
| `UMG` | UI 组件（NamingTokensUI 模块） |

其余均为标准 Core/Engine/Slate 依赖，无其他特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 未解析的标记键在警告提示中用 {} 包裹显示 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动补全菜单单击即提交的问题 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键操作覆盖已标记文本的问题 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i | 添加编辑器工具命名标记的工厂和资产定义 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将 VP 资产移至不同分类并迁移到新路径 |

### 维护评价

**活跃维护**。该插件于 2025 年 1 月创建，至今约 1 年，近期（2026 年 5 月）仍有多次功能性更新，主要集中在 UI 体验改进（自动补全、右键菜单、资产浏览器集成）。

**注意事项**：
- 当前标记为实验性（`IsExperimentalVersion = true`），API 可能发生变化
- 默认未启用（`Installed = false`），需要在插件设置中手动启用
- 从最近的提交看，该插件正在积极完善编辑器端的用户体验，预示着可能在后续版本中正式发布

**推荐度**：适合在项目内部工具中使用，但由于实验性状态，不建议作为核心生产管线的唯一依赖。可先在工具开发中试用，待正式发布后再考虑全面集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- 官方文档：无