# Optimus

> Deprecated plugin now redirected to DeformerGraph

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | *(无模块，仅依赖 DeformerGraph)* |
| 创建时间 | 2020-07-19 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Animation/Optimus/Optimus.uplugin) | |

## ⚠️ 重要：此插件已废弃

**Optimus 是一个已被废弃的空壳插件，所有功能已迁移至 [DeformerGraph](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/DeformerGraph/)。** Optimus 插件的 `.uplugin` 文件仅包含一个依赖声明，自动启用 DeformerGraph：

```json
{
    "Description": "Deprecated plugin now redirected to DeformerGraph",
    "EnabledByDefault": false,
    "Modules": [],
    "Plugins": [
        { "Name": "DeformerGraph", "Enabled": true }
    ]
}
```

如果你在项目中仍然引用 Optimus 插件，它会透明地加载 DeformerGraph。**建议直接使用 DeformerGraph 插件**。

## 用途

Optimus / DeformerGraph 是 UE5 的 **GPU 网格变形图编辑器**，允许开发者通过可视化节点图的方式创建自定义的骨骼网格变形（Mesh Deformation）管线。核心思想是：

- 用 **Compute Shader** 在 GPU 上执行网格变形操作
- 通过 **节点图（Node Graph）** 可视化地编排计算逻辑
- 支持 **HLSL 自定义内核**，可以在节点中直接编写着色器代码
- 与 **ControlRig** 深度集成，可在动画蓝图中动态触发和控制变形

简单来说：如果你需要在 GPU 上对骨骼网格做自定义变形（如肌肉模拟、布料、程序化变形等），DeformerGraph（原 Optimus）就是你需要的工具。

## 历史沿革

| 时间 | 事件 |
|---|---|
| 2020-07-19 | Optimus 首次出现于 `Engine/Plugins/Experimental/Optimus/`，作为实验性插件 |
| 2022-08-30 | DeformerGraph 插件在 `Engine/Plugins/Animation/DeformerGraph/` 创建，继承所有源码 |
| 2022-09-22 | Optimus 被重新添加为 `Engine/Plugins/Experimental/Animation/Optimus/`，仅作为 DeformerGraph 的空壳重定向 |
| 持续至今 | 所有类名仍保留 `Optimus` 前缀（如 `UOptimusDeformer`、`UOptimusNodeGraph`） |

## 使用场景

- 你需要在 GPU 上对骨骼网格执行自定义变形 → 使用 **DeformerGraph**
- 你需要通过蓝图动态控制变形参数 → 使用 **DeformerGraph + 蓝图变量**
- 你需要在 ControlRig 中触发自定义 GPU 变形 → 使用 **DeformerGraph + FRigUnit_AddOptimusDeformer**
- 你需要全局自动应用变形器到所有骨骼网格 → 配置 **项目设置中的 DeformerGraph 默认变形器**
- 你只需要 CPU 端的动画逻辑 → 使用 ControlRig，**不需要** DeformerGraph

## 核心概念（DeformerGraph）

### 图类型

DeformerGraph 支持以下图类型（`EOptimusNodeGraphType`）：

| 图类型 | 说明 |
|---|---|
| **Setup** | 仅在组件首次初始化时执行一次，用于一次性设置 |
| **Update** | 每帧执行的主图，核心变形逻辑在此编写 |
| **ExternalTrigger** | 由蓝图触发的图，可用于按需执行特定操作 |
| **Function** | 可复用的函数图，通过函数引用节点调用 |
| **SubGraph** | 子图，用于组织和折叠节点以提高可读性 |

### 执行域（Execution Domain）

执行域定义了内核（Kernel）在哪个维度上并行执行：

| 域名 | 说明 |
|---|---|
| `Vertex` | 逐顶点执行 |
| `Triangle` | 逐三角形执行 |
| `Bone` | 逐骨骼执行 |
| `UVChannel` | 逐 UV 通道执行 |
| `Singleton` | 仅执行一次（全局数据） |

### 数据域（Data Domain）

资源的数据域决定了缓冲区的大小和索引方式。支持两种模式：

