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

NamingTokens 插件旨在解决 UE5 项目中字符串（尤其是文件路径、资产命名等）的标准化和动态化问题。它允许开发者定义一组可重用的“命名标记”（Tokens），这些标记可以在运行时或编辑器环境中被解析并替换为具体的字符串值。

**核心作用**：通过提供一个中央化的标记定义和解析系统，避免在蓝图或代码中硬编码复杂的格式化逻辑，从而提高一致性、可维护性和自动化水平。例如，可以将 `{ProjectName}`、`{UserName}` 或 `{YYYY-MM-DD}` 定义为标记，在创建文件或资产名时，系统会自动替换为当前的项目名、登录用户名或日期。

## 使用场景

-   **游戏资产命名规范**：在大型项目中，为确保美术、关卡、音效等资产的命名统一，可以定义如 `{Department}_{AssetType}_{Index}` 的模板，由标记系统自动填充部门、类型等信息。
-   **自动化流程与工具**：构建如“自动为每个镜头生成渲染输出文件夹”的工具。路径模板可设为 `{ProjectDir}/Renders/{ShotName}_{YYYYMMDD}`，标记系统负责解析项目目录、镜头名和当前日期。
-   **多人协作与个性化**：允许每个开发者或团队在他们的命名空间中定义个人标记，如 `{MyInitials}`，在本地开发时自动替换，而不影响主项目的配置。
-   **电影虚拟制片**：在虚拟制片工作流中，快速生成带有场景、镜头、Take 等信息的临时文件或文件夹路径。

## 蓝图用法

NamingTokens 核心功能通过 `UNamingTokens` 类暴露给蓝图。你可以创建其子类来定义项目特定的标记。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateString` | 评估输入的字符串，将其中定义的标记替换为当前值。 | `UNamingTokens` |
| `GetTokensByPrefix` | 获取特定命名空间前缀下的所有可用标记。 | `UNamingTokens` |
| `ValidateTokens` | 检查一个字符串中是否包含未定义或无效的标记。 | `UNamingTokens` |

### 使用示例（蓝图描述）

1.  **创建标记定义资产**：在内容浏览器中右键，选择 `Blueprints > Editor Utility > Naming Tokens` 创建一个继承自 `UEditorUtilityNamingTokens` 的蓝图资产。
2.  **定义标记**：在该蓝图的类默认值（Class Defaults）中，找到 `Tokens` 数组。添加新元素，为每个标记设置一个 `Key`（例如 `Date`）和一个 `Prefix`（可选，如 `myProject`，则完整标记为 `{myProject.Date}`）。并为其指定一个用于获取实际值的 `FunctionName`。
3.  **获取值**：在需要生成文件名的蓝图（如某个 Editor Utility Widget 或 Actor 的 Construction Script）中，使用 `Get Naming Tokens` 节点获取你的 `UEditorUtilityNamingTokens` 对象引用。
4.  **执行替换**：将格式字符串（例如 `Level_{MyProject.LevelNumber}_{Date}.umap`）连接到该对象的 `EvaluateString` 节点。输出的结果字符串中，`{MyProject.LevelNumber}` 和 `{Date}` 将被替换为实际值（如 `Level_01_20250514.umap`）。

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens.h"
// 如果需要使用编辑器专用功能
#include "NamingTokensEditorModule.h"
```

### 基本用法

使用 `UNamingTokens` 评估一个包含标记的字符串。

```cpp
// 假设你已经获取或创建了一个 UNamingTokens 对象实例 (例如在编辑器工具或 GameMode 中)
UNamingTokens* MyTokens = ...;

// 1. 定义一个带有标记的模板字符串
const FString Template = TEXT(“/Game/Maps/{ProjectName}_{Date}“);

// 2. 评估字符串，标记将被替换
FString EvaluatedString = MyTokens->EvaluateString(Template);

// 结果可能为：”/Game/Maps/MyProject_20250514”
```

### 进阶用法

创建自定义的标记类并注册函数。

