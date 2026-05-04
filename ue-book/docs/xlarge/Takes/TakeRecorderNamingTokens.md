# Take Recorder Naming Tokens

> A suite of tools and interfaces designed for recording, reviewing and playing back takes in a virtual production environment.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `CacheTrackRecorder` (Runtime), `TakeMovieScene` (Runtime), `TakeRecorder` (Runtime), `TakeRecorderNamingTokens` (Runtime), `TakeRecorderSources` (Runtime), `TakesCore` (Runtime), `TakeSequencer` (Runtime), `TakeTrackRecorders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes) | |

## 用途

`Take Recorder Naming Tokens` 模块是 **Take Recorder** 插件的一个子模块，专门负责处理录制过程中的**资产命名令牌**。它解决的核心问题是：在虚拟制片中录制大量镜头（Take）时，如何自动、一致且可预测地为生成的资产（如序列、动画、音频文件等）命名。

该模块提供了一个标准化的命名空间（`tr`），允许用户在录制配置中使用特定的令牌（例如 `%{tr.SequenceName}`），这些令牌会在录制开始时被动态替换为实际的值（如当前序列的名称、时间码、日期等）。这避免了手动输入复杂的命名规则，减少了人为错误，并确保了项目资产命名的统一性，便于后期管理和查找。

## 使用场景

- **虚拟制片现场录制**：在 LED Volume 或绿幕前进行多机位、多角色的实时拍摄时，需要为每个镜头的录制数据（动画、音频、视频代理）自动生成包含场景、镜头、Take 编号等信息的文件名。
- **批量处理与自动化流程**：当需要将录制的 Take 数据导入到后期制作流程（如 DaVinci Resolve, Nuke）时，标准化的命名是自动化脚本可靠运行的基础。
- **团队协作**：确保不同艺术家或部门在录制和引用资产时，使用的是同一套命名规则，避免混淆。

## 蓝图用法

该模块主要通过 `Take Recorder` 的主界面和配置资产进行交互，其核心功能集成在录制流程中。开发者可以通过蓝图访问与命名令牌相关的子系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Take Recorder Namespace` | 获取 Take Recorder 命名令牌使用的命名空间字符串（`tr`）。 | `ITakeRecorderNamingTokensModule` (静态函数) |
| `Set Naming Tokens` | 在 `TakeMetaData` 或录制设置中配置要使用的命名令牌字符串。 | `UTakeMetaData` / `UTakeRecorderSubsystem` |
| `Resolve Naming Tokens` | 将包含令牌的字符串解析为最终的实际名称。 | `UTakeRecorderSubsystem` / `UNamingTokensEngineSubsystem` |

### 使用示例（蓝图描述）

1.  **配置命名令牌**：在 `TakeRecorder` 面板的“设置”中，找到“命名”或“输出”相关选项。在“文件名格式”或类似字段中，输入包含令牌的字符串，例如：`%{tr.SequenceName}_%{tr.TakeNumber}`。
2.  **运行时解析**：当开始录制时，`Take Recorder` 系统会自动调用 `UNamingTokensEngineSubsystem` 来解析该字符串。蓝图中通常不需要手动调用解析，除非你在构建自定义的录制流程。
3.  **自定义集成**：如果你需要在其他地方（如自定义的资产导入工具）使用相同的命名规则，可以获取 `UNamingTokensEngineSubsystem`，然后调用其 `ResolveStringWithTokens` 函数，并传入包含 `tr.` 前缀令牌的字符串。

## C++ 用法

### 头文件引入

```cpp
#include "ITakeRecorderNamingTokensModule.h"
#include "NamingTokensEngineSubsystem.h"
```

### 基本用法

获取模块提供的静态命名空间字符串，用于构建自定义的令牌键。

```cpp
// 来源: Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderNamingTokens/Public/ITakeRecorderNamingTokensModule.h
FString TakeRecorderNamespace = ITakeRecorderNamingTokensModule::GetTakeRecorderNamespace();
// TakeRecorderNamespace 的值为 “tr”

// 构建一个完整的令牌键，例如用于自定义的命名规则
FString MyTokenKey = FString::Printf(TEXT("%s.MyCustomValue"), *TakeRecorderNamespace);
// MyTokenKey 的值为 “tr.MyCustomValue”
```

### 进阶用法

在自定义的录制或后处理逻辑中，集成命名令牌解析功能。这需要依赖 `NamingTokens` 模块。

