# Editor System Configuration Assistant

> Editor utility for offering system configuration suggestions

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器系统配置助手 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Slate UI 界面资源） |
| 模块 | `EditorSysConfigAssistant` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-10-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant) | |

## 用途

这个插件用于在 UE5 编辑器启动时检测操作系统级别的配置问题，并向开发者提供建议以优化开发体验。

它解决的核心问题是：某些操作系统默认设置会严重影响 Unreal 项目的文件 I/O 性能，但开发者通常不知道需要调整这些设置。插件通过 **ModularFeature** 架构设计，允许以插件形式注册系统检查项，每个检查项会扫描系统配置并报告潜在问题。当前实现的两个检查项均针对 **Windows/NTFS** 文件系统：

1. **USN Journal（更新序列号日志）**：NTFS 的变更日志功能，启用后可加速文件监控和资产扫描
2. **Last Access Time（最后访问时间戳）**：NTFS 默认记录文件最后访问时间，禁用此功能可减少磁盘写入、提升 I/O 性能

检测到问题后，插件会通过编辑器通知系统提示用户，支持一键自动修复（含提权操作和重启提示）。

## 使用场景

- 你在 Windows 上使用 UE5 进行大型项目开发，编辑器启动缓慢或文件操作卡顿 → 启用此插件检测系统配置瓶颈
- 你的团队需要统一开发环境配置，确保 NTFS 设置优化到位 → 使用此插件自动检测和修复
- 你想扩展自定义的系统检查项（如虚拟内存、磁盘空间等）→ 实现 `IEditorSysConfigFeature` 接口并注册为 ModularFeature

## 蓝图用法

此插件主要为编辑器内部子系统，不暴露蓝图节点。所有交互通过编辑器 UI 和 C++ API 完成。

### 核心节点

该插件无蓝图可调用函数。功能通过编辑器子系统 API 在 C++ 层面使用。

## C++ 用法

### 头文件引入

```cpp
#include "EditorSysConfigAssistantModule.h"
#include "EditorSysConfigAssistantSubsystem.h"
#include "EditorSysConfigFeature.h"
#include "EditorSysConfigIssue.h"
```

### 基本用法

#### 获取模块接口并显示配置助手 UI

```cpp
// 检查是否可以显示配置助手
IEditorSysConfigAssistantModule& Module = IEditorSysConfigAssistantModule::Get();
if (Module.CanShowSystemConfigAssistant())
{
    Module.ShowSystemConfigAssistant();
}
```

#### 获取子系统并查询/处理问题

```cpp
// 从编辑器子系统获取实例
UEditorSysConfigAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
if (Subsystem)
{
    // 获取当前所有系统配置问题（线程安全）
    TArray<TSharedPtr<FEditorSysConfigIssue>> Issues = Subsystem->GetIssues();

    for (const TSharedPtr<FEditorSysConfigIssue>& Issue : Issues)
    {
        // 获取问题关联的功能特性
        IEditorSysConfigFeature* Feature = Issue->Feature;
        
        // 获取显示信息
        FText Name = Feature->GetDisplayName();
        FText Description = Feature->GetDisplayDescription();
        
        // 检查修复标志
        EEditorSysConfigFeatureRemediationFlags Flags = Feature->GetRemediationFlags();
        bool bHasAutoRemediation = EnumHasAnyFlags(Flags, EEditorSysConfigFeatureRemediationFlags::HasAutomatedRemediation);
        bool bRequiresElevation = EnumHasAnyFlags(Flags, EEditorSysConfigFeatureRemediationFlags::RequiresElevation);
    }

    // 应用修复（必须在游戏线程调用）
    Subsystem->ApplySysConfigChanges(Issues);
}
```

### 进阶用法

#### 自定义系统检查特性（通过 ModularFeature 注册）

```cpp
#include "EditorSysConfigFeature.h"

class FMyCustomSysConfigFeature : public IEditorSysConfigFeature
{
public:
    virtual ~FMyCustomSysConfigFeature() = default;

    virtual FText GetDisplayName() const override
    {
        return FText::FromString(TEXT("自定义系统检查"));
    }

    virtual FText GetDisplayDescription() const override
    {
        return FText::FromString(TEXT("检查自定义系统配置项"));
    }

    virtual FGuid GetVersion() const override
    {
        return FGuid(0x12345678, 0x1234, 0x1234, 0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0);
    }

    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override
    {
        return EEditorSysConfigFeatureRemediationFlags::HasAutomatedRemediation;
    }

    // 从游戏线程调用，鼓励异步执行
    virtual void StartSystemCheck() override
    {
        Async(EAsyncExecution::Thread, [this]()
        {
            // 异步执行系统检查
            bool bHasIssue = CheckMySystemConfig();
            
            if (bHasIssue)
            {
                // 通过子系统添加问题（线程安全）
                UEditorSysConfigAssistantSubsystem* Subsystem = 
                    GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
                if (Subsystem)
                {
                    FEditorSysConfigIssue NewIssue;
                    NewIssue.Feature = this;
                    NewIssue.Severity = EEditorSysConfigIssueSeverity::Medium;
                    Subsystem->AddIssue(NewIssue);
                }
            }
        });
    }

    // 从游戏线程调用，必须同步完成
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override
    {
        // 执行修复操作
        // 如需提权命令，添加到 OutElevatedCommands
        OutElevatedCommands.Add(TEXT("reg add \"HKLM\\...\" /v SomeValue /t REG_DWORD /d 1 /f"));
    }

private:
    bool CheckMySystemConfig()
    {
        // 实现你的检查逻辑
        return false;
    }
};

// 注册为 ModularFeature（在模块 StartupModule 中）
void FMyModule::StartupModule()
{
    static FMyCustomSysConfigFeature Feature;
    IModularFeatures::Get().RegisterModularFeature(
        IEditorSysConfigFeature::GetModularFeatureName(), 
        &Feature
    );
}

// 反注册（在模块 ShutdownModule 中）
void FMyModule::ShutdownModule()
{
    IModularFeatures::Get().UnregisterModularFeature(
        IEditorSysConfigFeature::GetModularFeatureName(), 
        &Feature
    );
}
```

