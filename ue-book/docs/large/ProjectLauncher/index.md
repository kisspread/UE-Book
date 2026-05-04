# Project Launcher

> Configure custom launch profiles.

| 属性 | 值 |
|---|---|
| 分类 | Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ProjectLauncher` (Editor), `CommonLaunchExtensions` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/ProjectLauncher) | |

## 用途

Project Launcher 是 UnrealFrontend (UFE) 中的自定义启动配置管理插件。它提供了一个完整的 UI 面板，让用户可以创建、编辑和管理项目的启动配置（Launch Profile），控制从 Cook、Build、Deploy 到 Run 的完整工作流。

与编辑器内建的"Play In Editor"或简单的"Launch"按钮不同，Project Launcher 面向的是需要精细控制打包和部署流程的场景：选择目标平台、配置内容方案（Pak/Zen/Loose Files）、指定 Cook 的 Map、选择目标设备、设置命令行参数等。

该插件的核心价值在于其**可扩展架构**：通过 Tree Builder 和 Launch Extension 两个扩展点，其他插件可以自定义 Profile 编辑 UI 和命令行参数注入，实现自动化测试、性能分析等高级功能。

### 关键特性

- **三种 Profile 类型**：Basic（快速启动）、Custom（自定义配置）、Advanced（多平台/DLC/补丁等高级配置）
- **六种内容方案**：PakFiles、ZenStreaming、ZenPakStreaming、DevelopmentPackage、LooseFiles、CookOnTheFly
- **可扩展 UI**：通过 `ILaunchProfileTreeBuilderFactory` 注册自定义 Profile 编辑器
- **可扩展命令行**：通过 `FLaunchExtension` 注入自定义命令行参数和变量
- **内置扩展**：Globals（全局变量替换）、Insights（Unreal Insights 追踪）、BootTest（自动化启动测试）

## 使用场景

- 你需要为不同平台（Win64/Linux/Mac/Console）配置不同的打包和部署参数 → 用 Project Launcher 创建 Custom Profile
- 你需要一键将项目 Cook + Build + Deploy 到远程设备（如 Android/iOS/Console devkit）→ 在 Project Launcher 中配置设备和内容方案
- 你需要在启动时自动注入 Unreal Insights 追踪参数 → 使用内置的 Insights 扩展
- 你需要运行自动化启动测试（BootTest）→ 使用内置的 BootTest 扩展
- 你需要为团队创建标准化的启动配置模板 → 创建 Custom Profile 并保存
- 你需要自定义 Profile 编辑器的 UI 字段 → 实现 `ILaunchProfileTreeBuilderFactory`

## 蓝图用法

此插件不暴露 BlueprintCallable 接口。它是一个纯 Editor/DeveloperTool 插件，UI 完全通过 Slate 构建，不涉及蓝图交互。

## C++ 用法

### 模块接口

Project Launcher 通过 `IProjectLauncherModule` 暴露模块接口，支持注册 Tree Builder 和 Extension：

```cpp
#include "ProjectLauncherModule.h"

// 获取模块实例
IProjectLauncherModule& Module = IProjectLauncherModule::Get();

// 注册自定义 Tree Builder
Module.RegisterTreeBuilder(MyTreeBuilder.ToSharedRef());

// 注册自定义 Extension
Module.RegisterExtension(MyExtension.ToSharedRef());
```

### 核心概念

#### Profile 类型（EProfileType）

```cpp
enum class EProfileType : uint8
{
    Invalid,    // 无效
    Basic,      // 基础启动（默认推荐配置）
    Custom,     // 自定义配置
    Advanced,   // 高级配置（多平台、DLC、补丁等）
};
```

Profile 类型由 `FModel::GetProfileType()` 根据 Profile 的配置自动判断：
- **Basic**：内置的基础启动 Profile，不指定项目和构建目标
- **Custom**：用户创建的自定义 Profile
- **Advanced**：满足以下任一条件的 Profile：多平台 Cook、多语言、DLC、Release Version、Patch、Shared Repository、Copy Repository、Custom Roles

#### 内容方案（EContentScheme）

```cpp
enum class EContentScheme : uint8
{
    PakFiles,           // 打包为 .pak 文件
    ZenStreaming,       // 使用 Zen Server 流式传输
    ZenPakStreaming,    // Zen Pak 流式传输
    DevelopmentPackage, // 开发包
    LooseFiles,         // 松散文件（不打包）
    CookOnTheFly,       // 按需 Cook
};
```

内容方案决定了项目内容如何存储和部署到目标设备。不同方案有不同的可用性限制（如 Zen Store 启用时不能用 Loose Files）。

#### FModel — 核心数据模型

`ProjectLauncher::FModel` 是插件的核心数据类，管理所有 Profile 状态和辅助函数：

```cpp
// 构造（由模块内部完成）
TSharedRef<FModel> Model = MakeShared<FModel>(
    DeviceProxyManager, Launcher, ProfileManager
);

