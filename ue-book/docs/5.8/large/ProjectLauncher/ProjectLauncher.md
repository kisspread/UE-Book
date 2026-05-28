# Project Launcher

> Configure custom project launch profiles.

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

ProjectLauncher 是 UnrealFrontend (UFE) 中**项目启动配置系统**的插件，取代了旧版 CustomLaunchUI。它解决的核心问题是：**如何在统一的界面中管理复杂的多平台、多设备、多工作流的项目启动配置**。

该插件提供了一个基于树状结构的属性编辑 UI，允许开发者创建、编辑和管理启动配置文件（Profile），支持：

- **三种配置类型**：Basic（基础）、Custom（自定义）、Advanced（高级，多平台/文化/DLC 等复杂配置）
- **内容方案管理**：PakFiles、Zen Streaming、Zen Pak Streaming、CookOnTheFly、PreStaged Build 等 8 种内容部署策略
- **可扩展架构**：通过 `FLaunchExtension` / `FLaunchExtensionInstance` 机制，其他插件可以注入自定义 UI 和命令行参数
- **UAT 命令管理**：支持自动测试和自定义 UAT 命令的配置
- **构建/烹饪/部署/运行**全生命周期管理

**重要限制**：此插件仅在 UnrealFrontend 中加载（`ProgramAllowList: ["UnrealFrontend"]`），不在编辑器主程序中运行。

## 使用场景

- 你需要为不同目标平台（Win64、Linux、Mac、主机、移动端）配置各自的启动参数 → 使用 Custom Profile
- 你的项目使用 Zen Store 或 Io Store 工作流 → 在内容方案中选择 Zen Streaming 或 Zen Pak Streaming
- 你需要在启动前执行自动化测试（如 Gauntlet）→ 通过 Extensions 菜单添加 Automated Test 扩展
- 你需要为特定设备（如 devkit）配置专用的构建和部署流程 → 使用 Advanced Profile 配置
- 你需要为不同的启动场景（开发调试、QA 测试、提交验证）保存多套配置 → 创建多个 Custom Profile

## 蓝图用法

此插件是 Editor-only 且仅在 UnrealFrontend 中加载，不包含 BlueprintCallable 函数。所有 API 均为 C++ 接口，面向需要扩展启动配置系统的开发者。

## C++ 用法

### 头文件引入

```cpp
#include "ProjectLauncherModule.h"
#include "Extension/LaunchExtension.h"
#include "Extension/BuildCookRunCommandExtension.h"
#include "Model/ProjectLauncherModel.h"
#include "ProfileTree/ILaunchProfileTreeBuilder.h"
#include "ProfileTree/LaunchProfileTreeData.h"
```

### 基本用法 — 创建自定义 Launch Extension

启动扩展（Launch Extension）是此插件的核心扩展点。通过继承 `FLaunchExtension` 和 `FLaunchExtensionInstance`，你可以向启动配置 UI 注入自定义控件和逻辑。

```cpp
// MyLaunchExtension.h
#pragma once
#include "Extension/LaunchExtension.h"

// 扩展实例：绑定到特定 Profile，负责 UI 和命令行定制
class FMyLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    FMyLaunchExtensionInstance(FArgs& InArgs)
        : FLaunchExtensionInstance(InArgs)
    {}

    // 向属性树添加自定义 UI 控件
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        using namespace ProjectLauncher;
        FLaunchProfileTreeNode& Heading = AddDefaultHeading(ProfileTreeData);

        Heading.AddBoolean(
            LOCTEXT("MyOption", "Enable My Option"),
            FLaunchProfileTreeNode::FBooleanCallbacks{
                .GetValue = [this]() { return GetConfigBool(EConfig::User_PerProfile, TEXT("bMyOption")); },
                .SetValue = [this](bool bValue) { SetConfigBool(EConfig::User_PerProfile, TEXT("bMyOption"), bValue); },
                .GetDefaultValue = []() { return false; },
            }
        );
    }

    // 修改启动命令行
    virtual void CustomizeLaunchCommandLine(FString& InOutCommandLine) override
    {
        if (GetConfigBool(EConfig::User_PerProfile, TEXT("bMyOption")))
        {
            InOutCommandLine += TEXT(" -MyCustomOption");
        }
    }
};

// 扩展工厂：注册到模块，负责创建实例
class FMyLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyLaunchExtension"); }
    virtual FText GetDisplayName() const override { return NSLOCTEXT("MyExt", "Name", "My Extension"); }

    // 在 Extensions 菜单中的位置
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry = FExtensionsMenuEntry::OwnSection;
    }

    // 创建实例
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyLaunchExtensionInstance>(InArgs);
    }
};
```

