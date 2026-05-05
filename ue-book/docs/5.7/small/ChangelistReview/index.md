# Changelist Reviews

> Review source control changelists

| 属性 | 值 |
|---|---|
| 分类 | Source Control |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | ChangelistReview (Editor) |
| 创建时间 | 2022-11-03 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ChangelistReview) | |

## 用途

ChangelistReview 是一个 **编辑器内 Changelist 审查工具**，让你无需离开 UE5 编辑器即可查看 Perforce changelist 中的文件变更并进行 Code Review。

它解决的核心问题是：在大型游戏项目中，美术/设计/程序每天产生大量 changelist，传统流程需要切换到 P4V、Swarm 网页或其他外部工具来审查变更。这个插件把 changelist 浏览、文件 diff、评论标注全部集成到编辑器内部，形成一个完整的一站式审查流程。

**工作原理**：输入一个 Perforce changelist 编号后，插件异步执行以下步骤：
1. 通过 `FGetChangelistDetails`（底层调用 `p4 describe`）获取 changelist 元数据
2. 从 Perforce 拉取每个文件的当前版本和前一版本到临时目录
3. 通过 Perforce API 查询 Helix Swarm 的 `P4.Swarm.URL` 属性，连接 Swarm 评论 API
4. 从 Swarm 获取或创建关联的 Review Topic，拉取评论数据
5. 扫描临时文件注册到 AssetRegistry，缓存资产类型图标

**重要限制**：目前仅支持 **Perforce** 作为版本控制系统（源码中硬编码检查 `Provider.GetName() == "Perforce"`）。

## 使用场景

- 你的团队使用 Perforce 管理 UE5 项目 → 用 ChangelistReview 在编辑器内审查同事提交的 changelist
- 你需要快速查看某个已提交 CL 改了哪些资产，并在编辑器内直接 diff → 打开 Review 工具，输入 CL 号，点 Diff 按钮
- 你的团队使用 Helix Swarm 做 Code Review → 在编辑器内直接发评论、@回复，评论同步到 Swarm
- 你想审查 shelved（未提交/pending）的 changelist → 同样支持，输入 CL 号即可
- Lead/主程需要批量审查多个 CL → 下拉框记录最近 6 个 CL 历史，方便快速切换

## 蓝图用法

此插件 **不暴露任何蓝图节点**。没有 `BlueprintCallable` 或 `BlueprintReadWrite` 的 UFUNCTION/UPROPERTY。它是一个纯编辑器 UI 工具，功能全部通过 Slate 界面操作。

## C++ 用法

### 头文件引入

```cpp
#include "ChangelistReviewModule.h"
```

### 基本用法

通过模块单例打开 Review 工具并加载指定 changelist：

```cpp
// 获取模块单例
FChangelistReviewModule& ReviewModule = FChangelistReviewModule::Get();

// 打开 Review Tab 并加载指定 changelist（返回是否成功）
bool bSuccess = ReviewModule.OpenChangelistReview(TEXT("12345"));

// 仅显示 Review Tab（不自动加载 changelist）
ReviewModule.ShowReviewTab();

// 检查是否可以显示 Tab（需要 Perforce 已连接）
if (ReviewModule.CanShowReviewTab())
{
    ReviewModule.ShowReviewTab();
}

// 获取当前活跃的 Review Widget
TWeakPtr<SSourceControlReview> ActiveReview = ReviewModule.GetActiveReview();
```

*来源：`Source/Public/ChangelistReviewModule.h`*

### 与 Diff 查看器集成

模块通过全局函数指针向 Kismet 模块暴露 Review 状态，让 Diff 查看器可以在对比文件时显示评论：

```cpp
// 这些全局函数指针在 StartupModule 中注册，在 Diff 查看器中使用
namespace UE::DiffControl
{
    // 获取某个文件的评论列表
    extern KISMET_API const TArray<FReviewComment>*(*GGetReviewCommentsForFile)(const FString&);
    // 发表评论
    extern KISMET_API void(*GPostReviewComment)(FReviewComment&);
    // 编辑评论
    extern KISMET_API void(*GEditReviewComment)(FReviewComment&);
    // 获取当前审查者用户名
    extern KISMET_API FString(*GGetReviewerUsername)(void);
    // 检查某个文件是否正在被审查
    extern KISMET_API bool (*GIsFileInReview)(const FString& File);
}
```

*来源：`Source/Private/ChangelistReviewModule.cpp`*

### Swarm 评论 API

`FSwarmCommentsAPI` 封装了 Helix Swarm REST API v9，支持创建/获取/编辑评论。认证方式是从 P4 ticket 文件读取凭证：

```cpp
#include "FSwarmCommentsAPI.h"

// 尝试自动连接 Swarm（从 P4 ticket 读取认证信息，从 P4 property 获取 Swarm URL）
TSharedPtr<FSwarmCommentsAPI> API = FSwarmCommentsAPI::TryConnect();
if (API)
{
    // 获取某个 Review 的所有评论
    FReviewTopic Topic{/* id */ "42", EReviewTopicType::Review};
    API->GetComments(Topic, FSwarmCommentsAPI::OnGetCommentsComplete::CreateLambda(
        [](const TArray<FReviewComment>& Comments, const FString& Error)
        {
            for (const FReviewComment& Comment : Comments)
            {
                // 处理评论...
            }
        }
    ));

    // 获取或创建某个 CL 的 Review Topic
    API->GetOrCreateReviewTopicForCL(TEXT("12345"),
        FSwarmCommentsAPI::OnGetReviewTopicForCLComplete::CreateLambda(
            [](const FReviewTopic& Topic, const FString& Error)
            {
                // 处理 review topic...
            }
        ));
}
```