- **维度型（Dimensional）**：预定义维度名 + 可选倍率，如 `Vertex`、`Bone`、`Vertex.Bone x 2`
- **表达式型（Expression）**：算术表达式，如 `Vertex * 2 + 1`、`1024`

### 资源与变量

- **资源（Resource）**：GPU 缓冲区，有固定大小和数据类型，绑定到特定组件源。多个内核之间通过资源共享数据。
- **变量（Variable）**：可在运行时通过蓝图或 ControlRig 修改的参数，用于动态控制变形行为。

### 内置数据接口

DeformerGraph 提供了丰富的内置数据接口（Data Interface）：

| 数据接口 | 说明 |
|---|---|
| `SkinnedMesh` | 读取蒙皮网格数据 |
| `SkinnedMeshRead` | 只读蒙皮网格数据 |
| `SkinnedMeshWrite` | 写入蒙皮网格数据 |
| `MorphTarget` | 变形目标数据 |
| `Skeleton` | 骨骼数据 |
| `Bone` | 骨骼变换数据 |
| `AdvancedSkeleton` | 高级骨骼数据 |
| `Scene` | 场景信息 |
| `Cloth` | 布料模拟数据 |
| `DebugDraw` | 调试绘制 |
| `Connectivity` | 网格连通性 |
| `HalfEdge` | 半边数据结构 |
| `DuplicateVertices` | 重复顶点 |
| `AnimAttribute` | 动画属性 |
| `SkinWeightsAsVertexMask` | 蒙皮权重作为顶点掩码 |
| `RawBuffer` | 原始缓冲区 |
| `Graph` | 子图数据接口 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Float Variable` | 设置浮点变量值 | `UOptimusDeformerInstance` |
| `Set Vector Variable` | 设置向量变量值 | `UOptimusDeformerInstance` |
| `Set Int Variable` | 设置整数变量值 | `UOptimusDeformerInstance` |
| `Set Bool Variable` | 设置布尔变量值 | `UOptimusDeformerInstance` |
| `Set Transform Variable` | 设置变换变量值 | `UOptimusDeformerInstance` |
| `Set Rotator Variable` | 设置旋转变量值 | `UOptimusDeformerInstance` |
| `Set Quat Variable` | 设置四元数变量值 | `UOptimusDeformerInstance` |
| `Set LinearColor Variable` | 设置颜色变量值 | `UOptimusDeformerInstance` |
| `Set Name Variable` | 设置名称变量值 | `UOptimusDeformerInstance` |
| `Enqueue Trigger Graph` | 触发指定的触发图在下一帧执行 | `UOptimusDeformerInstance` |

所有 `Set*Variable` 节点都有对应的 `Array` 版本（如 `Set Float Array Variable`），用于设置数组类型变量。

### 使用示例（蓝图描述）

**动态设置变形变量：**

1. 获取骨骼网格组件（Skeletal Mesh Component）
2. 获取其 `MeshDeformerInstance`（需要先在组件上配置 DeformerGraph）
3. Cast 到 `UOptimusDeformerInstance`
4. 调用 `Set Float Variable`，传入变量名和值

**触发图执行：**

1. 获取 `UOptimusDeformerInstance`
2. 调用 `Enqueue Trigger Graph`，传入触发图名称
3. 该触发图将在下一帧的 Update 图之前执行

## C++ 用法

### 头文件引入

```cpp
#include "OptimusDeformer.h"              // 变形图资产
#include "OptimusDeformerInstance.h"      // 变形图实例（运行时）
#include "OptimusNodeGraph.h"             // 节点图操作
#include "OptimusResourceDescription.h"   // 资源描述
#include "OptimusVariableDescription.h"   // 变量描述
```

### 创建和管理变形图

`UOptimusDeformer` 是核心资产类，继承自 `UMeshDeformer`。它管理：

- 节点图集合（Setup / Update / Trigger / Function / SubGraph）
- 资源（Resources）：GPU 缓冲区描述
- 变量（Variables）：运行时可修改参数
- 组件绑定（Component Bindings）：连接到场景中的组件

```cpp
// 获取 Update 图
UOptimusNodeGraph* UpdateGraph = Deformer->GetUpdateGraph();

