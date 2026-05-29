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

Project Launcher 是 Unreal Frontend (UFE) 中的自定义项目启动配置系统。它替代了旧有的 CustomLaunchUI（从首次 commit 的重命名信息可知），为开发者提供了一个可扩展的、基于属性树的界面来配置项目的构建-烘焙-运行（Build-Cook-Run）流程。

该插件解决的核心问题是：**统一管理复杂的项目启动配置**。在 Unreal Engine 的开发工作流中，启动一个项目涉及多个步骤——选择构建目标、平台、设备、内容方案（Pak / Zen / Loose Files 等）、命令行参数、自动化测试等。Project Launcher 将这些配置抽象为"启动配置文件"（Launch Profile），并提供了类型化的内容方案（Content Scheme）系统和可扩展的扩展点（Extension），使得不同团队可以自定义启动流程而无需修改核心代码。

**仅在 UnrealFrontend 中加载**，不在编辑器主程序中运行。

## 使用场景

- 你在 UFE 中需要为不同目标平台（Win64/Linux/Mac）配置不同的启动方案 → 使用自定义配置文件
- 你需要管理多种内容部署方式（Pak、Zen Streaming、Loose Files、Staged Build 等）→ 使用 Content Scheme 系统
- 你需要在启动前自动执行自动化测试或自定义 UAT 命令 → 使用 UAT Command 扩展
- 你的团队需要在启动流程中注入自定义逻辑（如自定义命令行参数、环境检查）→ 开发 Launch Extension
- 你需要为不同的构建目标（Game、Editor、Server、Client）配置独立的启动参数 → 使用 BuildCookRun 扩展

## 蓝图用法

该插件为纯 C++ Editor 模块，不暴露 BlueprintCallable API。所有操作通过 C++ 接口完成。

## C++ 用法

### 模块接口

Project Launcher 通过 `IProjectLauncherModule` 提供注册扩展点和树构建器的入口。

### 头文件引入

```cpp
#include "ProjectLauncherModule.h"
#include "Extension/LaunchExtension.h"
#include "Extension/BuildCookRunCommandExtension.h"
#include "Extension/CmdLineParametersExtension.h"
#include "Extension/AutomatedTestLaunchExtension.h"
#include "Extension/CustomUATCommandLaunchExtension.h"
#include "Model/ProjectLauncherModel.h"
```

### 基本用法：注册一个 Launch Extension

Launch Extension 是 Project Launcher 的核心扩展点。每个扩展可以向属性树添加 UI 字段、修改命令行参数、监听属性变更事件。

