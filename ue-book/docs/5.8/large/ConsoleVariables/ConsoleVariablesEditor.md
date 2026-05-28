# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Slate 面板资产、样式资源） |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-04-01 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

这个插件提供了一个基于 Slate 的可视化编辑器面板，用于管理和控制引擎的 Console Variables (cvars) 和 Console Commands。它解决的核心问题是：在虚拟制片和大型项目中，开发者需要频繁调整大量控制台变量（如渲染设置、LOD 参数、后处理参数等），传统的控制台命令行输入方式效率低下且难以管理。

该插件的实际功能远超 `.uplugin` 描述所涵盖的范围：

- **Preset 管理**：将 cvar 集合保存为 `UConsoleVariablesAsset` 资产，支持导入/导出、添加/替换模式切换
- **全局搜索**：支持跨 Preset 的全局变量搜索，使用 token 匹配（OR/AND 组合搜索）
- **值追踪**：记录每个变量的启动值、预设值、当前值，并以不同来源（Source）标签区分
- **过滤系统**：按来源（Constructor/Scalability/GameSetting/ProjectSetting 等）、类型（变量/命令）、修改状态等过滤
- **排序与拖拽**：支持按列排序、列表项拖拽重排
- **复制/粘贴**：支持复制变量名、变量名+值、仅值，以及粘贴操作
- **Multi-User 同步**：通过 Concert 框架在多用户编辑会话中同步 cvar 变更，防止 ping-pong 更新
- **自动追踪**：在编辑器启动时自动查询并追踪所有控制台变量的变化

## 使用场景

- 你在进行虚拟制片，需要在不同拍摄场景之间快速切换一组渲染参数（如阴影质量、后处理设置） → 保存为 Preset，一键加载
- 你在做性能调试，需要同时监控和调整多个 cvar 并记录当前配置 → 使用编辑器面板集中管理
- 你的团队使用 Multi-User 编辑，需要在多个节点间同步控制台变量设置 → 启用 Multi-User CVar Sync
- 你需要排查某个 cvar 被谁修改过（来源追踪：Code/Console/GameSetting 等） → 使用 Source 过滤列
- 你想在蓝图中批量设置或读取控制台变量 → 使用 `UConsoleVariablesEditorFunctionLibrary`

## 蓝图用法

插件提供了 `UConsoleVariablesEditorFunctionLibrary` 作为蓝图函数库，所有函数均为 `BlueprintCallable`。

### Preset 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Currently Loaded Preset` | 返回编辑器中当前加载的 Preset 资产 | `UConsoleVariablesEditorFunctionLibrary` |
| `Load Preset Into Console Variables Editor` | 加载指定 Preset 到编辑器并设置所有变量值，支持导入模式选择 | `UConsoleVariablesEditorFunctionLibrary` |
| `Copy Current List To Asset` | 将当前编辑器列表保存到指定资产（不会自动保存到磁盘） | `UConsoleVariablesEditorFunctionLibrary` |
| `Get List Of Commands From Preset` | 获取 Preset 中所有命令名列表 | `UConsoleVariablesEditorFunctionLibrary` |

### 变量操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Validated Command To Current Preset` | 将命令添加到当前 Preset（带验证） | `UConsoleVariablesEditorFunctionLibrary` |
| `Remove Command From Current Preset` | 从当前 Preset 中移除命令 | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Console Variable By Name (Float)` | 按名称设置浮点型 cvar | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Console Variable By Name (Bool)` | 按名称设置布尔型 cvar | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Console Variable By Name (Int)` | 按名称设置整型 cvar | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Console Variable By Name (String)` | 按名称设置字符串型 cvar | `UConsoleVariablesEditorFunctionLibrary` |
| `Get Console Variable String Value` | 按名称获取 cvar 的字符串值 | `UConsoleVariablesEditorFunctionLibrary` |
| `Get Console Variable Source By Name` | 获取 cvar 的设置来源 | `UConsoleVariablesEditorFunctionLibrary` |

### Multi-User 设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Enable Multi User CVar Sync` | 查询当前实例的 Multi-User CVar 同步是否启用 | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Enable Multi User CVar Sync` | 启用或禁用当前实例的 Multi-User CVar 同步 | `UConsoleVariablesEditorFunctionLibrary` |

### 使用示例（蓝图描述）

**批量设置 cvar 并保存为 Preset：**

