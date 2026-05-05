# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-31 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

Console Variables Editor 是一个编辑器面板插件，提供了一个 Slate UI 界面来集中管理 Unreal Engine 的控制台变量（CVar）和控制台命令。它解决的核心问题是：在虚拟制片（Virtual Production）工作流中，团队需要频繁调整大量 CVar（如渲染设置、后处理参数等），但原生的控制台只有一个命令行输入框，无法批量管理、保存预设、或在多用户协作环境中同步变量变更。

此插件提供了：
- **预设系统**：将一组 CVar 保存为 `UConsoleVariablesAsset`，可随时加载/切换
- **可视化管理**：以列表形式展示所有 CVar，支持搜索、过滤、勾选/取消勾选
- **值追踪**：记录每个变量的启动值、当前值、设置来源（Source）
- **Multi-User 同步**：通过 Concert 多用户系统同步 CVar 变更
- **蓝图 API**：提供 `BlueprintCallable` 函数库，可在运行时/编辑器脚本中操作 CVar
- **Sequencer 集成**：实现 `IMovieSceneConsoleVariableTrackInterface`，可在 Sequencer 轨道中控制 CVar

⚠️ 注意：此插件标记为 `IsBetaVersion=true`，且 `EnabledByDefault=false`，需要在 Edit → Plugins 中手动启用。

## 使用场景

- **虚拟制片调色/灯光**：你在做 LED Volume 拍摄，需要快速切换多组渲染 CVar 预设（如 `r.ScreenPercentage`、`r.DefaultFeature.AntiAliasing` 等）→ 用 Console Variables Editor 保存预设，一键切换
- **性能分析工作流**：你需要在不同画质档位之间快速切换，对比帧率表现 → 创建多个预设（Low/Medium/High），通过 CVE 面板快速切换
- **团队协作**：你的团队使用 Multi-User Editing，需要确保所有人的 CVar 保持同步 → 启用 Multi-User CVar Sync，变更自动广播
- **Sequencer 动画**：你需要在过场动画中动态改变渲染参数 → 将 CVE 预设资产拖入 Sequencer 的 Console Variable Track
- **自动化脚本**：你需要在构建管线或测试脚本中批量设置 CVar → 使用蓝图函数库的 `SetConsoleVariableByName_*` 节点

## 蓝图用法

### 核心节点

#### 预设管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCurrentlyLoadedPreset` | 返回当前编辑器中加载的预设资产 | `UConsoleVariablesEditorFunctionLibrary` |
| `LoadPresetIntoConsoleVariablesEditor` | 将指定资产加载到 CVE 面板并应用所有变量值 | `UConsoleVariablesEditorFunctionLibrary` |
| `CopyCurrentListToAsset` | 将当前 CVE 列表保存到指定资产（不自动保存到磁盘） | `UConsoleVariablesEditorFunctionLibrary` |
| `AddValidatedCommandToCurrentPreset` | 向当前预设添加一条已验证的命令 | `UConsoleVariablesEditorFunctionLibrary` |
| `RemoveCommandFromCurrentPreset` | 从当前预设中移除一条命令 | `UConsoleVariablesEditorFunctionLibrary` |
| `GetListOfCommandsFromPreset` | 获取预设中所有命令名称列表 | `UConsoleVariablesEditorFunctionLibrary` |

#### 直接设置 CVar

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetConsoleVariableByName_Float` | 按名称设置浮点型 CVar | `UConsoleVariablesEditorFunctionLibrary` |
| `SetConsoleVariableByName_Bool` | 按名称设置布尔型 CVar | `UConsoleVariablesEditorFunctionLibrary` |
| `SetConsoleVariableByName_Int` | 按名称设置整型 CVar | `UConsoleVariablesEditorFunctionLibrary` |
| `SetConsoleVariableByName_String` | 按名称设置字符串型 CVar | `UConsoleVariablesEditorFunctionLibrary` |
| `GetConsoleVariableStringValue` | 获取 CVar 的当前字符串值 | `UConsoleVariablesEditorFunctionLibrary` |
| `GetConsoleVariableSourceByName` | 获取 CVar 的设置来源（如 "Console"、"Project Setting" 等） | `UConsoleVariablesEditorFunctionLibrary` |

#### Multi-User 同步

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetEnableMultiUserCVarSync` | 获取 Multi-User CVar 同步是否启用 | `UConsoleVariablesEditorFunctionLibrary` |
| `SetEnableMultiUserCVarSync` | 启用/禁用 Multi-User CVar 同步 | `UConsoleVariablesEditorFunctionLibrary` |