```cpp
// MyLaunchExtension.h
#pragma once

#include "Extension/LaunchExtension.h"

// 1. 定义扩展实例（每个 Profile 对应一个实例）
class FMyLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    using FLaunchExtensionInstance::FLaunchExtensionInstance;

    // 向属性树添加自定义 UI 节点
    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override
    {
        // 添加一个顶级分类节点
        auto& Heading = ProfileTreeData.AddHeading(
            TEXT("MyExtension"),
            NSLOCTEXT("MyExtension", "Heading", "我的扩展"),
            100 // 排序值
        );

        // 添加布尔属性
        Heading.AddBoolean(
            NSLOCTEXT("MyExtension", "EnableFeature", "启用特性"),
            ProjectLauncher::FLaunchProfileTreeNode::FBooleanCallbacks{
                .GetValue = [this]() -> bool {
                    return GetConfigBool(EConfig::PerProfile, TEXT("bEnableFeature"));
                },
                .SetValue = [this](bool bValue) {
                    SetConfigBool(EConfig::PerProfile, TEXT("bEnableFeature"), bValue);
                },
                .GetDefaultValue = []() -> bool { return false; },
            },
            LOCTEXT("ToolTip", "勾选后将启用自定义特性")
        );

        // 添加字符串属性
        Heading.AddString(
            NSLOCTEXT("MyExtension", "CustomArg", "自定义参数"),
            ProjectLauncher::FLaunchProfileTreeNode::FStringCallbacks{
                .GetValue = [this]() -> FString {
                    return GetConfigString(EConfig::PerProfile, TEXT("CustomArg"));
                },
                .SetValue = [this](FString Value) {
                    SetConfigString(EConfig::PerProfile, TEXT("CustomArg"), Value);
                },
                .GetDefaultValue = []() -> FString { return TEXT(""); },
            }
        );
    }

    // 自定义启动命令行
    virtual void CustomizeLaunchCommandLine(FString& InOutCommandLine) override
    {
        bool bEnable = GetConfigBool(EConfig::PerProfile, TEXT("bEnableFeature"));
        if (bEnable)
        {
            InOutCommandLine += TEXT(" -MyCustomArg");
        }
    }

    // 属性变更回调
    virtual void OnPropertyChanged() override
    {
        // 当用户在 UI 中修改属性后被调用
    }
};

// 2. 定义扩展（单例，注册到模块）
class FMyLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual const TCHAR* GetInternalName() const override
    {
        return TEXT("MyLaunchExtension");
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyExtension", "Name", "我的启动扩展");
    }

    // 在扩展菜单中的位置
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry = FExtensionsMenuEntry::Default;
    }

protected:
    // 为每个 Profile 创建实例
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyLaunchExtensionInstance>(InArgs);
    }
};

// 3. 在模块启动时注册
// 通常在你的 Editor 模块的 StartupModule() 中：
void FMyEditorModule::StartupModule()
{
    if (IProjectLauncherModule* Module = IProjectLauncherModule::TryGet())
    {
        MyExtension = MakeShared<FMyLaunchExtension>();
        Module->RegisterExtension(MyExtension.ToSharedRef());
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (IProjectLauncherModule* Module = IProjectLauncherModule::TryGet())
    {
        Module->UnregisterExtension(MyExtension.ToSharedRef());
    }
}
```

**来源**：基于 `Public/Extension/LaunchExtension.h` 和 `Public/ProjectLauncherModule.h` 的接口定义。

### 进阶用法：开发 BuildCookRun 扩展

BuildCookRun 扩展是专门针对构建-烘焙-运行流程的扩展，允许为每个 UAT 命令实例添加独立的配置字段。

```cpp
// MyBuildCookRunExtension.h
#pragma once

#include "Extension/BuildCookRunCommandExtension.h"

// 1. 定义 BuildCookRun 扩展实例（每个 BuildCookRun 命令对应一个）
class FMyBCRExtension : public ProjectLauncher::FBuildCookRunExtension
{
public:
    using FBuildCookRunExtension::FBuildCookRunExtension;

    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeNode& ProfileTreeNode) override
    {
        auto& Heading = AddDefaultHeading(ProfileTreeNode);

        // 添加整数属性（带范围和滑块）
        Heading.AddInteger(
            LOCTEXT("MaxThreads", "最大线程数"),
            ProjectLauncher::FLaunchProfileTreeNode::TTypeCallbacks<int32>{
                .GetValue = [this]() -> int32 {
                    return GetConfigInteger(EConfig::PerProfile, TEXT("MaxThreads"), 4);
                },
                .SetValue = [this](int32 Value) {
                    SetConfigInteger(EConfig::PerProfile, TEXT("MaxThreads"), Value);
                },
                .GetDefaultValue = []() -> int32 { return 4; },
                .IsVisible = [this]() -> bool {
                    // 仅在烘焙模式下可见
                    auto BCR = GetBuildCookRun();
                    return BCR.IsValid() && BCR->GetCook();
                },
            },
            FInt32Interval(1, 32),
            true // 显示滑块
        );
    }

    // 修改 UAT 命令行
    virtual void CustomizeUATCommandLine(FString& InOutCommandLine) override
    {
        int32 MaxThreads = GetConfigInteger(EConfig::PerProfile, TEXT("MaxThreads"), 4);
        InOutCommandLine += FString::Printf(TEXT(" -NumCookWorkers=%d"), MaxThreads);
    }
};

// 2. 定义 BuildCookRun 扩展实例管理类
class FMyBCRExtensionInstance : public ProjectLauncher::FBuildCookRunCommandExtensionInstance
{
public:
    using FBuildCookRunCommandExtensionInstance::FBuildCookRunCommandExtensionInstance;

    virtual const TCHAR* GetInternalName() const override { return TEXT("MyBCRExtension"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("Name", "我的 BCR 扩展"); }

    virtual TSharedRef<ProjectLauncher::FBuildCookRunExtension> CreateBuildCookRunExtension(
        const ProjectLauncher::FBuildCookRunExtension::FArgs& InArgs) override
    {
        return MakeShared<FMyBCRExtension>(InArgs);
    }

    virtual bool IsBuildCookRunExtensionEnabledByDefault(
        const ILauncherProfileBuildCookRunRef& InBuildCookRun) const override
    {
        return false; // 默认关闭
    }

    virtual bool CanToggleBuildCookRunExtension(
        const ILauncherProfileBuildCookRunRef& InBuildCookRun, bool bWantToEnable) const override
    {
        return true; // 允许用户开关
    }
};

// 3. 定义扩展（单例）
class FMyBCRLaunchExtension : public ProjectLauncher::FBuildCookRunCommandExtension
{
    // FBuildCookRunCommandExtension 的 IsAlwaysCreated 返回 true，
    // 这意味着它对每个 profile 都会被创建，用户不能移除
public:
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyBCRLaunchExtension"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("Name", "我的 BCR 启动扩展"); }

    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry = FExtensionsMenuEntry::Default;
    }

protected:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyBCRExtensionInstance>(InArgs);
    }
};
```