1. 使用 `Create Asset` 节点创建一个 `ConsoleVariablesAsset`
2. 调用 `Load Preset Into Console Variables Editor` 将其加载（Import Mode 选 `ReplaceExisting`）
3. 对需要调整的每个 cvar，调用对应的 `Set Console Variable By Name` 节点
4. 调用 `Add Validated Command To Current Preset` 将已修改的变量加入 Preset
5. 调用 `Copy Current List To Asset` 将当前列表保存到资产
6. 使用 `Save Asset To Disk`（标准引擎节点）持久化资产

**从 Preset 恢复设置：**

1. 使用 `Load Object From Path` 加载 `ConsoleVariablesAsset`
2. 调用 `Load Preset Into Console Variables Editor`，Import Mode 选 `ReplaceExisting`
3. 所有变量将恢复为 Preset 中记录的值

## C++ 用法

### 头文件引入

```cpp
#include "ConsoleVariablesEditorModule.h"
#include "ConsoleVariablesEditorFunctionLibrary.h"
#include "ConsoleVariablesEditorCommandInfo.h"
```

### 基本用法

**访问模块并管理 Preset：**

```cpp
// 获取模块单例
FConsoleVariablesEditorModule& CVEModule = FConsoleVariablesEditorModule::Get();

// 打开编辑器面板并加载指定 Preset
UConsoleVariablesAsset* MyPreset = LoadObject<UConsoleVariablesAsset>(nullptr, TEXT("/Game/MyCVarsPreset"));
CVEModule.OpenConsoleVariablesDialogWithPreset(MyPreset);

// 保存当前 Preset
CVEModule.SavePreset();

// 另存为新 Preset
CVEModule.SavePresetAs();

// 刷新列表（保留当前值缓存）
CVEModule.RebuildList();

// 仅刷新过滤和排序（变量数量未变时使用）
CVEModule.RefreshList();
```

**搜索和查询已追踪的变量：**

```cpp
// 按名称查找单个变量
TWeakPtr<FConsoleVariablesEditorCommandInfo> Info = CVEModule.FindCommandInfoByName(TEXT("r.ScreenPercentage"));

if (TSharedPtr<FConsoleVariablesEditorCommandInfo> Pinned = Info.Pin())
{
    // 获取当前值
    FString CurrentValue;
    if (Pinned->GetCurrentValueAsString(CurrentValue))
    {
        UE_LOG(LogTemp, Log, TEXT("r.ScreenPercentage = %s"), *CurrentValue);
    }

    // 获取来源信息
    FText SourceText = Pinned->GetSourceAsText();
    UE_LOG(LogTemp, Log, TEXT("Source: %s"), *SourceText.ToString());
}

// 使用 token 搜索多个变量（支持 OR 和 AND 组合）
TArray<FString> Tokens = { TEXT("r. Screen"), TEXT("shadow") };
TArray<TWeakPtr<FConsoleVariablesEditorCommandInfo>> Results = CVEModule.FindCommandInfosMatchingTokens(Tokens);

for (const auto& Result : Results)
{
    if (TSharedPtr<FConsoleVariablesEditorCommandInfo> Pinned = Result.Pin())
    {
        UE_LOG(LogTemp, Log, TEXT("Found: %s"), *Pinned->Command);
    }
}
```

### 进阶用法

**直接执行控制台命令并通过 Multi-User 同步：**

```cpp
// 创建 CommandInfo 并执行命令
FConsoleVariablesEditorCommandInfo CommandInfo(TEXT("r.ScreenPercentage"));
CommandInfo.ExecuteCommand(TEXT("100.0"), true);  // bShouldTransactInConcert = true，同步到 Multi-User

// 打印变量当前状态（类似在控制台手动输入命令的输出）
CommandInfo.PrintCommandOrVariable();

// 获取变量的帮助文本
FString HelpText = CommandInfo.GetHelpText();
```

**使用蓝图函数库进行程序化操作：**

```cpp
#include "ConsoleVariablesEditorFunctionLibrary.h"

// 批量设置 cvar
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(TEXT("r.ScreenPercentage"), 100.0f);
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Int(TEXT("r.ShadowQuality"), 4);
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Bool(TEXT("r.DefaultFeature.Bloom"), false);

// 获取变量值
FString Value;
UConsoleVariablesEditorFunctionLibrary::GetConsoleVariableStringValue(TEXT("r.ScreenPercentage"), Value);

// 加载 Preset
UConsoleVariablesAsset* Preset = LoadObject<UConsoleVariablesAsset>(nullptr, TEXT("/Game/CVars/DefaultQuality"));
UConsoleVariablesEditorFunctionLibrary::LoadPresetIntoConsoleVariablesEditor(
    Preset, 
    EConsoleVariablesEditorPresetImportMode::ReplaceExisting
);

// 控制 Multi-User 同步
bool bIsSynced = UConsoleVariablesEditorFunctionLibrary::GetEnableMultiUserCVarSync();
UConsoleVariablesEditorFunctionLibrary::SetEnableMultiUserCVarSync(true);
```

