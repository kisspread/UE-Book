# Project Launcher

> Configure custom launch profiles.

| 属性 | 值 |
|---|---|
| 中文名 | 项目启动器 |
| 分类 | Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProjectLauncher` (Editor), `CommonLaunchExtensions` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher) | |

## 用途

ProjectLauncher 是 UnrealFrontend (UFE) 中的**下一代项目启动配置框架**，用于替代旧版 Custom Launch UI。它基于模块化的「启动扩展」(Launch Extension) 架构，允许以插件方式向启动配置面板添加各类功能模块。

核心解决的问题：
- **旧版启动配置 UI 不可扩展**：新的 Extension 架构允许通过继承基类为 Build/Cook/Run 流程添加自定义选项
- **Tree Builder 系统**：每个 Extension 通过 `CustomizeTree()` 修改启动配置的 UI 树结构，动态注入设置面板
- **与 Zen Build 服务集成**：支持从内部构建服务拉取预编译构建，实现 Build Sync 工作流
- **UGS (Unreal Game Sync) 集成**：支持 Perforce changelist 同步

**重要限制**：此插件仅在 `UnrealFrontend` 程序中加载，不会在编辑器 (UnrealEditor) 中生效。

## 使用场景

- 你在 UE 项目中需要配置自定义的 Build/Cook/Run 流程并保存为可复用的启动配置 → 使用 ProjectLauncher
- 你的团队使用 Zen Build 服务进行 CI/CD，需要在 UFE 中选择并同步预编译构建 → 使用 BuildSync 扩展
- 你需要为特定平台配置不同的 Cook 参数（如只 Cook 特定 Map 或 Culture）→ 使用 AdvancedCook 扩展
- 你需要在启动时自动配置 Unreal Insights 的 Trace Channel → 使用 Insights 扩展

## 架构概览

ProjectLauncher 采用**扩展 (Extension) + 实例 (Instance)** 的两层架构：

```
FLaunchExtension (扩展定义，每个 Profile 一个)
    └─ FLaunchExtensionInstance (扩展实例，管理状态和 UI)
         ├─ FBuildCookRunExtensionInstance (Build/Cook/Run 命令扩展)
         │    └─ FBuildCookRunExtension (子扩展，定制 BuildCookRun 的行为)
         ├─ FCustomUATCommandLaunchExtensionInstance (自定义 UAT 命令扩展)
         └─ FAutomatedTestLaunchExtensionInstance (自动化测试扩展)
```

### CommonLaunchExtensions 包含的扩展

| 扩展 | 内部名称 | 说明 |
|---|---|---|
| AdvancedCook | `AdvancedCook` | 高级 Cook 选项：指定 Cook 的 Map 列表、Culture 列表 |
| BuildSync | `BuildSync` | 从 Zen Build 服务拉取预编译构建并同步到本地 |
| UgsSync | `UgsSync` | 通过 UAT 命令执行 UGS Perforce 同步 |
| Insights | `Insights` | 配置 Unreal Insights Trace 参数（通道、文件、主机） |
| Globals | `Globals` | 提供全局变量（`%ProjectName%`、`%PlatformName%` 等） |
| DeprecatedProperties | `DeprecatedProperties` | 处理已废弃的启动配置属性 |
| UserUATArgs | `UserUATArgs` | 允许用户添加自定义 UAT 命令行参数 |
| UserUATCommand | `UserUATCommand` | 允许用户添加自定义 UAT 命令 |
| BootTest | `BootTest` | 启动测试 (Boot Test) 配置 |
| ProfileWizard | `ProfileWizard` | 启动配置向导 |

## 蓝图用法

此插件为 **Editor 模块**，且仅在 UnrealFrontend 中加载，不提供 BlueprintCallable 函数。所有交互通过 UFE 的 Slate UI 完成。

## C++ 用法

### 头文件引入

```cpp
// 使用 ProjectLauncher 框架
#include "ProjectLauncherModule.h"

// 使用内置扩展
#include "CommonLaunchExtensionsModule.h"

// 使用特定扩展
#include "AdvancedCookLaunchExtension.h"
#include "BuildSyncLaunchExtension.h"
#include "InsightsLaunchExtension.h"
#include "GlobalsLaunchExtension.h"
```

### 创建自定义启动扩展

最核心的用法是继承基类创建自定义扩展。以下示例展示如何创建一个简单的 BuildCookRun 扩展。

```cpp
// MyLaunchExtension.h
#pragma once

#include "LaunchExtension.h"
#include "LaunchExtensionInstance.h"
#include "BuildCookRunCommandExtension.h"
#include "BuildCookRunExtension.h"

