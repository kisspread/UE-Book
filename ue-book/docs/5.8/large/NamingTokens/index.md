# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名标记 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、编辑器工具、UI界面） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

`NamingTokens` 插件提供了一个系统，用于定义和评估在字符串中的自定义标记（Token）。它解决的核心问题是**批量、标准化地生成和替换文件名、路径或任何字符串中的动态部分**。例如，你可以定义 `{ProjectName}`, `{AssetType}`, `{Date}` 等标记，在创建或重命名资产时自动替换为实际的项目名称、资产类型和当前日期。这对于维护大型项目中的文件命名一致性、自动化工作流至关重要。

## 使用场景

- **批量资产命名与重命名**：在为大量资产（如序列、纹理、蓝图）生成标准化名称时使用。
- **项目路径标准化**：在自动化脚本或编辑器工具中，为导出路径、存档路径生成包含变量的动态路径。
- **内容浏览器集成**：在内容浏览器的创建资产对话框中，为“命名模式”字段提供自动补全和预览的标记。

## 模块概览

| 模块 | 说明 |
|---|---|
| `NamingTokens` | 核心运行时模块，定义标记数据、评估逻辑和子系统接口。 |
| `NamingTokensEditor` | 编辑器模块，提供资产编辑器、自定义资产工厂、以及将标记系统集成到引擎创建资产对话框的细节。 |
| `NamingTokensUI` | UI模块，提供标记自动补全菜单、标记预览等用户界面组件。 |
| `NamingTokensUncookedOnly` | 仅未打包时使用的模块，通常包含编辑器扩展所需的蓝图功能（如Editor Utility Blueprints）。 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Naming Tokens` | 对一个包含标记的字符串进行评估，返回替换后的新字符串。 | `UNamingTokensSubsystem` |
| `Get All Naming Tokens Data Assets` | 获取当前项目中所有已注册的命名标记资产。 | `UNamingTokensSubsystem` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `GetGameInstanceSubsystem` 获取 `UNamingTokensSubsystem` 的实例。然后，调用 “Evaluate Naming Tokens” 节点，将包含 `{ProjectName}` 等标记的格式化字符串（如 `{ProjectName}_Texture_{Date}`）输入，节点会输出替换后的最终字符串（如 `MyProject_Texture_2025-05-27`）。

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokensSubsystem.h"
#include "NamingTokensDataAsset.h"
```

### 基本用法

```cpp
// 1. 获取命名标记子系统
UNamingTokensSubsystem* NamingTokensSubsystem = GEngine->GetEngineSubsystem<UNamingTokensSubsystem>();

// 2. 准备一个包含标记的字符串
FString TemplateString = TEXT(“/Game/Characters/{CharacterName}/Textures/{AssetType}_Diffuse”);

// 3. 评估并获取结果
FString EvaluatedString = NamingTokensSubsystem->EvaluateNamingTokens(TemplateString);
// EvaluatedString 可能是 “/Game/Characters/Hero/Textures/T_Diffuse”
```

## Demo 示例

```cpp
// MyNamingTokensDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyNamingTokensDemo
{
public:
    static void RunDemo();
};

// MyNamingTokensDemo.cpp
#include “MyNamingTokensDemo.h”
#include “NamingTokensSubsystem.h”

void FMyNamingTokensDemo::RunDemo()
{
    // 获取子系统
    UNamingTokensSubsystem* NamingTokensSubsystem = GEngine->GetEngineSubsystem<UNamingTokensSubsystem>();
    if (NamingTokensSubsystem)
    {
        // 评估一个路径模板
        FString OriginalPath = TEXT(“{ProjectBase}/Maps/{LevelName}_{Date}.umap”);
        FString ResolvedPath = NamingTokensSubsystem->EvaluateNamingTokens(OriginalPath);

        UE_LOG(LogTemp, Log, TEXT(“原始路径: %s, 解析后路径: %s”), *OriginalPath, *ResolvedPath);
    }
}
```

## 模块依赖

要使用此插件，你的模块需依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 核心运行时功能 |
| `NamingTokensUI` | 如果你需要访问标记选择器UI组件 |
| `EditorFramework` | (仅 `NamingTokensUI` 依赖) 提供编辑器工具栏和菜单集成 |
| `Blutility` | (仅 `NamingTokensUncookedOnly` 依赖) 支持编辑器工具蓝图 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 优化警告提示，未解析的标记键会以{}包裹显示 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动补全菜单单击即提交的功能 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键操作会意外替换已标记文本的问题 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears in the content browser. | 添加工厂和资产定义，使编辑器工具类命名标记资产在内容浏览器可见 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the … | (属于更大范围的Virtual Production资产迁移) |

### 维护评价

`NamingTokens` 是一个**较新的、处于实验阶段**的插件（创建于2025年初）。近期（2026年5月）的提交记录显示它**正在被积极开发和修复**，主要集中在提升UI/UX体验（自动补全、右键菜单）和完善资产管理系统。作为实验性功能，其API和功能在未来版本中可能会发生变化。目前看来，它对于有标准化命名需求的项目是一个有价值的、值得关注和试用的工具，但不建议在极其稳定的产品管线中毫无保留地采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens/Tests)