### 注册扩展

```cpp
// 在你的模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    TSharedPtr<FMyLaunchExtension> MyExtension = MakeShared<FMyLaunchExtension>();
    IProjectLauncherModule::Get().RegisterExtension(MyExtension.ToSharedRef());
}

void FMyModule::ShutdownModule()
{
    IProjectLauncherModule::Get().UnregisterExtension(MyExtension.ToSharedRef());
}
```

### 进阶用法 — 自定义 Tree Builder

如果你需要完全自定义 Profile 的属性编辑界面（而非在默认界面上添加扩展），可以注册自定义的 Tree Builder Factory：

```cpp
// 来源: Public/ProfileTree/CustomProfileTreeBuilder.h
class FMyProfileTreeBuilder : public ProjectLauncher::FGenericProfileTreeBuilder
{
public:
    FMyProfileTreeBuilder(const ILauncherProfileRef& Profile, const TSharedRef<ProjectLauncher::FModel>& InModel)
        : FGenericProfileTreeBuilder(Profile, Profile, InModel)
    {}

    virtual void Construct() override
    {
        FGenericProfileTreeBuilder::Construct(); // 调用基类构建通用属性
        // 在此添加或修改自定义属性节点
    }

    virtual FString GetName() const override { return TEXT("MyProfile"); }
};

class FMyProfileTreeBuilderFactory : public ProjectLauncher::ILaunchProfileTreeBuilderFactory
{
public:
    virtual TSharedPtr<ProjectLauncher::ILaunchProfileTreeBuilder> TryCreateTreeBuilder(
        const ILauncherProfileRef& Profile, const TSharedRef<ProjectLauncher::FModel>& InModel) override
    {
        return MakeShared<FMyProfileTreeBuilder>(Profile, InModel);
    }

    virtual bool IsProfileTypeSupported(ProjectLauncher::EProfileType ProfileType) const override
    {
        return ProfileType == ProjectLauncher::EProfileType::Custom;
    }
};

// 注册
IProjectLauncherModule::Get().RegisterTreeBuilder(MakeShared<FMyProfileTreeBuilderFactory>());
```

### 进阶用法 — 内容方案配置

通过 `FModel` 管理 Profile 的内容部署策略：

```cpp
using namespace ProjectLauncher;

// 获取当前 Profile 的内容方案
EContentScheme CurrentScheme = Model->DetermineProfileContentScheme(BuildCookRun);

// 设置为 Zen Streaming 模式
FProjectSettings Settings = Model->GetProjectSettings(Profile);
Model->SetProfileContentScheme(
    EContentScheme::ZenStreaming,
    Settings,
    BuildCookRun,
    /*bWantToCook=*/ true,
    ELauncherProfileDeploymentModes::CopyToDevice
);

// 获取所有可用方案及其显示名称
TArray<EContentScheme> AllSchemes = GetAllContentSchemes();
for (EContentScheme Scheme : AllSchemes)
{
    FText Name = GetContentSchemeDisplayName(Scheme);
    FText Tip = GetContentSchemeToolTip(Scheme);
}
```

## Demo 示例

一个最小的自定义启动扩展，向启动配置添加一个文本字段并注入命令行参数：

