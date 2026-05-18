# Interchange Chaos Cloth Asset

> Contains the classes and objects required to allow Interchange to produce Chaos Cloth Assets

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产互换导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `InterchangeChaosClothAssetImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset) | |

## 用途

该插件是 **UE5 Interchange 导入框架** 的一个扩展，专门用于将外部格式（如 USD）中的布料数据导入为引擎内的 `ChaosClothAsset` 资产。它解决了将布料网格（包含渲染和模拟数据）、求解器属性以及关联的 `Dataflow` 图作为完整资产进行导入和集成的问题，确保了布料数据在导入过程中保持其物理模拟所需的结构与属性。

## 使用场景

- 当你的美术流程使用 **USD** 等格式交换布料资产，并希望一键导入为 UE5 可用的 `ChaosClothAsset` 时。
- 当你需要从外部 DCC 工具导入带有完整物理设置的布料，并希望自动生成对应的 `Dataflow` 图时。
- 当你在使用 **Interchange 管线** 进行资产批量导入，并需要包含布料类型的资产时。

## 蓝图用法

本插件的蓝图 API 主要集中在 **工厂节点（Factory Node）** 和 **导入管线（Pipeline）** 的配置上，允许在导入前预设或在导入对话框中调整布料导入参数。

### 核心节点

#### 工厂节点 (`UInterchangeChaosClothAssetFactoryNode`)

用于配置单个布料资产的导入细节。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetImportSimulationMeshes` / `SetImportSimulationMeshes` | 获取/设置是否导入模拟网格数据 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetImportRenderMeshes` / `SetImportRenderMeshes` | 获取/设置是否导入渲染网格数据 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetDataflowGraphPath` / `SetDataflowGraphPath` | 获取/设置用于实例化 `Dataflow` 图模板的资源路径 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetAirDamping` / `SetAirDamping` | 获取/设置布料求解器的空气阻力参数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetGravity` / `SetGravity` | 获取/设置布料求解器的重力方向向量 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetSubStepCount` / `SetSubStepCount` | 获取/设置模拟的子步进数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetTimeStep` / `SetTimeStep` | 获取/设置模拟的时间步长 | `UInterchangeChaosClothAssetFactoryNode` |

#### 导入管线 (`UInterchangeChaosClothAssetPipeline`)

控制整个布料资产导入流程的全局设置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PipelineDisplayName` (属性) | 在导入对话框中显示的管线名称 | `UInterchangeChaosClothAssetPipeline` |
| `bImportClothAssets` (属性) | 总开关，是否导入源文件中发现的所有布料资产 | `UInterchangeChaosClothAssetPipeline` |
| `bImportSimulationMeshes` (属性) | 是否向生成的布料集合中添加模拟数据 | `UInterchangeChaosClothAssetPipeline` |
| `bImportRenderMeshes` (属性) | 是否向生成的布料集合中添加渲染数据 | `UInterchangeChaosClothAssetPipeline` |
| `DataflowGraphAsset` (属性) | 生成的布料资产将使用的 `Dataflow` 图模板资源路径 | `UInterchangeChaosClothAssetPipeline` |

### 使用示例（蓝图描述）

1.  在 **Interchange 导入对话框** 中，你会看到一个名为 `PipelineDisplayName` 指定的管线（例如 “Cloth Asset Pipeline”）。
2.  选中该管线，可以在 **细节面板** 中配置 `bImportClothAssets`、`bImportSimulationMeshes`、`bImportRenderMeshes` 以及 `DataflowGraphAsset`。
3.  当导入流程执行时，插件会为每个识别出的布料源数据创建一个 `UInterchangeChaosClothAssetFactoryNode`。
4.  在蓝图脚本中，你可以在导入流程执行前，通过遍历节点容器找到这些工厂节点，并使用上述 `Get/Set` 函数动态修改其导入参数，例如：
    ```
    查找所有 ChaosClothAssetFactoryNode -> 循环 -> SetImportSimulationMeshes(True) -> SetGravity((0, 0, -980))。
    ```

## C++ 用法

C++ 用法通常用于深度定制导入行为或编写自动化工具。

### 头文件引入

```cpp
#include “InterchangeChaosClothAssetFactoryNode.h”
#include “InterchangeChaosClothAssetPipeline.h”
```

### 基本用法

获取并配置一个布料资产的工厂节点属性。

```cpp
// 假设你已经有了一个 UInterchangeBaseNodeContainer* NodeContainer 和一个节点 UID
const FString ClothNodeUid = TEXT(“SomeClothRootNodeUid”);
UInterchangeChaosClothAssetFactoryNode* ClothFactoryNode = Cast<UInterchangeChaosClothAssetFactoryNode>(NodeContainer->GetFactoryNode(ClothNodeUid));

