# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 创建时间未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途

此插件旨在提供一个图形化、可视化的界面来管理虚幻引擎中的控制台变量（Console Variables, CVars）。传统的命令行或控制台方式管理大量CVars时效率低下且容易出错。本插件通过一个基于Slate的编辑器面板，允许用户将特定的CVars集合保存为资产（`.uasset`），方便地加载、编辑和应用这些预设。它特别适用于需要快速在不同渲染、调试或项目配置间切换的场景，并且通过集成Concert同步插件，支持多用户环境下的配置同步，是虚拟制片和复杂项目开发中的高效工具。

## 使用场景

- **虚拟制片现场**：在电影拍摄现场，需要根据不同镜头、灯光或环境快速切换一组渲染和后期处理参数（如曝光、色调映射、LUT），使用本插件可以一键加载预设。
- **开发调试**：开发者可以保存多组用于不同测试场景的CVars（如启用/禁用特定渲染特性、开启调试可视化），并能在它们之间快速切换。
- **配置管理**：技术美术（TA）可以创建并共享不同美术风格或性能等级的CVars配置包，并通过资产的形式进行版本管理。
- **多用户协作**：在基于Concert的多用户编辑会话中，通过本插件管理的CVars配置可以被同步或快速分享给团队成员。

## 蓝图用法

核心资产类 `UConsoleVariablesAsset` 提供了丰富的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Saved Commands` | 获取资产中保存的原始命令数据数组 | `UConsoleVariablesAsset` |
| `Get Saved Commands As String Array` | 以字符串数组形式获取保存的命令 | `UConsoleVariablesAsset` |
| `Get Saved Commands As Comma Separated String` | 以逗号分隔的单个字符串形式获取命令，适合传递给命令行 | `UConsoleVariablesAsset` |
| `Execute Saved Commands` | 执行资产中保存的所有命令 | `UConsoleVariablesAsset` |
| `Add Or Set Console Object Saved Data` | 添加新的CVar数据或更新已存在的同名CVar数据 | `UConsoleVariablesAsset` |
| `Find Saved Data By Command String` | 根据命令名称字符串查找对应的保存数据 | `UConsoleVariablesAsset` |
| `Remove Console Variable` | 根据命令名称移除一个CVar | `UConsoleVariablesAsset` |
| `Replace Saved Commands` | 用新的数据完全替换资产中原有的保存数据 | `UConsoleVariablesAsset` |
| `Copy From` / `Add From` | 从另一个 `UConsoleVariablesAsset` 复制或追加变量数据 | `UConsoleVariablesAsset` |

### 使用示例（蓝图描述）

1.  **创建并保存一组变量**：
    - 使用 “Create Asset” 节点创建一个 `UConsoleVariablesAsset` 实例。
    - 调用 “Set Variable Collection Description” 节点为其添加描述。
    - 创建 `FConsoleVariablesEditorAssetSaveData` 结构体，设置 `CommandName` (如 `r.DefaultFeature.AntiAliasing`) 和 `CommandValueAsString` (如 `2`)。
    - 调用 “Add Or Set Console Object Saved Data” 节点将此数据添加到资产中。重复此过程添加多个变量。
    - 通过右键菜单或资产编辑器保存此资产。

2.  **应用一个预设**：
    - 通过 “Load Asset” 节点加载一个已保存的 `UConsoleVariablesAsset`。
    - 直接调用 “Execute Saved Commands” 节点，将所有保存的变量应用到当前世界/编辑器。

3.  **获取预设用于命令行**：
    - 加载资产后，调用 “Get Saved Commands As Comma Separated String” 节点。
    - 将返回的字符串传递给 “Execute Console Command” 节点或用作外部程序的参数。

## C++ 用法

主要围绕 `UConsoleVariablesAsset` 和 `FConsoleVariablesEditorAssetSaveData` 结构体进行操作。

### 头文件引入

```cpp
#include "ConsoleVariablesAsset.h"
```

### 基本用法

```cpp
// 创建或加载资产
UConsoleVariablesAsset* CVarAsset = NewObject<UConsoleVariablesAsset>();
// 或从路径加载: UConsoleVariablesAsset* CVarAsset = LoadObject<UConsoleVariablesAsset>(nullptr, TEXT("/Game/MyCVars"));

// 设置描述
CVarAsset->SetVariableCollectionDescription(TEXT("Quality Settings - High"));

// 准备并添加一个CVar数据
FConsoleVariablesEditorAssetSaveData NewCVarData;
NewCVarData.CommandName = TEXT("r.Streaming.PoolSize");
NewCVarData.CommandValueAsString = TEXT("2048");
NewCVarData.CheckedState = ECheckBoxState::Checked;
CVarAsset->AddOrSetConsoleObjectSavedData(NewCVarData);

// 执行资产中的所有命令
CVarAsset->ExecuteSavedCommands(GetWorld());

