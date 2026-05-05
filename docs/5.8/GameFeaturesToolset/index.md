# Game Features Toolset

> Toolset for listing, inspecting, and creating Game Feature Plugins via the AI Toolset Registry.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameFeaturesToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameFeaturesToolset) | |

## 用途

GameFeaturesToolset 是 UE5 AI 助手（AI Assistant）工具集生态的一部分。它通过 Toolset Registry 向 AI 助手暴露一组工具函数，使 AI 能够以编程方式与 Game Feature Plugin 系统交互。

具体来说，这个插件解决的问题是：**AI 助手无法直接操作 Game Feature Plugin**。Game Feature Plugin 是 UE5 的模块化游戏功能系统（用于 DLC、可选功能模块等），但其创建和管理流程涉及目录结构生成、.uplugin 文件编写、插件挂载、数据资产创建等多个步骤。本插件将这些操作封装为 AI 可调用的工具，让 AI 助手能够：

1. **列举**当前项目中所有已注册的 Game Feature Plugin
2. **检查**任意 Game Feature Plugin 的详细数据（GameFeatureData 资产及其包含的 Actions）
3. **创建**全新的 Game Feature Plugin（包括完整的目录结构、.uplugin 文件和初始数据资产）

所有函数都标记了 `AICallable` 元数据标签，而非 `BlueprintCallable`，说明这些工具专为 AI 助手设计，不直接暴露为蓝图节点。

## 使用场景

- 你正在使用 UE5 的 AI 助手功能，需要 AI 帮你管理 Game Feature Plugin → 启用此插件
- 你想通过 AI 对话快速创建一个新的 Game Feature Plugin（如 "ShooterCore"），而不手动搭建目录结构 → AI 助手会调用 `CreateGameFeaturePlugin`
- 你想让 AI 助手检查某个 Game Feature Plugin 包含哪些 Actions，以便进行分析或修改 → AI 助手会调用 `FindGameFeatureData` + `GetActions`
- 你需要 AI 助手列出项目中所有 Game Feature Plugin 以便选择操作目标 → AI 助手会调用 `ListGameFeatures`

## 蓝图用法

> **注意**：本插件的所有函数均标记为 `AICallable` 而非 `BlueprintCallable`，且类标记为 `Hidden`。这些函数**不能**直接在蓝图中作为节点使用，它们是通过 Toolset Registry 注册给 AI 助手系统的专用工具。

如果你需要在蓝图中操作 Game Feature Plugin，请直接使用 `GameFeatures` 模块提供的公开 API（如 `UGameFeaturesSubsystem`）。

### AI 工具列表

以下是本插件向 AI 助手注册的全部工具：

| 工具函数 | 说明 | 所在类 |
|---|---|---|
| `ListGameFeatures` | 返回所有已知 Game Feature Plugin 的名称列表（按字母排序）。判定标准：插件声明了对 "GameFeatures" 的依赖 | `UGameFeaturesToolset` |
| `FindGameFeatureData` | 根据插件名称查找并加载对应的 `UGameFeatureData` 资产 | `UGameFeaturesToolset` |
| `GetPluginName` | 从 `UGameFeatureData` 资产反查其所属的插件名称 | `UGameFeaturesToolset` |
| `GetActions` | 获取 `UGameFeatureData` 资产中定义的所有 `UGameFeatureAction` | `UGameFeaturesToolset` |
| `CreateGameFeaturePlugin` | 创建一个全新的 Game Feature Plugin（含目录结构、.uplugin、挂载、初始数据资产） | `UGameFeaturesToolset` |

### AI 助手调用示例（文字描述）

**场景：让 AI 助手列出所有 Game Feature Plugin 并检查其中一个**

1. AI 助手调用 `ListGameFeatures()` → 获得 `["ShooterCore", "InventorySystem", ...]`
2. AI 助手调用 `FindGameFeatureData("ShooterCore")` → 获得 `UGameFeatureData*` 指针
3. AI 助手调用 `GetActions(Data)` → 获得该插件注册的所有 Actions 列表

**场景：让 AI 助手创建新的 Game Feature Plugin**

1. 用户向 AI 助手描述需求："帮我创建一个名为 MyAbilitySystem 的 Game Feature Plugin"
2. AI 助手调用 `CreateGameFeaturePlugin("MyAbilitySystem", "Provides modular ability system")` → 返回新创建的 `UGameFeatureData*`
3. AI 助手可继续调用 `GetActions` 确认创建结果

## C++ 用法

> 本插件的函数设计目标是被 AI 工具系统调用，而非直接在 C++ 游戏代码中使用。以下内容仅供理解其内部实现和扩展参考。

### 头文件引入

