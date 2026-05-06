# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 交换架构编辑器集成 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor) | |

## 用途

Interchange Editor 插件将 Unreal Engine 的新一代导入框架 **Interchange** 无缝集成到编辑器工作流中。它主要解决以下问题：

- 为 `.uasset` 类型的 **InterchangeSceneImportAsset**（场景导入资产）提供完整的资产编辑器支持（显示、图标、类别、打开行为）。
- 提供 **重置（Reset）** 功能，允许在编辑器中对已经通过 Interchange 导入的关卡、场景资产、Actor 进行一键回退，恢复为导入前的原始状态，便于反复迭代导入流程。
- 在关卡视口上下文菜单中添加 **重置** 菜单项，方便美术/设计人员快速操作。
- 管理导入管道（Pipeline）的设置缓存，确保当资产被删除时缓存同步失效。
- 提供 **FBX 资产导入数据转换**，帮助从旧版 FBX 导入数据迁移到 Interchange 体系。

## 使用场景

- **场景导入迭代**：在调试或调整 Interchange 管道时，需要反复将外部场景文件导入关卡；使用插件提供的重置功能可以一键清除之前导入产生的所有 Actor 和资产，保留关卡的其他内容，避免重复手动删除。
- **关卡实例编辑**：导入的场景往往以 LevelInstance 形式存在，插件提供了进入/退出编辑模式、获取可编辑 Actor、提交/放弃更改的蓝图函数，方便自动化批量处理。
- **旧版 FBX 迁移**：项目从旧版 FBX 导入转换到 Interchange 时，借助 `UInterchangeFbxAssetImportDataConverter` 可以自动将现有的 `UFbxAssetImportData` 转换为 `UInterchangeAssetImportData`，保持资源引用有效。
- **自定义重置流程**：通过蓝图或 C++ 调用 `ResetLevelAsset`、`ResetActors` 等 API，集成到工具链或自动化测试中。

## 蓝图用法

所有蓝图可直接调用的接口集中在 `UInterchangeEditorScriptLibrary` 中，用于重置导入状态和管理关卡实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetLevelAsset` | 重置整个关卡资产，清除之前 Interchange 导入的所有内容 | `UInterchangeEditorScriptLibrary` |
| `ResetSceneImportAsset` | 重置指定的 InterchangeSceneImportAsset，移除其关联的 Actor 和资产 | `UInterchangeEditorScriptLibrary` |
| `ResetActors` | 重置传入的 Actor 数组（只对可通过 Interchange 重置的 Actor 生效） | `UInterchangeEditorScriptLibrary` |
| `CanResetActor` | 判断指定 Actor 是否可以被重置 | `UInterchangeEditorScriptLibrary` |
| `CanResetWorld` | 判断指定 World 是否可以被重置 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceEnterEditMode` | 使关卡实例（LevelInstance）进入编辑模式，允许修改内部 Actor | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceCommit` | 提交或放弃关卡实例的编辑更改 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetEditableActors` | 获取当前处于编辑模式的关卡实例中可编辑的 Actor 数组 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

**场景：在关卡蓝图中一键重置所有导入的 Actor**

1. 从 `事件开始运行` 引出连线，使用 `Get All Actors Of Class` 获取当前关卡中所有 Actor（可根据需要按照标签或类过滤）。
2. 将 Actor 数组连接到 `ResetActors` 节点的 `Actors` 输入引脚。
3. 执行时，所有符合条件的 Actor 将被重置为导入前的状态（如果它们是由 Interchange 导入的）。

**场景：进入 LevelInstance 编辑模式并获取可编辑 Actor**

1. 获取目标 `LevelInstance` 引用。
2. 调用 `LevelInstance Enter Edit Mode`，成功时返回 true。
3. 调用 `LevelInstance Get Editable Actors` 获得当前可编辑的 Actor 列表。
4. 对列表进行操作（如移动、删除），完成后调用 `LevelInstance Commit`（`bDiscardChanges` 设为 false）以应用更改。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorModule.h"           // 模块访问
#include "InterchangeEditorScriptLibrary.h"    // 蓝图暴露的静态函数
#include "InterchangeFbxAssetImportDataConverter.h" // 导入数据转换
#include "AssetDefinition_InterchangeSceneImportAsset.h" // 资产定义
```

### 基本用法

**检查并重置关卡资产（来自脚本库）**

```cpp
// 获取当前编辑器世界
UWorld* World = GEditor->GetEditorWorldContext().World();
if (World && UInterchangeEditorScriptLibrary::CanResetWorld(World))
{
    UInterchangeEditorScriptLibrary::ResetLevelAsset(World);
}
```

来源：[InterchangeEditorScriptLibrary.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Interchange/Editor/Source/InterchangeEditor/Public/InterchangeEditorScriptLibrary.h)

**转换旧版 FBX 导入数据到 Interchange**

```cpp
// 创建一个转换器
UInterchangeFbxAssetImportDataConverter* Converter = NewObject<UInterchangeFbxAssetImportDataConverter>();
UObject* DestinationData = nullptr;
if (Converter->CanConvertClass(SourceImportData->GetClass(), UInterchangeAssetImportData::StaticClass()))
{
    Converter->ConvertImportData(SourceImportData, UInterchangeAssetImportData::StaticClass(), &DestinationData);
}
```

来源：[InterchangeFbxAssetImportDataConverter.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Interchange/Editor/Source/InterchangeEditor/Public/InterchangeFbxAssetImportDataConverter.h)

### 进阶用法

**自定义上下文菜单重置项**

如果希望在编辑器模式下扩展右键菜单，可以在模块启动时调用：

```cpp
void MyModule::StartupModule()
{
    FInterchangeResetContextMenuExtender::SetupLevelEditorContextMenuExtender();
}