#### 预设资产操作（UConsoleVariablesAsset 上的方法）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteSavedCommands` | 执行资产中保存的所有命令 | `UConsoleVariablesAsset` |
| `GetSavedCommandsAsStringArray` | 以字符串数组形式返回保存的命令 | `UConsoleVariablesAsset` |
| `GetSavedCommandsAsCommaSeparatedString` | 以逗号分隔字符串返回命令（适合命令行） | `UConsoleVariablesAsset` |
| `FindSavedDataByCommandString` | 按名称查找保存的变量数据 | `UConsoleVariablesAsset` |
| `AddOrSetConsoleObjectSavedData` | 添加或更新一个 CVar 的保存数据 | `UConsoleVariablesAsset` |
| `RemoveConsoleVariable` | 从资产中移除一个 CVar | `UConsoleVariablesAsset` |
| `CopyFrom` | 从另一个资产完全复制变量列表 | `UConsoleVariablesAsset` |
| `AddFrom` | 从另一个资产追加变量（已存在的会更新值） | `UConsoleVariablesAsset` |
| `ReplaceSavedCommands` | 完全替换保存数据 | `UConsoleVariablesAsset` |
| `GetSavedCommandsCount` | 返回保存的变量数量 | `UConsoleVariablesAsset` |
| `SetVariableCollectionDescription` | 设置预设的描述文本 | `UConsoleVariablesAsset` |
| `GetVariableCollectionDescription` | 获取预设的描述文本 | `UConsoleVariablesAsset` |

### 使用示例（蓝图描述）

**加载预设并应用**：
1. 获取一个 `UConsoleVariablesAsset` 资产引用（如通过变量或 Get Asset 节点）
2. 调用 `LoadPresetIntoConsoleVariablesEditor`，传入资产和导入模式（`AddToExisting` 或 `ReplaceExisting`）
3. CVE 面板会自动打开并加载该预设中的所有 CVar

**运行时批量设置 CVar**：
1. 使用 `SetConsoleVariableByName_Float` 节点，传入 CVar 名称如 `"r.ScreenPercentage"` 和目标值 `50.0`
2. 对每个需要调整的 CVar 重复此操作

**导出预设为命令行参数**：
1. 获取 `UConsoleVariablesAsset` 引用
2. 调用 `GetSavedCommandsAsCommaSeparatedString`，`bOnlyIncludeChecked` 设为 `true`
3. 输出的字符串可直接用于命令行 `-ExecCmds` 参数

## C++ 用法

### 头文件引入

```cpp
// 函数库（蓝图可调用 API）
#include "ConsoleVariablesEditorFunctionLibrary.h"

// 预设资产类
#include "ConsoleVariablesAsset.h"

// 编辑器模块（高级用法）
#include "ConsoleVariablesEditorModule.h"

// 命令信息结构体（高级用法）
#include "ConsoleVariablesEditorCommandInfo.h"
```

### 基本用法

**设置 CVar 值**（来源：`ConsoleVariablesEditorFunctionLibrary.cpp`）：

```cpp
#include "ConsoleVariablesEditorFunctionLibrary.h"

// 设置浮点 CVar
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(
    TEXT("r.ScreenPercentage"), 75.0f);

// 设置布尔 CVar
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Bool(
    TEXT("r.DefaultFeature.AntiAliasing"), true);

// 设置整型 CVar
UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Int(
    TEXT("r.ShadowQuality"), 3);

// 获取 CVar 当前值
FString OutValue;
if (UConsoleVariablesEditorFunctionLibrary::GetConsoleVariableStringValue(
        TEXT("r.ScreenPercentage"), OutValue))
{
    UE_LOG(LogTemp, Log, TEXT("r.ScreenPercentage = %s"), *OutValue);
}
```

**操作预设资产**（来源：`ConsoleVariablesAsset.cpp`）：

