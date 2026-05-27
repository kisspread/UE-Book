# Editor System Configuration Assistant

> Editor utility for offering system configuration suggestions

| 属性 | 值 |
|---|---|
| 中文名 | 系统配置助手 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Slate 界面资产） |
| 模块 | `EditorSysConfigAssistant` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-10-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant) | |

## 用途

这个插件是一个**编辑器级的系统配置检查与优化工具**。它解决的核心问题是：许多开发者在使用 UE5 时，由于操作系统级别的配置不是最优的，导致编辑器性能下降或开发体验不佳（例如 NTFS 文件系统的 Last Access Time 更新会拖慢大项目索引速度，USN Journal 未启用会影响文件监控效率等）。

插件采用**模块化特性（Modular Feature）模式**设计，内置的检查项（如 Windows 的 USN Journal 和 NTFS LastAccessTime）作为独立的 Feature 实现，第三方也可以注册自己的检查项，使得系统配置检查可以灵活扩展。当检测到配置不理想时，插件会通过编辑器通知提示用户，并提供一键修复或引导用户手动修改的选项。

**注意**：此插件目前为实验性状态，默认未启用，仅支持 Windows 平台的部分检查功能。

## 使用场景

- 你在 Windows 上进行 UE5 大型项目开发，希望编辑器运行更流畅 → 用此插件检测并优化系统级配置
- 你是技术美术或项目负责人，需要为团队统一开发环境的系统配置 → 用此插件批量检查和修复
- 你正在开发自定义的编辑器系统检查功能（如检测显卡驱动版本、磁盘空间等）→ 通过实现 `IEditorSysConfigFeature` 接口注册自定义检查项

## 蓝图用法

此插件的公开 API 主要通过 C++ 子系统暴露，蓝图可调用的节点有限，但核心操作均可通过蓝图触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanShowSystemConfigAssistant` | 检查当前是否可以展示系统配置助手界面 | `IEditorSysConfigAssistantModule` |
| `ShowSystemConfigAssistant` | 展示系统配置助手界面（打开 Tab/窗口） | `IEditorSysConfigAssistantModule` |
| `AddIssue` | 向子系统添加一个系统配置问题（任意线程安全） | `UEditorSysConfigAssistantSubsystem` |
| `GetIssues` | 获取当前所有系统配置问题列表（任意线程安全） | `UEditorSysConfigAssistantSubsystem` |
| `ApplySysConfigChanges` | 对选中的问题执行修复操作（必须在游戏线程调用） | `UEditorSysConfigAssistantSubsystem` |
| `DismissSystemConfigNotification` | 关闭系统配置通知弹窗（必须在游戏线程调用） | `UEditorSysConfigAssistantSubsystem` |

### 使用示例（蓝图描述）

**场景 1：通过蓝图触发系统配置检查**

1. 使用 `Get Game Instance` 节点获取游戏实例
2. 通过 `Get Editor Subsystem` 节点传入 `UEditorSysConfigAssistantSubsystem` 类，获取子系统引用
3. 调用 `Get Issues` 节点获取当前已检测到的问题列表
4. 将结果连接到 `For Each Loop` 节点遍历每个问题
5. 通过问题结构体的 `Feature` 指针访问 `Get Display Name` 获取问题名称

**场景 2：手动添加自定义检查问题**

1. 获取 `UEditorSysConfigAssistantSubsystem` 子系统引用
2. 构造 `FEditorSysConfigIssue` 结构体，设置 `Severity` 为 `High`/`Medium`/`Low`
3. 调用 `Add Issue` 节点将问题添加到子系统

## C++ 用法

### 头文件引入

```cpp
#include "EditorSysConfigAssistantSubsystem.h"
#include "EditorSysConfigAssistantModule.h"
#include "EditorSysConfigFeature.h"
#include "EditorSysConfigIssue.h"
```

### 基本用法

**获取子系统并查询问题**（来源：`EditorSysConfigAssistantSubsystem.h`）

```cpp
// 获取子系统实例
UEditorSysConfigAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
if (Subsystem)
{
    // 获取所有已检测到的系统配置问题
    TArray<TSharedPtr<FEditorSysConfigIssue>> Issues = Subsystem->GetIssues();
    
    for (const TSharedPtr<FEditorSysConfigIssue>& Issue : Issues)
    {
        // 获取问题的显示名称和严重程度
        FText Name = Issue->Feature->GetDisplayName();
        EEditorSysConfigIssueSeverity Severity = Issue->Severity;
        
        UE_LOG(LogTemp, Log, TEXT("问题: %s, 严重程度: %d"), *Name.ToString(), static_cast<int32>(Severity));
    }
}
```

**展示系统配置助手界面**（来源：`EditorSysConfigAssistantModule.h`）

```cpp
IEditorSysConfigAssistantModule& Module = IEditorSysConfigAssistantModule::Get();