// 扩展定义（每个 Profile 一个）
class FMyLaunchExtension : public ProjectLauncher::FBuildCookRunCommandExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyLaunchExtensionInstance>(InArgs);
    }

    virtual const TCHAR* GetInternalName() const override
    {
        return TEXT("MyExtension");
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyExtension", "DisplayName", "My Extension");
    }
};

// 扩展实例（管理状态）
class FMyLaunchExtensionInstance : public ProjectLauncher::FBuildCookRunCommandExtensionInstance
{
public:
    FMyLaunchExtensionInstance(FArgs& InArgs)
        : FBuildCookRunCommandExtensionInstance(InArgs) {}

    virtual TSharedRef<ProjectLauncher::FBuildCookRunExtension> CreateBuildCookRunExtension(
        const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs) override
    {
        return MakeShared<FMyBuildCookRunInstance>(InArgs);
    }

private:
    // 子扩展实例：定制 BuildCookRun 的行为和 UI
    class FMyBuildCookRunInstance : public ProjectLauncher::FBuildCookRunExtension
    {
    public:
        FMyBuildCookRunInstance(const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs)
            : FBuildCookRunExtension(InArgs) {}

        virtual void CustomizeTree(
            ProjectLauncher::FLaunchProfileTreeNode& ProfileTreeNode) override
        {
            // 在此修改启动配置的 UI 树，注入自定义设置面板
        }

        virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
        {
            // 在此向 UAT 命令行追加自定义参数
        }
    };
};
```

### 使用 FBuildInfoHelper 获取 Zen Build 信息

来自 `Public/BuildSync/BuildInfoHelper.h`：

```cpp
#include "BuildInfoHelper.h"

// 创建 BuildInfoHelper 实例
TSharedRef<FBuildInfoHelper> BuildInfo = MakeShared<FBuildInfoHelper>();

// 设置项目名和构建类型
BuildInfo->SetProjectName(TEXT("MyProject"));
BuildInfo->SetBuildType(FBuildInfoHelper::DefaultBuildType);

// 监听构建列表刷新完成
BuildInfo->SetBuildsRefreshedHandler([BuildInfo]()
{
    // 获取所有可用构建
    const auto& BuildInfos = BuildInfo->GetBuildInfos();
    for (const auto& Info : BuildInfos)
    {
        // Info->Platforms - 构建支持的平台
        // Info->Backends - 构建后端
        // Info->PlatformToArtifacts - 平台到制品的映射
    }

    // 获取所有已知命名制品
    const TSet<FString>& Artifacts = BuildInfo->GetAllKnownNamedArtifacts();
});

// 连接 Zen Build 服务
BuildInfo->Connect();
if (BuildInfo->IsConnected())
{
    // 设置过滤器
    FBuildInfoHelper::FFilter Filter;
    Filter.MaxAge = FTimespan::FromDays(7);
    Filter.MaxItems = 50;
    BuildInfo->SetFilter(Filter);

    // 刷新构建列表
    BuildInfo->Refresh(true);
}
```

### 使用 FUGSBuildInfoRetriever 获取 UGS 构建信息

来自 `Public/Shared/UGSBuildInfoRetriever.h`：

```cpp
#include "UGSBuildInfoRetriever.h"

TSharedRef<FUGSBuildInfoRetriever> Retriever = MakeShared<FUGSBuildInfoRetriever>();

if (Retriever->IsConfigured())
{
    TArray<int32> Changelists = { 12345, 12346 };
    Retriever->GetUGSBuildInfoAsync(
        TEXT("MyProject"),
        Changelists,
        [Retriever]()
        {
            // 获取 UGS 构建信息
            const auto& Map = Retriever->GetBuildToUGSBuildInfoMap();
            for (const auto& Pair : Map)
            {
                int32 Changelist = Pair.Key;
                const auto& Info = Pair.Value;
                // Info->NumUsers - 使用此构建的用户数
                // Info->NumSuccess / NumFailed - 成功/失败计数
                // Info->Badges - 构建 badge 列表（每个 badge 有 Name, URL, State）
            }
        }
    );
}
```

### 提供全局变量

来自 `Private/Globals/GlobalsLaunchExtension.h`。Globals 扩展展示了如何向启动配置提供模板变量：

```cpp
// 内置全局变量：
// %LocalHost%        - 本地主机地址
// %LocalHosts%       - 本地主机列表
// %ProjectName%      - 项目名称
// %ProjectPath%      - 项目路径
// %TargetName%       - 目标名称
// %PlatformName%     - 平台名称
// %Configuration%    - 构建配置（Development/Shipping 等）

