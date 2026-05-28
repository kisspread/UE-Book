# Editor DataflowGraph

> Editor Dataflow Graph（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | 数据流图编辑器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（模板资产、材质、蓝图） |
| 模块 | `DataflowEditor` (Editor), `DataflowEnginePlugin` (Runtime), `DataflowNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow) | |

## 用途

Dataflow 插件提供了一套完整的**节点图式数据流编辑器**，用于在 UE5 编辑器中以可视化方式构建和执行程序化资产处理管线。它解决了以下核心问题：

1. **程序化资产构建**：通过节点图定义几何数据（网格、骨骼、蒙皮权重、布料等）的生成与处理流程，替代手动建模
2. **构造与模拟分离**：明确区分"构造阶段"（生成几何体）和"模拟阶段"（运行物理模拟），每个阶段有独立的视口和场景
3. **交互式编辑工具集成**：将权重绘制、骨骼编辑、网格选择等交互工具直接嵌入节点图工作流，工具操作可写回节点属性
4. **资产类型无关的通用框架**：为布料（ChaosCloth）、几何集合（GeometryCollection）、毛发（Groom）等多种资产类型提供统一的数据流编辑基础设施

该插件从 Experimental 阶段迁出，经过模块重组（合并 DataflowAssetTools 到 DataflowCore/DataflowNodes），已成为正式功能。

## 使用场景

- 你在制作 Chaos 布料资产 → 用 Dataflow 图定义布料网格的几何生成、蒙皮权重绑定、碰撞体配置等流程
- 你需要程序化生成 GeometryCollection → 用 Dataflow 节点串联几何操作、破碎策略、物理属性设置
- 你要为 Groom（毛发）资产构建数据处理管线 → 注册自定义模板和渲染类型，用 Dataflow 图编排毛发生成逻辑
- 你需要对网格进行交互式蒙皮权重校正 → 使用内置的 Weight Map Paint 工具和 CorrectSkinWeights 节点
- 你需要可视化调试数据流中间结果 → 利用 Sampler 可渲染类型查看标量/向量场的切片可视化

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDataflowNode` | 在 Dataflow 资产中添加指定类型的节点，返回节点名称 | `UDataflowEditorBlueprintLibrary` |
| `ConnectDataflowNodes` | 连接一个节点的输出到另一个节点的输入 | `UDataflowEditorBlueprintLibrary` |
| `AddDataflowFromClipboardContent` | 从剪贴板内容粘贴节点到指定位置 | `UDataflowEditorBlueprintLibrary` |
| `SetDataflowNodeProperty` | 设置 Dataflow 节点的属性值（以字符串形式） | `UDataflowEditorBlueprintLibrary` |

### 使用示例（蓝图描述）

在编辑器工具蓝图中：
1. 获取目标 `UDataflow` 资产引用
2. 调用 `AddDataflowNode` 创建一个节点（指定 `NodeTypeName` 如 `"MergeCollections"`、`BaseName`、`Location`）
3. 重复上述步骤创建第二个节点
4. 调用 `ConnectDataflowNodes`，传入两个节点名和对应的输出/输入引脚名
5. 调用 `SetDataflowNodeProperty` 设置节点的参数值

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/DataflowEditorCommands.h"
#include "Dataflow/DataflowAssetEditUtils.h"
#include "Dataflow/DataflowEditor.h"
```

### 基本用法 — 编程式编辑 Dataflow 资产

以下示例展示如何在 C++ 中程序化地修改 Dataflow 资产（添加节点、连接、变量管理等）。

```cpp
// 来源: Public/Dataflow/DataflowAssetEditUtils.h

#include "Dataflow/DataflowAssetEditUtils.h"
#include "DataflowAsset.h"