```cpp
#include "ConsoleVariablesAsset.h"

// 创建一个预设并添加变量
UConsoleVariablesAsset* MyPreset = NewObject<UConsoleVariablesAsset>();

FConsoleVariablesEditorAssetSaveData SaveData;
SaveData.CommandName = TEXT("r.ScreenPercentage");
SaveData.CommandValueAsString = TEXT("100");
SaveData.CheckedState = ECheckBoxState::Checked;
MyPreset->AddOrSetConsoleObjectSavedData(SaveData);

// 在运行时执行预设中保存的所有命令
MyPreset->ExecuteSavedCommands(GetWorld(), true);

// 导出为逗号分隔字符串（可用于命令行）
FString CmdLine = MyPreset->GetSavedCommandsAsCommaSeparatedString(true);
// 输出: "r.ScreenPercentage 100"
```

### 进阶用法

**直接使用模块 API 查找和操作 CVar**（来源：`ConsoleVariablesEditorModule.cpp`）：

```cpp
#include "ConsoleVariablesEditorModule.h"
#include "ConsoleVariablesEditorCommandInfo.h"

// 获取编辑器模块实例
FConsoleVariablesEditorModule& Module = FConsoleVariablesEditorModule::Get();

// 按名称查找已追踪的 CVar
TWeakPtr<FConsoleVariablesEditorCommandInfo> Info = 
    Module.FindCommandInfoByName(TEXT("r.ScreenPercentage"));

if (Info.IsValid())
{
    TSharedPtr<FConsoleVariablesEditorCommandInfo> Pinned = Info.Pin();
    
    // 获取启动时的值
    FString StartupValue = Pinned->StartupValueAsString;
    
    // 获取设置来源
    EConsoleVariableFlags Source = Pinned->GetSource();
    FText SourceText = Pinned->GetSourceAsText();
    
    // 执行命令（保持 SetBy 标志）
    Pinned->ExecuteCommand(TEXT("50.0"), true, true, false);
    
    // 获取当前值
    FString CurrentValue;
    if (Pinned->GetCurrentValueAsString(CurrentValue))
    {
        UE_LOG(LogTemp, Log, TEXT("Current: %s"), *CurrentValue);
    }
}

// 搜索匹配的 CVar（支持 OR 和 AND 搜索）
TArray<FString> Tokens = { TEXT("shadow quality") }; // AND 搜索
TArray<TWeakPtr<FConsoleVariablesEditorCommandInfo>> Results = 
    Module.FindCommandInfosMatchingTokens(Tokens);
```

**Multi-User CVar 同步控制**（来源：`ConsoleVariablesEditorFunctionLibrary.cpp`）：

```cpp
// 检查 Multi-User 同步状态
bool bSyncEnabled = UConsoleVariablesEditorFunctionLibrary::GetEnableMultiUserCVarSync();

// 启用同步
UConsoleVariablesEditorFunctionLibrary::SetEnableMultiUserCVarSync(true);
```

## Demo 示例

### 最小可用示例：运行时设置 CVar

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ConsoleVariablesEditorRuntime"  // 预设资产类
});
```

**MyCVarManager.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCVarManager.generated.h"

class UConsoleVariablesAsset;

UCLASS()
class AMyCVarManager : public AActor
{
    GENERATED_BODY()

public:
    // 在编辑器中指定预设资产
    UPROPERTY(EditAnywhere, Category = "CVar Manager")
    TObjectPtr<UConsoleVariablesAsset> QualityPreset;

    // 应用预设中保存的所有 CVar
    UFUNCTION(BlueprintCallable, Category = "CVar Manager")
    void ApplyPreset();

    // 动态设置单个 CVar
    UFUNCTION(BlueprintCallable, Category = "CVar Manager")
    void SetScreenPercentage(float Percentage);
};
```

**MyCVarManager.cpp**：