```cpp
// 假设在某个 UObject 或 Actor 的函数中
void AMyRecordingHelper::GenerateAssetName(const FString& TemplateName)
{
    // 获取命名令牌子系统
    UNamingTokensEngineSubsystem* NamingTokensSubsystem = GEngine->GetEngineSubsystem<UNamingTokensEngineSubsystem>();
    if (NamingTokensSubsystem)
    {
        // 解析包含令牌的模板字符串
        // TemplateName 可能是 “Shot_%{tr.ShotNumber}_%{tr.Date}”
        FString ResolvedName = NamingTokensSubsystem->ResolveStringWithTokens(TemplateName, GetWorld());
        
        // 使用解析后的名称
        UE_LOG(LogTemp, Log, TEXT("Resolved asset name: %s"), *ResolvedName);
        // ... 后续创建资产或文件的逻辑
    }
}
```

## Demo 示例

一个最小示例，演示如何在 C++ 中获取命名空间并模拟一个简单的令牌解析流程。

**MyNamingTokenDemo.h**
```cpp
// MyNamingTokenDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyNamingTokenDemo.generated.h"

UCLASS(BlueprintType)
class UMyNamingTokenDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 演示如何获取 Take Recorder 的命名空间 */
    UFUNCTION(BlueprintCallable, Category = "Naming Tokens Demo")
    static FString GetTakeRecorderNamespace();

    /** 演示一个简单的、不依赖子系统的令牌替换（仅用于教学） */
    UFUNCTION(BlueprintCallable, Category = "Naming Tokens Demo")
    static FString SimpleResolveDemo(const FString& TemplateString, const FString& SequenceName, int32 TakeNumber);
};
```

**MyNamingTokenDemo.cpp**
```cpp
// MyNamingTokenDemo.cpp
#include "MyNamingTokenDemo.h"
#include "ITakeRecorderNamingTokensModule.h"

FString UMyNamingTokenDemo::GetTakeRecorderNamespace()
{
    return ITakeRecorderNamingTokensModule::GetTakeRecorderNamespace();
}

FString UMyNamingTokenDemo::SimpleResolveDemo(const FString& TemplateString, const FString& SequenceName, int32 TakeNumber)
{
    FString Result = TemplateString;
    const FString Namespace = GetTakeRecorderNamespace();
    
    // 手动替换两个示例令牌
    Result.ReplaceInline(*FString::Printf(TEXT("%%{%s.SequenceName}"), *Namespace), *SequenceName);
    Result.ReplaceInline(*FString::Printf(TEXT("%%{%s.TakeNumber}"), *Namespace), *FString::FromInt(TakeNumber));
    
    return Result;
}
```

## 模块依赖

从 `TakeRecorderNamingTokens.Build.cs` 分析，该模块依赖于核心的命名令牌系统。

| 模块 | 用途 |
|---|---|
| `NamingTokens` | 提供命名令牌的核心框架、子系统和解析引擎。 |
| `TakesCore` | 提供 Take 录制的核心数据结构和元数据（如 `UTakeMetaData`），命名令牌常用于填充这些数据。 |

## 维护状态

### 近期更新

```
- a36dfd6d7127 NamingTokens: Add auto complete suggestion dropdown to UMG widget.
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- a16a9f6c27e0 TakeRecorder: Improve object reference management in subsystem and tokens. Clear cached TakeMetaData from the editor subsystem if user is force deleting the contained level sequence. This allows users to safely delete a level sequence which has just been recorded.
```

**解读**：
1.  最近的提交为命名令牌的 UMG 控件添加了自动完成建议下拉框，提升了用户体验。
2.  代码维护性更新，添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏。
3.  修复了一个重要的对象引用管理问题，增强了删除已录制序列时的稳定性。

### 维护评价

- **创建时间**：2019年，是虚拟制作工具链的早期组成部分。
- **活跃度**：**活跃维护中**。最近的提交（2024年）包含功能增强（自动完成）和重要的 Bug 修复，表明 Epic 仍在积极改进此模块。
- **稳定性**：作为虚拟制作核心流程的一部分，经过了大量项目验证，相对稳定。
- **推荐度**：**强烈推荐**。如果你在项目中使用 `Take Recorder` 进行任何形式的录制，那么理解和使用其命名令牌功能是管理资产命名的最佳实践。该模块是 `Take Recorder` 不可或缺的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Source/TakeRecorderNamingTokens)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/take-recorder-in-unreal-engine/) (Take Recorder 整体文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/Takes/Tests) (Takes 插件的测试目录)