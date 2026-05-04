# Editor System Configuration Assistant

> Editor utility for offering system configuration suggestions

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | EditorSysConfigAssistant (Editor) |
| 创建时间 | 2023-10-19 |
| 年龄标签 | 🆕 (~2.5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorSysConfigAssistant) | |

## 用途

EditorSysConfigAssistant 是一个**操作系统级别的配置检测与修复工具**。它在编辑器启动时自动扫描宿主操作系统（目前仅 Windows）的文件系统设置，检测可能拖慢 UE5 编辑器性能的系统配置问题，并以通知栏 + 面板的形式告知用户，提供一键修复能力。

它解决的核心问题是：UE5 的资产扫描、目录监听等操作依赖特定的 NTFS 文件系统特性，如果操作系统未正确配置这些特性，编辑器的启动和运行速度会显著下降。普通开发者往往不知道这些底层配置的存在，此插件将"专家级系统调优知识"自动化。

### 当前内置的检测项

| 检测项 | 问题 | 修复方式 |
|---|---|---|
| **NTFS Last Access Time** | Windows 默认启用文件"最后访问时间"记录，每次文件读写都会产生额外的磁盘 I/O，导致资产注册表扫描变慢 | 通过 `fsutil behavior set disableLastAccess 1` 禁用（需管理员权限） |
| **USN Journal 配置** | 项目所在磁盘的 USN Journal 大小不足（推荐 ≥1 GiB），导致文件变更发现操作变慢，编辑器启动时间增加 | 通过 `fsutil usn createjournal` 创建/扩展 Journal（需管理员权限） |

## 使用场景

- 你在 Windows 上开发大型 UE5 项目，编辑器启动明显缓慢 → 启用此插件，它会自动检测并提示修复系统配置
- 你是一个团队的技术负责人，希望确保团队成员的开发环境配置一致 → 让团队成员启用此插件
- 你想了解哪些操作系统级设置会影响 UE5 编辑器性能 → 打开 System Config 面板查看检测结果

> ⚠️ 目前仅在 **Windows** 平台有效。Mac/Linux 平台会加载插件但不会注册任何检测功能。

## 蓝图用法

此插件**没有蓝图接口**。它是一个纯编辑器 UI 工具，通过编辑器面板和通知栏交互。

## C++ 用法

此插件采用 **Modular Feature** 架构，允许其他插件/模块注册自定义的系统配置检测项。

### 头文件引入

```cpp
#include "EditorSysConfigAssistantModule.h"   // 模块接口
#include "EditorSysConfigFeature.h"           // 检测功能接口
#include "EditorSysConfigAssistantSubsystem.h" // 子系统
#include "EditorSysConfigIssue.h"             // 问题结构体
```

### 检查/打开 System Config 面板

```cpp
// 来源: EditorSysConfigAssistantModule.h
IEditorSysConfigAssistantModule& Module = IEditorSysConfigAssistantModule::Get();

// 检查是否可以显示面板（受 Tab 权限列表控制）
if (Module.CanShowSystemConfigAssistant())
{
    // 打开 System Config 面板
    Module.ShowSystemConfigAssistant();
}
```

### 注册自定义系统配置检测功能

通过实现 `IEditorSysConfigFeature` 接口并注册到 Modular Features 系统：

```cpp
#include "EditorSysConfigFeature.h"
#include "Features/IModularFeatures.h"

class FMyCustomSysConfigFeature : public IEditorSysConfigFeature
{
public:
    // 显示名称
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyPlugin", "FeatureName", "My Custom Check");
    }

    // 问题描述（展示给用户看）
    virtual FText GetDisplayDescription() const override
    {
        return NSLOCTEXT("MyPlugin", "FeatureDesc", "Description of the problem...");
    }

    // 版本号（用于跟踪检测逻辑变更）
    virtual FGuid GetVersion() const override
    {
        static FGuid Version(0x12345678, 0x12345678, 0x12345678, 0x12345678);
        return Version;
    }

    // 修复能力标志
    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override
    {
        return EEditorSysConfigFeatureRemediationFlags::HasAutomatedRemediation |
               EEditorSysConfigFeatureRemediationFlags::RequiresElevation;
    }

    // 执行系统检测（建议异步执行）
    virtual void StartSystemCheck() override
    {
        Async(EAsyncExecution::TaskGraph, [this]()
        {
            UEditorSysConfigAssistantSubsystem* Subsystem =
                GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
            if (!Subsystem) return;

            // 执行检测逻辑...
            bool bHasProblem = true; // 替换为实际检测
            if (bHasProblem)
            {
                FEditorSysConfigIssue Issue;
                Issue.Feature = this;
                Issue.Severity = EEditorSysConfigIssueSeverity::High;
                Subsystem->AddIssue(Issue); // 线程安全
            }
        });
    }

    // 执行修复（必须在 GameThread 同步完成）
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override
    {
        // 添加需要以管理员权限执行的命令
        OutElevatedCommands.Add(TEXT("some_admin_command arg1 arg2"));
    }
};
```

