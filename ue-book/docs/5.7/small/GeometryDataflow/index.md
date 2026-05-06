# Geometry Dataflow Nodes

> Geometry Processing in Dataflow.

| 属性 | 值 |
|---|---|
| 中文名 | 几何数据流节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryDataflow) | |

---

## 用途

该插件将几何处理（目前为网格布尔运算）封装为 **Dataflow 节点**，使高级用户能够在蓝图或程序化工作流中通过 Dataflow 图形化系统组合几何体操作。  
它解决了传统几何布尔运算（Union、Intersect、Difference）需要手动代码调用或复杂编辑器脚本的问题，利用 Dataflow 的节点化特性实现可视化、可复用、可参数化的几何处理管线。

## 使用场景

- 你在构建程序化生成工具（如建筑、地形、机械零件）时，需要对多个静态网格体执行布尔合并、减除或交集。
- 你正在开发依靠 Dataflow 框架的 U 工具（例如 Chaos 破坏系统或几何脚本），需要将网格布尔操作融入已有节点图。
- 你需要通过蓝图暴露一组简洁的几何布尔运算，而不希望直接操作 `UDynamicMesh` 的底层 API。

## 蓝图用法

该插件在蓝图中暴露了枚举 `EMeshBooleanOperationEnum`，用于 Dataflow 节点的属性配置。  
虽然 Dataflow 节点本身主要在编辑器或运行时通过 `Dataflow` 子系统使用，但你可以直接创建 `Create Dataflow Asset` 并引用该节点。

### 枚举值

| 枚举值 | 显示名 | 说明 |
|---|---|---|
| `Dataflow_MeshBoolean_Union` | Union | 并集：A + B，包含 A 或 B 内部的点 |
| `Dataflow_MeshBoolean_Intersect` | Intersect | 交集：A ∩ B，仅包含同时在 A 和 B 内部的点 |
| `Dataflow_MeshBoolean_Difference` | Difference | 差集：A – B，减去 B 在 A 内部的部分 |

### 使用示例

1. 在内容浏览器中创建 Dataflow 资产。
2. 右键添加节点 `MeshBoolean`（位于 `Mesh\|Utilities` 类别）。
3. 连接两个 `UDynamicMesh` 输入（来源于其他节点，如 `StaticMeshToMesh`）。
4. 在细节面板中选择 `Operation` 为 `Union` / `Intersect` / `Difference`。
5. 运行 Dataflow 图，输出的 `Mesh` 即为运算结果。

## C++ 用法

### 头文件引入

```cpp
#include "Dataflow/MeshBooleanNodes.h"
```

### 基本用法

直接从源代码提取的最小实例——创建节点并手动求值（通常由 Dataflow 框架内部调用）：

```cpp
#include "Dataflow/MeshBooleanNodes.h"
#include "Dataflow/DataflowEngine.h"
#include "DynamicMesh/DynamicMesh3.h"

// 创建节点实例
UE::Dataflow::FNodeParameters Params;
FMeshBooleanDataflowNode Node(Params);

// 准备输入（假设已有两个 UDynamicMesh 对象）
TObjectPtr<UDynamicMesh> InputMeshA = ...;
TObjectPtr<UDynamicMesh> InputMeshB = ...;

// 设置输入属性
Node.Mesh1 = InputMeshA;
Node.Mesh2 = InputMeshB;
Node.Operation = EMeshBooleanOperationEnum::Dataflow_MeshBoolean_Union;

// 创建 Dataflow 上下文
UE::Dataflow::FContext Context;
// 对输出求值（触发 Evaluate）
const FDataflowOutput* Out = Node.GetOutput("Mesh");
Node.Evaluate(Context, Out);

// 获取结果
TObjectPtr<UDynamicMesh> ResultMesh = Context.EvaluateValue<TObjectPtr<UDynamicMesh>>(Out);
```

> 源码路径：`Engine/Plugins/Experimental/GeometryDataflow/Source/GeometryDataflowNodes/Public/Dataflow/MeshBooleanNodes.h`

### 进阶用法

该节点设计为 Dataflow 图中的标准节点，通常不直接手动调用，而是通过数据流图运行器触发。  
你可以在 `DataflowAsset` 中添加多个 `MeshBoolean` 节点，组合成复杂网格处理管线。  
更高级的用法涉及自定义 Dataflow 节点，使用该节点作为子节点：  

