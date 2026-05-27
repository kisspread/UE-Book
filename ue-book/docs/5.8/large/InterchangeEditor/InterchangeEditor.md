# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器集成 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-11-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

`InterchangeEditor` 插件的核心作用是作为 Unreal Engine 编辑器与底层 `Interchange` 框架之间的集成层。它并非一个独立的导入器，而是为编辑器用户界面（UI）和工作流提供必要的支持，使得开发者能够通过 Interchange 管线（Pipeline）高效地管理资产的导入、转换和重置过程。它具体解决了以下问题：

1.  **编辑器集成**：将 Interchange 的导入功能和管线暴露给编辑器，使得用户可以通过标准的编辑器操作（如拖放、菜单）触发基于 Interchange 的导入。
2.  **资产生命周期管理**：提供核心的“重置”（Reset）功能，允许用户将已通过 Interchange 导入的资产（如关卡、场景、Actor）恢复到其导入时的初始状态，便于迭代和修正。
3.  **场景导入资产管理**：专门管理 `UInterchangeSceneImportAsset` 这种特殊资产，它记录了整个场景的导入配置和状态，并能通过 `AssetDefinition` 在内容浏览器中以特定图标和颜色进行标识和操作。
4.  **数据格式转换**：提供 `UInterchangeFbxAssetImportDataConverter`，用于在 FBX 导入数据（`UFbxImportUI`）和 Interchange 导入数据之间进行双向转换，确保与旧有 FBX 导入流程的兼容性。
5.  **管线配置缓存**：通过 `FInterchangePipelineSettingsCacheHandler` 缓存管线设置，以优化编辑器性能，并在相关资产被删除时自动清理缓存。

## 使用场景

-   **通过 Interchange 导入资产**：当您在编辑器中使用 Interchange 工作流导入 FBX、glTF 等格式的资产时，此插件负责驱动编辑器侧的流程。
-   **重置已导入的资产**：您导入了一个角色模型到关卡中，后来发现原始 FBX 文件有更新。您可以使用此插件提供的“重置”功能，将场景中的该 Actor 及其引用的资产一键重置为最新导入版本。
-   **管理场景导入资产**：当您使用 `ImportScene` 功能一次性导入一个包含多个资产和 Actor 的场景文件（如 FBX 场景）时，会生成一个 `InterchangeSceneImportAsset`。您可以使用此插件中的功能来重置整个场景导入，或进入关卡实例的编辑模式进行局部修改。
-   **兼容旧版 FBX 导入**：在从传统的 FBX 导入界面过渡到 Interchange 的过程中，此插件提供的转换器可以确保基于旧数据格式的导入设置能够被正确识别和使用。

## 蓝图用法

蓝图功能主要集中在 `UInterchangeEditorScriptLibrary` 类中，为资产重置和关卡实例操作提供便捷节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetLevelAsset` | 重置一个关卡（World）资产中所有由 Interchange 导入的内容。 | `UInterchangeEditorScriptLibrary` |
| `ResetSceneImportAsset` | 重置一个场景导入资产（`UInterchangeSceneImportAsset`），包括其管理的所有 Actor 和关联资产。 | `UInterchangeEditorScriptLibrary` |
| `ResetActors` | 重置一个 Actor 数组中的所有 Actor。仅对可通过 Interchange 重置的 Actor 生效。 | `UInterchangeEditorScriptLibrary` |
| `CanResetActor` | 检查一个 Actor 是否可以通过 Interchange 进行重置。 | `UInterchangeEditorScriptLibrary` |
| `CanResetWorld` | 检查一个 World（关卡）是否可以通过 Interchange 进行重置。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceEnterEditMode` | 使一个关卡实例（Level Instance）进入编辑模式，以允许修改其内部的 Actor。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceCommit` | 提交（应用）或丢弃在关卡实例编辑模式下所做的修改。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetEditableActors` | 获取在指定关卡实例的编辑模式下可被编辑的 Actor 列表。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetActors` | 获取一个已加载的关卡实例内包含的所有 Actor，无需进入编辑模式。 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

**示例 1：重置单个 Actor**
1.  获取一个对场景中 Actor 的引用（例如，通过 `Get Actor of Class` 节点）。
2.  连接到 `CanResetActor` 节点，检查该 Actor 是否可重置。
3.  如果为真，将该 Actor 放入一个数组中。
4.  连接到 `ResetActors` 节点，传入包含该 Actor 的数组。
5.  执行蓝图，该 Actor 及其依赖的资产将被重置。

**示例 2：编辑关卡实例**
1.  获取一个关卡实例 Actor 的引用。
2.  连接到 `LevelInstanceEnterEditMode` 节点，使关卡实例进入编辑模式。
3.  使用 `LevelInstanceGetEditableActors` 节点获取可编辑的 Actor 列表。
4.  对列表中的某个 Actor 进行属性修改（如移动位置）。
5.  连接到 `LevelInstanceCommit` 节点，将 `bDiscardChanges` 设为 `false` 以应用修改，或设为 `true` 以丢弃。

## C++ 用法

### 头文件引入

主要的可访问接口通过 `InterchangeEditorModule` 和 `InterchangeEditorScriptLibrary` 头文件暴露。

```cpp
#include "InterchangeEditorModule.h"
#include "InterchangeEditorScriptLibrary.h"
```

### 基本用法

**检查并获取编辑器模块实例**

```cpp
// 确保编辑器模块可用
if (FInterchangeEditorModule::IsAvailable())
{
    // 获取模块引用，可用于后续可能提供的模块级API
    FInterchangeEditorModule& EditorModule = FInterchangeEditorModule::Get();
    // ... 使用模块功能
}
```

**在C++中执行蓝图中的重置功能**

```cpp
#include "InterchangeEditorScriptLibrary.h"
// 假设已经有一个 AActor* MyActor 指针

