# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名标记 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

Naming Tokens 是一个字符串标记系统，允许开发者定义在字符串中可被识别和替换的“标记”。它主要解决需要在运行时或编辑器中动态生成和替换字符串中特定部分的问题。例如，在生成文件路径、资产命名规则或任何需要模板化的字符串时，可以使用该插件定义如 `{ProjectName}`、`{Date}` 等标记，然后在运行时或编辑时将这些标记替换为实际的值。该插件提供了创建、评估和管理这些标记的完整框架。

## 使用场景

- 你在制作一个自动化资源处理工具，需要根据当前日期、平台等信息动态生成文件名。
- 你需要为资产创建一套命名规范，并希望在编辑器中预览替换后的结果。
- 你需要在蓝图或C++中执行复杂的字符串模板替换逻辑，并希望有一个可扩展、可复用的系统。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Naming Tokens` | 查找并返回可用的命名标记资产 | `UNamingTokensBPLibrary` |
| `Evaluate Naming Tokens` | 评估一个字符串，替换其中的标记 | `UNamingTokensBPLibrary` |
| `Get Token Value` | 获取指定标记的当前值 | `UNamingTokensBPLibrary` |
| `Set Token Value` | 设置指定标记的值 | `UNamingTokensBPLibrary` |

### 使用示例（蓝图描述）

1.  **查找标记资产**：使用 `Find Naming Tokens` 节点来获取项目中的命名标记资产（通常是一个蓝图实例）。
2.  **评估字符串**：将包含标记的模板字符串（如 `"{ProjectName}/Meshes/{AssetName}"`）和上一步获取的标记资产一起输入到 `Evaluate Naming Tokens` 节点。该节点会输出替换后的字符串。
3.  **动态操作单个标记**：可以使用 `Get Token Value` 和 `Set Token Value` 节点来读取或覆盖特定标记的值。

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens.h"
#include "NamingTokensBPLibrary.h"
```

### 基本用法

从 `NamingTokensUncookedOnly` 模块和核心模块推断的基本用法。

```cpp
// (来源: NamingTokensUncookedOnly 模块推断)
// 1. 获取命名标记库实例
UNamingTokensBPLibrary* NamingTokensLib = UNamingTokensBPLibrary::Get();

// 2. 准备一个需要被评估的字符串
FString TemplateString = TEXT("Export/{Platform}/{BuildVersion}/Level.pak");

// 3. 评估字符串，替换其中的标记
FString EvaluatedString = NamingTokensLib->EvaluateNamingTokens(TemplateString, /* 标记上下文 */);

// 结果可能是: "Export/Windows/1.0.1/Level.pak"
```

### 进阶用法

基于插件架构推断的进阶用法，涉及自定义标记。

```cpp
// (来源: 整体架构推断)
// 1. 创建自定义的命名标记蓝图（继承自 UNamingTokens）
//    这可以在编辑器中通过“新建资产 -> NamingTokens”完成。
//    在该蓝图中，你可以通过 Override 函数来定义自定义标记的返回值。

// 2. 在C++中，你可以查找并使用特定的命名标记资产
TArray<UObject*> NamingTokensAssets;
UNamingTokensBPLibrary::FindNamingTokens(NamingTokensAssets);

// 3. 或者，你可以直接实例化并配置一个标记上下文
FNamingTokensContext Context;
Context.AddOrSetToken(TEXT("CustomToken"), TEXT("MyValue"));

// 4. 使用该上下文进行评估
FString Result = UNamingTokensBPLibrary::EvaluateNamingTokens(TEXT("Start_{CustomToken}_End"), Context);
// Result 将是 "Start_MyValue_End"
```

## Demo 示例

以下是一个完整的最小示例，展示如何在C++中定义和使用自定义标记。

### NamingTokensDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"

// 前向声明
class UNamingTokens;