```cpp
#include "GameFeaturesToolset.h"
```

### 基本用法

由于所有函数都是 `static` 且标记为 `AICallable`，它们由 Toolset Registry 框架自动发现和调用。以下是各函数的签名和行为说明：

```cpp
// 列举所有 Game Feature Plugin 名称
// 判定标准：插件的 .uplugin 中声明了对 "GameFeatures" 的依赖
TArray<FString> Names = UGameFeaturesToolset::ListGameFeatures();
// 返回值示例: ["ShooterCore", "InventorySystem"]

// 根据插件名获取 GameFeatureData 资产
// 如果插件不存在、不是 Game Feature Plugin、或资产加载失败，会触发脚本错误
UGameFeatureData* Data = UGameFeaturesToolset::FindGameFeatureData(TEXT("ShooterCore"));

// 从 GameFeatureData 反查插件名称
FString Name = UGameFeaturesToolset::GetPluginName(Data);
// 返回值示例: "ShooterCore"

// 获取 GameFeatureData 中的所有 Actions
TArray<UGameFeatureAction*> Actions = UGameFeaturesToolset::GetActions(Data);
```

### 进阶用法：创建 Game Feature Plugin

```cpp
// 创建全新的 Game Feature Plugin
// 这会完成以下步骤：
//   1. 创建插件目录结构
//   2. 写入 .uplugin 文件
//   3. 挂载插件
//   4. 创建初始 GameFeatureData 资产
//
// PluginName 要求：
//   - 非空
//   - 唯一（不能与已有插件重名）
//   - 仅包含字母、数字和下划线（如 "ShooterCore"，不能是 "My-Plugin"）
//
// 注意：此函数应在获得用户明确指示/许可后才调用
UGameFeatureData* NewData = UGameFeaturesToolset::CreateGameFeaturePlugin(
    TEXT("MyAbilitySystem"),
    TEXT("Provides modular ability system for the project")
);
```

## Demo 示例

以下展示如何扩展 `UToolsetDefinition` 创建自定义工具集，参考本插件的实现模式：

```cpp
// MyCustomToolset.h
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "MyCustomToolset.generated.h"

UCLASS(BlueprintType, Hidden)
class UMyCustomToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // AICallable 标记使此函数被 Toolset Registry 自动发现
    UFUNCTION(meta = (AICallable), Category = "MyTools")
    static TArray<FString> ListItems();

    UFUNCTION(meta = (AICallable), Category = "MyTools")
    static FString GetItemDetails(const FString& ItemName);
};
```

```cpp
// MyCustomToolset.cpp
#include "MyCustomToolset.h"

TArray<FString> UMyCustomToolset::ListItems()
{
    // 实现列举逻辑
    return { TEXT("ItemA"), TEXT("ItemB") };
}

FString UMyCustomToolset::GetItemDetails(const FString& ItemName)
{
    // 实现详情查询逻辑
    return FString::Printf(TEXT("Details for %s"), *ItemName);
}
```

## 模块依赖

本插件声明了以下插件级依赖（在 .uplugin 的 `Plugins` 字段中）：

| 模块/插件 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 `UToolsetDefinition` 基类和 AI 工具注册框架 |
| `GameFeatures` | 提供 `UGameFeatureData`、`UGameFeatureAction`、`UGameFeaturesSubsystem` 等 Game Feature 系统核心类 |

无其他特殊依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

```
- 6471b168 2026-04-18 [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools
- 8c911af5 2026-04-17 [Backout] - CL52878047
- 9404cd3e 2026-04-17 [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools
```

### 维护评价

- **创建时间**：2026-03-31，非常新的插件
- **更新频率**：创建后 2 周内有 3 次提交，其中一次是回退操作，说明底层工具注册机制仍在快速迭代
- **实验性状态**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，属于早期实验阶段
- **代码规模**：仅 4 个源文件，功能精简但完整
- **依赖稳定性**：依赖的 `ToolsetRegistry` 同为实验性插件，API 可能发生变化（从近期 commit 可见工具发现机制正在调整）

**综合评价**：这是一个刚创建不久的实验性插件，属于 UE5 AI 助手工具集生态的早期组件。由于 Toolset Registry 框架本身仍在演进（近期有 API 变更和回退），本插件的接口可能会随之调整。**不建议在生产环境中依赖此插件**，但如果你在探索 UE5 AI 助手的扩展能力，这是一个很好的参考实现。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/GameFeaturesToolset)
- [GameFeaturesToolset.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/Toolsets/GameFeaturesToolset/Source/GameFeaturesToolset/Private/GameFeaturesToolset.h)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)（依赖项）
- [GameFeatures 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/GameFeatures/GameFeatures)（依赖项）