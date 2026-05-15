# Config Settings Toolset

> Toolset for listing, inspecting, and editing Config Settings sections via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 中文名 | 配置设置工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConfigSettingsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset) | |

## 用途

这个插件为 UE5 的 **AI Toolset Registry** 提供了一套操作配置设置（Config Settings）的工具。它将编辑器的 Settings 面板功能抽象为一组标准化的 AI 可调用函数，使 AI 助手能够：

1. **发现设置结构**：列举所有设置容器（Container）、分类（Category）和分区（Section）
2. **检查设置元数据**：获取某个设置分区的 JSON Schema 描述，包括属性类型、描述和约束
3. **读取属性值**：以 JSON 格式读取指定属性的当前值
4. **编辑与保存**：通过 JSON 对象批量设置属性值并保存，或重置为默认值

本质上，它是 UE 设置编辑器（`ISettingsSection`）与 AI 工具集（`UToolsetDefinition`）之间的桥梁，让 AI 代理能够以编程方式管理和修改项目的配置设置。

## 使用场景

- 你需要让 AI 助手自动检查或修改项目的引擎/编辑器设置 → 用 ConfigSettingsToolset
- 你在构建一个自动化配置工具，需要程序化读取和写入 UE 设置 → 用 ConfigSettingsToolset
- 你需要批量重置或迁移项目配置 → 用 ConfigSettingsToolset

> **注意**：此插件的所有函数标记为 `AICallable`（而非 `BlueprintCallable`），面向 AI Toolset Registry 注册使用，不直接出现在蓝图节点列表中。

## 蓝图用法

此插件的函数通过 `UFUNCTION(meta = (AICallable))` 暴露，通过 **AI Toolset Registry** 注册而非传统蓝图调用。以下为函数说明：

### 核心节点

#### 发现（Discovery）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListContainers` | 列举所有已知的设置容器名称（如 "Editor"、"Project"），按字母排序 | `UConfigSettingsToolset` |
| `ListCategories` | 列举指定容器下的所有分类名称，按字母排序 | `UConfigSettingsToolset` |
| `ListSections` | 列举指定容器+分类下的所有分区名称，按字母排序 | `UConfigSettingsToolset` |

#### 查询（Schema & Values）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSectionSchema` | 返回设置分区的 JSON Schema，描述属性名称、类型、描述和约束 | `UConfigSettingsToolset` |
| `GetSectionPropertyValues` | 返回指定属性的当前值，以 JSON 对象形式 | `UConfigSettingsToolset` |

#### 编辑（Editing）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSectionProperties` | 通过 JSON 对象批量设置属性值并保存 | `UConfigSettingsToolset` |
| `SaveSection` | 保存指定分区的设置 | `UConfigSettingsToolset` |
| `ResetSectionToDefaults` | 将指定分区的设置重置为默认值 | `UConfigSettingsToolset` |

### 使用示例

典型 AI 调用流程：

1. **探索设置结构**：先调用 `ListContainers()` 获取 `["Editor", "Project"]`
2. **层层下钻**：调用 `ListCategories("Project")` → `ListSections("Project", "Engine")`
3. **了解分区结构**：调用 `GetSectionSchema("Project", "Engine", "General")` 获取 JSON Schema
4. **读取当前值**：调用 `GetSectionPropertyValues("Project", "Engine", "General", ["bUseRelativePath", ...])`
5. **修改并保存**：调用 `SetSectionProperties("Project", "Engine", "General", '{"bUseRelativePath": true}')`

## C++ 用法

### 头文件引入

```cpp
#include "ConfigSettingsToolset.h"
```

### 基本用法

此插件主要通过 AI Toolset Registry 使用，以下是 C++ 中直接调用静态函数的示例：

```cpp
// 列举所有设置容器
TArray<FString> Containers = UConfigSettingsToolset::ListContainers();
// Containers: ["Editor", "Project"]

// 列举 "Project" 容器下的所有分类
TArray<FString> Categories = UConfigSettingsToolset::ListCategories(TEXT("Project"));
// Categories: ["Engine", "Game", ...]

// 列举 "Project" -> "Engine" 下的所有分区
TArray<FString> Sections = UConfigSettingsToolset::ListSections(TEXT("Project"), TEXT("Engine"));
// Sections: ["General", "Rendering", ...]
```

### 进阶用法

