# Gameplay Tags Toolset

> Toolset for reading and managing gameplay tags via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏标签工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayTagsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset) | |

## 用途

该插件为 Unreal Engine 的 Gameplay Tags 系统提供了一个面向 AI 工具（AI Toolset Registry）的接口。它允许 AI 助手或通过脚本查询、创建、修改和删除项目中的 Gameplay Tags。核心目的是将标签管理功能开放给 AI 辅助工作流，实现自动化的标签查询、分析和维护。

## 使用场景

- 你在开发一个需要大量标签管理的项目，希望借助 AI 助手快速查找、创建或重构标签。
- 需要通过 AI 助手自动分析哪些资产引用了某个特定标签，以便进行批量检查或清理。
- 希望通过自然语言或脚本指令来操作 Gameplay Tags，而无需在编辑器中手动查找和编辑。

## 蓝图用法

所有功能均通过 `UGameplayTagsToolset` 类的静态函数暴露，并标记为 `AICallable`，主要面向 AI 工具调用。在常规蓝图中使用较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListTags` | 列出项目中的标签，可按父级标签过滤。 | `UGameplayTagsToolset` |
| `GetTagInfo` | 获取指定标签的详细信息（注释、来源、子标签）。 | `UGameplayTagsToolset` |
| `AddTag` | 向项目中添加一个新的 Gameplay Tag。 | `UGameplayTagsToolset` |
| `RemoveTag` | 从项目中移除一个 Gameplay Tag。 | `UGameplayTagsToolset` |
| `RenameTag` | 重命名一个 Gameplay Tag，并更新所有引用。 | `UGameplayTagsToolset` |
| `FindReferencersByTag` | 查找所有引用了指定 Gameplay Tag 的资产。 | `UGameplayTagsToolset` |

### 使用示例（蓝图描述）

由于该插件主要面向 AI 调用，在常规蓝图中，你可以通过 `Call Function` 节点直接调用这些静态函数。例如，要查找引用了 `"Character.State.Dead"` 标签的资产：
1. 添加一个 `Call Function` 节点。
2. 将函数选择为 `GameplayTagsToolset -> FindReferencersByTag`。
3. 将 `TagName` 输入引脚连接到一个包含 `"Character.State.Dead"` 字符串的节点。
4. 将输出的 `TArray<FString>` 连接到一个循环或打印节点以查看结果。

## C++ 用法

该插件的功能主要通过静态函数提供，因此在 C++ 中的用法是直接调用这些静态方法。

### 头文件引入

```cpp
#include "GameplayTagsToolset/GameplayTagsToolset.h"
```

### 基本用法

```cpp
// 引入头文件
#include "GameplayTagsToolset/GameplayTagsToolset.h"

// 列出所有以 "Weapon" 开头的标签
TArray<FString> WeaponTags = UGameplayTagsToolset::ListTags(TEXT("Weapon"));

// 获取标签 "Character.State.Dead" 的详细信息
FGameplayTagInfo TagInfo = UGameplayTagsToolset::GetTagInfo(TEXT("Character.State.Dead"));
UE_LOG(LogTemp, Log, TEXT("Tag Comment: %s"), *TagInfo.Comment);

// 查找引用了 "Character.State.Dead" 标签的所有资产
TArray<FString> Referencers = UGameplayTagsToolset::FindReferencersByTag(TEXT("Character.State.Dead"));
```
*注：此代码为基于头文件函数的示例，并非来自特定测试用例。*

### 进阶用法

```cpp
// 在明确获得用户许可后，添加一个新标签
UGameplayTagsToolset::AddTag(TEXT("Character.State.Invincible"), TEXT("Temporary invincibility after taking damage"), TEXT("DefaultGameplayTags.ini"));

// 重命名标签，并更新所有引用
UGameplayTagsToolset::RenameTag(TEXT("Old.OldTag"), TEXT("New.NewTag"));
```

## Demo 示例

以下是一个最小化的 C++ 类，用于展示如何在插件中使用这些工具函数。

```cpp
// MyGameplayTagManager.h
#pragma once
#include "CoreMinimal.h"
#include "GameplayTagsToolset/GameplayTagsToolset.h"

class FMyGameplayTagManager
{
public:
	static void LogAllCharacterStateTags()
	{
		// 列出所有 Character.State 子标签
		TArray<FString> StateTags = UGameplayTagsToolset::ListTags(TEXT("Character.State"));
		for (const FString& Tag : StateTags)
		{
			FGameplayTagInfo Info = UGameplayTagsToolset::GetTagInfo(Tag);
			UE_LOG(LogTemp, Warning, TEXT("Tag: %s, Source: %s, Comment: %s"), *Tag, *Info.Source, *Info.Comment);
		}
	}
};
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools | 调整了工具集定义发现工具函数的逻辑 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回退了之前的提交 CL52878047 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools | 更改了工具集定义确定工具函数的方式（后被回退） |
| 2026-04-10 | `1cd269a7` | [AI Assistant] Fix GameplayTagsToolsetSpec tests failing on build machines | 修复了构建机器上测试失败的问题 |
| 2026-04-10 | `7daf3063` | [GameplayTagsToolset] Add FindReferencersByTag tool | 添加了查找标签引用者的工具功能 |

### 维护评价

- **创建时间**：2026年4月1日，是一个非常新的实验性插件。
- **最近更新频率**：创建后短时间内（半个月内）有多次更新，包括功能添加、重构和修复。
- **活跃度**：目前处于早期活跃开发阶段，但主要由 Epic Games 的 AI 助手（或相关开发流程）驱动。
- **已知问题/限制**：作为实验性插件，默认未启用，且依赖 ToolsetRegistry 和 GameplayTagsEditor 插件。主要面向 AI 工具调用，常规蓝图/C++ 使用场景有限。
- **推荐使用**：**仅推荐给希望集成 AI 辅助 Gameplay Tags 管理的高级开发者**。对于常规项目，建议继续使用标准的 GameplayTags 编辑器功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameplayTagsToolset/Source/GameplayTagsToolset/Private/GameplayTagsToolset/Tests)