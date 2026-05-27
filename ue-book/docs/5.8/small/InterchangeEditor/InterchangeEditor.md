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
| 创建时间 | 2023-12-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

此插件是 Unreal Engine 中 **Interchange 框架** 的**编辑器端集成层**。Interchange 框架本身是一个模块化的资产导入/导出系统，而 `InterchangeEditor` 插件将其功能（如导入管线、管线配置、资产处理等）暴露给虚幻编辑器，使得用户可以通过编辑器界面配置和执行通过 Interchange 定义的资产导入流程。它还提供了额外的工具，如重置通过 Interchange 导入的资产、操作关卡实例等。

简单来说，它是 **Interchange 导入系统在编辑器中的“遥控器”和“工具箱”**。

## 使用场景

-   **使用自定义导入管线**：当你的项目使用基于 Interchange 的自定义管线（例如，对 FBX/glTF 导入有特殊处理逻辑）时，你需要此插件来让这些管线在编辑器中可用。
-   **管理导入的资产**：你需要批量重置或管理一批通过 Interchange 导入的资产（如模型、场景）时。
-   **操作关卡实例**：你需要以编程方式进入、退出或获取关卡实例（Level Instance）内的 Actor 信息，这些关卡实例是通过 Interchange 导入的。
-   **转换资产数据**：需要将一种格式的资产导入数据（如 FBX 导入数据）转换为另一种格式时。

## 蓝图用法

主要蓝图功能集中在 `UInterchangeEditorScriptLibrary` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetSceneImportAsset` | 重置整个通过 Interchange 导入的场景资产，包括其包含的 Actor 和关联资产。 | `UInterchangeEditorScriptLibrary` |
| `ResetActors` | 重置一个 Actor 数组（这些 Actor 必须是通过 Interchange 导入且可重置的）。 | `UInterchangeEditorScriptLibrary` |
| `CanResetActor` | 检查指定的 Actor 是否支持通过 Interchange 进行重置。 | `UInterchangeEditorScriptLibrary` |
| `CanResetWorld` | 检查指定的 World（关卡）是否支持通过 Interchange 进行重置。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceEnterEditMode` | 将一个关卡实例（Level Instance）置于可编辑模式。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceCommit` | 将处于编辑模式的关卡实例所做的修改应用或丢弃。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetEditableActors` | 获取处于编辑模式的关卡实例内的所有可编辑 Actor 列表。 | `UInterchangeEditorScriptLibrary` |
| `LevelInstanceGetActors` | 获取已加载的关卡实例内的所有 Actor 列表（无需处于编辑模式）。 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

1.  **重置一个通过 Interchange 导入的场景资产**：
    -   从内容浏览器或变量获取一个 `UInterchangeSceneImportAsset` 对象。
    -   将其连接到 `ResetSceneImportAsset` 节点的 `SceneImportAsset` 引脚。
    -   执行该节点，场景中的所有相关 Actor 和资产将被重置为其原始导入状态。

2.  **在编辑关卡实例前进行检查**：
    -   获取一个 `ALevelInstance` 对象。
    -   将其连接到 `LevelInstanceGetActors` 节点，预先查看其包含的 Actor。
    -   调用 `LevelInstanceEnterEditMode` 节点进入编辑模式。
    -   使用 `LevelInstanceGetEditableActors` 获取可编辑的 Actor 列表进行操作。
    -   最后调用 `LevelInstanceCommit` 并传入 `bDiscardChanges` 参数（如 `false`）来应用修改。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeEditorModule.h"
#include "InterchangeEditorLog.h"
// 其他需要的头文件，例如用于重置的脚本库
#include "InterchangeEditorScriptLibrary.h"
```

### 基本用法

1.  **获取模块实例**：
    ```cpp
    // 确保模块已加载并可用
    if (FInterchangeEditorModule::IsAvailable())
    {
        FInterchangeEditorModule& InterchangeEditorModule = FInterchangeEditorModule::Get();
        // 可以在此处使用模块提供的服务（如果有公开接口）
    }
    ```
    *来源：* `Public/InterchangeEditorModule.h`

2.  **使用日志分类**：
    ```cpp
    UE_LOG(LogInterchangeEditor, Log, TEXT("Interchange Editor 相关操作信息: %s"), *SomeMessage);
    ```
    *来源：* `Public/InterchangeEditorLog.h`

### 进阶用法

调用蓝图库中的静态函数（需要确保 `UInterchangeEditorScriptLibrary` 所在模块已被依赖）：
```cpp
// 检查一个 Actor 是否可重置
AActor* MyActor = /* 获取 Actor 指针 */;
bool bCanReset = UInterchangeEditorScriptLibrary::CanResetActor(MyActor);