void MyModule::ShutdownModule()
{
    FInterchangeResetContextMenuExtender::RemoveLevelEditorContextMenuExtender();
}
```

来源：[InterchangeResetContextMenuExtender.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Interchange/Editor/Source/InterchangeEditor/Private/InterchangeResetContextMenuExtender.h)

**缓存处理**

在需要时初始化 Pipeline 设置缓存（通常在模块启动时自动调用）：

```cpp
FInterchangePipelineSettingsCacheHandler::InitializeCacheHandler();
// ... 在资产被删除时缓存会自动失效
// 模块关闭时
FInterchangePipelineSettingsCacheHandler::ShutdownCacheHandler();
```

## Demo 示例

以下是一个完整的 C++ 控制台命令示例，用于在编辑器中重置当前关卡的所有 Interchange Actor。

**InterchangeResetCommands.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "EditorSubsystem.h"
#include "InterchangeResetCommands.generated.h"

UCLASS()
class UInterchangeResetSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    UFUNCTION(Exec)
    void ResetCurrentLevelInterchangeActors();
};
```

**InterchangeResetCommands.cpp**

```cpp
#include "InterchangeResetCommands.h"
#include "InterchangeEditorScriptLibrary.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Actor.h"
#include "Editor.h"

void UInterchangeResetSubsystem::ResetCurrentLevelInterchangeActors()
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World)
        return;

    TArray<AActor*> Actors;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (UInterchangeEditorScriptLibrary::CanResetActor(*It))
        {
            Actors.Add(*It);
        }
    }

    if (Actors.Num() > 0)
    {
        UInterchangeEditorScriptLibrary::ResetActors(Actors);
        UE_LOG(LogTemp, Log, TEXT("Reset %d Interchange actors in current level."), Actors.Num());
    }
}
```

**在模块 StartupModule 中注册控制台命令：**

```cpp
#include "InterchangeEditorModule.h"
#include "Editor/EditorEngine.h"
#include "InterchangeResetCommands.h"

void FMyModule::StartupModule()
{
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("Interchange.ResetLevel"),
        TEXT("Reset all Interchange actors in the current level"),
        FConsoleCommandWithArgsDelegate::CreateLambda([](const TArray<FString>& Args)
        {
            UInterchangeResetSubsystem* Subsystem = GEditor->GetEditorSubsystem<UInterchangeResetSubsystem>();
            if (Subsystem)
                Subsystem->ResetCurrentLevelInterchangeActors();
        })
    );
}
```

## 模块依赖

**省略常见依赖**（Core, Engine, Slate, UnrealEd 等），仅列出该插件特有的模块依赖。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心类型与调度 |
| `InterchangeEngine` | 引擎层导入管线管理与资产创建 |
| `InterchangePipelines` | 导入管道定义（由子模块 `InterchangeEditorPipelines` 提供 UI） |
| `InterchangeImport` | 静态网格体、材质等具体导入实现 |
| `LevelInstanceEditor` | 关卡实例编辑模式支持 |
| `AssetDefinition` | 资产定义框架，用于注册 InterchangeSceneImportAsset |

> 实际使用 `InterchangeEditor` 插件时，你的模块通常只需要在 `PublicDependencyModuleNames` 中添加 `"InterchangeEditor"`，其余依赖会自动传递。

## 维护状态

### 近期更新

- 2025-10-02 `35b266d6` — [Interchange UI] - Add separator section headings in the Import Dialog details view panel settings dialog. （界面优化）
- 2025-09-24 `d2b213b6` — Interchange - Import performance improvement attempt （性能提升）
- 2025-09-24 `c5a21eff` — [BUGFIX][Interchange] FBX Python Level Import Test Failing （修复测试）
- 2025-09-23 `dcd0cb0d` — Tentatively fixed crash reported by users when closing import dialog （崩溃修复）
- 2025-09-23 `24638fbb` — [Interchange] Temp fix for Interchange Logging （日志修复）

### 维护评价

- **创建时间**：2025-09-23，属于全新的插件（不到一个月）。
- **近期更新**：非常活跃，几乎每天都有提交，涵盖界面、性能、Bug 修复。
- **维护状态**：**活跃维护**，Epic 正在积极开发和改进 Interchange 生态。
- **稳定性**：仍处于早期阶段，可能出现 API 变化，但已有较多使用。
- **推荐使用**：✅ 推荐用于需要 Interchange 导入编辑器的项目，尤其是需要进行场景导入重置和旧版 FBX 迁移的场景。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor)
- [Interchange Editor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Source/InterchangeEditor)
- [Interchange Editor Pipelines 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Source/Pipelines)
- [Interchange Editor Utilities 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Editor/Source/Utilities)
- [官方文档（暂无专用页面）](https://docs.unrealengine.com/5.4/en-US/interchange-framework-in-unreal-engine/)
- [测试用例（引擎级）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Tests)