**来源**：基于 `Public/Extension/BuildCookRunCommandExtension.h` 的 `FBuildCookRunExtension`、`FBuildCookRunCommandExtensionInstance` 和 `FBuildCookRunCommandExtension` 类。

### 进阶用法：自定义 UAT 命令扩展

用于向 Profile 添加自定义的 UAT 命令步骤，如自动化测试、数据迁移等。

```cpp
// MyDataMigrationExtension.h
#pragma once

#include "Extension/CustomUATCommandLaunchExtension.h"

class FMyDataMigrationInstance : public ProjectLauncher::FCustomUATCommandLaunchExtensionInstance
{
public:
    using FCustomUATCommandLaunchExtensionInstance::FCustomUATCommandLaunchExtensionInstance;

protected:
    virtual void OnUATCommandAdded(ILauncherProfileUATCommandRef InUATCommand) override
    {
        // 设置 UAT 命令名称
        InUATCommand->SetCommandName(LOCTEXT("Name", "数据迁移"));

        // 在属性树中添加配置
        auto& Heading = AddDefaultHeading(*GetOwnerTreeDataPtr());
        Heading.AddString(
            LOCTEXT("MigrationPath", "迁移路径"),
            ProjectLauncher::FLaunchProfileTreeNode::FStringCallbacks{
                .GetValue = [this]() -> FString {
                    return GetConfigString(EConfig::PerProfile, TEXT("MigrationPath"));
                },
                .SetValue = [this](FString Value) {
                    SetConfigString(EConfig::PerProfile, TEXT("MigrationPath"), Value);
                },
            }
        );
    }

    virtual void OnUATCommandRemoved(ILauncherProfileUATCommandRef InUATCommand) override
    {
        // 清理
    }
};

class FMyDataMigrationExtension : public ProjectLauncher::FCustomUATCommandLaunchExtension
{
public:
    virtual const TCHAR* GetInternalName() const override { return TEXT("DataMigration"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("Name", "数据迁移"); }

    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override
    {
        MenuEntry.Type = FExtensionsMenuEntry::Type_SubMenu;
        MenuEntry.SectionName = TEXT("UATCommands");
        MenuEntry.SubmenuName = TEXT("DataMigration");
        MenuEntry.SubmenuDisplayName = LOCTEXT("Submenu", "数据迁移工具");
    }

protected:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyDataMigrationInstance>(InArgs);
    }

    virtual ILauncherProfileUATCommandRef CreateUATCommand(
        ILauncherProfileRef InProfile, TSharedRef<ProjectLauncher::FModel> InModel) const override
    {
        // 创建 UAT 命令实例
        return InProfile->AddUATCommand();
    }
};
```

**来源**：基于 `Public/Extension/CustomUATCommandLaunchExtension.h` 的 `FCustomUATCommandLaunchExtensionInstance` 和 `FCustomUATCommandLaunchExtension`。