*来源：`Source/Private/FSwarmCommentsAPI.cpp`, `Source/Private/FSwarmCommentsAPI.h`*

### 进阶用法

`SSourceControlReview` 是核心 UI Widget，可以直接在自定义编辑器工具中实例化：

```cpp
// 创建 Review Widget
TSharedRef<SSourceControlReview> ReviewWidget = SNew(SSourceControlReview);

// 程序化加载 changelist
ReviewWidget->LoadChangelist(TEXT("67890"));

// 查询文件是否在当前 review 中
bool bInReview = ReviewWidget->IsFileInReview(TEXT("//depot/MyProject/Content/MyAsset.uasset"));

// 获取文件评论
const TArray<FReviewComment>* Comments = ReviewWidget->GetReviewCommentsForFile(
    TEXT("//depot/MyProject/Content/MyAsset.uasset"));
```

*来源：`Source/Public/SSourceControlReview.h`*

## Demo 示例

### 最小集成示例

在你的编辑器模块中打开 ChangelistReview：

```cpp
// MyEditorModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorModule : public FDefaultModuleImpl
{
public:
    virtual void StartupModule() override;
    void OpenReviewForCL(const FString& ChangelistNum);
};

// MyEditorModule.cpp
#include "MyEditorModule.h"
#include "ChangelistReviewModule.h"

void FMyEditorModule::StartupModule()
{
    // 可以在这里添加自定义菜单项来触发 review
}

void FMyEditorModule::OpenReviewForCL(const FString& ChangelistNum)
{
    if (FChangelistReviewModule::Get().CanShowReviewTab())
    {
        FChangelistReviewModule::Get().OpenChangelistReview(ChangelistNum);
    }
}

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "ChangelistReview",
    "SourceControl",  // 检查 SCC 状态
});
```

## 模块依赖

### Public 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、字符串、路径处理 |
| `Engine` | 引擎核心（AssetRegistry 等） |
| `CoreUObject` | UObject 系统 |

### Private 依赖

| 模块 | 用途 |
|---|---|
| `SlateCore` / `Slate` | UI Widget 框架（SSourceControlReview 等） |
| `UnrealEd` | 编辑器框架（Tab 管理、ToolMenus） |
| `Kismet` | 与 Diff 查看器集成（全局函数指针） |
| `SourceControl` | 源码控制抽象层（FGetChangelistDetails, FGetFile 等操作） |
| `HTTP` / `Json` | Swarm REST API 通信 |
| `ToolMenus` | 状态栏菜单扩展 |
| `EditorFramework` / `EditorStyle` | 编辑器样式 |
| `InputCore` | 输入处理 |

### 第三方依赖

| 库 | 用途 |
|---|---|
| `Perforce` | 直接调用 P4 C++ API 获取 Swarm URL（`ClientApi`） |
| `OpenSSL` | HTTPS 通信（仅 Win64/Mac） |
| `zlib` | 压缩（仅 Win64/Mac） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `02997ee6` | [Bugfix] Swarm API 中 `silenceNotification` 标志大小写错误修复 | 修复了审查 Blueprint 时发送过多邮件通知的 bug。涉及 `FSwarmCommentsAPI::PostComment` 和 `EditComment` 中的 `silenceNotification` 参数大小写。 |
| 2025-05-30 | `8396b185` | 使用 UnrealCodeFixup 更新头文件的 DLL 导出标记 | 基础设施维护，将 `CHANGELISTREVIEW_API` 从类型移到方法/静态变量上，确保正确的 DLL 导出。 |
| 2025-01-06 | `342da102` | [BugFix] Blueprint Review 工具 diff 面板中前一版本的 revision 和 datetime 始终显示为 0 | 修复了 `SSourceControlReviewEntry` 中获取前一版本 revision 信息的逻辑。 |

### 维护评价

- **创建时间**：2022-11-03，约 3.5 年历史
- **维护状态**：**活跃维护** — 最近 6 个月内有实质性 bug 修复（2025-07-14）
- **更新频率**：中等，大约每 2-6 个月有更新，主要是 bug 修复和兼容性改进
- **已知限制**：
  - 仅支持 Perforce，不支持 Git 或其他版本控制系统
  - Swarm 评论 API 是 v9，可能与新版 Swarm 不完全兼容
  - 评论元数据（File、ReplyTo、Category）嵌入在评论 body 中作为 workaround，因为 Swarm API 对这些属性支持不完整
- **推荐使用**：✅ 推荐。活跃维护，功能实用，是 Epic 自用的工具。如果你的团队使用 Perforce + Swarm，这是一个很好的内建审查工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ChangelistReview)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ChangelistReview)：此插件没有独立测试用例目录
