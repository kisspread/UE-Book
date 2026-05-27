# AI Assistant

> 

| 属性 | 值 |
|---|---|
| 中文名 | AI 助手 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Web 资源） |
| 模块 | `AIAssistant` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AIAssistant) | |

## 用途

这是 Epic Developer Assistant（EDA）的 Unreal Editor 集成插件，提供一个嵌入在编辑器中的 AI 聊天助手面板。

该插件的核心架构是：在编辑器内嵌一个 WebBrowser 控件，通过 JavaScript 与 Epic 后端 AI 服务通信，实现对话管理、工具调用（Tool Call）和文件变更跟踪。助手可以根据用户的自然语言描述，调用注册的工具集（Toolset）来检查项目上下文、编辑器状态，甚至生成/修改资产文件。生成的文件变更需要用户明确审批后才能生效。

**为什么存在**：为 Unreal 开发者提供一个集成在编辑器内的 AI 编程助手，支持上下文感知（当前编辑的资产、选中的节点、项目设置等），能够回答问题并执行项目操作。

## 使用场景

- 你在编辑器中遇到不熟悉的功能或面板 → 选中相关 UI 元素后查询 AI 助手，获得该功能的说明
- 你需要基于当前项目上下文获取编程建议 → AI 助手会自动获取项目信息、用户角色、编辑器状态作为上下文
- 你想让 AI 辅助生成代码或资产文件 → AI 通过 Tool Call 机制创建文件，你可以在文件变更列表中审批或拒绝
- 你使用 UEFN 模式开发 → 插件支持 UE/UEFN 双模式切换

## 蓝图用法

该插件主要面向编辑器内部使用，Blueprint API 较少。以下是从源码中提取的可用蓝图/编辑器节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetProjectContext` | 获取当前项目和用户的上下文信息（游戏类型、命名规范等） | `UAIAssistantToolset` |
| `GetDockedContext` | 获取助手停靠面板的上下文（当前编辑的资产、图表、选中节点） | `UAIAssistantToolset` |
| `ShowContextMenuViaJavaScript` | 通过 JavaScript 显示上下文菜单 | `UAIAssistantSubsystem` |

### 编辑器设置

插件提供了两个编辑器设置面板，可在 **编辑 → 编辑器偏好设置** 中找到：

**用户上下文** (`UAIAssistantContextUser`)：
- **Prompt** 字段：用于描述你的角色、偏好、当前目标等信息，AI 助手会自动在对话中考虑这些信息

**项目上下文** (`UAIAssistantContextProject`)：
- **Prompt** 字段：用于描述项目信息，如游戏类型、命名规范、美术风格等

## C++ 用法

该插件主要是编辑器内部组件，没有面向外部开发者的 BlueprintCallable 公共 API。以下展示如何与插件的内部系统交互：

### 头文件引入

```cpp
#include "AIAssistant.h"
```

### 基本用法 — 获取子系统

```cpp
// 获取 AI 助手子系统（来源：AIAssistantSubsystem.h）
#include "AIAssistantSubsystem.h"

// 方式一：通过编辑器子系统获取
UAIAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAIAssistantSubsystem>();

// 方式二：通过静态方法获取（带错误处理）
auto Result = UAIAssistantSubsystem::Get(TEXT("Failed to get AI Assistant subsystem"));
if (Result.HasValue())
{
    UAIAssistantSubsystem* Assistant = Result.GetValue();
    TSharedPtr<SAIAssistantWebBrowser> Browser = Assistant->GetAIAssistantWebBrowserWidget();
}
```

### 基本用法 — 查询 Slate 控件

```cpp
// 查询鼠标下方的 Slate 控件（来源：AIAssistantSlateQuerier.h）
#include "AIAssistantSlateQuerier.h"

// 获取鼠标下方的控件路径
FWidgetPath WidgetPath = UE::AIAssistant::SlateQuerier::GetWidgetPathUnderCursor();

// 向 AI 助手发送关于该控件的查询
UE::AIAssistant::SlateQuerier::QueryAIAssistantAboutSlateWidget(WidgetPath);
```

### 进阶用法 — 文件锁定管理

```cpp
// 文件锁定管理（来源：AIAssistantFileLockManager.h）
#include "AIAssistantFileLockManager.h"

// 锁定一个文件，使其在编辑器中以只读模式打开
UE::AIAssistant::FFileLockManager::AddLockedFile(TEXT("/Game/MyAsset"));

// 检查文件是否被锁定
bool bLocked = UE::AIAssistant::FFileLockManager::IsFileLocked(TEXT("/Game/MyAsset"));

// 获取所有被锁定的文件
TSet<FString> LockedFiles = UE::AIAssistant::FFileLockManager::GetLockedFiles();

// 解锁文件
UE::AIAssistant::FFileLockManager::RemoveLockedFile(TEXT("/Game/MyAsset"));