### 进阶用法：自定义命令行参数扩展

用于向命令行菜单添加可切换的命令行参数。

```cpp
// MyCmdLineExtension.h
#pragma once

#include "Extension/CmdLineParametersExtension.h"
#include "Extension/LaunchExtension.h"

class FMyCmdLineExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    using FLaunchExtensionInstance::FLaunchExtensionInstance;

protected:
    // 声明此扩展实现了命令行参数工厂
    virtual ProjectLauncher::ICmdLineParametersExtensionFactory* AsCmdLineParametersFactory() override
    {
        return &CmdLineFactory;
    }

private:
    class FMyCmdLineFactory : public ProjectLauncher::ICmdLineParametersExtensionFactory
    {
    public:
        // 返回此扩展提供的命令行参数列表
        virtual void GetCmdLineParameters(TArray<FString>& OutParameters) const override
        {
            OutParameters.Add(TEXT("-MyCustomParam"));
            OutParameters.Add(TEXT("-MyOtherParam"));
        }

        // 参数的显示名称
        virtual FText GetCmdLineParameterDisplayName(const FString& InParameter) const override
        {
            if (InParameter == TEXT("-MyCustomParam"))
                return LOCTEXT("Custom", "自定义参数");
            return FText::FromString(InParameter);
        }

        // 默认启用的参数
        virtual void GetDefaultCmdLineParameters(TArray<FString>& OutParameters) const override
        {
            // 默认不添加任何参数
        }

        // 支持的命令行类型
        virtual FString GetCmdLineType() const override
        {
            return ProjectLauncher::CmdLineType::Launch;
        }
    };

    FMyCmdLineFactory CmdLineFactory;
};
```

**来源**：基于 `Public/Extension/CmdLineParametersExtension.h` 的 `ICmdLineParametersExtensionFactory` 和 `FCmdLineParametersExtension`。

### 进阶用法：注册自定义属性树构建器

如果你需要完全自定义配置文件的 UI 布局（而非在标准布局上追加字段），可以注册自定义的 `ILaunchProfileTreeBuilderFactory`。

```cpp
// MyTreeBuilderFactory.h
#pragma once

#include "ProfileTree/ILaunchProfileTreeBuilder.h"
#include "ProfileTree/GenericProfileTreeBuilder.h"

class FMyTreeBuilder : public ProjectLauncher::FGenericProfileTreeBuilder
{
public:
    FMyTreeBuilder(const ILauncherProfileRef& Profile, const TSharedRef<ProjectLauncher::FModel>& InModel)
        : FGenericProfileTreeBuilder(Profile, Profile, InModel)
    {}

    virtual void Construct() override
    {
        // 调用基类构造获取标准字段
        FGenericProfileTreeBuilder::Construct();

        // 可在此基础上追加自定义分类
        auto& CustomHeading = TreeData->AddHeading(
            TEXT("CustomSettings"),
            LOCTEXT("CustomHeading", "自定义设置"),
            50
        );

        // 使用 FBuildCookRun 内部类添加字段
        if (TreeData->Profile.IsValid())
        {
            auto BCR = TreeData->Profile->GetBuildCookRun(0);
            if (BCR.IsValid())
            {
                auto& BCRData = Get(BCR);
                // 利用 BCRData 添加自定义属性...
            }
        }
    }

    virtual FString GetName() const override { return TEXT("MyTreeBuilder"); }
};

class FMyTreeBuilderFactory : public ProjectLauncher::ILaunchProfileTreeBuilderFactory
{
public:
    virtual TSharedPtr<ProjectLauncher::ILaunchProfileTreeBuilder> TryCreateTreeBuilder(
        const ILauncherProfileRef& Profile,
        const TSharedRef<ProjectLauncher::FModel>& Model) override
    {
        return MakeShared<FMyTreeBuilder>(Profile, Model);
    }

    // 高优先级，优先于默认工厂
    virtual int GetPriority() const override { return 100; }

    // 支持自定义配置文件类型
    virtual bool IsProfileTypeSupported(ProjectLauncher::EProfileType ProfileType) const override
    {
        return ProfileType == ProjectLauncher::EProfileType::Custom;
    }
};
```