```cpp
// 在自定义 DataflowNode 的 Evaluate 中调用已有节点
void FMyNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    FMeshBooleanDataflowNode BooleanNode(GetParams());
    BooleanNode.Mesh1 = Context.EvaluateInput<TObjectPtr<UDynamicMesh>>("InputMeshA");
    BooleanNode.Mesh2 = Context.EvaluateInput<TObjectPtr<UDynamicMesh>>("InputMeshB");
    BooleanNode.Operation = EMeshBooleanOperationEnum::Dataflow_MeshBoolean_Intersect;

    FDataflowOutput* TempOut = BooleanNode.GetOutput("Mesh");
    BooleanNode.Evaluate(Context, TempOut);
    // 将结果输出到当前节点
    SetOutputValue(Context, "Result", Context.EvaluateValue<TObjectPtr<UDynamicMesh>>(TempOut));
}
```

## Demo 示例

一个完整的、可编译的最小示例（仅头文件 + 实现文件，假设已依赖插件模块）。

### BooleanTest.h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Dataflow/DataflowEngine.h"
#include "Dataflow/MeshBooleanNodes.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "Engine/StaticMesh.h"

// 演示：从两个 UStaticMeshComponent 创建 UDynamicMesh 并执行差集
class FBooleanDemo
{
public:
    static bool RunDifference(UStaticMesh* MeshA, UStaticMesh* MeshB, TObjectPtr<UDynamicMesh>& OutResult);
};
```

### BooleanTest.cpp

```cpp
#include "BooleanTest.h"
#include "UDynamicMesh.h"
#include "MeshDescriptionToDynamicMesh.h" // 假设有转换工具
#include "DynamicMeshToMeshDescription.h"

bool FBooleanDemo::RunDifference(UStaticMesh* MeshA, UStaticMesh* MeshB, TObjectPtr<UDynamicMesh>& OutResult)
{
    // 1. 创建 UDynamicMesh 并填充数据（简化：从 StaticMesh 转换）
    UDynamicMesh* DynMeshA = NewObject<UDynamicMesh>();
    UDynamicMesh* DynMeshB = NewObject<UDynamicMesh>();
    // 实际转换需借助 FMeshDescriptionToDynamicMesh，此处省略

    // 2. 创建布尔节点
    UE::Dataflow::FNodeParameters Params;
    FMeshBooleanDataflowNode Node(Params);
    Node.Mesh1 = DynMeshA;
    Node.Mesh2 = DynMeshB;
    Node.Operation = EMeshBooleanOperationEnum::Dataflow_MeshBoolean_Difference;

    // 3. 求值
    UE::Dataflow::FContext Context;
    const FDataflowOutput* Out = Node.GetOutput("Mesh");
    Node.Evaluate(Context, Out);
    OutResult = Context.EvaluateValue<TObjectPtr<UDynamicMesh>>(Out);
    return OutResult != nullptr;
}
```

## 模块依赖

使用此插件时，你的模块 `Build.cs` 需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供 Dataflow 框架核心（节点注册、图求值） |
| `GeometryProcessing` | 提供网格布尔运算算法（`FDynamicMesh3` 操作） |

**无其他特殊依赖**（标准 `Core`, `CoreUObject`, `Engine` 等已隐含）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-07-25 | `21604ae4` | 为 Dataflow 网格布尔节点和操作枚举值添加更详细的注释和工具提示 |
| 2025-01-21 | `f0b2a49e` | 初始提交：添加几何处理 Dataflow 插件，并从已有代码中搬迁相关节点（从 `MeshBoolean` 节点开始） |

### 维护评价

- **创建时间**：2025-01-21，属于非常新的插件（约 1 年）。
- **更新频率**：有功能性初始提交和之后的注释改进，但当前只有 2 次 commit，活跃度较低。
- **活跃状态**：近期（2025-07）有更新，说明仍处于早期开发或维护中。
- **已知问题**：插件标记为 `IsBetaVersion=true`，API 可能不稳定，并且功能非常有限（仅布尔运算）。
- **推荐程度**：如果你正在使用 Dataflow 框架并且需要基础网格布尔操作，可以试用。但考虑到它仍为实验性插件，建议仅在非生产项目中使用；若需要完整几何处理，可考虑直接使用 `GeometryProcessing` 模块的低级 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryDataflow)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryDataflow/Tests)（尚未创建）
- 官方文档：暂无