# Interchange Chaos Cloth Asset

> Contains the classes and objects required to allow Interchange to produce Chaos Cloth Assets

| 属性 | 值 |
|---|---|
| 中文名 | Interchange布料导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeChaosClothAssetImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset) | |

## 用途

此插件是 Unreal Engine **Interchange 导入框架**的一个扩展，专门用于支持**Chaos Cloth 布料资产**的导入。它解决的核心问题是：将外部数字内容创作工具（DCC，如 Maya、Houdini、Blender）中创建的布料模拟数据（网格、属性、拓扑），通过 Interchange 的标准化管线，自动转换为 UE 内部的 `UChaosClothAsset`。这使得布料资产的导入过程能够复用 Interchange 框架的批量处理、管线自定义和自动化能力，简化角色服装、旗帜、柔性物体等布料效果的制作流程。

## 使用场景

- 你的美术团队使用 Maya 或 Houdini 等工具制作角色服装的布料模拟，并需要将其批量、标准化地导入 UE 项目。
- 你需要一个可定制的导入管线，在导入布料资产时自动附加特定的 Dataflow 图以定义后续处理逻辑。
- 你希望利用 USD 等通用交换格式，通过 Interchange 框架将布料数据从其他 DCC 工具引入 UE 的 Chaos 物理系统。

## 蓝图用法

此插件的蓝图 API 主要通过 `UInterchangeChaosClothAssetFactoryNode` 类暴露，用于在 Interchange 管线执行期间配置布料资产的导入参数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetImportSimulationMeshes` / `SetImportSimulationMeshes` | 获取或设置是否导入模拟网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetImportRenderMeshes` / `SetImportRenderMeshes` | 获取或设置是否导入渲染网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetDataflowGraphPath` / `SetDataflowGraphPath` | 获取或设置用于实例化到布料资产中的 Dataflow 图模板路径 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetAirDamping` / `SetAirDamping` | 获取或设置空气阻尼求解器参数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetGravity` / `SetGravity` | 获取或设置重力求解器参数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetSubStepCount` / `SetSubStepCount` | 获取或设置子步进求解器参数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetTimeStep` / `SetTimeStep` | 获取或设置时间步长求解器参数 | `UInterchangeChaosClothAssetFactoryNode` |

### 使用示例（蓝图描述）

在自定义的 Interchange 管线蓝图中，当执行到布料相关的节点时，可以通过 `Find Interchange Factory Node` 节点找到 `UInterchangeChaosClothAssetFactoryNode`。然后，使用上述的 `Set` 节点来配置本次导入任务的具体参数，例如：
1.  调用 `Set Import Simulation Meshes` 并传入 `true`，表示本次导入需要包含模拟网格。
2.  调用 `Set Import Render Meshes` 并传入 `false`，表示不需要导入渲染网格。
3.  调用 `Set Dataflow Graph Path` 并传入一个 `Dataflow` 资产路径，使生成的布料资产自动绑定该图。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeChaosClothAssetFactoryNode.h"
#include "InterchangeChaosClothAssetFactory.h"
#include "InterchangeChaosClothAssetPipeline.h"
```

### 基本用法

以下代码演示了如何在 C++ 中配置 `UInterchangeChaosClothAssetPipeline` 的参数，以控制布料资产的导入行为。

```cpp
// 来源于管线类 UInterchangeChaosClothAssetPipeline 的属性
// 在创建或修改导入管线实例时设置
void ConfigureClothImportPipeline(UInterchangeChaosClothAssetPipeline* Pipeline)
{
    if (Pipeline)
    {
        Pipeline->PipelineDisplayName = TEXT("角色服装导入");
        Pipeline->bImportClothAssets = true; // 启用布料资产导入
        Pipeline->bImportSimulationMeshes = true; // 包含模拟网格
        Pipeline->bImportRenderMeshes = true; // 包含渲染网格
        // 设置数据流图模板的软引用路径
        Pipeline->DataflowGraphAsset = FSoftObjectPath(TEXT("/Game/Dataflows/ClothPostProcess.ClothPostProcess"));
    }
}
```

### 进阶用法

在自定义工厂的处理逻辑中，你可能需要直接操作 `UInterchangeChaosClothAssetFactoryNode`。