```cpp
#include "MyCVarManager.h"
#include "ConsoleVariablesAsset.h"
#include "ConsoleVariablesEditorFunctionLibrary.h"

void AMyCVarManager::ApplyPreset()
{
    if (QualityPreset)
    {
        // 执行预设中所有勾选的命令
        QualityPreset->ExecuteSavedCommands(GetWorld(), true);
        
        UE_LOG(LogTemp, Log, TEXT("Applied preset: %s (%d variables)"),
            *QualityPreset->GetVariableCollectionDescription(),
            QualityPreset->GetSavedCommandsCount());
    }
}

void AMyCVarManager::SetScreenPercentage(float Percentage)
{
    UConsoleVariablesEditorFunctionLibrary::SetConsoleVariableByName_Float(
        TEXT("r.ScreenPercentage"), Percentage);
}
```

## 模块依赖

### ConsoleVariablesEditorRuntime（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | 引擎核心（GEngine、World 等） |
| `MovieSceneTracks` | Sequencer 集成（IMovieSceneConsoleVariableTrackInterface） |
| `CoreUObject` | UObject 系统 |
| `SlateCore` | Slate 基础类型（ECheckBoxState 等） |

### ConsoleVariablesEditor（UncookedOnly 模块）

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `OutputLog` | 输出日志面板集成 |
| `AssetRegistry` | 资产注册表查询 |
| `AssetTools` | 资产类型操作注册 |
| `CoreUObject` | UObject 系统 |
| `Concert` | Multi-User 基础框架 |
| `ConcertSharedSlate` | Multi-User 共享 UI |
| `ConcertSyncClient` | Multi-User 同步客户端 |
| `ConcertSyncCore` | Multi-User 同步核心 |
| `ConcertTransport` | Multi-User 传输层 |
| `ConsoleVariablesEditorRuntime` | 本插件的 Runtime 模块（预设资产） |
| `ContentBrowser` | 内容浏览器集成 |
| `Engine` | 引擎核心 |
| `EditorStyle` | 编辑器样式 |
| `EditorWidgets` | 编辑器通用控件 |
| `InputCore` | 输入系统 |
| `Kismet` | 蓝图函数库基类 |
| `Projects` | 项目/插件信息 |
| `PropertyEditor` | 属性编辑器 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心 |
| `ToolMenus` | 工具菜单注册 |
| `ToolWidgets` | 工具控件 |
| `UnrealEd` | 编辑器核心 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |

## 架构概览

### 模块划分

```
ConsoleVariablesEditor (UncookedOnly)
├── Views/
│   ├── MainPanel/          ← 主面板 UI（SConsoleVariablesEditorMainPanel）
│   ├── List/               ← 变量列表 UI
│   │   ├── SConsoleVariablesEditorList      ← 列表控件
│   │   ├── SConsoleVariablesEditorListRow   ← 行控件
│   │   ├── SConsoleVariablesEditorListValueInput ← 值输入控件
│   │   └── ConsoleVariablesEditorListFilters/ ← 过滤器系统
│   │       ├── IConsoleVariablesEditorListFilter ← 过滤器接口
│   │       ├── ...Filter_ShowOnlyVariables       ← 仅显示变量
│   │       ├── ...Filter_ShowOnlyCommands        ← 仅显示命令
│   │       ├── ...Filter_ShowOnlyModifiedVariables ← 仅显示已修改
│   │       ├── ...Filter_SetInSession            ← 会话中设置
│   │       ├── ...Filter_SetByCurrentPreset      ← 当前预设设置
│   │       └── ...Filter_Source                  ← 按来源过滤
│   └── Widgets/
│       └── SConsoleVariablesEditorCustomConsoleInputBox ← 自定义输入框
├── MultiUser/
│   ├── ConsoleVariableSync.h/cpp        ← Multi-User 同步管理器
│   ├── ConsoleVariableSyncData.h        ← 同步数据结构（UConcertCVarSynchronization 等）
│   ├── ConcertConsoleVariableSyncCustomization.h    ← Concert 同步自定义
│   └── ConcertConsoleVariableSessionCustomization.h/cpp ← Concert 会话自定义
├── Factories/ConsoleVariablesEditorFactory ← 资产工厂
├── AssetTypeActions/                        ← 资产类型操作
├── ConsoleVariablesEditorModule.h/cpp       ← 主模块
├── ConsoleVariablesEditorFunctionLibrary.h/cpp ← 蓝图函数库
├── ConsoleVariablesEditorCommandInfo.h/cpp  ← CVar 命令信息结构
├── ConsoleVariablesEditorProjectSettings.h  ← 项目设置
└── ConsoleVariablesEditorStyle.h/cpp        ← 编辑器样式

ConsoleVariablesEditorRuntime (Runtime)
├── ConsoleVariablesAsset.h/cpp              ← 预设资产类（UConsoleVariablesAsset）
└── ConsoleVariablesEditorRuntimeLog.h       ← 日志分类
```

