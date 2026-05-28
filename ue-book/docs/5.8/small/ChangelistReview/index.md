# Changelist Reviews

> Review source control changelists

| 属性 | 值 |
|---|---|
| 中文名 | 变更列表审查 |
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChangelistReview` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-11-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ChangelistReview) | |

## 用途

该插件提供了一个集成在编辑器内的变更列表（Changelist）审查工具。它解决的核心问题是让开发者能够直接在 Unreal Editor 中查看、比较和评审版本控制系统（主要是 Perforce）中的变更列表。它不仅仅是一个简单的列表查看器，更是一个集成了差异比较、资产浏览和协作评论（通过 Swarm API）功能的综合审查平台，允许团队成员对代码和资产的变更进行评审和讨论。

## 使用场景

- 你正在使用 Perforce 进行版本控制，并希望直接在编辑器内审查其他开发者提交的变更列表（CL）。
- 你准备提交自己的一批变更，在提交前希望更直观地查看所有修改的文件，并一键进行差异对比。
- 你需要查看某个特定 CL 中包含了哪些资产、源代码的改动，以及这些改动的状态（添加、编辑、删除等）。
- 团队使用 Perforce Swarm 进行代码审查，你需要在编辑器中直接查看和回复审查评论，而无需切换到浏览器。

## 蓝图用法

该插件主要通过其模块接口 `FChangelistReviewModule` 暴露功能。由于其核心是一个 Slate UI 控件，蓝图可直接调用的节点有限，主要集中在打开审查工具和加载指定变更列表。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `显示审查标签页` | 在编辑器中打开“变更列表审查”停靠标签页。 | `FChangelistReviewModule` |
| `打开变更列表审查` | 打开审查工具并尝试加载指定编号的变更列表。如果工具未打开则会先打开。返回 `true` 表示成功触发加载流程。 | `FChangelistReviewModule` |

### 使用示例（蓝图描述）

1.  **打开审查窗口**：调用 `FChangelistReviewModule::ShowReviewTab` 函数。这将在编辑器布局中创建一个名为“Changelist Review”的停靠窗口。
2.  **加载特定变更列表**：调用 `FChangelistReviewModule::OpenChangelistReview` 函数，并传入变更列表的编号字符串（如 `123456`）。函数会自动显示审查窗口（如果尚未显示），然后开始从源代码控制下载并展示该变更列表的详细信息。

## C++ 用法

插件主要通过 `FChangelistReviewModule` 模块类进行操作。`SSourceControlReview` 是核心 UI 控件，但通常由模块管理。

### 头文件引入

```cpp
#include "ChangelistReviewModule.h"
```

### 基本用法

**显示或切换到审查工具标签页**。
```cpp
// 获取模块单例
FChangelistReviewModule& ReviewModule = FChangelistReviewModule::Get();

// 显示（或激活已存在的）审查标签页
ReviewModule.ShowReviewTab();
```

**编程方式打开并加载一个变更列表**。
```cpp
FChangelistReviewModule& ReviewModule = FChangelistReviewModule::Get();

// 检查是否可以显示标签页（例如，编辑器是否完全启动）
if (ReviewModule.CanShowReviewTab())
{
    // 尝试打开编号为 “12345” 的变更列表
    bool bSuccessfullyTriggeredLoad = ReviewModule.OpenChangelistReview(TEXT("12345"));
    if (!bSuccessfullyTriggeredLoad)
    {
        UE_LOG(LogTemp, Warning, TEXT("无法打开变更列表审查工具。"));
    }
}
```

### 进阶用法

**获取当前活动的审查控件以操作其内部功能**。
```cpp
// 通过模块获取当前活动的 SSourceControlReview 控件
TWeakPtr<SSourceControlReview> ActiveReviewWeak = ReviewModule.GetActiveReview();

if (TSharedPtr<SSourceControlReview> ActiveReview = ActiveReviewWeak.Pin())
{
    // 例如，获取某个文件的审查评论
    const FString SomeAssetPath = TEXT("/Game/MyAsset.uasset");
    const TArray<FReviewComment>* Comments = ActiveReview->GetReviewCommentsForFile(SomeAssetPath);

    if (Comments && Comments->Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("资产 '%s' 有 %d 条评论。"), *SomeAssetPath, Comments->Num());
    }

    // 或者，为当前加载的变更列表添加一条评论
    FReviewComment NewComment;
    // ... 填充评论内容 ...
    ActiveReview->PostComment(NewComment);
}
```

## Demo 示例

以下是一个简单的 C++ Actor，它在构造时（或通过控制台命令）尝试打开变更列表审查工具并加载一个示例变更列表。

**头文件 (ChangelistReviewDemoActor.h)**:
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChangelistReviewDemoActor.generated.h"

UCLASS()
class AChangelistReviewDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AChangelistReviewDemoActor();

protected:
    virtual void BeginPlay() override;

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void OpenDemoChangelist(const FString& ChangelistNum);
};
```

**源文件 (ChangelistReviewDemoActor.cpp)**:
```cpp
#include "ChangelistReviewDemoActor.h"
#include "ChangelistReviewModule.h"

AChangelistReviewDemoActor::AChangelistReviewDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AChangelistReviewDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 示例：在游戏开始时尝试打开一个 CL
    // 注意：这需要编辑器环境和有效的源代码控制连接
    if (GIsEditor)
    {
        // 使用一个假设的 CL 号
        OpenDemoChangelist(TEXT("22968413"));
    }
}

void AChangelistReviewDemoActor::OpenDemoChangelist(const FString& ChangelistNum)
{
    FChangelistReviewModule& ReviewModule = FChangelistReviewModule::Get();
    if (ReviewModule.CanShowReviewTab())
    {
        UE_LOG(LogTemp, Log, TEXT("正在尝试打开变更列表 %s 进行审查..."), *ChangelistNum);
        ReviewModule.OpenChangelistReview(ChangelistNum);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("无法显示变更列表审查标签页。"));
    }
}
```

## 模块依赖

从 `ChangelistReview.Build.cs` 分析，除了常见的编辑器模块外，该插件依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `SourceControl` | 用于与版本控制系统（主要是 Perforce）交互，获取变更列表详情、文件内容和版本历史。 |
| `Swarm` | 用于与 Perforce Swarm 评论 API 通信，实现协作代码审查功能（评论、点赞、已读状态同步）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将插件内的日志宏升级到新的 `UE_LOGF` 格式。 |
| 2025-09-15 | `0633accb` | [CrashFix] Changelist review tool was crashing when reading saved CL history. Now if the history is | 修复了读取保存的变更列表历史时可能导致工具崩溃的严重错误。 |
| 2025-07-14 | `02997ee6` | [Bugfix] casing was wrong for the silenceNotification flag in swarm api. Hopefully this should fix a | 修复了调用 Swarm API 时静默通知标志大小写错误的 Bug。 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 更新了头文件的 `DLLAPI` 宏声明，修正了导入/导出规范。 |
| 2025-01-06 | `342da102` | [BugFix] Blueprint Review tool always displayed the revision and the datetime of the previous asset | 修复了蓝图审查工具错误显示资产上一版本修订号和日期时间的问题。 |

### 维护评价

该插件创建于 2022 年底，是一个相对较新的工具。从提交历史看，它**仍在维护中**，最近在 2025 年有多次 Bug 修复和代码质量改进。尽管更新频率不算非常高，但均为针对实际使用问题的修复，表明 Epic 对其进行了持续的关注和必要的维护。插件集成了 Swarm 评论功能，功能较为完整。鉴于其持续的 Bug 修复记录和作为官方源码控制审查流程的核心工具，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ChangelistReview)