```cpp
// MySimpleLaunchExtension.h
#pragma once
#include "Extension/LaunchExtension.h"
#include "Model/ProjectLauncherModel.h"
#include "ProfileTree/LaunchProfileTreeData.h"

class FMySimpleLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    FMySimpleLaunchExtensionInstance(FArgs& InArgs)
        : FLaunchExtensionInstance(InArgs)
    {}

    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        using namespace ProjectLauncher;
        FLaunchProfileTreeNode& Heading = AddDefaultHeading(ProfileTreeData);

        Heading.AddString(
            LOCTEXT("CustomTag", "Custom Tag"),
            FLaunchProfileTreeNode::FStringCallbacks{
                .GetValue = [this]() {
                    return GetConfigString(EConfig::User_PerProfile, TEXT("CustomTag"), TEXT(""));
                },
                .SetValue = [this](const FString& Value) {
                    SetConfigString(EConfig::User_PerProfile, TEXT("CustomTag"), Value);
                },
                .GetDefaultValue = []() { return FString(); },
                .IsVisible = []() { return true; },
                .IsEnabled = []() { return true; },
            },
            LOCTEXT("CustomTagTip", "A custom tag added to the launch command line")
        );
    }

    virtual void CustomizeLaunchCommandLine(FString& InOutCommandLine) override
    {
        FString Tag = GetConfigString(EConfig::User_PerProfile, TEXT("CustomTag"), TEXT(""));
        if (!Tag.IsEmpty())
        {
            InOutCommandLine += FString::Printf(TEXT(" -CustomTag=%s"), *Tag);
        }
    }
};

class FMySimpleLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual const TCHAR* GetInternalName() const override { return TEXT("MySimpleLaunchExtension"); }
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MySimpleExt", "Name", "Simple Extension");
    }
    virtual FSlateIcon GetIcon() const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports");
    }
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry = FExtensionsMenuEntry::Default;
    }
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMySimpleLaunchExtensionInstance>(InArgs);
    }
};
```

## 模块依赖

基于源码中使用的接口和类型推断（Build.cs 未完整提供，以下为关键外部依赖）：

| 模块 | 用途 |
|---|---|
| `LauncherProfile` | 提供 `ILauncherProfile`、`ILauncherProfileManager` 等配置文件核心接口 |
| `DeviceManager` | 提供 `ITargetDeviceProxy`、`ITargetDeviceProxyManager` 设备代理管理 |
| `TargetDeviceServices` | 目标设备服务层 |
| `PlatformInfo` | 平台信息查询（`FTargetPlatformInfo`） |
| `AutomationController` | 自动化测试控制器（用于 Automated Test 扩展） |

无特殊依赖（仅标准 Core/Engine/Slate 等基础模块 + 上述 Launcher 相关模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 移除打包与部署不能同时指定的限制 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStore | 使用项目设置中的 bUseZenStore 值决定是否传递 ZenStore 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | Build Sync 扩展支持下载暂存构建时跳过特定内容 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个 Developer 模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 支持选择插件中的地图 |

### 维护评价

- **创建时间**：2025-04-24，约 1 年历史，是较新的插件
- **维护状态**：**活跃维护中**。最近 1 个月内有多次功能性更新，持续改进 Zen 工作流支持和设备部署功能
- **Beta 状态**：标记为 `IsBetaVersion=true`，API 可能发生变化（源码中可见多个 `UE_DEPRECATED(5.8, ...)` 标记，说明旧 API 正在被重构）
- **架构演化**：从第一个 commit 可见，此插件由旧版 CustomLaunchUI 重命名而来，概念上从 "marshal" 改为 "tree builder"，说明架构仍在优化中
- **推荐程度**：作为 UnrealFrontend 内置的启动配置系统，它是 Epic 官方维护的核心工具。如果你需要扩展 UFE 的启动配置功能（如添加自定义自动化测试、自定义部署流程），此插件是必经之路。但需注意其 Beta 状态和正在演化的 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)