// 先检查是否可以展示
if (Module.CanShowSystemConfigAssistant())
{
    // 展示系统配置助手 UI
    Module.ShowSystemConfigAssistant();
}
```

### 进阶用法

**实现自定义系统配置检查特性**（来源：`EditorSysConfigFeature.h`）

通过实现 `IEditorSysConfigFeature` 接口并注册为 Modular Feature，可以添加自定义的系统配置检查项：

```cpp
// MyCustomSysConfigFeature.h
#include "EditorSysConfigFeature.h"

class FMyCustomSysConfigFeature : public IEditorSysConfigFeature
{
public:
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MySysConfig", "CustomFeature", "自定义磁盘空间检查");
    }

    virtual FText GetDisplayDescription() const override
    {
        return NSLOCTEXT("MySysConfig", "CustomFeatureDesc", 
            "检查项目所在磁盘是否有足够的可用空间以保证编译和打包正常进行。");
    }

    virtual FGuid GetVersion() const override
    {
        return FGuid(0x12345678, 0xABCD, 0xEF01, {0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0x01});
    }

    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override
    {
        // 此检查无自动化修复方案
        return EEditorSysConfigFeatureRemediationFlags::NoAutomatedRemediation;
    }

    // 从游戏线程调用，鼓励异步执行实际检查
    virtual void StartSystemCheck() override
    {
        Async(EAsyncExecution::Thread, [this]()
        {
            // 异步执行磁盘空间检查
            bool bHasEnoughSpace = CheckDiskSpace();
            
            if (!bHasEnoughSpace)
            {
                // 在游戏线程上报告问题
                AsyncTask(ENamedThreads::GameThread, [this]()
                {
                    FEditorSysConfigIssue Issue;
                    Issue.Feature = this;
                    Issue.Severity = EEditorSysConfigIssueSeverity::High;
                    
                    UEditorSysConfigAssistantSubsystem* Subsystem = 
                        GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
                    if (Subsystem)
                    {
                        Subsystem->AddIssue(Issue);
                    }
                });
            }
        });
    }

    // 从游戏线程调用，必须同步完成
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override
    {
        // 此检查无自动化修复
        // OutElevatedCommands 可以输出需要管理员权限执行的命令
    }

private:
    bool CheckDiskSpace()
    {
        // 实际的磁盘空间检查逻辑
        return true;
    }
};

// 注册 Modular Feature（通常在模块 StartupModule 中）
FMyCustomSysConfigFeature* CustomFeature = new FMyCustomSysConfigFeature();
IModularFeatures::Get().RegisterModularFeature(
    IEditorSysConfigFeature::GetModularFeatureName(), 
    CustomFeature);
```

**应用系统配置修复**（来源：`EditorSysConfigAssistantSubsystem.h`）

```cpp
// 应用修复（必须在游戏线程调用）
UEditorSysConfigAssistantSubsystem* Subsystem = 
    GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();

if (Subsystem)
{
    TArray<TSharedPtr<FEditorSysConfigIssue>> Issues = Subsystem->GetIssues();
    
    // 筛选出需要修复的高优先级问题
    TArray<TSharedPtr<FEditorSysConfigIssue>> HighSeverityIssues;
    for (const TSharedPtr<FEditorSysConfigIssue>& Issue : Issues)
    {
        if (Issue->Severity == EEditorSysConfigIssueSeverity::High)
        {
            HighSeverityIssues.Add(Issue);
        }
    }
    
    // 批量应用修复
    Subsystem->ApplySysConfigChanges(HighSeverityIssues);
    
    // 关闭通知
    Subsystem->DismissSystemConfigNotification();
}
```

## Demo 示例

以下是一个完整的最小示例，实现一个自定义系统检查并在编辑器启动时自动注册：

**MySysConfigCheckModule.h**

```cpp
#pragma once

#include "Modules/ModuleManager.h"
#include "EditorSysConfigFeature.h"
#include "EditorSysConfigAssistantSubsystem.h"

class FMySysConfigCheckFeature : public IEditorSysConfigFeature
{
public:
    virtual FText GetDisplayName() const override;
    virtual FText GetDisplayDescription() const override;
    virtual FGuid GetVersion() const override;
    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override;
    virtual void StartSystemCheck() override;
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override;
};

class FMySysConfigCheckModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FMySysConfigCheckFeature* RegisteredFeature = nullptr;
};
```

**MySysConfigCheckModule.cpp**

```cpp
#include "MySysConfigCheckModule.h"

#define LOCTEXT_NAMESPACE "MySysConfigCheck"

FText FMySysConfigCheckFeature::GetDisplayName() const
{
    return LOCTEXT("FeatureName", "Virtual Memory Check");
}