**来源**：基于 `Public/ProfileTree/ILaunchProfileTreeBuilder.h` 和 `Public/ProfileTree/GenericProfileTreeBuilder.h`。

### 属性树节点类型参考

`FLaunchProfileTreeNode` 提供以下 UI 节点类型：

| 方法 | 说明 | 回调类型 |
|---|---|---|
| `AddBoolean` | 勾选框 | `FBooleanCallbacks` |
| `AddString` | 文本输入框 | `FStringCallbacks` |
| `AddDirectoryString` | 目录选择器（相对路径） | `FStringCallbacks` |
| `AddFileString` | 文件选择器（带过滤器） | `FStringCallbacks` |
| `AddCommandLineString` | 命令行输入框（带参数菜单） | `FStringCallbacks` + 类型名 |
| `AddInteger` | 整数输入（可带滑块和范围） | `TTypeCallbacks<int32>` |
| `AddFloat` | 浮点输入（可带滑块和范围） | `TTypeCallbacks<float>` |
| `AddWidget` | 自定义 Slate 控件 | `FCallbacks` |
| `AddSubHeading` | 子标题（用于分组） | 无 |

所有节点都支持 `IsVisible`、`IsEnabled`、`Validation` 回调用于控制可见性、可用性和验证逻辑。

**来源**：基于 `Public/ProfileTree/LaunchProfileTreeData.h`。

### 配置存储

扩展实例通过 `EConfig` 枚举控制配置值的存储位置：

| 值 | 说明 |
|---|---|
| `User_Common` | 跨 Profile 共享的用户配置 |
| `User_PerProfile` | 特定于 Profile 和扩展的用户配置 |
| `PerProfile` | 随 Profile 保存（持久化到 .profile 文件） |

支持 `Get/SetConfigString`、`Get/SetConfigBool`、`Get/SetConfigInteger`、`Get/SetConfigFloat` 四种类型。

**来源**：基于 `Public/Extension/LaunchExtension.h` 中 `FLaunchExtensionInstance::EConfig` 枚举。

### 内容方案（Content Scheme）

`EContentScheme` 枚举定义了所有支持的内容部署方式：

| 值 | 说明 |
|---|---|
| `PakFiles` | 传统 Pak 文件打包 |
| `ZenStreaming` | Zen Store 流式传输 |
| `ZenPakStreaming` | Zen Pak 流式传输 |
| `DevelopmentPackage` | 开发包 |
| `SubmissionPackage` | 提交包 |
| `LooseFiles` | 松散文件（不打包） |
| `CookOnTheFly` | 即时烘焙 |
| `PreStagedBuild` | 预暂存构建 |

通过 `FModel::DetermineProfileContentScheme()` 自动检测当前 Profile 使用的内容方案，通过 `FModel::SetProfileContentScheme()` 应用方案（自动设置烘焙、部署、打包选项）。

**来源**：基于 `Public/Model/ProjectLauncherModel.h`。

### 命令行工具

`ProjectLauncher::CmdLineUtils` 命名空间提供了命令行参数操作的静态工具函数：

```cpp
#include "Utils/LauncherCmdLineUtils.h"

FString CmdLine = TEXT("-game -log");

// 检查参数是否存在
bool bHasGame = ProjectLauncher::CmdLineUtils::IsParameterUsed(CmdLine, TEXT("-game"));

// 添加/移除参数
ProjectLauncher::CmdLineUtils::SetParameterUsed(CmdLine, TEXT("-windowed"), true);

// 读取/修改带值的参数
FString Resolution = ProjectLauncher::CmdLineUtils::GetParameterValue(CmdLine, TEXT("-ResX="));
ProjectLauncher::CmdLineUtils::UpdateParameterValue(CmdLine, TEXT("-ResX="), TEXT("1920"));

// 获取最终参数（合并默认值和用户修改）
FString FinalParam = ProjectLauncher::CmdLineUtils::GetFinalParameter(CmdLine, TEXT("-key=value"));
```

**来源**：基于 `Public/Utils/LauncherCmdLineUtils.h`。