// Profile 管理
TArray<ILauncherProfilePtr> AllProfiles = Model->GetAllProfiles();
ILauncherProfilePtr BasicProfile = Model->GetBasicLaunchProfile();
Model->SelectProfile(MyProfile);
EProfileType Type = Model->GetProfileType(Profile);

// 创建 Profile
ILauncherProfileRef NewProfile = Model->CreateCustomProfile(TEXT("MyProfile"));
ILauncherProfilePtr Cloned = Model->CloneCustomProfile(ExistingProfile);

// 内容方案
EContentScheme Scheme = Model->DetermineProfileContentScheme(Profile);
Model->SetProfileContentScheme(EContentScheme::PakFiles, Profile);

// 设备管理
TSharedPtr<ITargetDeviceProxy> Proxy = FModel::GetDeviceProxy(Profile);
Model->UpdatedCookedPlatformsFromDeployDeviceProxy(Profile, DeviceProxy);

// 项目设置
FProjectSettings Settings = Model->GetProjectSettings(Profile);
bool bIsHost = FModel::IsHostPlatform(Profile);

// 日志
Model->AddLogMessage(TEXT("Cook completed"), ELogVerbosity::Log);
Model->ClearLogMessages();
```

### 扩展系统

#### Tree Builder — 自定义 Profile 编辑 UI

Tree Builder 决定 Profile 编辑器中显示哪些字段和控件。通过实现 `ILaunchProfileTreeBuilderFactory` 和 `ILaunchProfileTreeBuilder` 接口来创建自定义编辑器：

```cpp
#include "ProfileTree/ILaunchProfileTreeBuilder.h"
#include "ProfileTree/GenericProfileTreeBuilder.h"

using namespace ProjectLauncher;

// 1. 实现 Tree Builder
class FMyProfileTreeBuilder : public FGenericProfileTreeBuilder
{
public:
    FMyProfileTreeBuilder(
        const ILauncherProfileRef& Profile,
        const TSharedRef<FModel>& InModel)
        : FGenericProfileTreeBuilder(Profile, GetDefaultProfile(), InModel)
    {}

    virtual void Construct() override
    {
        // 添加 "General" 分组
        FLaunchProfileTreeNode& General = TreeData->AddHeading(
            TEXT("General"), LOCTEXT("General", "General")
        );

        // 使用基类提供的属性创建函数
        AddProjectProperty(General);
        AddBuildTargetProperty(General);
        AddPlatformProperty(General);
        AddConfigurationProperty(General);
        AddContentSchemeProperty(General);

        // 添加 "Cooking" 分组
        FLaunchProfileTreeNode& Cooking = TreeData->AddHeading(
            TEXT("Cooking"), LOCTEXT("Cooking", "Cooking")
        );
        AddCookProperty(Cooking);
        AddMapsToCookProperty(Cooking);
        AddIncrementalCookProperty(Cooking);

        // 添加 "Deployment" 分组
        FLaunchProfileTreeNode& Deploy = TreeData->AddHeading(
            TEXT("Deployment"), LOCTEXT("Deployment", "Deployment")
        );
        AddDeployProperty(Deploy);
        AddTargetDeviceProperty(Deploy);
        AddRunProperty(Deploy);
    }

    virtual FString GetName() const override { return TEXT("MyProfile"); }
};

// 2. 实现 Factory
class FMyProfileTreeBuilderFactory : public ILaunchProfileTreeBuilderFactory
{
public:
    virtual TSharedPtr<ILaunchProfileTreeBuilder> TryCreateTreeBuilder(
        const ILauncherProfileRef& Profile,
        const TSharedRef<FModel>& Model) override
    {
        return MakeShared<FMyProfileTreeBuilder>(Profile, Model);
    }

    virtual bool IsProfileTypeSupported(EProfileType ProfileType) const override
    {
        return ProfileType == EProfileType::Custom;
    }

    virtual int GetPriority() const override { return 10; }
};