## Demo 示例

一个完整的自定义系统配置检查特性的最小实现：

```cpp
// MySysConfigFeature.h
#pragma once

#include "EditorSysConfigFeature.h"

class FMyDiskSpaceCheckFeature : public IEditorSysConfigFeature
{
public:
    virtual ~FMyDiskSpaceCheckFeature() = default;

    // IEditorSysConfigFeature 接口
    virtual FText GetDisplayName() const override;
    virtual FText GetDisplayDescription() const override;
    virtual FGuid GetVersion() const override;
    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override;
    virtual void StartSystemCheck() override;
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override;

private:
    double AvailableSpaceGB = 0.0;
};
```

```cpp
// MySysConfigFeature.cpp
#include "MySysConfigFeature.h"
#include "EditorSysConfigAssistantSubsystem.h"
#include "Editor.h"

FText FMyDiskSpaceCheckFeature::GetDisplayName() const
{
    return FText::FromString(TEXT("磁盘空间不足"));
}

FText FMyDiskSpaceCheckFeature::GetDisplayDescription() const
{
    return FText::FromString(TEXT("系统盘可用空间低于 10GB，可能影响编辑器性能和编译缓存。"));
}

FGuid FMyDiskSpaceCheckFeature::GetVersion() const
{
    return FGuid(0xAABBCCDD, 0xEEFF, 0x0011, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99);
}

EEditorSysConfigFeatureRemediationFlags FMyDiskSpaceCheckFeature::GetRemediationFlags() const
{
    return EEditorSysConfigFeatureRemediationFlags::NoAutomatedRemediation;
}

void FMyDiskSpaceCheckFeature::StartSystemCheck()
{
    // 异步检查磁盘空间
    Async(EAsyncExecution::ThreadPool, [this]()
    {
        const FString RootPath = FPaths::ProjectDir();
        const int64 TotalBytes = 0;
        const int64 FreeBytes = 0;

        // 使用平台文件系统 API 获取可用空间
        FPlatformFileManager::Get().GetPlatformFile().GetFileSystemStats().GetFreeSpaceOnDisk(
            *RootPath, FreeBytes, TotalBytes);
        AvailableSpaceGB = static_cast<double>(FreeBytes) / (1024.0 * 1024.0 * 1024.0);

        if (AvailableSpaceGB < 10.0)
        {
            UEditorSysConfigAssistantSubsystem* Subsystem =
                GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
            if (Subsystem)
            {
                FEditorSysConfigIssue Issue;
                Issue.Feature = this;
                Issue.Severity = EEditorSysConfigIssueSeverity::Low;
                Subsystem->AddIssue(Issue);
            }
        }
    });
}

void FMyDiskSpaceCheckFeature::ApplySysConfigChanges(TArray<FString>& OutElevatedCommands)
{
    // 此检查无法自动修复，仅提示用户
    UE_LOG(LogTemp, Warning, TEXT("请手动清理磁盘空间，当前可用: %.1f GB"), AvailableSpaceGB);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 批量将析构函数改为 `= default` 语法 |
| 2025-07-12 | `3413adf5` | Ran UnrealCodeFixup to fix dll storage | 修复 DLL 导出/存储修饰符问题 |
| 2025-04-14 | `9cd415be` | Fix parsing of NtfsDisableLastAccessUpdate for EditorSysConfigAssistant | 修复 NTFS 最后访问时间设置的注册表解析逻辑 |
| 2025-04-08 | `3ec80dc5` | [EditorSysConfigAssistant] | 编辑器系统配置助手相关更新 |
| 2025-04-08 | `c8a6ed6e` | [EditorSysConfigAssistant] | 编辑器系统配置助手相关更新 |

### 维护评价

该插件创建于 2023 年 10 月，标记为**实验性**且**默认未启用**。代码规模较小（17 个源文件），当前仅实现两个 Windows 特定的系统检查项（USN Journal 和 Last Access Time）。

**积极方面**：
- 架构设计良好，通过 ModularFeature 接口可扩展自定义检查项
- 2025 年 4 月有实质性 bug 修复（NTFS 设置解析问题），说明仍在被使用和维护
- 子系统使用读写锁保证线程安全

**注意事项**：
- ⚠️ 标记为实验性功能（`IsExperimentalVersion=true`），不建议在生产环境中依赖
- ⚠️ 默认未启用（`EnabledByDefault=false`），需手动在插件设置中开启
- 当前仅支持 Windows 平台（NTFS 文件系统特性）
- 无官方文档，蓝图 API 不可用

**总体建议**：适合在 Windows 开发环境中作为性能优化辅助工具使用。如需扩展系统检查项，可参考其 ModularFeature 架构实现自定义特性。不建议将核心逻辑依赖于此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant)