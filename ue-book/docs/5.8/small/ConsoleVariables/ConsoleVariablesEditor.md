# Console Variables Editor

> Save, load and control Console Variables (cvars) from this panel using Slate.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 控制台变量编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ConsoleVariablesEditor` (UncookedOnly), `ConsoleVariablesEditorRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-04-13 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor) | |

## 用途
该插件为UE提供了一个可视化的控制台变量管理面板。它解决了在开发、测试和虚拟制片过程中，手动记忆和输入大量控制台命令（Console Variables， cvars）的痛点。开发者和艺术家可以通过该面板浏览、搜索、筛选所有可用的控制台变量，实时查看和修改其值，并将特定的变量集合保存为“预设”（`UConsoleVariablesAsset`）进行加载和管理。它还集成了Multi-User编辑功能，支持在团队协作会话中同步控制台变量的更改。

## 使用场景
- 你在进行虚拟制片，需要频繁切换不同的渲染设置（如 `r.ScreenPercentage`, `r.DefaultFeature.AntiAliasing`）以平衡画质与性能。
- 你是一名技术美术，正在调试材质或特效，需要批量开启或关闭一系列相关的控制台变量（如 `r.Material.EditorPerformanceMode`）。
- 你需要分析性能，需要同时跟踪 `stat unit`, `stat fps` 等命令，并将结果与特定的变量配置关联。
- 你需要与团队共享一套特定的控制台变量配置（例如，用于特定场景的渲染调试配置），并希望通过资产来管理和分发。

## 蓝图用法
该插件提供了 `UConsoleVariablesEditorFunctionLibrary` 蓝图函数库，允许在运行时通过蓝图与编辑器面板进行交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Currently Loaded Preset` | 返回当前在控制台变量编辑器面板中加载的预设资产。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Load Preset Into Console Variables Editor` | 将给定的 `UConsoleVariablesAsset` 加载到编辑器面板中，并设置其所有变量值。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Copy Current List To Asset` | 将编辑器面板中的当前变量列表保存到给定的资产中（资产不会自动保存到磁盘）。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Add Validated Command To Current Preset` | 向当前预设中添加一个经过验证的命令及其当前值。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Remove Command From Current Preset` | 从当前预设中移除一个命令（如果存在）。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Get List Of Commands From Preset` | 从给定的预设资产中获取所有命令名称的列表。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Set Console Variable By Name (Float/Bool/Int/String)` | 根据名称直接设置控制台变量的值。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Get Console Variable String Value` | 根据名称直接获取控制台变量的字符串值。 | `UConsoleVariablesEditorFunctionLibrary` |
| `Get/Set Enable Multi-User CVar Sync` | 获取或设置当前编辑器实例的Multi-User同步功能是否启用。 | `UConsoleVariablesEditorFunctionLibrary` |

### 使用示例（蓝图描述）
1.  **加载预设**：在蓝图中，调用 `Load Preset Into Console Variables Editor` 节点，将你的一个 `UConsoleVariablesAsset` 引用作为输入。这会立即将该预设中的所有变量应用到场景中，并在编辑器面板中显示。
2.  **程序化修改变量**：使用 `Set Console Variable By Name (Float)` 节点，将变量名（如 `“r.ScreenPercentage”`）和目标值（如 `100.0`）作为输入，即可直接修改该变量，效果与在控制台输入命令相同。
3.  **保存当前配置**：调用 `Copy Current List To Asset` 节点，并将一个 `UConsoleVariablesAsset` 变量作为输入，可以将面板中当前的所有变量配置快照保存到该资产中，便于后续调用或分享给团队。

## C++ 用法
核心交互通过 `FConsoleVariablesEditorModule` 单例完成，通常用于编辑器工具或自定义的资产编辑器集成。

### 头文件引入
```cpp
#include "ConsoleVariablesEditorModule.h"
#include "ConsoleVariablesEditorFunctionLibrary.h" // 用于蓝图函数库的静态方法
```

### 基本用法
以下示例展示了如何在C++中以编程方式打开编辑器面板并加载一个预设。
*(来源: `ConsoleVariablesEditorModule.h` 接口)*
```cpp
// 获取模块实例
FConsoleVariablesEditorModule& CVEModule = FConsoleVariablesEditorModule::Get();

// 打开编辑器面板，并加载指定的预设资产
UConsoleVariablesAsset* MyPreset = /* 你的预设资产引用 */;
CVEModule.OpenConsoleVariablesDialogWithPreset(MyPreset);

// 查找特定变量信息
TWeakPtr<FConsoleVariablesEditorCommandInfo> Info = CVEModule.FindCommandInfoByName(TEXT(“r.ScreenPercentage”));
if (Info.IsValid())
{
    // Info.Pin()->GetCurrentValueAsString(...)
}
```

### 进阶用法
在自定义编辑器工具中，可能需要监听变量变化并触发列表刷新。
*(来源: `ConsoleVariablesEditorModule.h` 委托与方法)*
```cpp
// 假设你有一个自定义的编辑器工具，希望与CVE面板联动
void MyEditorTool::Setup()
{
    // 模块会在变量改变时调用此回调
    // 通常通过重写 OnConsoleVariableChanged 或连接到模块提供的委托
}

// 当外部逻辑添加了一个变量，需要通知CVE面板刷新列表
void MyEditorTool::AddNewCVar(const FString& Command, const FString& Value)
{
    FConsoleVariablesEditorModule& CVEModule = FConsoleVariablesEditorModule::Get();
    // 验证并添加到当前预设
    CVEModule.ValidateConsoleInputAndAddToCurrentPreset(FText::FromString(Command + TEXT(“ “) + Value));
    // 重建列表以显示新添加的变量
    CVEModule.RebuildList(Command);
}
```

## Demo 示例
一个最小的C++示例，演示如何在编辑器工具中触发控制台变量编辑器打开特定预设。
```cpp
// MyAssetEditor.h
#pragma once
#include “CoreMinimal.h”
#include “ConsoleVariablesAsset.h” // 预设资产类
#include “MyAssetEditor.generated.h”

UCLASS()
class UMyAssetEditor : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere)
    TObjectPtr<UConsoleVariablesAsset> AssociatedCVMPreset;

    UFUNCTION(BlueprintCallable)
    void OpenAssociatedPresetInCVM() const;
};

// MyAssetEditor.cpp
#include “MyAssetEditor.h”
#include “ConsoleVariablesEditorModule.h”

void UMyAssetEditor::OpenAssociatedPresetInCVM() const
{
    if (AssociatedCVMPreset)
    {
        FConsoleVariablesEditorModule& CVEModule = FConsoleVariablesEditorModule::Get();
        CVEModule.OpenConsoleVariablesDialogWithPreset(AssociatedCVMPreset);
    }
}
```

## 模块依赖
要使用此插件的功能，你的项目模块需要依赖其提供的库。

| 模块 | 用途 |
|---|---|
| `ConsoleVariablesEditorRuntime` | 提供运行时可用的蓝图函数库 (`UConsoleVariablesEditorFunctionLibrary`)。 |
| `ConsoleVariablesEditor` | 提供编辑器面板的核心逻辑和UI，仅在编辑器中使用 (`UncookedOnly`)。 |
| `ConcertSyncClient`, `ConcertSyncCore`, `ConcertMain`, `ConcertSharedSlate` | 为Multi-User编辑会话中的控制台变量同步功能提供支持。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整了虚拟制片相关资产的分类。 |
| 2026-05-12 | `de91208d` | CVAR Editor - Copy/Paste Cosmetic Fixes | 修复了控制台变量编辑器中复制/粘贴功能的显示问题。 |
| 2026-04-22 | `0f1a8af2` | Copy / Paste support for Console Variable Editor | 为控制台变量编辑器添加了复制/粘贴变量名和值的支持。 |
| 2026-04-14 | `c19c7e83` | [ContentBrowser] New Add Menu Misc Menu | (此提交为通用引擎改动，非插件专属功能) |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新的UE_LOGF宏。 |

### 维护评价
- **年龄**：插件创建于2021年，约有5年历史。
- **近期活跃度**：在2026年4-5月有持续的更新，增加了实用的复制/粘贴功能并进行了一些UI修复，表明插件仍在**积极维护**中。
- **功能完整性**：插件功能完善，涵盖了预设管理、变量浏览筛选、多用户同步等核心需求。
- **已知限制**：该插件主要在编辑器环境中使用（`UncookedOnly` 模块），其蓝图函数库（`Runtime` 模块）允许在打包后的游戏中进行一定程度的程序化控制。
- **推荐**：**强烈推荐**使用。这是UE官方提供的、功能强大且持续维护的控制台变量管理工具，能显著提升美术、开发和测试人员的工作效率，尤其在虚拟制片流程中价值巨大。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ConsoleVariablesEditor)
- [官方文档]() （暂无）
- [测试用例]() （源码中未发现独立测试目录）