## Demo 示例

一个最小的编辑器工具模块示例，在编辑器中使用控制台变量编辑器 API：

**MyCVarTool.h**

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyCVarTool
{
public:
    /** 初始化时批量设置一组渲染 cvar */
    static void ApplyQualityPreset(int32 QualityLevel);

    /** 将当前 cvar 状态保存为 Preset 资产 */
    static bool SaveCurrentCVarsToPreset(UConsoleVariablesAsset* TargetAsset);

    /** 从 Preset 恢复所有 cvar */
    static void RestoreFromPreset(UConsoleVariablesAsset* SourceAsset);
};
```

**MyCVarTool.cpp**

```cpp
#include "MyCVarTool.h"

#include "ConsoleVariablesEditorModule.h"
#include "ConsoleVariablesEditorFunctionLibrary.h"
#include "ConsoleVariablesAsset.h"

void FMyCVarTool::ApplyQualityPreset(int32 QualityLevel)
{
    switch (QualityLevel)
    {
    case 0: // Low
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(TEXT("r.ScreenPercentage"), 50.0f);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Int(TEXT("r.ShadowQuality"), 0);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Bool(TEXT("r.DefaultFeature.Bloom"), false);
        break;

    case 1: // Medium
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(TEXT("r.ScreenPercentage"), 75.0f);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Int(TEXT("r.ShadowQuality"), 2);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Bool(TEXT("r.DefaultFeature.Bloom"), true);
        break;

    case 2: // High
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(TEXT("r.ScreenPercentage"), 100.0f);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Int(TEXT("r.ShadowQuality"), 4);
        UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Bool(TEXT("r.DefaultFeature.Bloom"), true);
        break;
    }

    // 将变更同步到 Multi-User（如果启用）
    FConsoleVariablesEditorModule& CVEModule = FConsoleVariablesEditorModule::Get();
    CVEModule.RebuildList();
}

bool FMyCVarTool::SaveCurrentCVarsToPreset(UConsoleVariablesAsset* TargetAsset)
{
    if (!TargetAsset)
    {
        return false;
    }
    return UConsoleVariablesEditorFunctionLibrary::CopyCurrentListToAsset(TargetAsset);
}

void FMyCVarTool::RestoreFromPreset(UConsoleVariablesAsset* SourceAsset)
{
    if (!SourceAsset)
    {
        return;
    }
    UConsoleVariablesEditorFunctionLibrary::LoadPresetIntoConsoleVariablesEditor(
        SourceAsset,
        EConsoleVariablesEditorPresetImportMode::ReplaceExisting
    );
}
```

## 模块依赖

从 Build.cs 中的依赖项提取，以下为该插件**独特**的依赖模块：

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient` | Multi-User 编辑客户端同步 |
| `ConcertSyncCore` | Multi-User 编辑核心协议 |
| `ConcertMain` | Multi-User 编辑主模块 |
| `ConcertSharedSlate` | Multi-User 共享 Slate UI 组件 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the new content browser add menu | 将虚拟制片资产迁移到新的资产分类和内容浏览器添加菜单 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复复制/粘贴功能的界面显示问题 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 新增控制台变量编辑器的复制/粘贴功能 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 内容浏览器新增"添加"菜单分类调整 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移到 UE_LOGF 格式化宏 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐

- 该插件处于**持续活跃维护**状态，最近的更新（2026年4月-5月）集中在功能增强（复制/粘贴支持）和 UI 改进
- 作为虚拟制片（Virtual Production）类别下的核心工具插件，Epic 在持续投入开发
- Multi-User 集成（Concert 同步）表明其面向团队协作场景，功能设计成熟
- 包含完整的过滤、排序、搜索系统，API 设计规范（提供蓝图函数库）
- 默认启用且非实验性/非 Beta，表明已达到生产可用状态
- **推荐使用**：对于需要频繁调整控制台变量的项目（尤其是虚拟制片场景），这是必备工具

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)
- [官方文档]()（暂无）