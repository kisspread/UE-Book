# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频事件资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🏛️ 文物（约 -1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个面向音频设计师的**高级音频内容创作和播放框架**。它旨在解决复杂音频事件管理的问题，允许开发者通过一个可视化的编辑器来定义、组织和预览音频事件及其相关动作，而不是在代码中硬编码复杂的音频播放逻辑。

它与引擎内置的简单音频播放系统不同，提供了一个结构化的方式，将音频事件（Event）与一个或多个要执行的动作（Action，例如播放声音、设置参数）关联起来，并支持参数化绑定，使得音频系统可以对外部游戏状态做出响应。

## 使用场景

-   你需要为一个大型游戏创建复杂的、数据驱动的音频系统，其中包含数百个需要根据游戏逻辑触发的不同音效。
-   你希望在编辑器内通过可视化界面快速创建、测试和调试音频事件，而无需频繁运行游戏。
-   你的音频事件需要接收来自游戏对象（如角色、环境）的参数（如速度、距离），并根据这些参数动态调整播放效果。

## 蓝图用法

Subsonic 主要提供**编辑器端**的功能，用于创建和管理音频资产（`USubsonicEventCollection`）。它的蓝图可用 API 主要集中在运行时播放这些创建好的音频事件集合。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Audition` | 在编辑器中预览播放指定的音频事件。 | `FEventCollectionEditorCommands` (命令) |
| `Stop Audition` | 停止编辑器中正在预览的音频播放。 | `FEventCollectionEditorCommands` (命令) |
| `Toggle Audition` | 切换编辑器音频预览的播放/停止状态。 | `FEventCollectionEditorCommands` (命令) |

**使用示例（蓝图描述）：**
1.  在“内容浏览器”中，右键创建 `Subsonic Event Collection` 资产。
2.  双击该资产，打开专用的“Subsonic Event Collection Editor”窗口。
3.  在编辑器中，使用工具栏上的播放按钮（`Start Audition` / `Stop Audition`）来预览定义好的音频事件。

## C++ 用法

Subsonic 的 C++ 用法主要体现在两个层面：1) 扩展编辑器，处理自定义资产；2) 在运行时加载和执行音频事件集合。

### 头文件引入

```cpp
#include "SubsonicEventCollection.h" // 核心资产类
#include "SubsonicEditorSubsystem.h" // 编辑器子系统，用于访问注册的类型
```

### 基本用法

以下代码演示了如何在 C++ 中访问 `USubsonicEditorSubsystem` 并遍历注册的音频动作类型。
*（示例基于 `SubsonicEditorSubsystem.h` 推断）*

```cpp
// 获取编辑器子系统实例
USubsonicEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
if (EditorSubsystem)
{
    // 遍历所有注册的音频动作结构体类型
    EditorSubsystem->ForEachActionStruct([](const UScriptStruct& Struct)
    {
        UE_LOG(LogTemp, Log, TEXT("Found Subsonic Action Struct: %s"), *Struct.GetName());
    });
}
```

### 进阶用法

在自定义编辑器工具中，可能需要集成 Subsonic 的事件集合。以下代码展示了如何初始化并打开 `FEventCollectionEditor`。
*（示例基于 `SubsonicEventCollectionEditor.h` 推断）*

```cpp
// 假设你已经有一个 USubsonicEventCollection* 指针 EventCollectionAsset
if (EventCollectionAsset)
{
    // 使用编辑器模块的功能来打开资产
    FAssetEditorManager::Get().OpenEditorForAsset(EventCollectionAsset);
    // 或者更直接地使用 FEventCollectionEditor::Init
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何通过子系统与 Subsonic 编辑器交互。

**头文件 (MySubsonicIntegration.h):**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MySubsonicIntegration.generated.h"

UCLASS()
class UMySubsonicIntegrationSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    void LogAvailableAudioActions();
};
```

**源文件 (MySubsonicIntegration.cpp):**
```cpp
#include "MySubsonicIntegration.h"
#include "SubsonicEditorSubsystem.h" // 依赖 SubsonicEditor 模块

void UMySubsonicIntegrationSubsystem::LogAvailableAudioActions()
{
    // 获取 Subsonic 的编辑器子系统
    USubsonicEditorSubsystem* SubsonicSubsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
    if (!SubsonicSubsystem)
    {
        UE_LOG(LogTemp, Warning, TEXT("Subsonic Editor Subsystem not available."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("=== Available Subsonic Audio Actions ==="));
    SubsonicSubsystem->ForEachActionStruct([](const UScriptStruct& Struct)
    {
        UE_LOG(LogTemp, Log, TEXT("- %s"), *Struct.GetName());
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | 定义核心数据结构（如事件、动作句柄），是其他模块的基础。 |
| `SubsonicEditor` | 提供编辑器 UI、资产工厂、自定义细节面板等，用于创作音频内容。 |
| `SubsonicEngine` | 提供运行时音频事件集合的执行器（Executor）。 |
| `AudioWidgets` | 用于构建编辑器中的音频相关 UI 控件（来自 `SubsonicSlateStyle` 的父样式）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复合并错误，撤销对Subsonic订阅系统的意外修改，并应用最小化的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与FSoundWaveData API废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静音PVS（静态分析）警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“新增”菜单中集成音频相关菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移到UE_LOGF。 |

### 维护评价

-   **创建时间**：插件于 2026 年 1 月创建，**数据异常**（当前为 2025 年），可能为测试分支或数据错误。
-   **活跃度**：从提交记录看，近期（2026年4-5月）有更新，但主要是集成、合并修复和编译器警告处理，**未见核心功能更新**。
-   **状态**：插件被明确标记为 `IsExperimentalVersion = true`，且位于 `Experimental` 目录，属于**实验性功能**。
-   **风险与建议**：插件 API **没有向后兼容性保证**。目前的更新集中在维护而非新功能。**仅推荐用于研究、原型开发或对音频工作流有强定制需求的项目**，不建议用于需要长期稳定支持的生产环境。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
-   官方文档（无）
-   测试用例（见 `SubsonicEngineTest` 模块）