### 扩展间通信

扩展实例之间可以通过事件机制相互通信：

```cpp
// 广播事件
void FMyExtensionInstance::OnSomeAction()
{
    BroadcastEvent(TEXT("MyCustomEvent"), &MyEventData);
}

// 接收事件
void FMyOtherExtensionInstance::HandleEventCallback(const FString& EventName, void* EventData)
{
    if (EventName == TEXT("MyCustomEvent"))
    {
        auto* Data = static_cast<FMyEventData*>(EventData);
        // 处理事件...
    }
}

// 查找同 Profile 下其他扩展实例
auto Instances = FLaunchExtensionInstance::GetProfileExtensionInstancesByName(
    TEXT("OtherExtension"), GetProfile());
```

**来源**：基于 `Public/Extension/LaunchExtension.h` 中的 `BroadcastEvent` 和 `HandleEventCallback`。

## Demo 示例

以下是一个最小可编译的自定义启动扩展示例，包含一个布尔开关和一个字符串参数：

```cpp
// MyCustomLaunchExtension.h
#pragma once

#include "Extension/LaunchExtension.h"
#include "CoreMinimal.h"

class FMyCustomLaunchExtensionInstance : public ProjectLauncher::FLaunchExtensionInstance
{
public:
    FMyCustomLaunchExtensionInstance(FArgs& InArgs);

    virtual void CustomizeTree(ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData) override;
    virtual void CustomizeLaunchCommandLine(FString& InOutCommandLine) override;
    virtual void OnPropertyChanged() override;
};

class FMyCustomLaunchExtension : public ProjectLauncher::FLaunchExtension
{
public:
    virtual const TCHAR* GetInternalName() const override;
    virtual FText GetDisplayName() const override;
    virtual void GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const override;

protected:
    virtual TSharedPtr<ProjectLauncher::FLaunchExtensionInstance> CreateInstanceForProfile(
        ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs) override;
};
```

```cpp
// MyCustomLaunchExtension.cpp
#include "MyCustomLaunchExtension.h"
#include "ProfileTree/LaunchProfileTreeData.h"

#define LOCTEXT_NAMESPACE "MyCustomLaunchExtension"

FMyCustomLaunchExtensionInstance::FMyCustomLaunchExtensionInstance(FArgs& InArgs)
    : FLaunchExtensionInstance(InArgs)
{
}

void FMyCustomLaunchExtensionInstance::CustomizeTree(
    ProjectLauncher::FLaunchProfileTreeData& ProfileTreeData)
{
    auto& Heading = ProfileTreeData.AddHeading(
        TEXT("MyCustom"),
        LOCTEXT("Heading", "自定义设置"),
        200
    );

    Heading.AddBoolean(
        LOCTEXT("Verbose", "详细日志"),
        ProjectLauncher::FLaunchProfileTreeNode::FBooleanCallbacks{
            .GetValue = [this]() -> bool {
                return GetConfigBool(EConfig::PerProfile, TEXT("bVerboseLogging"));
            },
            .SetValue = [this](bool bValue) {
                SetConfigBool(EConfig::PerProfile, TEXT("bVerboseLogging"), bValue);
            },
            .GetDefaultValue = []() -> bool { return false; },
        },
        LOCTEXT("VerboseTip", "启用后将输出详细启动日志")
    );

    Heading.AddString(
        LOCTEXT("ExtraArgs", "额外启动参数"),
        ProjectLauncher::FLaunchProfileTreeNode::FStringCallbacks{
            .GetValue = [this]() -> FString {
                return GetConfigString(EConfig::PerProfile, TEXT("ExtraArgs"));
            },
            .SetValue = [this](FString Value) {
                SetConfigString(EConfig::PerProfile, TEXT("ExtraArgs"), Value);
            },
            .GetDefaultValue = []() -> FString { return TEXT(""); },
        },
        LOCTEXT("ExtraArgsTip", "附加到启动命令行的额外参数")
    );
}

void FMyCustomLaunchExtensionInstance::CustomizeLaunchCommandLine(FString& InOutCommandLine)
{
    if (GetConfigBool(EConfig::PerProfile, TEXT("bVerboseLogging")))
    {
        InOutCommandLine += TEXT(" -Verbose");
    }

    FString Extra = GetConfigString(EConfig::PerProfile, TEXT("ExtraArgs"));
    if (!Extra.IsEmpty())
    {
        InOutCommandLine += TEXT(" ") + Extra;
    }
}

void FMyCustomLaunchExtensionInstance::OnPropertyChanged()
{
    // 属性变更后的逻辑
}

const TCHAR* FMyCustomLaunchExtension::GetInternalName() const
{
    return TEXT("MyCustomLaunchExtension");
}

FText FMyCustomLaunchExtension::GetDisplayName() const
{
    return LOCTEXT("DisplayName", "自定义启动扩展");
}

void FMyCustomLaunchExtension::GetExtensionsMenuEntry(FExtensionsMenuEntry& MenuEntry) const
{
    MenuEntry = FExtensionsMenuEntry::Default;
}

TSharedPtr<ProjectLauncher::FLaunchExtensionInstance>
FMyCustomLaunchExtension::CreateInstanceForProfile(
    ProjectLauncher::FLaunchExtensionInstance::FArgs& InArgs)
{
    return MakeShared<FMyCustomLaunchExtensionInstance>(InArgs);
}

#undef LOCTEXT_NAMESPACE
```

