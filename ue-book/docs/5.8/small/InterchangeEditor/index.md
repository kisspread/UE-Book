# Interchange Editor

> The Interchange Editor plugin exposes the Interchange import framework and pipelines to Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 资产交换编辑器 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeEditor` (Runtime), `InterchangeEditorPipelines` (Runtime), `InterchangeEditorUtilities` (Runtime) |
| 实验性 | 否 |
| 创建时间 | ~2022 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor) | |

## 用途

InterchangeEditor 是 Unreal Engine 中负责将资产从外部格式（如 FBX、glTF、OBJ）导入编辑器的核心框架的**编辑器端实现**。它的核心作用是将 Interchange 运行时框架（负责解析和转换资产数据）与 Unreal Editor 的用户界面、操作流程和数据管线连接起来。该插件使得开发者可以通过蓝图或 C++ 自定义导入设置、处理导入事件、创建导入管线，并将这些自定义逻辑无缝集成到编辑器的资产导入对话框和拖放导入流程中。

简单来说，它解决了“**如何在编辑器中配置和触发自定义的资产导入流程**”这个问题。

## 使用场景

- **从外部 DCC 工具（如 Maya, Blender）导入动画、网格体等资产时**：使用 Interchange 框架进行标准化、可扩展的导入，并通过此插件在编辑器中进行配置。
- **需要为特定项目或资产类型创建完全自定义的导入逻辑时**：通过实现自己的 Importer 和 Pipeline，并在编辑器中注册它们。
- **需要批量重新导入大量资产，并希望统一修改导入设置时**：利用此插件提供的工具函数和界面来操作资产的 Interchange 源数据。
- **开发需要深度集成导入流程的编辑器工具或插件时**：作为依赖的基础框架。

## 蓝图用法

蓝图功能主要通过 `UInterchangeEditorScriptLibrary` 和相关资产操作类暴露。使用前需在项目设置中启用 Interchange 插件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Reimport Asset with Interchange` | 使用 Interchange 框架重新导入指定资产 | `UInterchangeEditorScriptLibrary` |
| `Import Scene with Interchange` | 触发一个文件的 Interchange 导入流程 | `UInterchangeEditorScriptLibrary` |
| `Get Import Scene Dialog Settings` | 获取当前导入对话框的设置对象 | `UInterchangeEditorScriptLibrary` |
| `Set Import Scene Dialog Settings` | 修改导入对话框的设置 | `UInterchangeEditorScriptLibrary` |

### 使用示例（蓝图描述）

1. **自动重新导入**：
   - 在 `Event Tick` 或自定义事件中，通过 `Make Asset Data` 节点创建一个资产数据结构。
   - 连接到 `Reimport Asset with Interchange` 节点。可选择传入一个 `UInterchangePipelineConfigurationBase` 来覆盖默认的管线设置。
   - 处理 `On Reimport Completed` 委托来确认结果。

2. **自定义导入流程**：
   - 调用 `Import Scene with Interchange` 节点，传入源文件路径。
   - 可连接一个自定义的 `UInterchangeSceneImportAsset` 对象来进一步处理导入事件。

## C++ 用法

核心 API 用于程序化地触发导入、查询导入状态和管理导入管线。

### 头文件引入

```cpp
#include "InterchangeEditorScriptLibrary.h"
#include "InterchangeManager.h" // 运行时框架，通常也需要
```

### 基本用法

触发一个文件的导入，并处理结果。
```cpp
// 假设已经获取了 FInterchangeManager
FInterchangeManager& InterchangeManager = FInterchangeManager::Get();

// 准备导入参数
FInterchangeImportArguments ImportArgs;
ImportArgs.ImportFilename = TEXT("/path/to/your/mesh.fbx");

// 触发异步导入
FInterchangeTaskData TaskData = InterchangeManager.ImportScene(ImportArgs);

// 通过 TaskData 或回调监控进度和结果
```

### 进阶用法