```cpp
// 在 Interchange 工厂或管线的回调中，对找到的布料工厂节点进行精细控制
void CustomizeClothFactoryNode(UInterchangeChaosClothAssetFactoryNode* FactoryNode)
{
    if (FactoryNode)
    {
        // 覆盖工厂节点中的求解器属性
        FactoryNode->SetAirDamping(0.1f);
        FactoryNode->SetGravity(FVector3f(0.0f, 0.0f, -980.0f));
        FactoryNode->SetSubStepCount(2);
        FactoryNode->SetTimeStep(1.0f/30.0f);

        // 也可以覆盖工厂节点上的网格导入标志（优先级可能高于管线设置）
        FactoryNode->SetImportSimulationMeshes(true);
        FactoryNode->SetImportRenderMeshes(true);
    }
}
```

## Demo 示例

一个最小化的自定义导入管线示例，展示了如何从 C++ 层面创建和配置一个用于布料资产的 Interchange 导入流程。

### `ClothImportPipeline.h`
```cpp
#pragma once

#include "CoreMinimal.h"
#include "InterchangeChaosClothAssetPipeline.h"
#include "ClothImportPipeline.generated.h"

UCLASS()
class UClothImportPipeline : public UInterchangeChaosClothAssetPipeline
{
    GENERATED_BODY()

public:
    UClothImportPipeline();

    // 重写管线执行逻辑，可在调用父类前进行额外处理
    virtual void ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath) override;
};
```

### `ClothImportPipeline.cpp`
```cpp
#include "ClothImportPipeline.h"

UClothImportPipeline::UClothImportPipeline()
{
    // 在构造函数中设置默认管线参数
    PipelineDisplayName = TEXT("自定义布料管线");
    bImportClothAssets = true;
    bImportSimulationMeshes = true;
    bImportRenderMeshes = false; // 默认不导入渲染网格，以节省资源
    DataflowGraphAsset = FSoftObjectPath(TEXT("/Game/Dataflows/DefaultCloth.DefaultCloth"));
}

void UClothImportPipeline::ExecutePipeline(UInterchangeBaseNodeContainer* BaseNodeContainer, const TArray<UInterchangeSourceData*>& SourceDatas, const FString& ContentBasePath)
{
    // 在调用标准布料管线处理逻辑之前，可以添加自定义的节点扫描或修改逻辑
    // ...

    // 调用父类执行标准的布料资产导入管线处理
    Super::ExecutePipeline(BaseNodeContainer, SourceDatas, ContentBasePath);

    // 在调用之后，可以进行后处理，例如记录日志或更新其他资产
    UE_LOG(LogInterchangeChaosClothAssetImport, Log, TEXT("布料导入管线执行完成。"));
}
```

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下模块和插件：

| 模块/插件 | 用途 |
|---|---|
| `Interchange` | 核心的资产交换框架，提供导入/导出的基础架构 |
| `ChaosClothAsset` | 提供 `UChaosClothAsset` 资产类型和相关基础功能 |
| `ChaosClothAssetDataflowNodes` | 提供用于布料资产的 Dataflow 节点，与 `DataflowGraphAsset` 属性配合使用 |
| `DataflowEngine` | 运行时执行 Dataflow 图的引擎模块，工厂中 `DataflowGraphAsset` 属性需要它 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `c97da6bd` | Interchange ClothAsset: Use ShortName on the new modules to mitigate some long filepath issues | 重构模块命名，缩短文件路径以解决长度问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为布料资产添加重导入支持 |
| 2026-04-27 | `60127194` | [ChaosClothAsset] Simple fix for static analysis violation | 修复静态分析检测到的违规代码 |
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | 通过 USD Interchange 插件增加了对 Chaos 布料资产的支持 |

### 维护评价

此插件处于**活跃维护**状态。

- **创建时间**：插件本身创建时间未知，但作为 Interchange 框架的扩展，其更新与主引擎紧密相关。
- **近期活动**：在2026年4月至5月间有多次提交，包括功能增强（添加重导入支持、USD支持）、代码重构和bug修复，表明 Epic 内部仍在积极使用和改进此模块。
- **实验性状态**：插件被标记为 `IsExperimentalVersion = true`，且默认不启用。这意味着其API和行为可能在未来版本中发生变化，不建议在需要长期稳定性的生产项目中将其作为核心依赖。
- **推荐使用**：如果你的项目正在评估或需要从外部DCC工具通过 Interchange 框架导入布料数据，并且可以接受实验性API的潜在变动，此插件是官方提供的、正在维护的解决方案。对于生产环境，建议密切关注其版本更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset)
- 官方文档：暂无
- 测试用例：插件目录内未发现标准测试用例文件，其功能主要通过集成到Interchange导入流程中进行验证。