**注册（在你的 Editor 模块 StartupModule 中）**：

```cpp
#include "ProjectLauncherModule.h"
#include "MyCustomLaunchExtension.h"

void FMyEditorModule::StartupModule()
{
    if (IProjectLauncherModule* PLModule = IProjectLauncherModule::TryGet())
    {
        MyExtension = MakeShared<FMyCustomLaunchExtension>();
        PLModule->RegisterExtension(MyExtension.ToSharedRef());
    }
}

void FMyEditorModule::ShutdownModule()
{
    if (IProjectLauncherModule* PLModule = IProjectLauncherModule::TryGet())
    {
        PLModule->UnregisterExtension(MyExtension.ToSharedRef());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 设备代理管理，用于发现和连接目标设备 |
| `LauncherService` | 启动器服务，管理 Profile 和 Worker |
| `DeviceManager` | 设备管理器 UI 集成 |
| `ToolWidgets` | 工具控件（如分段进度条） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `4225c8f8` | Remove the restriction from Project Launcher that prevents package & deploy to be specified together | 移除打包与部署不能同时选择的限制 |
| 2026-04-27 | `77966850` | Launcher2: Use the value of bUseZenStore from ProjectSettings when deciding whether to pass -ZenStor | 根据项目设置的 bUseZenStore 决定是否传递 ZenStore 参数 |
| 2026-04-17 | `921928f4` | Add support for skipping content when downloading staged build via Project Launcher 2 Build Sync ext | 新增 Build Sync 扩展支持下载暂存构建时跳过指定内容 |
| 2026-04-16 | `9870b120` | Declare that several Developer modules only support desktop platforms | 声明多个开发者模块仅支持桌面平台 |
| 2026-04-14 | `c58ad33c` | Project Launcher now allows you to select maps that are in plugins. | 支持选择插件中的地图资源 |

### 维护评价

- **创建时间**：2025-04-24，约 1 年前，是一个相对较新的插件
- **近期活跃度**：最近一个月有 5 次提交，集中在功能增强和 bug 修复，属于**活跃维护**状态
- **状态标记**：`.uplugin` 中 `IsBetaVersion=true`，说明 API 仍可能发生变化
- **仅限 UFE**：`ProgramAllowList` 限定为 `UnrealFrontend`，不在编辑器主程序中加载
- **命名变更**：从首次 commit 可知，此插件由 `CustomLaunchUI` 重命名而来，"marshal" 概念被重命名为 "tree builder" 以提高清晰度
- **已知限制**：部分 API 已标记 `UE_DEPRECATED(5.8)`，正在从旧式参数管理迁移到 `ICmdLineParametersExtension` 模式
- **推荐使用**：如果你的项目需要在 UFE 中自定义启动配置流程，这是官方推荐的扩展方式。但由于 Beta 状态，建议关注版本升级时的 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ProjectLauncher)
- [官方文档]()（无）