void AddAndConnectNodes(UDataflow* DataflowAsset)
{
    UEdGraph* EdGraph = DataflowAsset->GetEdGraph();
    
    // 添加两个节点
    UDataflowEdNode* NodeA = UE::Dataflow::FEditAssetUtils::AddNewNode(
        EdGraph,
        FVector2D(0, 0),          // 位置
        FName("MyNodeA"),          // 节点名称
        FName("CollectionFromStaticMesh"), // 节点类型名
        nullptr                     // FromPin（可选，用于自动连接）
    );

    UDataflowEdNode* NodeB = UE::Dataflow::FEditAssetUtils::AddNewNode(
        EdGraph,
        FVector2D(400, 0),
        FName("MyNodeB"),
        FName("MergeCollections"),
        nullptr
    );

    // 管理变量
    FName VarName = UE::Dataflow::FEditAssetUtils::AddNewVariable(DataflowAsset, FName("Radius"));
    UE::Dataflow::FEditAssetUtils::SetVariableValue(DataflowAsset, VarName, SourcePropertyBag);
}
```

### 基本用法 — 评估节点

以下示例展示如何评估单个 Dataflow 节点：

```cpp
// 来源: Public/Dataflow/DataflowEditorCommands.h

#include "Dataflow/DataflowEditorCommands.h"

void EvaluateSingleNode(UDataflow* DataflowAsset, const FDataflowNode* Node)
{
    UE::Dataflow::FEngineContext Context;
    UE::Dataflow::FTimestamp LastTimestamp = UE::Dataflow::FTimestamp::Invalid;

    // 评估节点（如果时间戳更新则执行，否则跳过）
    const FDataflowNode* EvaluatedNode = FDataflowEditorCommands::EvaluateNode(
        Context,
        LastTimestamp,
        DataflowAsset,
        Node,
        nullptr,    // Output: nullptr = 评估所有输出
        FString(),  // NodeName: 当 Node 有效时忽略
        nullptr     // Asset: 终端节点会调用 SetAssetValue
    );
}
```

### 进阶用法 — 注册自定义工具到 Dataflow 编辑器

```cpp
// 来源: Public/Dataflow/DataflowToolRegistry.h

#include "Dataflow/DataflowToolRegistry.h"

void RegisterMyCustomTool()
{
    auto& ToolRegistry = UE::Dataflow::FDataflowToolRegistry::Get();
    
    // 注册一个节点类型到交互工具的映射
    ToolRegistry.AddNodeToToolMapping(
        FName("MyCustomNode"),                          // 节点类型名
        MyToolBuilder,                                   // UInteractiveToolBuilder*
        MyToolActionCommands,                            // 工具操作命令
        FSlateIcon("MyStyle", "MyIcon"),                 // 添加节点按钮图标
        LOCTEXT("AddMyNode", "Add My Node"),             // 按钮文本
        FName("General"),                                // 工具分类
        FName("FManagedArrayCollection"),                // 连接类型
        FName("Collection")                              // 连接名称
    );
}
```

### 进阶用法 — 注册可渲染类型

```cpp
// 来源: Public/DataflowRendering/DataflowRenderableTypeRegistry.h

#include "DataflowRendering/DataflowRenderableTypeRegistry.h"

// 在模块 StartupModule 中注册自定义可渲染类型
void FMyModule::StartupModule()
{
    // 使用宏注册自定义渲染类型
    UE_DATAFLOW_REGISTER_RENDERABLE_TYPE(FMyCustomRenderableType);
}
```

### 进阶用法 — 注册 Dataflow 模板

```cpp
// 来源: Public/Dataflow/DataflowTemplateRegistry.h

#include "Dataflow/DataflowTemplateRegistry.h"

void FMyEditorModule::StartupModule()
{
    auto& Registry = FDataflowTemplateRegistry::Get();

    // 方式1: 注册单个模板资产
    Registry.RegisterTemplateAsset(
        UMyAsset::StaticClass(),
        { FSoftObjectPath(TEXT("/MyPlugin/Dataflow/Templates/DF_BasicSetup")),
          LOCTEXT("BasicSetup", "Basic Setup"),
          LOCTEXT("BasicTooltip", "A basic processing template"),
          FSlateIcon("MyStyle", "ClassIcon.MyAsset") }
    );

    // 方式2: 注册模板文件夹（扫描文件夹中所有 UDataflow 资产）
    Registry.RegisterTemplateFolder(
        UMyAsset::StaticClass(),
        { TEXT("/MyPlugin/Dataflow/Templates"),
          FSlateIcon("MyStyle", "ClassIcon.MyAsset") }
    );
}
```

## Demo 示例

### 自定义 Dataflow 节点与属性 Gizmo

```cpp
// MyTransformNode.h
#pragma once