// 添加 Setup 图（首次运行时执行一次）
UOptimusNodeGraph* SetupGraph = Deformer->AddSetupGraph();

// 添加 Trigger 图（蓝图可触发）
UOptimusNodeGraph* TriggerGraph = Deformer->AddTriggerGraph(TEXT("MyTrigger"));

// 添加变量
UOptimusVariableDescription* Var = Deformer->AddVariable(
    FOptimusDataTypeRef(/* float type */),
    FName("MyFloatVariable")
);

// 添加资源
UOptimusResourceDescription* Res = Deformer->AddResource(
    FOptimusDataTypeRef(/* float3 type */),
    FName("VertexOffset")
);

// 设置资源数据域
Deformer->SetResourceDataDomain(Res, FOptimusDataDomain({FName("Vertex")}));

// 编译变形图
Deformer->Compile();
```

### 运行时设置变量

`UOptimusDeformerInstance` 提供了类型安全的变量设置接口：

```cpp
// 获取变形图实例
UOptimusDeformerInstance* Instance = /* ... */;

// 设置各种类型的变量
Instance->SetFloatVariable(FName("Strength"), 1.5f);
Instance->SetVectorVariable(FName("Direction"), FVector(0, 0, 1));
Instance->SetTransformVariable(FName("BoneOffset"), FTransform::Identity);
Instance->SetBoolVariable(FName("bEnableDeformation"), true);
Instance->SetIntVariable(FName("Mode"), 2);

// 设置数组变量
TArray<FVector> Offsets;
// ... 填充数据
Instance->SetVectorArrayVariable(FName("VertexOffsets"), Offsets);

// 触发图
Instance->EnqueueTriggerGraph(FName("MyTrigger"));
```

### ControlRig 集成

DeformerGraph 与 ControlRig 深度集成，提供 `FRigUnit_AddOptimusDeformer` Rig 单元，允许在 ControlRig 图中：

1. **指定要使用的 DeformerGraph 资产**（通过 Trait）
2. **配置执行设置**（执行阶段、执行组、是否变形子组件）
3. **设置变量值**（通过 Variable Trait）
4. **动态添加/移除变形器**到子组件

```cpp
// 在 ControlRig 中使用 DeformerGraph
// 需要包含：
#include "RigUnit_Optimus.h"

// 核心 Rig 单元：
// FRigUnit_AddOptimusDeformer    - 添加并执行变形器
// FRigVMTrait_OptimusDeformer    - 指定变形图资产
// FRigVMTrait_OptimusDeformerSettings - 执行设置
```

### 项目设置配置

```cpp
#include "OptimusSettings.h"

// 通过项目设置配置默认变形器
// 路径: Project Settings → Plugins → DeformerGraph
UOptimusSettings* Settings = GetMutableDefault<UOptimusSettings>();

// 默认模式: Never / OptIn / Always
Settings->DefaultMode = EOptimusDefaultDeformerMode::Always;

// 指定默认变形器资产
Settings->DefaultDeformer = MyDeformerGraphAsset;

// 指定重计算切线的默认变形器
Settings->DefaultRecomputeTangentDeformer = MyTangentDeformerAsset;
```

## Demo 示例

### 最小 DeformerGraph 资产创建（C++）

```cpp
// MyDeformerHelper.h
#pragma once

#include "CoreMinimal.h"
#include "OptimusDeformer.h"

class FMyDeformerHelper
{
public:
    /**
     * 创建一个简单的 DeformerGraph 资产
     * 1. 创建 UOptimusDeformer 资产
     * 2. 添加组件绑定
     * 3. 添加资源和变量
     * 4. 编译
     */
    static UOptimusDeformer* CreateSimpleDeformerGraph(
        const FString& AssetPath,
        const FString& AssetName
    );
};
```

```cpp
// MyDeformerHelper.cpp
#include "MyDeformerHelper.h"
#include "OptimusDeformer.h"
#include "OptimusResourceDescription.h"
#include "OptimusVariableDescription.h"
#include "OptimusComponentSource.h"
#include "OptimusDataDomain.h"
#include "OptimusDataType.h"
#include "OptimusNodeGraph.h"
#include "AssetToolsModule.h"
#include "UObject/Package.h"

