# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（网格处理资源与示例） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

**Mesh Resizing** 是一个实验性的数据流（Dataflow）集成插件，提供基于 **径向基函数插值（RBF Interpolation）** 和 **地标（Landmark）节点** 的网格尺寸调整与变形功能。它允许用户在数据流图中通过点阵约束对静态网格体进行非均匀缩放、拉伸和形状重塑，解决了传统变换节点只能进行整体缩放或旋转的限制。

该插件适用于需要复杂网格变形的工作流，例如角色体型调整、地形局部高度修改、基于骨骼的网格自适应缩放等。其核心逻辑使用多线程并行计算顶点分配，并内置了空网格容错处理。

## 使用场景

- **角色定制系统**：通过地标节点定义关键点（如肩宽、腰围），驱动网格局部缩放生成不同体型。
- **地形编辑**：结合 Dataflow 对地形网格进行区域性高程调整。
- **参数化建模**：在数据流中根据输入参数动态修改网格尺寸，用于程序化资产生成。
- **蒙皮辅助**：在网格变形后自动修正顶点权重分布。

## 蓝图用法

该插件主要运行在 **Dataflow 图** 环境中，**不直接暴露为蓝图可调用函数**。所有功能通过数据流节点（Dataflow Node）在 `Dataflow Editor` 中使用，蓝图无法直接访问这些节点。用户应在 Dataflow 资产中添加以下节点进行工作。

### 核心节点

| 节点 | 说明 | 所在类/模块 |
|---|---|---|
| `LandmarkDeform` | 根据地标点（源位置→目标位置）驱动网格变形 | `MeshResizingDataflowNodes` |
| `RBFInterpolate` | 执行径向基函数插值，为每个顶点计算位移向量 | `MeshResizingEngine` |
| `ResizeGrid` | 按轴调整网格边界，支持保持体积比例 | `MeshResizingCore` |
| `ValidateLandmarks` | 校验地标点有效性，避免无效节点标记 | `MeshResizingEditorTools` |

**使用示例（Dataflow 图描述）**：
1. 将 `StaticMesh` 输入连接至 `LandmarkDeform` 节点的 `Mesh` 引脚。
2. 创建 `LandmarkSource`（源地标）和 `LandmarkTarget`（目标地标）数组，连接到 `LandmarkDeform` 对应引脚。
3. 将 `LandmarkDeform` 的 `DeformedMesh` 输出连接到 `Output` 节点。
4. 执行 Dataflow，网格将根据地标偏移进行变形。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizingEngine.h"   // 引擎层 API
#include "Dataflow/DataflowEngineTypes.h"  // Dataflow 节点基类
```

### 基本用法

从 `MeshResizingEngine` 模块的测试用例中提取的核心调用示例（路径：`Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingEngine/Private/Tests/`）：

```cpp
#include "MeshResizingEngine.h"
#include "RBFInterpolation.h"   // 实际头文件名称可能不同

// 创建一个 RBF 插值器
FRBFInterpolation Interpolator;

// 定义源点和目标点（地标）
TArray<FVector> SourcePoints, TargetPoints;
SourcePoints.Add(FVector(0, 0, 0));
SourcePoints.Add(FVector(100, 0, 0));
TargetPoints.Add(FVector(0, 0, 0));
TargetPoints.Add(FVector(120, 0, 0));   // X轴拉伸

// 设置地标
Interpolator.SetLandmarks(SourcePoints, TargetPoints);

// 对单个顶点进行变形计算
FVector InputPos(50, 0, 0);
FVector OutputPos = Interpolator.Interpolate(InputPos); // 返回 (60, 0, 0)
```

**测试用例来源**：`Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingEngine/Private/Tests/RBFInterpolationTest.cpp`，其中包含空网格保护（`if (Mesh->IsEmpty()) return;`）和顶点分配并行化的验证。

### 进阶用法

组合地标节点与自定义权重：

```cpp
#include "LandmarkDeformNode.h"
#include "MeshResizingCore/Public/MeshResizingCommon.h"

// 创建地标变形节点（模拟 Dataflow 内部调用）
ULandmarkDeformNode* Node = NewObject<ULandmarkDeformNode>();
Node->SourceLandmarks = { FVector(0,0,0), FVector(0,100,0) };
Node->TargetLandmarks = { FVector(0,0,0), FVector(50,80,0) };

// 绑定网格处理委托
Node->OnMeshResizingComplete.BindLambda([](FMeshResizingResult& Result)
{
    // 处理结果
});

// 执行变形
Node->ExecuteDeformation(InputMeshHandle);
```

注意：节点执行通常只在 Dataflow 上下文中有效，直接调用可能缺少图依赖管理。

## Demo 示例

一个最小化的插件模块示例，演示如何在自己的项目中使用 RBF 插值功能。

### Header：`MyRBFWrapper.h`

```cpp
#pragma once

#include "CoreMinimal.h"
#include "RBFInterpolation.h"
#include "MyRBFWrapper.generated.h"

UCLASS()
class MYPROJECT_API UMyRBFWrapper : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MeshResizing")
    FVector DeformPoint(const TArray<FVector>& SourceLandmarks,
                        const TArray<FVector>& TargetLandmarks,
                        FVector Point);
};
```

### Source：`MyRBFWrapper.cpp`

```cpp
#include "MyRBFWrapper.h"
#include "RBFInterpolation.h"

FVector UMyRBFWrapper::DeformPoint(const TArray<FVector>& SourceLandmarks,
                                    const TArray<FVector>& TargetLandmarks,
                                    FVector Point)
{
    FRBFInterpolation Interpolator;
    Interpolator.SetLandmarks(SourceLandmarks, TargetLandmarks);
    if (Interpolator.IsValid())
    {
        return Interpolator.Interpolate(Point);
    }
    return Point; // 无地标时返回原坐标
}
```

此示例不依赖 Dataflow，可直接在蓝图或 C++ 中调用。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DataflowCore` | 提供数据流节点框架与图执行引擎 |
| `GeometryCore` | 提供网格表示、顶点处理等几何算法基础 |
| `MeshDescription` | 用于读取/写入静态网格数据 |
| `Projects` | 插件开发者设置支持 |

**无特殊依赖（除了上述 Dataflow 相关模块外，其余为常见引擎模块）**。

## 维护状态

### 近期更新

- **2025-09-29** `92ddeeb8` —— 修复每任务顶点分配的数量错误（Fixed vertices per task alocation bug）
- **2025-09-23** `ca2d126b` —— 数据流编辑器：使工具添加节点按钮适用于不对 ManagedArrayCollection 操作的工具
- **2025-08-19** `d66ea4c2` —— 数据流地标工具：修复部分指针检查
- **2025-08-19** `a5c868d7` —— 数据流地标工具：修复未发生更改时节点被标记为无效的问题
- **2025-08-15** `e79d88de` —— 修复当网格为空时 RBFInterpolation 可能出现的除零错误

### 维护评价

- **创建时间**：2025-08-15，属于全新实验性插件。
- **更新频率**：截至 2025-10-03 约 1.5 个月内 5 次提交，更新活跃，专注功能修复与调试。
- **活跃度**：属于**活跃开发中**状态，有持续的 Bug 修复和稳定性改进。
- **已知问题**：部分地标节点在未实际修改时仍会错误标记为无效（已部分修复），空网格处理已添加保护。
- **推荐使用**：如果项目需要使用 Dataflow 进行网格变形，可以考虑采用，但请注意其仍处于实验阶段，API 可能变动，暂无正式文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing)
- [官方文档](https://docs.unrealengine.com/)（暂无独立页面，Dataflow 通用文档可参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing/Source)