#include "Dataflow/DataflowNode.h"

// 通过 meta=(GizmoType="Translate") 在视口中显示位移 Gizmo
USTRUCT(Meta = (DataflowCollection))
struct FMyTransformNode : public FDataflowNode
{
    GENERATED_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyTransformNode, "MyTransform", "Collection", "Apply a custom transform to collection")

    FMyTransformNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection);
    }

    // 输入/输出 Collection（透传）
    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 位移 Gizmo — 选择节点后在视口中显示可交互的位移手柄
    UPROPERTY(EditAnywhere, Category = "Transform", meta = (GizmoType = "Translate"))
    FVector Origin = FVector::ZeroVector;

    // 旋转 Gizmo — 选择节点后在视口中显示可交互的旋转手柄
    UPROPERTY(EditAnywhere, Category = "Transform", meta = (GizmoType = "Rotate"))
    FQuat Orientation = FQuat::Identity;

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        FManagedArrayCollection& OutCollection = GetValue<FManagedArrayCollection>(Context, &Collection);
        // 在此处对 OutCollection 应用 Origin/Orientation 变换
    }
};
```

```cpp
// MyTransformNode.cpp
#include "MyTransformNode.h"

// 节点的 Evaluate 实现在 .cpp 中完成
// 注册宏确保节点类型在编辑器中可用
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` / `DataflowCore` | 数据流核心运行时：图、节点、连接、评估上下文 |
| `DataflowNodes` | 内置节点集合（网格操作、Collection 处理等） |
| `Chaos` / `ChaosSolverEngine` | Chaos 物理求解器集成 |
| `ChaosCaching` / `ChaosCacheManager` | 模拟结果缓存录制与回放 |
| `GeometryCollectionEngine` | GeometryCollection 资产支持 |
| `GeometryScriptingCore` / `GeometryFramework` | 动态网格操作与渲染 |
| `InteractiveToolsFramework` / `EditorInteractiveToolsFramework` | 交互式编辑工具基础设施 |
| `ModelingComponents` | 网格雕刻、权重绘制等工具组件 |
| `AssetTools` / `AssetDefinition` | 资产定义与编辑器集成 |
| `GroomPlugin` / `ChaosClothEditor` | 毛发/布料资产类型支持（可选） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `ee85ff45` | Dataflow : remove sections from rendering settings since they are half broken | 移除渲染设置中损坏的分节功能 |
| 2026-05-25 | `25af8e6f` | Dataflow : add extra checks on the edit skin weight tool to inform user about why the node may not s | 蒙皮权重编辑工具增加检查，提示节点无法操作的原因 |
| 2026-05-22 | `9a062c29` | [Dataflow Editor] Fixed container mutation during tick evaluation. | 修复 Tick 评估期间容器被意外修改的问题 |
| 2026-05-22 | `8dc486bc` | Dataflow Editor : Fix crash happening when using a tool with another Dataflow editor opened | 修复同时打开多个 Dataflow 编辑器时使用工具导致的崩溃 |
| 2026-05-22 | `8cfadbd3` | Dataflow Editor : fix Undo / redo issues with comment nodes | 修复注释节点的撤销/重做问题 |

### 维护评价

- **活跃维护**：该插件刚从 Experimental 迁出不到一个月（2026-04-17），近期有密集的功能完善和 Bug 修复
- **成熟度**：代码库规模庞大（399 个源文件），架构设计成熟，包含完整的工具链、渲染系统和模拟缓存支持
- **已知限制**：首次 commit 信息提及"Demoted internal-only public headers to Private"、"Removed redundant dependencies"，表明正在进行 API 清理，部分接口可能仍有变动
- **推荐程度**：作为 Epic 官方维护的核心编辑器功能，推荐用于布料/几何集合/毛发等资产的程序化工作流构建。但鉴于刚离开 Experimental，建议关注后续 API 稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Dataflow)
- [官方文档](https://docs.unrealengine.com)（.uplugin 中未提供专用文档链接）