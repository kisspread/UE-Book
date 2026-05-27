# Editor Sys Config Assistant

> Editor utility for offering system configuration suggestions

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器系统配置助手 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `EditorSysConfigAssistant` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-10-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant) | |

## 用途

EditorSysConfigAssistant 是一个**编辑器子系统插件**，用于检测 Windows 系统级配置是否对 UE5 开发体验最优，并在发现问题时向用户展示建议和一键修复按钮。

当前内置了两项 Windows NTFS 文件系统检查：

1. **USN Journal** — 检查 NTFS 卷的 USN 日志是否已启用（UE5 的文件监视依赖此功能）
2. **Last Access Time** — 检查 NTFS 的"最后访问时间"更新是否已禁用（关闭此项可减少不必要的磁盘写入，提升 I/O 性能）

该插件采用**模块化特性（Modular Feature）** 架构，其他插件可以注册自定义的 `IEditorSysConfigFeature` 检查项，扩展系统配置建议的范围。检测到问题后，会在编辑器中弹出通知，用户可以一键应用修复，部分修复需要管理员权限或系统重启。

## 使用场景

- 你在 Windows 上使用 UE5 开发，希望获得最佳 I/O 性能 → 启用此插件自动检测并修复 NTFS 配置
- 你正在开发一个需要检查编辑器环境配置的工具插件 → 注册 `IEditorSysConfigFeature` 来添加自定义检查项
- 你希望通过编辑器通知系统引导用户完成系统级配置优化 → 使用 `AddIssue` + 通知机制

## 蓝图用法

此插件**不提供蓝图 API**。所有功能均通过 C++ 接口和模块化特性系统暴露。

## C++ 用法

### 头文件引入

```cpp
#include "EditorSysConfigAssistantSubsystem.h"
#include "EditorSysConfigAssistantModule.h"
#include "EditorSysConfigFeature.h"
#include "EditorSysConfigIssue.h"
```

### 基本用法 — 显示配置助手 UI

```cpp
// 获取模块接口并显示系统配置助手
if (IEditorSysConfigAssistantModule::Get().CanShowSystemConfigAssistant())
{
    IEditorSysConfigAssistantModule::Get().ShowSystemConfigAssistant();
}
```

### 基本用法 — 添加自定义检查项

```cpp
// 在任何线程中向子系统报告一个系统配置问题
UEditorSysConfigAssistantSubsystem* Subsystem = GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
if (Subsystem)
{
    FEditorSysConfigIssue Issue;
    Issue.Feature = this;  // IEditorSysConfigFeature* 指针
    Issue.Severity = EEditorSysConfigIssueSeverity::High;
    
    Subsystem->AddIssue(Issue);
}
```

### 进阶用法 — 实现自定义系统配置检查

```cpp
// 自定义系统配置检查特性
class FMySysConfigFeature : public IEditorSysConfigFeature
{
public:
    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyConfig", "DisplayName", "My Custom Check");
    }
    
    virtual FText GetDisplayDescription() const override
    {
        return NSLOCTEXT("MyConfig", "Desc", "Checks a custom system setting.");
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
        // 异步检查系统配置...
        // 检查完成后，如果发现问题，调用 Subsystem->AddIssue()
    }
    
    // 从游戏线程调用，必须同步完成
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override
    {
        // 应用系统配置更改
        // 如果需要管理员权限，将命令追加到 OutElevatedCommands
    }
};
```

注册特性到 Modular Feature 系统：

```cpp
// 在模块启动时注册
FMySysConfigFeature* MyFeature = new FMySysConfigFeature();
IModularFeatures::Get().RegisterModularFeature(IEditorSysConfigFeature::GetModularFeatureName(), MyFeature);
```

## Demo 示例

完整的自定义系统配置检查特性实现：

**MySysConfigFeature.h**
```cpp
#pragma once

#include "EditorSysConfigFeature.h"

class FMySysConfigFeature : public IEditorSysConfigFeature
{
public:
    virtual ~FMySysConfigFeature() = default;

    // IEditorSysConfigFeature 接口
    virtual FText GetDisplayName() const override;
    virtual FText GetDisplayDescription() const override;
    virtual FGuid GetVersion() const override;
    virtual EEditorSysConfigFeatureRemediationFlags GetRemediationFlags() const override;
    virtual void StartSystemCheck() override;
    virtual void ApplySysConfigChanges(TArray<FString>& OutElevatedCommands) override;
};
```

**MySysConfigFeature.cpp**
```cpp
#include "MySysConfigFeature.h"
#include "EditorSysConfigAssistantSubsystem.h"

FText FMySysConfigFeature::GetDisplayName() const
{
    return NSLOCTEXT("MySysConfig", "Name", "Example System Check");
}

FText FMySysConfigFeature::GetDisplayDescription() const
{
    return NSLOCTEXT("MySysConfig", "Description", 
        "This is an example system configuration check that demonstrates how to extend the assistant.");
}

FGuid FMySysConfigFeature::GetVersion() const
{
    return FGuid(0xAABBCCDD, 0xEEFF, 0x0011, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99);
}

EEditorSysConfigFeatureRemediationFlags FMySysConfigFeature::GetRemediationFlags() const
{
    return EEditorSysConfigFeatureRemediationFlags::HasAutomatedRemediation;
}

void FMySysConfigFeature::StartSystemCheck()
{
    // 执行系统检查（可异步）
    bool bSystemNeedsChange = /* 检查逻辑 */;
    
    if (bSystemNeedsChange)
    {
        UEditorSysConfigAssistantSubsystem* Subsystem = 
            GEditor->GetEditorSubsystem<UEditorSysConfigAssistantSubsystem>();
        
        if (Subsystem)
        {
            FEditorSysConfigIssue Issue;
            Issue.Feature = this;
            Issue.Severity = EEditorSysConfigIssueSeverity::Medium;
            Subsystem->AddIssue(Issue);
        }
    }
}

void FMySysConfigFeature::ApplySysConfigChanges(TArray<FString>& OutElevatedCommands)
{
    // 应用修复逻辑
    // 如需管理员权限，追加到 OutElevatedCommands
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该插件依赖的标准模块包括：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`, `InputCore`, `EditorSubsystem`, `ModularFeatures`, `ToolWidgets`, `StatusBar`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码风格修复，析构函数改用 `= default` |
| 2025-07-12 | `3413adf5` | Ran UnrealCodeFixup to fix dll storage | 修复 DLL 导出宏标记 |
| 2025-04-14 | `9cd415be` | Fix parsing of NtfsDisableLastAccessUpdate for EditorSysConfigAssistant | 修复 NTFS 最后访问时间配置的解析逻辑 |
| 2025-04-08 | `3ec80dc5` | [EditorSysConfigAssistant] | 编辑器系统配置助手更新 |
| 2025-04-08 | `c8a6ed6e` | [EditorSysConfigAssistant] | 编辑器系统配置助手更新 |

### 维护评价

- **状态**：实验性插件，标记为 `IsExperimentalVersion=true`，默认未启用
- **年龄**：创建于 2023 年 10 月，约 2 年历史
- **活跃度**：2025 年 4 月有实质性功能更新和 bug 修复，之后为自动化代码整理，整体处于维护中状态
- **已知限制**：当前仅包含 Windows 平台的 NTFS 文件系统检查（USN Journal 和 Last Access Time），其他平台暂无实现
- **推荐**：如果你在 Windows 上开发并希望自动优化系统配置，可以启用此插件。由于仍是实验性功能，建议关注后续更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/EditorSysConfigAssistant)