// 3. 注册（在模块 StartupModule 中）
IProjectLauncherModule::Get().RegisterTreeBuilder(
    MakeShared<FMyProfileTreeBuilderFactory>()
);
```

`FGenericProfileTreeBuilder` 提供了大量预定义的属性创建函数：

| 函数 | 说明 |
|---|---|
| `AddProjectProperty` | 项目选择器 |
| `AddTargetProperty` | 构建目标选择器 |
| `AddPlatformProperty` | 平台选择器 |
| `AddConfigurationProperty` | 构建配置（Debug/Development/Shipping） |
| `AddContentSchemeProperty` | 内容方案选择器 |
| `AddCookProperty` | 是否 Cook |
| `AddMapsToCookProperty` | Cook 哪些 Map |
| `AddBuildProperty` | 是否 Build |
| `AddDeployProperty` | 是否 Deploy |
| `AddTargetDeviceProperty` | 目标设备选择器 |
| `AddRunProperty` | 是否 Run |
| `AddCommandLineProperty` | 自定义命令行参数 |
| `AddInitialMapProperty` | 初始 Map |
| `AddIncrementalCookProperty` | 增量 Cook 模式 |
| `AddCompressPakFilesProperty` | 压缩 Pak 文件 |
| `AddUseIoStoreProperty` | 使用 Io Store |
| `AddGenerateChunksProperty` | 生成 Chunks |
| `AddZenSnapshotProperty` | Zen 快照 |
| `AddArchitectureProperty` | 架构选择 |
| `AddArchiveBuildProperty` | 归档构建 |
| `AddStagingDirectoryProperty` | 暂存目录 |
| `AddForceBuildProperty` | 强制重新构建 |
| `AddBuildUATProperty` | 构建 UAT |

#### Launch Extension — 注入命令行参数

Extension 用于在 Profile 启动时注入额外的命令行参数和变量。通过实现 `FLaunchExtension` 和 `FLaunchExtensionInstance`：

```cpp
#include "Extension/LaunchExtension.h"

using namespace ProjectLauncher;

// 1. 实现 Extension Instance（每个 Profile 一个实例）
class FMyExtensionInstance : public FLaunchExtensionInstance
{
public:
    FMyExtensionInstance(FArgs& InArgs) : FLaunchExtensionInstance(InArgs) {}

    // 提供可切换的命令行参数
    virtual bool GetExtensionParameters(TArray<FString>& OutParameters) const override
    {
        OutParameters.Add(TEXT("-MyParam"));
        return true;
    }

    virtual FText GetExtensionParameterDisplayName(const FString& InParameter) const override
    {
        if (InParameter == TEXT("-MyParam"))
            return LOCTEXT("MyParam", "Enable My Feature");
        return FLaunchExtensionInstance::GetExtensionParameterDisplayName(InParameter);
    }

    // 提供可替换的变量
    virtual bool GetExtensionVariables(TArray<FString>& OutVariables) const override
    {
        OutVariables.Add(TEXT("$(MyVariable)"));
        return true;
    }

    virtual bool GetExtensionVariableValue(
        const FString& InVariable, FString& OutValue) const override
    {
        if (InVariable == TEXT("$(MyVariable)"))
        {
            OutValue = TEXT("Hello");
            return true;
        }
        return false;
    }

    // 自定义 Profile 编辑器中的 UI
    virtual void CustomizeTree(FLaunchProfileTreeData& ProfileTreeData) override
    {
        AddDefaultHeading(ProfileTreeData)
            .AddBoolean(LOCTEXT("VerboseLabel", "Verbose Logging"),
            {
                .GetValue = [this]() { return GetConfigBool(EConfig::PerProfile, TEXT("Verbose")); },
                .SetValue = [this](bool bVal) { SetConfigBool(EConfig::PerProfile, TEXT("Verbose"), bVal); },
            });
    }

    // 修改启动命令行
    virtual void CustomizeLaunchCommandLine(FString& InOutCommandLine) override
    {
        bool bVerbose = GetConfigBool(EConfig::PerProfile, TEXT("Verbose"));
        if (bVerbose)
        {
            InOutCommandLine += TEXT(" -Verbose");
        }
    }
};

