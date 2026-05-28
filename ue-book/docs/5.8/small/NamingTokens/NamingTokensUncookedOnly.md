# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名令牌 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产模板、编辑器工具资产） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 提供了一套**字符串模板令牌系统**，允许用户定义可识别的占位符（令牌），在字符串求值时将其替换为实际值。类似 `{project_name}` 这样的令牌可以在运行时或编辑时被动态解析。

该插件解决的核心问题是：**在文件路径、资产命名、字符串模板等场景中，需要一种标准化的、可扩展的命名变量替换机制**。与简单的字符串格式化不同，NamingTokens 提供了：

- **统一的令牌注册和管理框架**：通过 Blueprint 或 C++ 注册自定义令牌
- **编辑器集成**：带有自动补全、实时预览和错误提示的编辑体验
- **上下文感知**：支持在不同的评估上下文中使用不同的令牌值
- **未解析令牌警告**：当令牌无法解析时，在 tooltip 中用 `{}` 包裹显示，方便调试

## 使用场景

- 你在做一个自动化资产命名管线 → 用 NamingTokens 定义 `{asset_type}_{date}_{version}` 模板
- 你需要为文件路径提供动态变量替换（如 `{project_dir}/{level_name}/{sequence}`）→ 用 NamingTokens
- 你要构建一个批量处理工具，用户可以自定义输出命名规则 → 用 NamingTokens 提供令牌系统
- 你需要在编辑器中提供带自动补全的模板字符串输入框 → 用 NamingTokensUI 组件

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Resolve Tokens` | 对包含令牌的字符串进行求值，将令牌替换为实际值 | `UNamingTokensSubsystem` |
| `Create Naming Tokens Context` | 创建令牌评估上下文对象 | `UNamingTokensSubsystem` |
| `Register Tokens` | 注册一组自定义令牌定义 | `UNamingTokensSubsystem` |
| `Get Registered Tokens` | 获取当前已注册的所有令牌列表 | `UNamingTokensSubsystem` |

### 使用示例（蓝图描述）

**基本字符串解析：**
1. 创建一个 `Naming Tokens Context` 节点，设置评估所需的上下文信息
2. 使用 `Resolve Tokens` 节点，传入模板字符串（如 `"{project}_{level}_{date}"`）和上下文
3. 输出即为解析后的字符串（如 `"MyProject_MainLevel_20260514"`）

**编辑器自动补全：**
1. 在支持 NamingTokens 的文本输入框中，输入 `{` 触发自动补全菜单
2. 从下拉列表中选择已注册的令牌
3. 未解析的令牌会在 tooltip 中以 `{token_name}` 形式高亮显示

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokensSubsystem.h"
```

### 基本用法

```cpp
// 获取 Naming Tokens 子系统
UNamingTokensSubsystem* NamingTokensSubsystem = GEngine->GetEngineSubsystem<UNamingTokensSubsystem>();

// 创建评估上下文
TSharedRef<INamingTokensContext> Context = NamingTokensSubsystem->CreateNamingTokensContext();

// 对包含令牌的字符串进行求值
FString Template = TEXT("{project_name}/Maps/{level_name}");
FString Resolved = NamingTokensSubsystem->ResolveTokens(Template, Context);
// 结果: "MyProject/Maps/MainLevel"
```

**来源**: `NamingTokens` 核心模块，基于 subsystem 架构设计

### 进阶用法

```cpp
// 注册自定义令牌
FNamingTokenData TokenData;
TokenData.TokenKey = TEXT("custom_tag");
TokenData.DisplayName = TEXT("Custom Tag");
TokenData.Description = TEXT("A custom tag for asset naming");

UNamingTokensSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensSubsystem>();
Subsystem->RegisterTokens(/* namespace */, {TokenData});

// 在不同上下文中使用不同令牌值
TSharedRef<INamingTokensContext> Context = Subsystem->CreateNamingTokensContext();
// 通过 Context 设置令牌的解析逻辑

// 解析带有多个令牌的复杂模板
FString ComplexTemplate = TEXT("{project_name}/{asset_type}/{custom_tag}_{date}");
FString Result = Subsystem->ResolveTokens(ComplexTemplate, Context);
```

## Demo 示例

```cpp
// MyNamingTokensActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNamingTokensActor.generated.h"

UCLASS()
class AMyNamingTokensActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Naming")
    FString NamingTemplate = TEXT("{project}_{level}_{actor_name}");

    UFUNCTION(BlueprintCallable, Category = "Naming")
    FString ResolveNamingTemplate();
};
```

```cpp
// MyNamingTokensActor.cpp
#include "MyNamingTokensActor.h"
#include "NamingTokensSubsystem.h"

FString AMyNamingTokensActor::ResolveNamingTemplate()
{
    UNamingTokensSubsystem* Subsystem = GEngine->GetEngineSubsystem<UNamingTokensSubsystem>();
    if (!Subsystem)
    {
        return NamingTemplate;
    }

    TSharedRef<INamingTokensContext> Context = Subsystem->CreateNamingTokensContext();
    return Subsystem->ResolveTokens(NamingTemplate, Context);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 核心令牌系统，提供令牌定义、注册和解析功能 |

无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 未解析的令牌在警告提示中用 {} 包裹，便于调试识别 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动补全菜单单击即选中的交互问题 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键操作覆盖已令牌化文本的问题 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i | 为编辑器工具命名令牌添加工厂和资产定义，使其可在编辑器中显示 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将多个 VP 资产移至不同资产类别，并进行迁移 |

### 维护评价

**活跃维护中** ⚡

- **年龄**：创建于 2025-01-13，约 1.3 年历史
- **更新频率**：最近一周内有 5 次提交，集中在编辑器体验优化（自动补全、tooltip、交互修复）
- **状态**：标记为实验性（`IsExperimentalVersion: true`），尚未默认启用
- **活跃度**：持续有功能完善和 bug 修复，Epic Games 内部开发团队积极维护
- **注意事项**：作为实验性插件，API 可能在版本间发生变化；目前主要用于内部开发管线

**推荐使用**：如果你需要标准化的字符串令牌替换系统，可以关注此插件。作为实验性功能，建议在非关键项目中试用，并留意后续版本的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens/Tests)