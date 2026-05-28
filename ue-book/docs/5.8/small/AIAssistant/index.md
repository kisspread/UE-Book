# AI Assistant

> 

| 属性 | 值 |
|---|---|
| 中文名 | AI 助手 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AIAssistant` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AIAssistant) | |

## 用途

AI Assistant 是 Epic 为 Unreal Editor 打造的**内嵌式 AI 对话助手**（Epic Developer Assistant / EDA）。它在编辑器中嵌入一个基于 Web 的对话界面，通过 JavaScript 桥接与 Epic 后端 AI 服务通信，让开发者可以用自然语言向 AI 提问或下达指令。

核心解决的问题：
- **编辑器内知识获取**：无需离开编辑器即可向 AI 询问关于当前 UI、工具、资产的上下文相关问题
- **上下文感知查询**：AI 可以感知当前光标所在的 Slate 控件、正在编辑的资产、选中的图节点等，提供精确的回答
- **工具调用（Tool Calling）**：AI 可以通过工具调用系统读取项目信息、修改文件，甚至操作撤销缓冲区
- **文件变更管理**：AI 修改的文件会被锁定并要求用户审批（接受/拒绝），防止意外修改

## 使用场景

- 你在编辑器中看到一个陌生的 UI 控件 → 光标悬停后按快捷键，AI 会解释该控件的用途
- 你正在编辑蓝图资产 → AI 助手可以感知当前正在编辑的蓝图和图节点，回答相关问题
- 你想了解某个面板或工具的功能 → 对着 UI 元素触发 AI 查询，获得结构化的上下文回答
- 你需要 AI 帮你修改项目文件 → AI 通过工具调用修改文件，你审批后才生效

## 蓝图用法

该插件主要面向编辑器扩展开发，暴露了少量蓝图和 JavaScript 可调用的接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetProjectContext` | 获取当前项目和用户的上下文信息（引擎信息、项目描述、用户偏好） | `UAIAssistantToolset` |
| `GetDockedContext` | 获取助手停靠位置的上下文（当前编辑的资产、图、选中节点） | `UAIAssistantToolset` |
| `ShowContextMenuViaJavaScript` | 通过 JavaScript 显示上下文菜单 | `UAIAssistantSubsystem` |

### 用户/项目设置

AI 助手提供了两个开发者设置，可在编辑器设置面板中配置：

- **用户上下文** (`UAIAssistantContextUser`)：描述你的角色、偏好、当前目标等信息，AI 会自动参考
- **项目上下文** (`UAIAssistantContextProject`)：描述项目类型、命名规范、美术风格等信息，AI 会自动参考

### 使用示例（蓝图描述）

AI 助手本身不提供直接的蓝图节点供游戏逻辑使用。它的主要交互方式是：

1. **编辑器菜单**：通过 `Window > AI Assistant` 菜单项打开 AI 助手面板
2. **快捷键**：通过输入处理器全局捕获快捷键（Summon 命令）
3. **光标查询**：将光标放在任意 UI 元素上，触发 Slate 查询命令，AI 会自动分析上下文并回答
4. **状态栏抽屉**：通过编辑器状态栏按钮召唤 AI 助手面板

## C++ 用法

### 头文件引入

```cpp
#include "AIAssistantSubsystem.h"
#include "AIAssistantToolset.h"
```

### 基本用法：获取 AI 助手子系统

```cpp
// 获取 AI 助手子系统实例
auto [Subsystem, Error] = UAIAssistantSubsystem::Get(TEXT("获取AI助手"));
if (!Error.IsEmpty())
{
    UE_LOG(LogTemp, Warning, TEXT("AI Assistant 不可用: %s"), *Error);
    return;
}

// 获取 Web 浏览器控件（用于自定义交互）
TSharedPtr<SAIAssistantWebBrowser> WebBrowser = UAIAssistantSubsystem::GetAIAssistantWebBrowserWidget();
```

*来源：`Source/AIAssistant/Private/AIAssistantSubsystem.h`*

### 基本用法：定义 AI 可调用的工具

AI 助手通过 `UToolsetDefinition` 的子类注册工具，使用 `UFUNCTION(meta=(AICallable))` 宏标记 AI 可调用的函数：

```cpp
UCLASS(BlueprintType, Hidden)
class UMyCustomToolset : public UToolsetDefinition
{
    GENERATED_BODY()
public:
    // AI 可以调用此函数获取自定义信息
    UFUNCTION(meta = (AICallable), Category = "My Tools")
    static FMyCustomData GetCustomData();
};
```

*来源：`Source/AIAssistant/Private/AIAssistantToolset.h`*