// 清除所有锁定
UE::AIAssistant::FFileLockManager::ClearLockedFiles();
```

### 进阶用法 — 事务缓冲区管理

```cpp
// 事务缓冲区管理（来源：AIAssistantTransactionBufferManager.h）
#include "AIAssistantTransactionBufferManager.h"

// 创建独立的事务缓冲区（用于 AI 操作的撤销）
UTransBuffer* Buffer = UE::AIAssistant::FTransactionBufferManager::GetOrCreateTransactionBuffer(
    TEXT("AIAssistantBuffer"));

// 用 AI 事务缓冲区覆盖全局撤销缓冲区
UE::AIAssistant::FTransactionBufferManager::SetOverrideBuffer(Buffer);

// ... 执行 AI 操作 ...

// 从撤销栈中提取被修改的文件路径
TSet<FString> ModifiedFiles = UE::AIAssistant::FTransactionBufferManager::GetFilenamesFromUndoStack(Buffer);

// 恢复全局撤销缓冲区
UE::AIAssistant::FTransactionBufferManager::RestoreGlobalBuffer();

// 销毁事务缓冲区
UE::AIAssistant::FTransactionBufferManager::DestroyTransactionBuffer(TEXT("AIAssistantBuffer"));
```

## Demo 示例

以下展示如何在编辑器插件中查询 AI 助手关于当前鼠标位置的 Slate 控件：

```cpp
// MyWidgetQueryExample.h
#pragma once

#include "CoreMinimal.h"

class FMyWidgetQueryExample
{
public:
    /** 向 AI 助手查询鼠标当前所在的 Slate 控件信息 */
    static void QueryWidgetUnderCursor();
};
```

```cpp
// MyWidgetQueryExample.cpp
#include "MyWidgetQueryExample.h"

#include "AIAssistantSubsystem.h"
#include "AIAssistantSlateQuerier.h"

void FMyWidgetQueryExample::QueryWidgetUnderCursor()
{
    // 1. 确保 AI 助手子系统可用
    auto SubsystemResult = UAIAssistantSubsystem::Get(TEXT("Widget query failed"));
    if (!SubsystemResult.HasValue())
    {
        UE_LOG(LogTemp, Warning, TEXT("AI Assistant subsystem not available"));
        return;
    }

    // 2. 获取鼠标下方的控件路径
    FWidgetPath WidgetPath = UE::AIAssistant::SlateQuerier::GetWidgetPathUnderCursor();
    if (!WidgetPath.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No widget found under cursor"));
        return;
    }

    // 3. 发送查询到 AI 助手
    UE::AIAssistant::SlateQuerier::QueryAIAssistantAboutSlateWidget(WidgetPath);
    UE_LOG(LogTemp, Log, TEXT("Query sent to AI Assistant about widget under cursor"));
}
```

## 模块依赖

该插件依赖以下插件（在 .uplugin 的 Plugins 字段中声明）：

| 插件 | 用途 |
|---|---|
| `PythonScriptPlugin` | Python 脚本执行支持 |
| `EditorScriptingUtilities` | 编辑器脚本工具函数 |
| `ToolsetRegistry` | 工具集注册系统（用于向 AI 暴露可调用的工具） |

模块级依赖（从 Build.cs 推断）：无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-15 | `1afb16b2` | Fix toolset category name. | 修复工具集分类名称显示错误 |
| 2026-05-12 | `cbbb4f89` | [AIAssistant] Flip module `Type` from `EditorNoCommandlet` to `Editor`. | 将模块类型从 EditorNoCommandlet 改为 Editor |
| 2026-04-29 | `f01e07be` | LLM often messes up class paths the first time, so clarify expected behavior in engine context. | 在引擎上下文中澄清 LLM 常见的类路径错误行为 |
| 2026-04-28 | `ce5526cc` | Add support for disabling toolsets and tools by name. | 新增按名称禁用工具集和工具的功能 |
| 2026-04-24 | `0cd2b3ea` | [Backout] - CL53139837 | 回退一个之前的提交 |

### 维护评价

**活跃维护中** 🟢

- **创建时间**：2025 年 8 月，非常年轻的插件
- **更新频率**：最近一个月有多次功能性更新，开发活跃
- **实验性状态**：标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **NoRedist**：标记为 `NoRedist=true`，说明包含不可重新分发的内容
- **活跃迹象**：最近的 commit 涉及功能新增（工具集禁用）、架构调整（模块类型修改）和 LLM 行为优化，表明正在积极迭代

**注意事项**：
- 这是一个实验性插件，API 和行为可能在后续版本中发生变化
- 需要网络连接以与 Epic 后端 AI 服务通信
- 依赖 `ToolsetRegistry` 插件，需确保该插件也可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AIAssistant)