// 重置一个场景导入资产
UInterchangeSceneImportAsset* SceneAsset = /* 获取场景导入资产 */;
if (SceneAsset)
{
    UInterchangeEditorScriptLibrary::ResetSceneImportAsset(SceneAsset);
}
```
*来源：* `Public/InterchangeEditorScriptLibrary.h`

## Demo 示例

以下是一个控制台命令示例，用于检查当前编辑器中选定的第一个 Actor 是否为可重置的 Interchange Actor。

```cpp
// MyInterchangeTestCommand.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"

class UInterchangeTestCommand
{
public:
    static void RegisterConsoleCommand();
};

// MyInterchangeTestCommand.cpp
#include "MyInterchangeTestCommand.h"
#include "InterchangeEditorScriptLibrary.h"
#include "Editor.h"

void UInterchangeTestCommand::RegisterConsoleCommand()
{
    IConsoleManager::Get().RegisterConsoleCommand(
        TEXT("Interchange.CheckSelected"),
        TEXT("Checks if the first selected actor can be reset via Interchange."),
        FConsoleCommandDelegate::CreateLambda([]()
        {
            if (GEditor && GEditor->GetSelectedActors())
            {
                USelection* Selection = GEditor->GetSelectedActors();
                if (Selection->Num() > 0)
                {
                    AActor* SelectedActor = Cast<AActor>(Selection->GetSelectedObject(0));
                    if (SelectedActor)
                    {
                        bool bCanReset = UInterchangeEditorScriptLibrary::CanResetActor(SelectedActor);
                        UE_LOG(LogTemp, Log, TEXT("Actor '%s' CanReset: %s"),
                            *SelectedActor->GetName(),
                            bCanReset ? TEXT("True") : TEXT("False"));
                    }
                }
            }
        }),
        ECVF_Default
    );
}
```

## 模块依赖

从 `InterchangeEditor` 模块的 `Build.cs` 分析，除标准模块外，需特别关注以下依赖：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架的核心模块。 |
| `InterchangeImport` | 提供各种格式的具体导入器（Translator）。 |
| `InterchangeExport` | 提供各种格式的具体导出器（Writer）。 |
| `InterchangePipelines` | 提供基础的导入/导出管线（Pipeline）框架。 |
| `InterchangeEngine` | 管理 Interchange 任务的调度和执行。 |
| `InterchangeMessages` | 传递框架内部的消息。 |
| `AssetDefinition` | 用于定义资产在编辑器中的显示和操作方式（本插件的 `UAssetDefinition_InterchangeSceneImportAsset` 依赖此）。 |
| `ContentBrowser` | 与内容浏览器交互。 |
| `LevelEditor` | 用于扩展关卡编辑器的右键菜单（`FInterchangeResetContextMenuExtender` 依赖此）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 为自动保存器添加了临时挂起功能，可能影响编辑器资产保存流程。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除了动画帧对齐和 glTF 翻译器的帧对齐器，是一次功能清理。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loading | 向脚本库添加了新函数，用于获取关卡实例内的 Actor 而无需加载关卡，优化了性能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版 UE_LOG 宏迁移到 UE_LOGF 格式化宏，属于代码现代化重构。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重构了静态网格和骨骼网格的导入设置，涉及底层导入逻辑变更。 |

### 维护评价

-   **活跃维护**：从最近的提交记录（2026年）看，该插件仍在 **积极维护** 中。近期的更新包括功能添加（`LevelInstanceGetActors`）、功能清理（移除帧对齐）和代码现代化（日志宏迁移），表明 Epic 团队仍在持续改进此插件。
-   **推荐使用**：作为 Unreal Engine 官方 Interchange 系统的核心编辑器集成部分，它是使用 Interchange 框架进行资产导入的 **必要组件**。对于依赖 Interchange 管线的项目，此插件是标准且推荐使用的。
-   **注意**：此插件是 `Interchange` 主插件的配套编辑器部分，通常与 `Interchange`（运行时部分）一起使用。确保两者版本匹配。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
-   官方文档：暂无专属文档页面，主要参考 [Interchange 框架通用文档](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/)。
-   测试用例：测试文件位于 `Engine/Tests/Interchange` 目录下。