// 自定义扩展中提供变量：
virtual bool GetExtensionVariables(TArray<FString>& OutVariables) const override
{
    OutVariables.Add(TEXT("MyCustomVar"));
    return true;
}

virtual bool GetExtensionVariableValue(const FString& InVariable, FString& OutValue) const override
{
    if (InVariable == TEXT("MyCustomVar"))
    {
        OutValue = TEXT("MyValue");
        return true;
    }
    return false;
}
```

## Demo 示例

以下是一个完整的自定义启动扩展示例，向 UFE 的启动配置面板添加一个自定义文本字段。

```cpp
// MyCustomExtension.h
#pragma once

#include "CoreMinimal.h"
#include "LaunchExtension.h"
#include "LaunchExtensionInstance.h"
#include "BuildCookRunCommandExtension.h"
#include "BuildCookRunExtension.h"
#include "LaunchProfileTreeNode.h"

class FMyCustomExtension : public ProjectLauncher::FBuildCookRunCommandExtension
{
public:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override;
    virtual const TCHAR* GetInternalName() const override;
    virtual FText GetDisplayName() const override;
};

class FMyCustomExtensionInstance : public ProjectLauncher::FBuildCookRunCommandExtensionInstance
{
public:
    FMyCustomExtensionInstance(FArgs& InArgs)
        : FBuildCookRunCommandExtensionInstance(InArgs) {}

    virtual TSharedRef<ProjectLauncher::FBuildCookRunExtension> CreateBuildCookRunExtension(
        const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs) override;

private:
    class FMyBuildCookRun : public ProjectLauncher::FBuildCookRunExtension
    {
    public:
        FMyBuildCookRun(const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs)
            : FBuildCookRunExtension(InArgs) {}

        virtual void CustomizeTree(
            ProjectLauncher::FLaunchProfileTreeNode& ProfileTreeNode) override;
        virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override;

        FString CustomTag;
    };
};
```

```cpp
// MyCustomExtension.cpp
#include "MyCustomExtension.h"

TSharedPtr<ProjectLauncher::FLaunchExtensionInstance>
FMyCustomExtension::CreateInstanceForProfile(
    ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs)
{
    return MakeShared<FMyCustomExtensionInstance>(InArgs);
}

const TCHAR* FMyCustomExtension::GetInternalName() const
{
    return TEXT("MyCustom");
}

FText FMyCustomExtension::GetDisplayName() const
{
    return NSLOCTEXT("MyCustom", "Name", "My Custom Extension");
}

TSharedRef<ProjectLauncher::FBuildCookRunExtension>
FMyCustomExtensionInstance::CreateBuildCookRunExtension(
    const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs)
{
    return MakeShared<FMyBuildCookRun>(InArgs);
}

void FMyCustomExtensionInstance::FMyBuildCookRun::CustomizeTree(
    ProjectLauncher::FLaunchProfileTreeNode& ProfileTreeNode)
{
    // 向 UI 树注入自定义节点
    // 例如添加一个文本输入字段用于自定义 Tag
}

void FMyCustomExtensionInstance::FMyBuildCookRun::CustomizeUATCommandLine(
    FString& InOutCommandLine)
{
    if (!CustomTag.IsEmpty())
    {
        InOutCommandLine += FString::Printf(TEXT(" -CustomTag=%s"), *CustomTag);
    }
}
```

## 模块依赖

本插件的模块依赖未在提供的信息中完整列出。根据头文件引用推断：

| 模块 | 用途 |
|---|---|
| `ZenBuild` | Zen Build 服务集成（构建列表检索、连接管理） |
| `LauncherServices` | 启动器 Profile 接口（`ILauncherProfile`、`ILauncherProfileBuildCookRun` 等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 移除了打包与部署不能同时指定的限制 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStor | 使用项目设置中的 bUseZenStore 来决定是否传递 -ZenStore 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | BuildSync 扩展新增跳过指定内容下载的功能 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个 Developer 模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 支持选择插件内的 Map 进行 Cook |

### 维护评价

- **状态**：活跃维护中
- **创建时间**：2025-04-24，约 1 年历史
- **更新频率**：高，近一个月有 5 次功能性更新
- **实验性标记**：`IsBetaVersion=true`，仍处于 Beta 阶段
- **已知限制**：
  - 仅在 UnrealFrontend 中可用，不在编辑器中加载
  - Beta 版本，API 可能发生变化
- **推荐**：✅ 推荐关注和试用。作为下一代启动配置框架，正在被积极开发和完善。但由于是 Beta 状态，生产环境谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)
- 官方文档：暂无