if (ClothFactoryNode)
{
    // 启用模拟网格和渲染网格的导入
    ClothFactoryNode->SetImportSimulationMeshes(true);
    ClothFactoryNode->SetImportRenderMeshes(true);

    // 设置求解器属性
    ClothFactoryNode->SetGravity(FVector3f(0.0f, 0.0f, -980.0f)); // 使用厘米/秒^2为单位
    ClothFactoryNode->SetAirDamping(0.1f);
    ClothFactoryNode->SetSubStepCount(4);
    ClothFactoryNode->SetTimeStep(1.0f / 30.0f); // 30 FPS

    // 指定一个Dataflow图模板
    FSoftObjectPath GraphPath(“/Game/Dataflow/ClothSimulationTemplate”);
    ClothFactoryNode->SetDataflowGraphPath(GraphPath);
}
```

### 进阶用法

通过继承管线类，实现自定义的布料资产识别和处理逻辑。

```cpp
// MyCustomClothPipeline.h
UCLASS()
class UMyCustomClothPipeline : public UInterchangeChaosClothAssetPipeline
{
    GENERATED_BODY()
public:
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override
    {
        // 1. 先调用父类实现，完成标准的布料节点识别和工厂节点创建
        Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

        // 2. 添加自定义逻辑，例如：为所有找到的布料节点设置一个特定的Dataflow图
        TArray<UInterchangeFactoryNode*> FactoryNodes;
        BaseNodeContainer->GetFactoryNodes(FactoryNodes);
        for (UInterchangeFactoryNode* Node : FactoryNodes)
        {
            if (UInterchangeChaosClothAssetFactoryNode* ClothNode = Cast<UInterchangeChaosClothAssetFactoryNode>(Node))
            {
                FSoftObjectPath CustomGraphPath(“/Game/Dataflow/MySuperClothTemplate”);
                ClothNode->SetDataflowGraphPath(CustomGraphPath);
                // 也可以根据源数据路径等条件设置不同的图模板
            }
        }
    }
};
```

## Demo 示例

一个简单的示例，展示如何使用工厂节点类的 API。

```cpp
// MyClothImporter.h
#pragma once
#include “CoreMinimal.h”
#include “InterchangeChaosClothAssetFactoryNode.h”

class FMyClothImporter
{
public:
    void ConfigureClothNode(UInterchangeChaosClothAssetFactoryNode* ClothNode);
};

// MyClothImporter.cpp
#include “MyClothImporter.h”
#include “InterchangeChaosClothAssetDefinitions.h” // 用于常量引用

void FMyClothImporter::ConfigureClothNode(UInterchangeChaosClothAssetFactoryNode* ClothNode)
{
    if (!ClothNode) return;

    // 使用插件定义的常量名来获取/设置节点上的用户属性（这通常是内部流程，但展示了可访问性）
    // 注意：直接使用蓝图函数如 SetGravity 更为常用。

    // 设置基本导入选项
    ClothNode->SetImportSimulationMeshes(true);
    ClothNode->SetImportRenderMeshes(true);

    // 配置物理求解器
    ClothNode->SetGravity(FVector3f(0.f, 0.f, -980.f));
    ClothNode->SetAirDamping(0.05f);
    ClothNode->SetSubStepCount(8); // 更高的精度

    UE_LOG(LogTemp, Log, TEXT(“Configured Chaos Cloth Factory Node: %s”), *ClothNode->GetUniqueID());
}
```

## 模块依赖

根据插件功能分析，要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心模块 |
| `InterchangeNodes` | Interchange 基础节点定义 |
| `InterchangeFactoryNodes` | Interchange 工厂节点基类 |
| `ChaosClothAsset` | Chaos 布料资产核心类 |
| `DataflowEngine` | 用于处理 `Dataflow` 图和变量 |

## 维护状态

### 近期更新

从 git 历史看，该插件近期有持续更新：

- `852b276c` 2026-05-13 — 修复了在严格浮点模式下关于双精度常量截断为单精度的警告。
- `a7e94182` 2026-05-12 — **布料资产交换：添加了对重新导入的支持。** 这是一个重要的功能更新。
- `60127194` 2026-04-27 — [ChaosClothAsset] 修复静态分析违规的简单问题。
- `665076e6` 2026-04-27 — USD Interchange: 添加了对 ChaosCloth 资产的支持。（这可能是插件的初始提交或重大功能提交）

### 维护评价

- **创建时间**：非常新（2026年）。
- **活跃度**：**活跃维护中**。最近一个月内有多次提交，包括重要的“重导入”功能添加和代码质量修复。
- **状态**：插件被标记为 **实验性** (`IsExperimentalVersion: true`)，且 **默认不启用** (`EnabledByDefault: false`)。这表明它功能已实现但可能尚未完全稳定或面向所有用户开放，建议在需要时手动启用并关注其后续版本。
- **推荐使用**：如果你有通过 Interchange 导入 Chaos 布料资产的需求，并且能够接受实验性功能的潜在风险，可以启用和使用此插件。它正在被积极开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- [Interchange 系统文档](https://docs.unrealengine.com/5.8/en-US/interchange-overview-in-unreal-engine/)
- [Chaos Cloth 文档](https://docs.unrealengine.com/5.8/en-US/chaos-cloth-in-unreal-engine/)