```cpp
// 1. 头文件: MyProjectNamingTokens.h
#pragma once
#include “NamingTokens.h”
#include “MyProjectNamingTokens.generated.h”

UCLASS()
class UMyProjectNamingTokens : public UNamingTokens
{
    GENERATED_BODY()
public:
    // 定义一个用于提供值的 UFUNCTION
    UFUNCTION(BlueprintCallable, Category = “Naming Tokens“)
    static FString GetCurrentUserInitials();
};

// 2. 实现文件: MyProjectNamingTokens.cpp
#include “MyProjectNamingTokens.h“

FString UMyProjectNamingTokens::GetCurrentUserInitials()
{
    // 实现获取用户首字母的逻辑，例如从命令行或本地设置读取
    return TEXT(“JD“);
}
```

然后，在 `UMyProjectNamingTokens` 的蓝图中，你可以将一个标记的 `FunctionName` 属性设置为 `GetCurrentUserInitials`。当评估包含该标记的字符串时，`GetCurrentUserInitials` 函数将被自动调用以提供替换值。

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个简单的 `UNamingTokens` 子类并评估字符串。

**MyMinimalNamingTokens.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “NamingTokens.h”
#include “MyMinimalNamingTokens.generated.h”

UCLASS()
class UMyMinimalNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyMinimalNamingTokens();

    /** 自定义函数，用于提供一个简单的动态值 */
    UFUNCTION(BlueprintCallable, Category = “Naming Tokens“)
    static FString GetGreetingText();
};
```

**MyMinimalNamingTokens.cpp**
```cpp
#include “MyMinimalNamingTokens.h“

UMyMinimalNamingTokens::UMyMinimalNamingTokens()
{
    // 在构造函数中，可以静态注册一些简单的标记（非函数绑定方式）
    // 但通常建议通过蓝图编辑器的 Tokens 数组来配置，更直观。
}

FString UMyMinimalNamingTokens::GetGreetingText()
{
    return TEXT(“HelloWorld“);
}

// 示例使用：在某个地方（如某个 Commandlet 或 Editor Utility 函数中）
void EvaluateExample()
{
    UMyMinimalNamingTokens* Tokens = NewObject<UMyMinimalNamingTokens>();

    // 假设在蓝图中，我们为 Tokens 定义了一个键为 “Greet” 的标记，并绑定了 GetGreetingText 函数。
    // 模板字符串
    const FString Template = TEXT(“Output_{Greet}.txt“);
    const FString Result = Tokens->EvaluateString(Template);

    // Result 的值将是 “Output_HelloWorld.txt“
    UE_LOG(LogTemp, Display, TEXT(“Evaluated: %s“), *Result);
}
```

## 模块依赖

使用此插件的核心 `NamingTokens` 运行时模块，你的项目模块通常无需特殊依赖。但若要深度集成编辑器功能，可能需要考虑以下依赖：

| 模块 | 用途 |
|---|---|
| `NamingTokensUI` | 提供用于配置和显示命名令牌的用户界面组件，如果你在编辑器工具中需要嵌入相关 UI。 |
| `NamingTokensUncookedOnly` | 处理未打包（Uncooked）状态下的命名令牌逻辑，例如在编辑器中进行预处理或验证时使用。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 改进警告提示，将未解析的标记键用花括号包裹显示，使问题更清晰。 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动完成菜单，单击即可选中，提升操作流畅度。 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键菜单意外覆盖已标记文本的问题。 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i | 为编辑器效用命名令牌添加工厂和资产定义，使其能正常出现在创建菜单中。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | （跨插件提交）将虚拟制片相关资产移动到新的资产类别，其中可能涉及本插件的类别调整。 |

### 维护评价

- **状态**：**积极维护中**。插件创建于 2025 年初，非常年轻。从最近的 git 历史看，更新非常活跃（最近更新在 2026 年 5 月），且都集中在功能完善、UI 体验优化和 Bug 修复上。
- **实验性标记**：插件 `.uplugin` 中 `IsExperimentalVersion: true`，表明 Epic 官方认为其 API 和功能尚未完全稳定，未来可能会有变动。这是一个重要的使用注意事项。
- **推荐**：该插件处于早期但活跃的开发阶段，对于需要标准化字符串生成的编辑器工具和自动化流程来说，是一个非常有潜力的解决方案。尽管标记为实验性，但在可控范围内积极试用和采用是值得推荐的，可以显著提升工作流效率。建议密切关注其更新日志，以适应可能的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens/Tests) (如果存在)