注册到 Modular Features：

```cpp
// 在模块的 StartupModule() 中
static FMyCustomSysConfigFeature MyFeature;
IModularFeatures::Get().RegisterModularFeature(
    IEditorSysConfigFeature::GetModularFeatureName(), &MyFeature);

// 在模块的 ShutdownModule() 中
IModularFeatures::Get().UnregisterModularFeature(
    IEditorSysConfigFeature::GetModularFeatureName(), &MyFeature);
```

### 进阶用法：直接与子系统交互

```cpp
UEditorSysConfigAssistantSubsystem* Subsystem =
    GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();

// 获取所有当前问题（线程安全）
TArray<TSharedPtr<FEditorSysConfigIssue>> AllIssues = Subsystem->GetIssues();

// 手动应用修复
Subsystem->ApplySysConfigChanges(AllIssues);

// 关闭通知栏
Subsystem->DismissSystemConfigNotification();
```

### 修复能力标志枚举

```cpp
// 来源: EditorSysConfigFeature.h
enum class EEditorSysConfigFeatureRemediationFlags : uint32
{
    NoAutomatedRemediation      = 0,        // 无自动修复，仅提示
    HasAutomatedRemediation     = 1 << 0,   // 支持自动修复
    RequiresElevation           = 1 << 1,   // 需要管理员权限
    RequiresApplicationRestart  = 1 << 2,   // 需要重启编辑器
#if PLATFORM_WINDOWS
    RequiresSystemRestart       = 1 << 3,   // 需要重启操作系统（仅 Windows）
#endif
};
```

## Demo 示例

一个完整的最小自定义检测功能示例（Editor 模块）：

**MySysCheck.Build.cs**:
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "EditorSysConfigAssistant",
    "UnrealEd",
});
```

**MySysCheckFeature.h**:
```cpp
#pragma once
#include "EditorSysConfigFeature.h"

class FMySysCheckFeature : public IEditorSysConfigFeature
{
public:
    virtual FText GetDisplayName() const override;
    virtual FText GetDisplayDescription() const override;
    virtual FGuid GetVersion() const override;
    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override;
    virtual void StartSystemCheck() override;
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override;
};
```

**MySysCheckModule.cpp**（StartupModule 片段）:
```cpp
#include "Features/IModularFeatures.h"
#include "MySysCheckFeature.h"

static FMySysCheckFeature Feature;

void FMySysCheckModule::StartupModule()
{
    IModularFeatures::Get().RegisterModularFeature(
        IEditorSysConfigFeature::GetModularFeatureName(), &Feature);
}

void FMySysCheckModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(
        IEditorSysConfigFeature::GetModularFeatureName(), &Feature);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、异步执行、路径工具 |
| `UnrealEd` | 编辑器引擎、通知管理、Tab 管理 |
| `InputCore` | 输入系统 |
| `InteractiveToolsFramework` | 交互工具框架 |
| `CoreUObject` | UObject 系统（私有） |
| `Engine` | 引擎核心（私有） |
| `Slate` / `SlateCore` | UI 框架（私有） |
| `ToolWidgets` | 编辑器工具 Widget（私有） |
| `WorkspaceMenuStructure` | 工作区菜单结构（私有） |
| `EditorSubsystem` | Editor Subsystem 基类（私有） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-11 | `3413adf5` | Ran UnrealCodeFixup to fix dll storage | 自动化代码修复，修正 DLL 导出符号（技术维护） |
| 2025-04-14 | `9cd415be` | Fix parsing of NtfsDisableLastAccessUpdate | 修复 NTFS Last Access Time 注册表值的解析逻辑 bug |
| 2025-04-08 | `3ec80dc5` | [EditorSysConfigAssistant] | 初始提交，插件功能完整实现 |

### 维护评价

- **创建时间**: 2023-10-19，约 2.5 年前
- **更新频率**: 2025 年 4 月集中开发，之后有一次维护修复
- **维护状态**: 维护中（2025 年有实质性 bug 修复）
- **实验性标记**: `IsExperimentalVersion: true`，`EnabledByDefault: false` → 需手动启用
- **平台限制**: 仅 Windows 平台有实际检测功能
- **推荐**: 如果你在 Windows 上开发大型项目且遇到编辑器启动慢的问题，值得启用试试。但由于标记为实验性且默认关闭，Epic 可能尚未将其视为正式功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/EditorSysConfigAssistant)
- 官方文档（无）
- 测试用例（未找到独立测试文件）