FText FMySysConfigCheckFeature::GetDisplayDescription() const
{
    return LOCTEXT("FeatureDesc", 
        "Checks if system virtual memory is configured to at least 16GB "
        "for optimal large project compilation performance.");
}

FGuid FMySysConfigCheckFeature::GetVersion() const
{
    return FGuid(0xA1B2C3D4, 0xE5F6, 0x7890, {0xAB, 0xCD, 0xEF, 0x12, 0x34, 0x56, 0x78, 0x90});
}

EEditorSysConfigFeatureRemediationFlags FMySysConfigCheckFeature::GetRemediationFlags() const
{
    // 无自动化修复，但可以提示用户手动修改
    return EEditorSysConfigFeatureRemediationFlags::NoAutomatedRemediation;
}

void FMySysConfigCheckFeature::StartSystemCheck()
{
    // 异步执行检查，避免阻塞游戏线程
    Async(EAsyncExecution::Thread, [WeakThis = MakeWeakObjectPtr(Cast<UObject>(nullptr))]()
    {
        // 示例：检查虚拟内存大小（伪代码）
        bool bVirtualMemorySufficient = true; // 替换为实际检查逻辑
        
        if (!bVirtualMemorySufficient)
        {
            AsyncTask(ENamedThreads::GameThread, []()
            {
                if (GEditor)
                {
                    UEditorSysConfigAssistantSubsystem* Subsystem = 
                        GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
                    if (Subsystem)
                    {
                        FEditorSysConfigIssue Issue;
                        Issue.Feature = nullptr; // 需要指向已注册的 feature 实例
                        Issue.Severity = EEditorSysConfigIssueSeverity::Medium;
                        Subsystem->AddIssue(Issue);
                    }
                }
            });
        }
    });
}

void FMySysConfigCheckFeature::ApplySysConfigChanges(TArray<FString>& OutElevatedCommands)
{
    // 无自动化修复，输出提示信息即可
    // OutElevatedCommands 可用于传递需要管理员权限的命令
}

void FMySysConfigCheckModule::StartupModule()
{
    RegisteredFeature = new FMySysConfigCheckFeature();
    IModularFeatures::Get().RegisterModularFeature(
        IEditorSysConfigFeature::GetModularFeatureName(), 
        RegisteredFeature);
}

void FMySysConfigCheckModule::ShutdownModule()
{
    if (RegisteredFeature)
    {
        IModularFeatures::Get().UnregisterModularFeature(
            IEditorSysConfigFeature::GetModularFeatureName(), 
            RegisteredFeature);
        delete RegisteredFeature;
        RegisteredFeature = nullptr;
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySysConfigCheckModule, MySysConfigCheck)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ModularFeatures` | 提供 Modular Feature 注册/发现机制，用于注册自定义系统检查项 |
| `ToolWidgets` | 提供 SSimpleButton 等工具级 Slate 控件，用于问题列表中的操作按钮 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 自动化代码规范化：将析构函数改为 `= default` 写法 |
| 2025-07-12 | `3413adf5` | Ran UnrealCodeFixup to fix dll storage | 自动化修复 DLL 导出符号存储属性 |
| 2025-04-14 | `9cd415be` | Fix parsing of NtfsDisableLastAccessUpdate for EditorSysConfigAssistant | 修复 NTFS LastAccessUpdate 注册表值解析逻辑 |
| 2025-04-08 | `3ec80dc5` | [EditorSysConfigAssistant] | EditorSysConfigAssistant 相关改动（具体信息未在消息中说明） |
| 2025-04-08 | `c8a6ed6e` | [EditorSysConfigAssistant] | EditorSysConfigAssistant 相关改动（具体信息未在消息中说明） |

### 维护评价

**总体评价：实验性状态，维护不活跃**

- **年龄**：创建于 2023 年 10 月，约 2 年历史，属于较新的插件
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，`EnabledByDefault=false`，表明 Epic 尚未将其视为稳定功能
- **更新频率**：自创建以来更新非常稀疏。2025 年 4 月有一次针对 NTFS 解析 bug 的实质性修复，其余均为 Epic 全局自动化代码修复脚本的波及修改
- **功能成熟度**：内置的 Windows 检查项（USN Journal、LastAccessTime）非常有限，整体功能较基础
- **平台支持**：当前仅 Windows 平台有实际的系统检查实现（`RequiresSystemRestart` 标记用 `#if PLATFORM_WINDOWS` 保护）
- **API 稳定性**：接口设计清晰（`IEditorSysConfigFeature` 模块化特性模式），但由于实验性状态，API 随时可能变动

⚠️ **警告**：此插件目前处于实验性状态，默认未启用。虽然模块化特性接口设计良好，适合作为扩展点，但不建议在生产项目中依赖此插件的核心功能。适合用于了解系统配置检查的实现思路，或作为自定义系统检查功能的参考框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant)
- 官方文档：无
- 测试用例：无（此插件未包含自动化测试）