class FNamingTokensDemo
{
public:
    /** 演示如何使用命名标记库 */
    static void DemonstrateTokenEvaluation();

private:
    /** 演示如何查找一个命名标记资产 */
    static UNamingTokens* FindDemoNamingTokensAsset();
};
```

### NamingTokensDemo.cpp
```cpp
#include "NamingTokensDemo.h"
#include "NamingTokensBPLibrary.h"
#include "NamingTokens.h"

void FNamingTokensDemo::DemonstrateTokenEvaluation()
{
    // 获取蓝图库实例
    UNamingTokensBPLibrary* Library = UNamingTokensBPLibrary::Get();
    if (!Library)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get NamingTokens BPLibrary"));
        return;
    }

    // 准备模板字符串
    FString Template = TEXT("Generated_{Project}_{Date}.json");

    // 方法1：使用全局默认上下文评估
    FString Result1 = Library->EvaluateNamingTokens(Template);
    UE_LOG(LogTemp, Log, TEXT("Default Context Result: %s"), *Result1);

    // 方法2：使用自定义上下文评估
    FNamingTokensContext CustomContext;
    CustomContext.AddOrSetToken(TEXT("Project"), TEXT("MyGame"));
    CustomContext.AddOrSetToken(TEXT("Date"), TEXT("2026-05-15"));

    FString Result2 = Library->EvaluateNamingTokens(Template, CustomContext);
    UE_LOG(LogTemp, Log, TEXT("Custom Context Result: %s"), *Result2);
    // 输出: "Generated_MyGame_2026-05-15.json"

    // 方法3：通过资产对象评估（如果存在）
    UNamingTokens* Asset = FindDemoNamingTokensAsset();
    if (Asset)
    {
        FString Result3 = Library->EvaluateNamingTokens(Template, Asset);
        UE_LOG(LogTemp, Log, TEXT("Asset Context Result: %s"), *Result3);
    }
}

UNamingTokens* FNamingTokensDemo::FindDemoNamingTokensAsset()
{
    // 此函数需要根据实际资产路径查找
    // 示例路径，请替换为你的项目中的实际路径
    FString AssetPath = TEXT("/Game/MyNamingTokens/BP_MyNamingTokens");
    return LoadObject<UNamingTokens>(nullptr, *AssetPath);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 核心运行时模块，提供标记定义和评估的基础框架。 |
| `NamingTokensEditor` | 编辑器扩展，提供创建和管理命名标记资产的编辑器UI。 |
| `NamingTokensUI` | 包含编辑器UI组件，用于在编辑器中预览标记评估结果。 |
| `NamingTokensUncookedOnly` | 包含仅在开发（未打包）环境中运行的功能，如资产工厂和初始化逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 在警告提示中用 {} 包裹未解析的标记键，提升可读性。 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动完成菜单单击即确认的问题。 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键菜单会破坏已标记文本的问题。 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears in the correct category. | 为编辑器实用工具命名标记添加工厂和资产定义，使其出现在正确的类别中。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | （虚拟制作相关）移动了多个资产类别，可能影响了命名标记资产的归类。 |

### 维护评价

该插件创建于2025年初，是一个相对较新的实验性插件。从最近的提交记录（2026年5月）来看，**维护非常活跃**。最近的几次提交集中在修复编辑器交互的bug（如自动完成、右键菜单）和改进用户体验（如警告信息格式），表明开发团队正在积极打磨这个功能。

- **活跃维护**: 是
- **实验性**: 是（`IsExperimentalVersion=true`，`EnabledByDefault=false`）
- **推荐使用**: **推荐用于新项目或需要标记化字符串的场景**。由于处于实验阶段，API可能会有变动，需要关注更新日志。对于生产环境，建议评估其稳定性和适用性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- 官方文档: （插件信息中未提供）
- 测试用例: （基于提供的模块信息推断，测试可能分布在 `Tests/` 目录下，路径示例：`Engine/Plugins/Developer/NamingTokens/Tests/`）