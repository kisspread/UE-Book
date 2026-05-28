# Naming Tokens

> Define tokens which can be recognized during string evaluation.

| 属性 | 值 |
|---|---|
| 中文名 | 命名令牌 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NamingTokens` (Runtime), `NamingTokensEditor` (Runtime), `NamingTokensUI` (Runtime), `NamingTokensUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens) | |

## 用途

NamingTokens 插件提供了一套**令牌（Token）定义与字符串求值系统**，允许用户定义可被解析的占位符令牌，然后在字符串（如文件路径、资产命名）中使用这些令牌进行动态替换。

核心功能：
- 定义自定义命名令牌（如 `{project_name}`、`{date}` 等），绑定到蓝图函数获取运行时值
- 在字符串求值时自动识别并替换这些令牌
- 支持通过蓝图创建和管理令牌，无需 C++ 代码
- 提供编辑器工具资产（Editor Utility Naming Tokens）用于编辑器上下文的令牌定义
- 内置自动补全和错误提示的编辑器 UI

该插件主要解决虚拟制片（Virtual Production）和工作流中需要规范化、自动化文件/资产命名的问题。

## 使用场景

- 你在做虚拟制片，需要按照固定模板生成带项目名、日期、镜头号等信息的文件路径 → 用 NamingTokens
- 你需要在资产命名中动态插入上下文信息（如关卡名、平台名）→ 用 NamingTokens
- 你想要一个可复用的命名规则系统，团队成员通过蓝图即可维护 → 用 NamingTokens

## 蓝图用法

### 核心类

| 类 | 说明 |
|---|---|
| `UNamingTokens` | 基类，用于定义命名令牌。通过蓝图子类化来创建自定义令牌 |
| `UEditorUtilityNamingTokens` | 编辑器专用令牌子类，仅在编辑器中生效 |

### 令牌定义方式

1. 创建 `UNamingTokens` 的蓝图子类（或 `UEditorUtilityNamingTokens` 的子类用于编辑器专用令牌）
2. 在蓝图中定义函数，每个函数对应一个令牌键（Token Key）
3. 函数返回 `FString`，即该令牌在求值时的替换值
4. 编辑器中通过 Details 面板的自定义 UI 配置令牌与函数的映射关系

### 使用示例（蓝图描述）

1. **创建令牌蓝图**：在 Content Browser 右键 → 蓝图类 → 选择 `NamingTokens` 作为父类
2. **定义令牌函数**：在蓝图中添加公开函数（如 `GetProjectName`），返回当前项目名称字符串
3. **配置令牌映射**：在蓝图的 Details 面板中，通过 FNamingTokensData 的自定义属性面板将令牌键（如 `project`）绑定到函数 `GetProjectName`
4. **使用令牌**：在需要求值的字符串中使用 `{project}` 语法，运行时将自动替换为函数返回值

## C++ 用法

### 头文件引入

```cpp
#include "NamingTokens.h"
```

### 基本用法

创建一个自定义命名令牌子类：

```cpp
// MyNamingTokens.h
#pragma once

#include "CoreMinimal.h"
#include "NamingTokens.h"
#include "MyNamingTokens.generated.h"

UCLASS(Blueprintable)
class MYPROJECT_API UMyNamingTokens : public UNamingTokens
{
    GENERATED_BODY()

public:
    UMyNamingTokens();

    UFUNCTION(BlueprintCallable, Category = "NamingTokens")
    FString GetProjectName() const;

    UFUNCTION(BlueprintCallable, Category = "NamingTokens")
    FString GetBuildVersion() const;
};
```

```cpp
// MyNamingTokens.cpp
#include "MyNamingTokens.h"

UMyNamingTokens::UMyNamingTokens()
{
    // 构造函数中注册令牌
}

FString UMyNamingTokens::GetProjectName() const
{
    return FApp::GetProjectName();
}

FString UMyNamingTokens::GetBuildVersion() const
{
    return FApp::GetBuildVersion();
}
```

### 编辑器专用令牌

```cpp
// MyEditorNamingTokens.h
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityNamingTokens.h"
#include "MyEditorNamingTokens.generated.h"

UCLASS(Blueprintable)
class UMyEditorNamingTokens : public UEditorUtilityNamingTokens
{
    GENERATED_BODY()
    // 编辑器上下文专用的令牌定义
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `4e9e9490` | NamingTokens: Wrap unresolved token keys in {} in warning tooltip | 未解析的令牌键在警告提示中用 {} 包裹 |
| 2026-05-13 | `d8ce6393` | NamingTokens: Fix autocomplete menu to commit on single click. | 修复自动补全菜单单击即可确认选择 |
| 2026-05-12 | `17dd40b9` | NamingTokens: Fix right-click clobbering tokenized text. | 修复右键操作覆盖已令牌化文本的问题 |
| 2026-05-12 | `6bc85b80` | NamingTokens: Add factory and asset definition for Editor Utility Naming Tokens so that it appears i... | 添加 Editor Utility Naming Tokens 的工厂类和资产定义 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 将虚拟制片相关资产迁移到不同的资产分类 |

### 维护评价

- **创建时间**: 2025-01-13，非常新的插件（约 1 年）
- **实验性**: `IsExperimentalVersion=true`，尚未正式稳定
- **最近更新**: 2026 年 5 月有密集更新，主要围绕 UI 体验优化和编辑器资产定义完善
- **活跃维护**: ✅ 活跃开发中，近期有持续功能迭代和 Bug 修复
- **推荐使用**: 适合在虚拟制片或自动化命名工作流中尝试使用，但因处于实验阶段，API 可能发生变化，生产环境需谨慎评估

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/NamingTokens/Tests)