// 查询
TArray<FString> CommandStrings = CVarAsset->GetSavedCommandsAsStringArray(true);
FString CommandLineArgs = CVarAsset->GetSavedCommandsAsCommaSeparatedString(false);
```

### 进阶用法

```cpp
// 查找并修改特定CVar
FConsoleVariablesEditorAssetSaveData FoundData;
if (CVarAsset->FindSavedDataByCommandString(TEXT("r.Streaming.PoolSize"), FoundData))
{
    FoundData.CommandValueAsString = TEXT("4096"); // 更新值
    CVarAsset->AddOrSetConsoleObjectSavedData(FoundData); // 重新设置，会更新原数据
}

// 从另一个资产合并
UConsoleVariablesAsset* OtherAsset = LoadObject<UConsoleVariablesAsset>(...);
CVarAsset->AddFrom(OtherAsset); // 追加
// 或 CVarAsset->CopyFrom(OtherAsset); // 完全覆盖

// 移除一个变量
CVarAsset->RemoveConsoleVariable(TEXT("r.Streaming.PoolSize"));
```

## Demo 示例

```cpp
// MyCVarManager.h
#pragma once
#include "CoreMinimal.h"
#include "ConsoleVariablesAsset.h"
#include "MyCVarManager.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyCVarManager : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere)
    UConsoleVariablesAsset* DebugPresetAsset;

    UFUNCTION(BlueprintCallable)
    void InitializeDebugPreset();

    UFUNCTION(BlueprintCallable)
    void ToggleDebugVisualization(bool bEnable);
};

// MyCVarManager.cpp
#include "MyCVarManager.h"

void UMyCVarManager::InitializeDebugPreset()
{
    if (!DebugPresetAsset)
    {
        DebugPresetAsset = NewObject<UConsoleVariablesAsset>();
    }
    
    DebugPresetAsset->SetVariableCollectionDescription(TEXT("Debug Visualization Preset"));
    
    // 添加一个用于显示碰撞体的CVar
    FConsoleVariablesEditorAssetSaveData CollisionData;
    CollisionData.CommandName = TEXT("ShowFlag.Collision");
    CollisionData.CommandValueAsString = TEXT("1"); // 1 = 启用
    CollisionData.CheckedState = ECheckBoxState::Checked;
    DebugPresetAsset->AddOrSetConsoleObjectSavedData(CollisionData);
}

void UMyCVarManager::ToggleDebugVisualization(bool bEnable)
{
    if (DebugPresetAsset)
    {
        // 直接修改已保存数据的状态并执行
        // 注意：更严谨的做法是遍历并修改CheckedState，这里为示例简化
        // 我们假设资产中只有一个用于调试的CVar
        const TArray<FConsoleVariablesEditorAssetSaveData>& SavedCommands = DebugPresetAsset->GetSavedCommands();
        if (SavedCommands.Num() > 0)
        {
            FConsoleVariablesEditorAssetSaveData ModifiedData = SavedCommands[0];
            ModifiedData.CheckedState = bEnable ? ECheckBoxState::Checked : ECheckBoxState::Unchecked;
            // 构建临时资产来执行，或者修改原资产（这会持久化修改）
            UConsoleVariablesAsset* TempAsset = NewObject<UConsoleVariablesAsset>();
            TempAsset->AddOrSetConsoleObjectSavedData(ModifiedData);
            TempAsset->ExecuteSavedCommands(GetWorld());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConcertSyncClient`, `ConcertSyncCore`, `ConcertMain`, `ConcertSharedSlate` | 支持与Concert多用户系统的集成，实现CVars配置的同步和共享 |
| `Slate`, `SlateCore` | 构建插件的核心编辑器UI面板 |
| `PropertyEditor` | 集成到虚幻编辑器的属性面板中，提供资产编辑界面 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the... | 将多个虚拟制片资产归类到更合适的资产分类下，进行目录结构优化。 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复控制台变量编辑器中复制粘贴功能的显示问题。 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 为控制台变量编辑器添加复制和粘贴功能。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | 调整了内容浏览器中“添加”菜单的部分布局。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，可能涉及日志系统的改进或规范化。 |

### 维护评价

该插件目前处于**活跃维护**状态。从近期提交记录看，开发团队持续为其添加新功能（如复制粘贴支持）和优化用户体验（如UI修复、资产分类）。作为Epic官方虚拟制片工具链的一部分，其代码质量和兼容性有保障。插件依赖于Concert系统，表明其设计面向团队协作和专业工作流。创建时间未知，但从近期更新看，它是一个现代化且被重视的工具。

**推荐使用**：对于需要管理复杂或团队共享CVars配置的项目，尤其是虚拟制片相关项目，强烈推荐使用此插件。它将命令行操作提升到了图形化资产管理的层级。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)
- [官方文档]() (暂无特定文档链接)