### 核心类型

| 类型 | 说明 |
|---|---|
| `UConsoleVariablesAsset` | 预设资产，存储一组 CVar 名称/值/勾选状态。实现 `IMovieSceneConsoleVariableTrackInterface` 以支持 Sequencer |
| `FConsoleVariablesEditorAssetSaveData` | 资产中每个 CVar 的序列化数据（CommandName、ValueAsString、CheckedState） |
| `FConsoleVariablesEditorCommandInfo` | 单个 CVar/命令的运行时信息，包含启动值、当前值、来源标志、变更回调 |
| `UConsoleVariablesEditorFunctionLibrary` | 蓝图函数库，提供静态方法操作 CVar 和预设 |
| `UConsoleVariablesEditorProjectSettings` | 项目设置（行显示模式、导入模式、自动追踪变更等） |
| `FConsoleVariablesEditorModule` | 编辑器主模块，管理 UI 面板、变量追踪、Multi-User 同步 |
| `FConsoleVariablesEditorList` | 变量列表逻辑层，管理预设/全局搜索两种模式 |
| `IConsoleVariablesEditorListFilter` | 列表过滤器接口（MatchAny/MatchAll 两种匹配类型） |

### CVar 来源追踪

插件追踪每个 CVar 的 `SetBy` 标志，支持以下来源：

| 来源 | 说明 |
|---|---|
| Constructor | 代码中构造时设置 |
| Scalability | 可扩展性设置 |
| Game Setting | 游戏设置 |
| Project Setting | 项目设置 |
| System Settings ini | 系统设置 INI 文件 |
| Device Profile | 设备配置文件 |
| Game Override | 游戏覆盖 |
| Console Variables ini | ConsoleVariables.ini 文件 |
| Command line | 命令行参数 |
| Code | 代码中设置 |
| Console | 控制台手动输入 |
| Preview | 预览模式 |

### 列表过滤器

CVE 面板提供内置过滤器，可组合使用：

| 过滤器 | 说明 | 匹配类型 |
|---|---|---|
| Show Only Variables | 仅显示 CVar（排除命令） | MatchAny |
| Show Only Commands | 仅显示控制台命令 | MatchAny |
| Show Only Modified | 仅显示值被修改过的变量 | MatchAny |
| Set In Session | 仅显示在当前会话中设置过的变量 | MatchAny |
| Set By Current Preset | 仅显示被当前预设设置过的变量 | MatchAny |
| Source | 按设置来源过滤 | MatchAny |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-24 | `44a13f28967a` | Fix display of console variables when in Preview mode | 修复 Preview 模式下 CVar 显示问题，属于 bug 修复 |
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 批量添加内联生成代码宏，代码质量维护 |
| 2025-05-30 | `8396b185774c` | Updated headers using UnrealCodeFixup | 批量修复 DLL 导出声明，代码质量维护 |

### 维护评价

- **创建时间**：2022-01-31，约 4 年历史
- **维护频率**：最近一次实质性 bug 修复在 2025-07-24，整体保持维护
- **活跃度**：**活跃维护中**。虽然近期提交多为代码质量维护（UnrealCodeFixup），但仍在持续跟进
- **Beta 状态**：标记为 `IsBetaVersion=true`，但自 2022 年创建至今已有 4 年，功能相对成熟
- **已知限制**：
  - 默认禁用（`EnabledByDefault=false`），需手动启用
  - Multi-User CVar 同步在 PIE（Play In Editor）期间暂停
  - 依赖 Concert 插件系列（Multi-User Editing），如果未启用这些插件，Multi-User 功能不可用
- **推荐程度**：**推荐使用**，尤其适合虚拟制片和需要批量管理 CVar 的工作流。虽然标记为 Beta，但功能完整且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/ConsoleVariablesEditor)
- 官方文档：无（.uplugin 中 DocsURL 为空）