// 2. 实现 Extension 工厂
class FMyExtension : public FLaunchExtension
{
public:
    virtual TSharedPtr<FLaunchExtensionInstance> CreateInstanceForProfile(
        FLaunchExtensionInstance::FArgs& InArgs) override
    {
        return MakeShared<FMyExtensionInstance>(InArgs);
    }
    virtual const TCHAR* GetInternalName() const override { return TEXT("MyExtension"); }
    virtual FText GetDisplayName() const override { return LOCTEXT("Name", "My Extension"); }
};

// 3. 注册
IProjectLauncherModule::Get().RegisterExtension(MakeShared<FMyExtension>());
```

#### 自动化测试 Extension

对于自动化测试场景，可以继承 `FAutomatedTestLaunchExtensionInstance`，它提供了自动化的测试开关 UI：

```cpp
#include "Extension/LaunchExtension.h"

using namespace ProjectLauncher;

class FMyTestExtensionInstance : public FAutomatedTestLaunchExtensionInstance
{
public:
    FMyTestExtensionInstance(FArgs& InArgs)
        : FAutomatedTestLaunchExtensionInstance(InArgs) {}

    // 测试内部名称（全局唯一）
    virtual const FString GetTestInternalName() const override
    {
        return TEXT("MyExtension.MyTest");
    }

    // 添加测试时的配置
    virtual void OnTestAdded(ILauncherProfileAutomatedTestRef AutomatedTest) override
    {
        AutomatedTest->SetTests(TEXT("UE.MyTest"));
        AutomatedTest->SetPriority(500);
    }

    // 自定义测试命令行
    virtual void CustomizeAutomatedTestCommandLine(FString& InOutCommandLine) override
    {
        InOutCommandLine += TEXT(" -MyTestFlag");
    }
};
```

#### Extension 配置存储

Extension Instance 提供了三种配置存储位置：

```cpp
enum class EConfig : uint8
{
    User_Common,     // 用户级，所有 Profile 共享
    User_PerProfile, // 用户级，每个 Profile 独立
    PerProfile,      // 随 Profile 保存
};

