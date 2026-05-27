# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 插件是 Unreal Engine Interchange 资产导入框架的编辑器侧扩展。它不仅仅暴露框架，更在编辑器环境中提供了核心的**资产管理**和**重置**功能。具体来说，它解决了以下问题：
1.  **资产重置 (Reset)**：允许用户将通过 Interchange 导入的资产（如场景、演员）回退到其初始导入状态，撤销导入后所做的修改，而无需删除并重新导入。
2.  **关卡实例管理**：提供了在编辑器中以编程方式进入、编辑和提交关卡实例 (Level Instance) 的工具，简化了关卡实例的编辑工作流。
3.  **导入数据转换**：处理 FBX 等格式的资产导入数据 (ImportData) 的转换，为编辑器内的资产迁移和兼容性提供支持。
4.  **编辑器集成**：为 Interchange 资产（如 `UInterchangeSceneImportAsset`）定义编辑器内的显示方式、分类和操作，并集成到右键菜单等上下文。

## 使用场景

-   你通过 Interchange 框架将一个 FBX 文件导入到场景中（生成场景导入资产），之后在场景中对导入的演员和资产进行了大量调整，但希望将某些演员重置到初始导入状态。 → **使用 `ResetActors` 或 `ResetSceneImportAsset`**。
-   你正在使用关卡实例，并希望以编程方式进入编辑模式，修改实例内的演员，然后保存或放弃更改。 → **使用 `LevelInstanceEnterEditMode`, `LevelInstanceGetEditableActors`, `LevelInstanceCommit`**。
-   你需要在蓝图或 C++ 中检查一个演员或世界是否可以通过 Interchange 进行重置，以决定是否显示相关UI或执行操作。 → **使用 `CanResetActor` 或 `CanResetWorld`**。

## 蓝图用法

主要功能通过 `UInterchangeEditorScriptLibrary` 暴露，归类在 `Interchange Utilities` 子类别下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetLevelAsset` | 将一个关卡资产 (UWorld) 重置为 Interchange 导入的初始状态。 | `UInterchangeEditorScriptLibrary` |
| `ResetSceneImportAsset` | 重置一个场景导入资产及其关联的所有演员和资产。 | `UInterchangeEditorScriptLibrary` |
| `ResetActors` | 批量重置一组演员到初始导入状态。 | `UInterchangeEditorScriptLibrary` |
| `CanResetActor` | 检查一个演员是否可以通过 Interchange 框架重置。 | `UInterchangeEditorScriptLibrary` |
| `CanResetWorld` | 检查一个世界是否可以通过 Interchange 框架重置。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceEnterEditMode` | 将关卡实例设置为可编辑模式。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceCommit` | 提交或放弃对关卡实例的更改。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetEditableActors` | 获取在关卡实例编辑模式下可编辑的演员数组。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetActors` | 获取一个已加载的关卡实例中包含的所有演员（无需进入编辑模式）。 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

1.  **重置场景中的演员**：
    -   创建一个 `Get All Actors Of Class` 节点，目标类设为 `AActor`。
    -   将其输出引脚连接到一个 `Filter Array` 节点，过滤条件使用 `CanResetActor` 节点。
    -   将过滤后的演员数组连接到 `ResetActors` 节点执行。

2.  **编辑关卡实例**：
    -   获取一个 `ALevelInstance` 指针。
    -   连接 `LevelInstanceEnterEditMode` 节点，并检查其返回值。
    -   成功后，连接 `LevelInstanceGetEditableActors` 节点获取可编辑的演员进行修改。
    -   最后，连接 `LevelInstanceCommit` 节点，根据 `bDiscardChanges` 参数选择提交或放弃更改。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorScriptLibrary.h"
```

### 基本用法

直接调用 `UInterchangeEditorScriptLibrary` 的静态函数。以下示例展示了如何重置选中的演员并检查关卡状态。

```cpp
// 假设在 Actor 或 EditorUtilityWidget 中
#include "InterchangeEditorScriptLibrary.h"
#include "InterchangeSceneImportAsset.h"

void AMyEditorActor::ResetSelectedActors(const TArray<AActor*>& SelectedActors)
{
    // 过滤出可以重置的演员
    TArray<AActor*> ResettableActors;
    for (AActor* Actor : SelectedActors)
    {
        if (UInterchangeEditorScriptLibrary::CanResetActor(Actor))
        {
            ResettableActors.Add(Actor);
        }
    }

    // 执行批量重置
    if (ResettableActors.Num() > 0)
    {
        UInterchangeEditorScriptLibrary::ResetActors(ResettableActors);
        UE_LOG(LogTemp, Log, TEXT("Reset %d actors via Interchange."), ResettableActors.Num());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No actors selected are eligible for Interchange reset."));
    }
}

void AMyEditorActor::CheckLevelResetability(UWorld* InWorld)
{
    if (UInterchangeEditorScriptLibrary::CanResetWorld(InWorld))
    {
        // 执行关卡重置相关逻辑...
        // UInterchangeEditorScriptLibrary::ResetLevelAsset(InWorld);
    }
}
```