UOptimusDeformer* FMyDeformerHelper::CreateSimpleDeformerGraph(
    const FString& AssetPath,
    const FString& AssetName)
{
    // 1. 创建资产
    UPackage* Package = CreatePackage(*FString::Printf(TEXT("%s/%s"), *AssetPath, *AssetName));
    UOptimusDeformer* Deformer = NewObject<UOptimusDeformer>(
        Package, *AssetName, RF_Public | RF_Standalone);

    // 2. 添加默认骨骼网格组件绑定（自动创建）
    // 主组件绑定在创建 Deformer 时自动生成

    // 3. 添加资源：顶点偏移缓冲区
    UOptimusResourceDescription* OffsetResource = Deformer->AddResource(
        FOptimusDataTypeRef(/* Float3 类型 */),
        FName("VertexOffset")
    );

    // 4. 添加变量：变形强度
    UOptimusVariableDescription* StrengthVar = Deformer->AddVariable(
        FOptimusDataTypeRef(/* Float 类型 */),
        FName("Strength")
    );

    // 5. 获取 Update 图，后续可用编辑器添加节点
    UOptimusNodeGraph* UpdateGraph = Deformer->GetUpdateGraph();
    // UpdateGraph->AddNode(...) 等操作可通过编辑器或 Python 完成

    // 6. 标记已修改并保存
    Deformer->MarkModified();
    Package->MarkPackageDirty();

    return Deformer;
}
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "OptimusCore",
    "OptimusSettings",
    "ComputeFramework"
});
```

## 模块依赖

使用 DeformerGraph 功能时，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `OptimusCore` | 核心运行时模块，包含所有变形图类（UOptimusDeformer、UOptimusNodeGraph 等） |
| `OptimusSettings` | 项目设置模块，管理默认变形器配置 |
| `ComputeFramework` | GPU 计算框架，DeformerGraph 的底层依赖 |
| `ControlRig` | 集成 ControlRig Rig 单元（FRigUnit_AddOptimusDeformer） |
| `RigVM` | RigVM 运行时，ControlRig 集成所需 |

编辑器专用模块（仅编辑器代码需要）：

| 模块 | 用途 |
|---|---|
| `OptimusEditor` | 节点图编辑器 UI、资产工厂、Details 面板自定义 |
| `OptimusDeveloper` | 开发者工具（加载阶段较早的辅助模块） |
| `RigVMDeveloper` | RigVM 编辑器支持（仅编辑器构建时链接） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-16 | `01d1b777` | 修复实例设置对象替换问题：使用唯一名称创建新对象，避免直接替换已加载的实例设置对象 |
| 2025-10-09 | `d3a9b03f` | 修复复制粘贴包含 matrix3x4 类型的资源节点时创建无 Pin 节点的问题 |
| 2025-10-03 | `490a9485` | 确保蒙皮权重配置文件更早请求，避免变形器激活或 LOD 切换时出现 T-Pose 帧 |

### 维护评价

- **状态**：✅ **活跃维护**
- 创建于 2020 年（>5 年历史），但持续有实质性更新
- 最近一次更新距今不到 6 个月（2025-10-16）
- 更新内容涵盖 bug 修复、功能改进和性能优化
- 从 Experimental 迁移到正式 Animation 分类，表明 Epic 将其视为生产级工具
- 名称从 Optimus 更名为 DeformerGraph，但所有类名保留 `Optimus` 前缀
- **推荐使用**：如果需要 GPU 网格变形功能，DeformerGraph 是 UE5 的官方推荐方案
- **注意**：`IsBetaVersion = true`，仍标记为 Beta 状态，API 可能在未来版本中变化

## 相关链接

- [DeformerGraph 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/DeformerGraph/)
- [Optimus 重定向壳](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/Animation/Optimus/Optimus.uplugin)
- [ComputeFramework 插件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/DeformerGraph/DeformerGraph.uplugin)（DeformerGraph 的底层依赖）
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Plugins/Animation/ControlRig)（集成使用的 Rig 单元来源）