// 读写配置
bool bVal = GetConfigBool(EConfig::PerProfile, TEXT("MyKey"), false);
SetConfigBool(EConfig::PerProfile, TEXT("MyKey"), true);
FString Str = GetConfigString(EConfig::User_Common, TEXT("MyStr"));
int32 Num = GetConfigInteger(EConfig::User_PerProfile, TEXT("MyInt"), 0);
float F = GetConfigFloat(EConfig::PerProfile, TEXT("MyFloat"), 0.0f);
```

#### Extension 变量替换

Globals 扩展提供了内置变量，可在命令行参数中使用 `$(VariableName)` 语法：

| 变量 | 说明 |
|---|---|
| `$(LocalHost)` | 本机 IP 地址 |
| `$(ProjectName)` | 项目名称 |
| `$(ProjectPath)` | 项目路径 |
| `$(TargetName)` | 构建目标名称 |
| `$(Platform)` | 目标平台（多平台用 `+` 连接） |
| `$(Configuration)` | 构建配置（Debug/Development/Shipping 等） |

### 内置扩展

#### Globals

提供全局变量替换功能。这些变量可以在命令行参数和 Extension 的变量值中使用。Globals 扩展没有 UI 控件，只提供变量解析。

#### Insights

提供 Unreal Insights 性能分析工具的集成。支持以下参数：

| 参数 | 说明 |
|---|---|
| `-tracehost=$(LocalHost)` | 追踪数据发送到本机 |
| `-tracefile` | 追踪数据写入文件 |
| `-statnamedevents` | 捕获命名事件 |
| `-trace=Channel1,Channel2` | 选择追踪频道 |

Insights 扩展提供了频道选择子菜单，允许用户勾选需要的 Trace Channel。

#### BootTest

自动化启动测试扩展。基于 `FAutomatedTestLaunchExtensionInstance`，提供：
- 测试开关菜单项（在 Extensions 菜单的 "Automated Tests" 子菜单中）
- `Windowed` 选项（控制是否全屏运行）
- 测试优先级设为 1000（最轻量的测试，优先运行）
- 测试名称：`UE.BootTest`

## UI 架构

插件的 UI 由以下 Slate Widget 组成：

### 主面板

```
SProjectLauncher (主 Widget)
├── SWidgetSwitcher
│   ├── Panel 0: SCustomLaunchProfilesPanel (Profile 选择和编辑)
│   └── Panel 1: SCustomLaunchLaunchPanel (启动进度和日志)
```

### Profile 选择面板

```
SCustomLaunchProfilesPanel
├── SCustomLaunchCustomProfileSelector (Profile 列表)
│   └── SListView<ILauncherProfilePtr> (Profile 行)
├── SCustomLaunchCustomProfileEditor (Profile 属性编辑器)
│   └── STreeView<FLaunchProfileTreeNodePtr> (属性树)
└── SCustomLaunchOutputLog (输出日志)
```

### 共享 Widget

| Widget | 说明 |
|---|---|
| `SCustomLaunchCombo<T>` | 通用下拉选择框模板 |
| `SCustomLaunchStringCombo` | 字符串下拉选择框 |
| `SCustomLaunchProjectCombo` | 项目选择器（支持浏览文件） |
| `SCustomLaunchPlatformCombo` | 平台选择器（带图标） |
| `SCustomLaunchBuildTargetCombo` | 构建目标选择器 |
| `SCustomLaunchContentSchemeCombo` | 内容方案选择器 |
| `SCustomLaunchDeviceCombo` | 设备下拉选择器 |
| `SCustomLaunchDeviceListView` | 设备列表视图（带复选框） |
| `SCustomLaunchMapListView` | Map 列表视图（树形结构 + 复选框） |
| `SSegmentedProgressBar` | 分段进度条（显示各任务状态） |

### 启动进度面板

```
SCustomLaunchLaunchPanel
├── Profile 信息（名称、描述、项目、配置等）
├── SSegmentedProgressBar (分段进度条)
│   ├── Build 段
│   ├── Cook 段
│   ├── Deploy 段
│   └── Launch 段
├── SCustomLaunchOutputLog (输出日志)
└── 操作按钮（Cancel / Retry / Done）
```

进度条状态枚举：

```cpp
enum class EState : uint8
{
    None,      // 未开始
    Busy,      // 进行中（带旋转动画）
    Canceled,  // 已取消
    Completed, // 已完成
    Failed,    // 失败
    Pending,   // 等待中
};
```

## 模块依赖

### ProjectLauncher 模块

| 模块 | 用途 |
|---|---|
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `LauncherServices` | 启动器服务（ILauncher, ILauncherProfileManager） |
| `Core` | 核心库 |
| `CoreUObject` | UObject 系统 |
| `TargetPlatform` | 目标平台接口 |
| `DesktopPlatform` | 桌面平台（获取构建目标信息） |
| `ApplicationCore` | 应用核心 |
| `InputCore` | 输入核心 |
| `WorkspaceMenuStructure` | 工作区菜单结构（Tab 注册） |
| `ToolWidgets` | 工具 Widget |
| `TargetDeviceServices` | 目标设备代理管理 |
| `Projects` | 项目信息 |
| `DeveloperToolSettings` | 开发者工具设置 |
| `Zen` | Zen Server 接口 |
| `Engine` | 引擎（仅编辑器构建） |
| `AssetRegistry` | 资产注册表（仅编辑器构建，用于枚举 Map） |

### CommonLaunchExtensions 模块

| 模块 | 用途 |
|---|---|
| `Core` | 核心库 |
| `CoreUObject` | UObject 系统 |
| `Json` | JSON 解析 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `Sockets` | 网络套接字（获取本机 IP） |
| `TraceLog` | 追踪日志（枚举 Trace Channel） |
| `ProjectLauncher` | Project Launcher 模块接口 |
| `DeveloperSettings` | 开发者设置 |
| `UnrealEd` | 编辑器（仅编辑器构建） |
| `Engine` | 引擎（仅编辑器构建） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-03 | `5524a8137c99` | 确保 AutomatedPerfTest 插件默认不启用 |
| 2025-10-03 | `cd5aabaa9804` | 修复 PL2 不为本地构建生成报告的问题 |
| 2025-08-21 | `acc3e66e823d` | Extension 菜单改进：支持独立 section、公共 section 和子菜单；自动化测试默认归入共享子菜单 |

### 维护评价

- **状态**：⚠️ 实验性（IsBetaVersion=true）
- **活跃度**：活跃维护中，2025 年 8-10 月有功能性更新
- **年龄**：约 1 年（2025-04 创建），属于较新的插件
- **特殊说明**：此插件仅在 UnrealFrontend (UFE) 中加载（`SupportedPrograms: ["UnrealFrontend"]`），不会在编辑器或游戏中加载
- **推荐**：适合需要自定义启动流程的高级用户和工具开发者。由于是实验性 API，接口可能会有变动，建议关注版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/ProjectLauncher)
- [官方文档]()（无）