```cpp
// 获取分区的 JSON Schema
FString Schema = UConfigSettingsToolset::GetSectionSchema(
    TEXT("Project"), TEXT("Engine"), TEXT("General"));

// 读取指定属性的当前值
TArray<FString> PropNames = { TEXT("bUseRelativePath"), TEXT("bAllowMatureLanguage") };
FString Values = UConfigSettingsToolset::GetSectionPropertyValues(
    TEXT("Project"), TEXT("Engine"), TEXT("General"), PropNames);
// Values: {"bUseRelativePath": false, "bAllowMatureLanguage": false}

// 批量设置属性并保存
FString NewValues = TEXT(R"({"bUseRelativePath": true})");
bool bSuccess = UConfigSettingsToolset::SetSectionProperties(
    TEXT("Project"), TEXT("Engine"), TEXT("General"), NewValues);

// 重置分区为默认值
UConfigSettingsToolset::ResetSectionToDefaults(
    TEXT("Project"), TEXT("Engine"), TEXT("General"));
```

## Demo 示例

```cpp
// ConfigSettingsDemo.h
#pragma once

#include "CoreMinimal.h"

class FConfigSettingsDemo
{
public:
    static void RunDemo();
};
```

```cpp
// ConfigSettingsDemo.cpp
#include "ConfigSettingsDemo.h"
#include "ConfigSettingsToolset.h"

void FConfigSettingsDemo::RunDemo()
{
    // 1. 发现所有容器
    TArray<FString> Containers = UConfigSettingsToolset::ListContainers();
    UE_LOG(LogTemp, Log, TEXT("Found %d settings containers"), Containers.Num());

    // 2. 遍历容器 → 分类 → 分区的层级结构
    for (const FString& Container : Containers)
    {
        TArray<FString> Categories = UConfigSettingsToolset::ListCategories(Container);
        for (const FString& Category : Categories)
        {
            TArray<FString> Sections = UConfigSettingsToolset::ListSections(Container, Category);
            for (const FString& Section : Sections)
            {
                UE_LOG(LogTemp, Log, TEXT("  %s / %s / %s"), *Container, *Category, *Section);
            }
        }
    }

    // 3. 查询某个分区的 Schema
    FString Schema = UConfigSettingsToolset::GetSectionSchema(
        TEXT("Project"), TEXT("Engine"), TEXT("General"));
    UE_LOG(LogTemp, Log, TEXT("Schema: %s"), *Schema);

    // 4. 读取属性值
    TArray<FString> Props = { TEXT("bUseRelativePath") };
    FString Values = UConfigSettingsToolset::GetSectionPropertyValues(
        TEXT("Project"), TEXT("Engine"), TEXT("General"), Props);
    UE_LOG(LogTemp, Log, TEXT("Values: %s"), *Values);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI Toolset Registry 基础设施，提供 `UToolsetDefinition` 基类和工具注册机制 |
| `Settings` / `SettingsEditor` | UE 设置编辑器后端，提供 `ISettingsSection` 接口用于访问配置设置 |

> 注：此插件的 Build.cs 未在提供的文件列表中，依赖关系基于源码中的 `UToolsetDefinition` 基类和 `ISettingsSection` 使用推断。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `02299b89` | [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties | 修复设置对象属性变更时的容器通知机制 |
| 2026-05-13 | `978a5c16` | [Backout] - CL53875137 | 回退 CL53875137 的改动 |
| 2026-05-13 | `e58befb6` | [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties | 首次尝试修复容器变更通知（后被回退） |
| 2026-05-12 | `4c45fb27` | [ConfigSettingsToolset] Fix round-trip test for read-only config on Horde | 修复在 Horde CI 环境下只读配置的往返测试 |
| 2026-05-12 | `b0a44cc5` | Add ConfigSettingsToolset plugin | 初始提交，新增 ConfigSettingsToolset 插件 |

### 维护评价

- **创建时间**：2026-05-12，插件非常新（不到一个月）
- **更新频率**：创建后 2 天内有 5 次提交，处于密集开发阶段
- **维护状态**：**活跃开发中** — 初始提交后立即进入测试修复和依赖插件（ToolsetRegistry）的联动修复
- **实验性标记**：`IsExperimentalVersion=true`，且位于 `Experimental` 目录，尚未稳定
- **已知限制**：部分设置分区使用自定义 Widget 而非标准设置对象，`GetSectionSchema` 和 `GetSectionPropertyValues` 对这些分区会报错

⚠️ **警告**：此插件为实验性（Experimental），API 可能在后续版本中发生重大变更。建议仅在内部工具开发中使用，暂不推荐用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ConfigSettingsToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)（前置依赖）