重新导入一个已有的资产，并指定自定义管线。
```cpp
// 获取要重新导入的资产
UStaticMesh* ExistingMesh = /* ... */;

// 创建或获取自定义管线实例
UMyCustomPipeline* MyPipeline = NewObject<UMyCustomPipeline>();

// 使用蓝图库中的函数触发重新导入
FInterchangeReimportArguments ReimportArgs;
ReimportArgs.Asset = ExistingMesh;
ReimportArgs.PipelineOverride = MyPipeline;

UInterchangeEditorScriptLibrary::ReimportAssetWithInterchange(ReimportArgs);
```

## Demo 示例

以下示例演示如何在 C++ 中创建一个简单的编辑器工具按钮，用于重新导入指定的静态网格体。

**MyReimportTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyReimportTool.generated.h"

UCLASS()
class UMyReimportTool : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    void Initialize(FSubsystemCollectionBase& Collection) override;
    void Deinitialize() override;
    void ReimportSelectedStaticMesh();

private:
    TSharedPtr<FUICommandList> CommandList;
    TSharedPtr<FExtender> MenuExtender;
};
```

**MyReimportTool.cpp**
```cpp
#include "MyReimportTool.h"
#include "InterchangeEditorScriptLibrary.h"
#include "Engine/StaticMesh.h"

void UMyReimportTool::Initialize(FSubsystemCollectionBase& Collection)
{
    // 创建命令列表和菜单项等初始化代码（省略）
    // ...
}

void UMyReimportTool::ReimportSelectedStaticMesh()
{
    // 假设有一个选择的静态网格体资产
    UStaticMesh* MeshToReimport = /* 从内容浏览器获取 */;

    if (MeshToReimport)
    {
        FInterchangeReimportArguments Args;
        Args.Asset = MeshToReimport;

        // 调用 Interchange 重新导入
        UInterchangeEditorScriptLibrary::ReimportAssetWithInterchange(Args);
        UE_LOG(LogTemp, Log, TEXT("Triggered Interchange reimport for: %s"), *MeshToReimport->GetName());
    }
}

void UMyReimportTool::Deinitialize()
{
    // 清理命令列表等
    CommandList.Reset();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | 提供 Interchange 框架的基础运行时接口和管理器 |
| `InterchangeNodes` | 定义用于表示资产和场景的通用中间节点类型 |
| `InterchangePipelines` | 提供基础的导入/导出管线框架和常用内置管线 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `fb1426e8` | [PackageAutoSaver] Add the ability to temporarily suspend the autosaver. | 为自动保存器添加临时挂起功能，影响导入时的自动保存行为。 |
| 2026-05-12 | `099f7387` | [Interchange] Animation frame alignment and glTF translator frame aligner removed. | 移除动画帧对齐和glTF转换器帧对齐器，属于功能清理。 |
| 2026-04-22 | `cc360b1e` | Add accessor to InterchangeEditorScriptLibrary that returns actors in a level instance without loadi | 向脚本库添加新访问器，可获取关卡实例中的Actor而不加载整个关卡，提升查询效率。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到UE_LOGF，属于代码质量改进。 |
| 2026-04-13 | `05458c60` | [Interchange] Reworking Static and Skeletal Mesh import settings | 重新设计静态和骨骼网格体的导入设置，是重要的功能更新。 |

### 维护评价

**活跃维护**。Interchange 是 Epic Games 当前主推的下一代资产导入框架，用以替代旧的 FBX 导入器。此编辑器插件是该框架不可或缺的一部分，持续获得实质性更新（如新功能、API 重构、性能优化）。从提交记录看，它与运行时框架紧密同步开发，修复及时，新特性不断。它是官方推荐使用的资产导入通道，强烈建议在新项目中使用。虽然框架成熟度可能还在完善中，但其作为未来标准的地位明确，无废弃风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Editor)
- [子模块文档: InterchangeEditor](InterchangeEditor.md)
- [子模块文档: InterchangeEditorPipelines](InterchangeEditorPipelines.md)
- [子模块文档: InterchangeEditorUtilities](InterchangeEditorUtilities.md)