### 进阶用法：对话管理与 WebApi

AI 助手的对话管理通过 `FWebApi` 和 `FWebApplication` 进行：

```cpp
// 创建新对话
WebApplication->CreateConversation();

// 向对话添加用户消息
FAddMessageToConversationOptions Options;
Options.Message.MessageRole = EMessageRole::User;
Options.Message.MessageContent.Add(FMessageContent{
    .ContentType = EMessageContentType::Text,
    .Content = FMessageContentVariant(TInPlaceType<FTextMessageContent>(), FTextMessageContent{.Text = TEXT("Hello")})
});
WebApplication->AddUserMessageToConversation(MoveTemp(Options));

// 更新待处理文件列表（工具调用修改的文件）
FUpdatePendingFileListOptions FileOptions;
FileOptions.Files.Add(FPendingFileMetadata{
    .DisplayName = TEXT("MyAsset.uasset"),
    .FullPath = TEXT("/Game/MyAsset"),
    .Status = EPendingFileStatus::Modified
});
WebApplication->UpdatePendingFileList(MoveTemp(FileOptions));
```

*来源：`Source/AIAssistant/Private/AIAssistantWebApplication.h`, `Source/AIAssistant/Private/AIAssistantTypes.h`*

## Demo 示例

以下展示如何在编辑器工具中集成 AI 助手的上下文感知功能：

```cpp
// MyAIAssistantToolset.h
#pragma once

#include "CoreMinimal.h"
#include "ToolsetDefinition.h"
#include "MyAIAssistantToolset.generated.h"

USTRUCT(BlueprintType)
struct FMyProjectInfo
{
    GENERATED_USTRUCT_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "AI")
    FString ProjectName;

    UPROPERTY(BlueprintReadOnly, Category = "AI")
    FString CurrentLevel;

    UPROPERTY(BlueprintReadOnly, Category = "AI")
    int32 ActorCount;
};

UCLASS(BlueprintType, Hidden)
class UMyAIAssistantToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 让 AI 获取当前关卡的基本信息
    UFUNCTION(meta = (AICallable), Category = "Project Info")
    static FMyProjectInfo GetProjectInfo();
};
```

```cpp
// MyAIAssistantToolset.cpp
#include "MyAIAssistantToolset.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

FMyProjectInfo UMyAIAssistantToolset::GetProjectInfo()
{
    FMyProjectInfo Info;
    Info.ProjectName = FApp::GetProjectName();

    if (UWorld* World = GEditor->GetEditorWorldContext().World())
    {
        Info.CurrentLevel = World->GetMapName();
        
        // 统计当前关卡中的 Actor 数量
        TArray<AActor*> AllActors;
        UGameplayStatics::GetAllActorsOfClass(World, AActor::StaticClass(), AllActors);
        Info.ActorCount = AllActors.Num();
    }

    return Info;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | Python 脚本支持（可能用于工具链集成） |
| `EditorScriptingUtilities` | 编辑器脚本工具函数 |
| `ToolsetRegistry` | 工具集注册系统（`UToolsetDefinition` 基类、工具调用架构） |

此外，插件内部隐式依赖 WebBrowser（嵌入式 Web 浏览器）和 Slate UI 系统。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-15 | `1afb16b2` | Fix toolset category name. | 修复工具集分类名称错误 |
| 2026-05-12 | `cbbb4f89` | [AIAssistant] Flip module `Type` from `EditorNoCommandlet` to `Editor`. | 将模块类型从 EditorNoCommandlet 改为 Editor |
| 2026-04-29 | `f01e07be` | LLM often messes up class paths the first time, so clarify expected behavior in engine context. | 优化 AI 对引擎中类路径的理解行为 |
| 2026-04-28 | `ce5526cc` | Add support for disabling toolsets and tools by name. | 新增按名称禁用工具集和工具的功能 |
| 2026-04-24 | `0cd2b3ea` | [Backout] - CL53139837 | 回退之前的某次变更 |

### 维护评价

- **活跃维护中**：该插件创建于 2025 年 8 月，至今不足 1 年，近期（2026 年 4-5 月）仍有持续的功能更新和修复
- **实验性状态**：`.uplugin` 标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需要手动启用
- **快速迭代中**：从 commit 记录来看，这是一个正在积极开发的新功能，API 和架构可能频繁变动
- **推荐**：适合对 Epic 最新 AI 集成技术感兴趣的开发者了解和试用，但不建议在生产环境中重度依赖，因为 API 可能不稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AIAssistant)
- 官方文档：暂无（实验性插件）