// 检查 Actor 是否可重置
if (UInterchangeEditorScriptLibrary::CanResetActor(MyActor))
{
    // 构造包含该 Actor 的数组
    TArray<AActor*> ActorsToReset;
    ActorsToReset.Add(MyActor);
    
    // 执行重置
    UInterchangeEditorScriptLibrary::ResetActors(ActorsToReset);
}
```

### 进阶用法

**操作关卡实例的完整工作流**

```cpp
#include "InterchangeEditorScriptLibrary.h"
#include "Engine/LevelInstance/LevelInstanceActor.h"

// 假设已经有一个 ALevelInstance* MyLevelInstance 指针

// 1. 进入编辑模式
bool bSuccess = UInterchangeEditorScriptLibrary::LevelInstanceEnterEditMode(MyLevelInstance);
if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("无法进入关卡实例编辑模式"));
    return;
}

// 2. 获取内部可编辑的 Actor
const TArray<AActor*>& EditableActors = UInterchangeEditorScriptLibrary::LevelInstanceGetEditableActors(MyLevelInstance);
if (EditableActors.Num() > 0)
{
    // 例如，获取第一个 Actor 并修改其位置
    AActor* ActorToModify = EditableActors[0];
    ActorToModify->SetActorLocation(FVector(100.f, 0.f, 0.f));

    // 3. 提交修改
    bSuccess = UInterchangeEditorScriptLibrary::LevelInstanceCommit(MyLevelInstance, false); // false 表示应用，true 表示丢弃
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("提交关卡实例修改失败"));
        // 可能需要手动退出编辑模式或处理错误
    }
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("关卡实例内部没有可编辑的 Actor"));
    // 即使没有 Actor，也可能需要退出编辑模式
    UInterchangeEditorScriptLibrary::LevelInstanceCommit(MyLevelInstance, true); // 丢弃空的“修改”
}
```

*注意：以上 C++ 示例基于头文件推断，实际使用时需参考具体项目上下文和引擎版本进行调整。测试用例（如 `Engine/Tests/Interchange/`）是学习官方用法的最佳来源。*

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在一个编辑器工具按钮点击后，检查并重置当前关卡。

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorTool : public UObject
{
    GENERATED_BODY()

public:
    // 一个可以绑定到编辑器按钮的函数
    UFUNCTION(BlueprintCallable, Category="EditorTool")
    void ResetCurrentLevel();
};

// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "InterchangeEditorScriptLibrary.h"
#include "Engine/World.h"

void UMyEditorTool::ResetCurrentLevel()
{
    // 获取编辑器世界上下文（通常在编辑器工具中这样获取）
    UWorld* EditorWorld = GEditor->GetEditorWorldContext().World();
    if (!EditorWorld)
    {
        return;
    }

    // 使用 Interchange 脚本库进行重置
    if (UInterchangeEditorScriptLibrary::CanResetWorld(EditorWorld))
    {
        UInterchangeEditorScriptLibrary::ResetLevelAsset(EditorWorld);
        UE_LOG(LogTemp, Log, TEXT("当前关卡已通过 Interchange 重置。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("当前关卡不支持或无需通过 Interchange 重置。"));
    }
}
```

## 模块依赖

此插件的模块依赖相对集中，主要依赖于 `Interchange` 核心框架。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心运行时库 |
| `InterchangeImport` | Interchange 的导入功能实现库 |

*无其他特殊模块依赖。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 为自动保存器添加了临时挂起功能，与InterchangeEditor无直接关系。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐功能和glTF转换器的帧对齐器。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi | 在脚本库中添加了新接口，可在不加载关卡实例的情况下获取其内部的Actor列表。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF，进行日志系统现代化更新。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重做了静态网格体和骨骼网格体的导入设置，是框架功能的重要更新。 |

### 维护评价

`InterchangeEditor` 插件处于**活跃维护**状态。
-   **创建时间**：首次提交记录可追溯至 2024 年末。
-   **更新频率**：从最近 5 次提交来看，更新非常频繁（最近一次在 2026 年 5 月），且包含新功能添加（如获取关卡实例Actor的访问器）和框架重构（如重做网格体导入设置）。
-   **维护团队**：由 Epic Games 官方维护，与 UE 核心引擎开发同步。
-   **已知问题/限制**：无特别说明。作为框架集成插件，其稳定性与底层 `Interchange` 模块密切相关。
-   **推荐使用**：**强烈推荐**。这是在 Unreal Editor 中使用 Interchange 资产导入管线的**必备插件**。如果您计划采用或已经在使用 Interchange 工作流进行资产导入，此插件必须启用。它提供了编辑器侧的全部必要支持。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
-   官方文档链接未在 `.uplugin` 中提供。
-   [测试用例（参考）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Interchange) （注意：测试可能位于引擎测试目录下）