### 进阶用法

结合 `FInterchangeEditorModule` 进行模块状态检查，或使用 `UInterchangeFbxAssetImportDataConverter` 处理导入数据。

```cpp
#include "InterchangeEditorModule.h"
#include "InterchangeFbxAssetImportDataConverter.h"

void SomeEditorFunction()
{
    // 检查模块是否可用
    if (FInterchangeEditorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("Interchange Editor module is ready."));
    }

    // 转换资产导入数据的示例（需要具体的源对象和目标类）
    UInterchangeFbxAssetImportDataConverter* Converter = NewObject<UInterchangeFbxAssetImportDataConverter>();
    // ... 配置 SourceImportData 和 DestinationClass ...
    UObject* DestinationImportData = nullptr;
    // Converter->ConvertImportData(SourceImportData, DestinationClass, &DestinationImportData);
}
```

## Demo 示例

以下是一个完整的编辑器工具类示例，演示了如何在 C++ 中使用 Interchange Editor 插件的功能。

### MyInterchangeEditorTool.h

```cpp
// MyInterchangeEditorTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyInterchangeEditorTool.generated.h"

UCLASS(BlueprintType)
class UMyInterchangeEditorTool : public UObject
{
    GENERATED_BODY()

public:
    /** 尝试重置给定的演员列表 */
    UFUNCTION(BlueprintCallable, Category="MyTools|Interchange")
    void TryResetActors(const TArray<AActor*>& Actors);

    /** 打印指定关卡实例中的演员信息 */
    UFUNCTION(BlueprintCallable, Category="MyTools|Interchange")
    void PrintLevelInstanceActors(ALevelInstance* LevelInstance);
};
```

### MyInterchangeEditorTool.cpp

```cpp
// MyInterchangeEditorTool.cpp
#include "MyInterchangeEditorTool.h"
#include "InterchangeEditorScriptLibrary.h"
#include "LevelInstance/LevelInstanceActor.h"

void UMyInterchangeEditorTool::TryResetActors(const TArray<AActor*>& Actors)
{
    TArray<AActor*> Resettable;
    for (AActor* Actor : Actors)
    {
        if (Actor && UInterchangeEditorScriptLibrary::CanResetActor(Actor))
        {
            Resettable.Add(Actor);
        }
    }

    if (Resettable.Num() > 0)
    {
        UInterchangeEditorScriptLibrary::ResetActors(Resettable);
        UE_LOG(LogTemp, Display, TEXT("[InterchangeEditorTool] Successfully reset %d actors."), Resettable.Num());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("[InterchangeEditorTool] No eligible actors to reset."));
    }
}

void UMyInterchangeEditorTool::PrintLevelInstanceActors(ALevelInstance* LevelInstance)
{
    if (!LevelInstance)
    {
        UE_LOG(LogTemp, Warning, TEXT("[InterchangeEditorTool] Invalid LevelInstance provided."));
        return;
    }

    TArray<AActor*> ActorsInInstance = UInterchangeEditorScriptLibrary::LevelInstanceGetActors(LevelInstance);
    UE_LOG(LogTemp, Display, TEXT("[InterchangeEditorTool] Level Instance '%s' contains %d actors:"), *LevelInstance->GetName(), ActorsInInstance.Num());
    for (const AActor* Actor : ActorsInInstance)
    {
        if (Actor)
        {
            UE_LOG(LogTemp, Display, TEXT("  - %s"), *Actor->GetName());
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的核心依赖（如 `InterchangeCore`, `InterchangeEngine`, `AssetTools`, `EditorSubsystem` 等）通常由 UE 标准环境提供，对于使用者无需额外添加。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 自动保存器更新，关联功能改进。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 清理了动画帧对齐和 glTF 转换器代码。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi | 为关卡实例添加新API，无需加载即可获取内部演员。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏标准化更新，迁移至UE_LOGF。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 对静态和骨骼网格体的导入设置进行了重构。 |

### 维护评价

**活跃维护**。该插件在近期（2026年4月-5月）有持续的代码更新，包括功能增强（新的 `LevelInstanceGetActors` API）、代码清理和重构（动画对齐、导入设置）。更新记录显示它作为核心 Interchange 框架的一部分在积极开发和优化。实验性状态为“否”且默认启用，表明它是一个稳定且官方支持的功能。**推荐使用**，特别是对于需要 Interchange 导入后资产管理和关卡实例编辑的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- 官方文档：暂无
- 测试用例：暂无（插件目录内未提供独立测试文件）