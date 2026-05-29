# Sample Mesh Reconstructor

> Sample of how to drive mesh reconstruction. Generates dummy geometry to demonstrate API usage.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟网格重建示例 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DummyMeshReconstructor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-05-28 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshReconstruction/DummyMeshReconstructor) | |

## 用途

本插件是 **MRMesh（Mixed Reality Mesh）** API 的一个最小化、可编译的 **示例实现**。它并非用于生产环境，而是为了演示如何通过继承 `UMeshReconstructorBase` 接口，来创建一个自定义的网格重建器。

其核心作用是：
1.  **教学与模板**：为开发者提供一个如何驱动 `MRMesh` 系统的清晰范例。
2.  **调试与验证**：当使用 `MRMesh` API 进行开发时，可以用此插件快速验证管线是否工作，因为它会生成已知的、简单的“虚拟”几何体，而不依赖于真实的传感器（如深度摄像头）。
3.  **理解流程**：展示了 `Start`、`Stop`、`Pause`、`Connect`、`Disconnect` 等生命周期和连接管理的标准流程。

## 使用场景

-   **你正在学习 UE5 的 MRMesh 或 AR 混合现实网格重建功能** → 用此插件作为代码模板。
-   **你开发了一个自定义的网格重建器（如用于特定的 AR 硬件或算法）** → 可以参考此插件的结构来组织你的代码。
-   **你需要一个不依赖真实硬件的网格重建器来测试 MRMeshComponent 的功能** → 启用此插件，它将为你提供虚拟网格数据。
-   **你正在为 Android 或 Win64 平台开发涉及实时网格生成的应用** → 此插件可作为 API 使用的起点。

## 蓝图用法

该插件主要提供了一个蓝图可用的类 `UDummyMeshReconstructor`，它继承自引擎提供的基类 `UMeshReconstructorBase`。你可以通过蓝图创建它的实例，并调用其继承的方法来控制网格重建过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Reconstruction` | 启动网格重建过程。对于 Dummy 实现，这将开始生成虚拟几何体。 | `UDummyMeshReconstructor` |
| `Stop Reconstruction` | 停止网格重建并清理已生成的数据。 | `UDummyMeshReconstructor` |
| `Pause Reconstruction` | 暂停网格重建。 | `UDummyMeshReconstructor` |
| `Connect MRMesh` | 将此重建器连接到一个 `MRMeshComponent`。重建器生成的网格将应用到该组件上。 | `UDummyMeshReconstructor` |
| `Disconnect MRMesh` | 断开与当前 `MRMeshComponent` 的连接。 | `UDummyMeshReconstructor` |
| `Is Reconstruction Started` | 查询重建是否已启动。 | `UDummyMeshReconstructor` |
| `Is Reconstruction Paused` | 查询重建是否处于暂停状态。 | `UDummyMeshReconstructor` |

### 使用示例（蓝图描述）

1.  在你的 Actor 蓝图中，添加一个 `MRMeshComponent`。
2.  在构造函数或事件图表中，使用 `Create Object from Class` 节点创建一个 `UDummyMeshReconstructor` 的实例。
3.  调用 `Connect MRMesh` 节点，将新创建的重建器实例连接到步骤1中的 `MRMeshComponent`。
4.  当你需要开始生成网格时（例如，按下某个键），调用 `Start Reconstruction` 节点。
5.  你将观察到 `MRMeshComponent` 开始显示由 Dummy 重建器生成的几何体。
6.  要停止时，调用 `Stop Reconstruction` 或 `Disconnect MRMesh`。

## C++ 用法

### 头文件引入

```cpp
#include "DummyMeshReconstructor.h"
#include "MRMeshComponent.h" // 用于连接 MRMesh
```

### 基本用法

该插件的核心是 `UDummyMeshReconstructor` 类。其主要用途是作为 **自定义重建器的参考实现**。

```cpp
// 假设你有一个 Actor，它拥有一个 MRMeshComponent
// 你需要动态创建或引用一个 UDummyMeshReconstructor
void AMyActor::SetupDummyReconstruction()
{
    // 1. 创建重建器实例
    UDummyMeshReconstructor* MyReconstructor = NewObject<UDummyMeshReconstructor>();
    
    // 2. 连接到你的 MRMeshComponent
    //    假设 MyMRMeshComponent 是你的 AMyActor 拥有的一个 MRMeshComponent 指针
    if (MyMRMeshComponent)
    {
        MyReconstructor->ConnectMRMesh(MyMRMeshComponent);
    }
    
    // 3. 启动重建（将开始向 MyMRMeshComponent 提交网格数据）
    MyReconstructor->StartReconstruction();
    
    // 保存指针以便后续控制
    ActiveReconstructor = MyReconstructor;
}
```

### 进阶用法

该插件的源码非常简单，没有复杂的进阶用法。其主要价值在于展示 `UMeshReconstructorBase` 接口的完整实现骨架。你可以通过查看 `DummyMeshReconstructor.cpp` 中的实现，来学习如何在自己的重建器中处理顶点缓冲区、三角形索引等数据的生成和提交流程。

## Demo 示例

以下是一个最小的、基于 `UDummyMeshReconstructor` 的自定义重建器示例，它简单地生成一个固定位置的三角形。

**MyCustomReconstructor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MeshReconstructorBase.h"
#include "MyCustomReconstructor.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyCustomReconstructor : public UMeshReconstructorBase
{
    GENERATED_BODY()

public:
    // 重写基类接口
    virtual void StartReconstruction() override;
    virtual void StopReconstruction() override;
    virtual void PauseReconstruction() override;
    virtual bool IsReconstructionStarted() const override;
    virtual bool IsReconstructionPaused() const override;
    virtual void ConnectMRMesh(UMRMeshComponent* Mesh) override;
    virtual void DisconnectMRMesh() override;

private:
    UPROPERTY()
    UMRMeshComponent* ConnectedMesh = nullptr;

    bool bIsRunning = false;
    bool bIsPaused = false;
    
    // 辅助函数：向连接的 MRMesh 提交一个简单的网格
    void SubmitDummyMesh();
};
```

**MyCustomReconstructor.cpp**
```cpp
#include "MyCustomReconstructor.h"
#include "MRMeshComponent.h"

void UMyCustomReconstructor::StartReconstruction()
{
    if (ConnectedMesh)
    {
        bIsRunning = true;
        bIsPaused = false;
        // 在实际应用中，这里可能会启动一个后台线程或定时器来持续更新网格
        // 为了示例，我们直接提交一次网格
        SubmitDummyMesh();
    }
}

void UMyCustomReconstructor::StopReconstruction()
{
    bIsRunning = false;
    bIsPaused = false;
    // 清理网格数据
    if (ConnectedMesh)
    {
        ConnectedMesh->ClearMesh();
    }
}

void UMyCustomReconstructor::PauseReconstruction()
{
    if (bIsRunning)
    {
        bIsPaused = true;
    }
}

bool UMyCustomReconstructor::IsReconstructionStarted() const
{
    return bIsRunning;
}

bool UMyCustomReconstructor::IsReconstructionPaused() const
{
    return bIsPaused;
}

void UMyCustomReconstructor::ConnectMRMesh(UMRMeshComponent* Mesh)
{
    if (ConnectedMesh)
    {
        DisconnectMRMesh();
    }
    ConnectedMesh = Mesh;
}

void UMyCustomReconstructor::DisconnectMRMesh()
{
    if (bIsRunning)
    {
        StopReconstruction();
    }
    ConnectedMesh = nullptr;
}

void UMyCustomReconstructor::SubmitDummyMesh()
{
    if (!ConnectedMesh || !bIsRunning || bIsPaused) return;
    
    // 定义顶点和三角形
    TArray<FVector> Vertices = { FVector(0, 0, 0), FVector(100, 0, 0), FVector(0, 100, 0) };
    TArray<MRMESH_INDEX_TYPE> Triangles = { 0, 1, 2 };
    TArray<FVector> Normals = { FVector::UpVector, FVector::UpVector, FVector::UpVector };
    
    // 将网格数据提交给 MRMeshComponent
    ConnectedMesh->SetMeshSections(MakeArrayView(&Vertices, 1), MakeArrayView(&Triangles, 1), MakeArrayView(&Normals, 1));
}
```

## 模块依赖

要使用此插件提供的类（如 `UDummyMeshReconstructor`），你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MRMesh` | 核心依赖，提供 `UMRMeshComponent` 和 `UMeshReconstructorBase` 基类。 |
| `MeshReconstruction` | 提供网格重建的基础设施和管理器。 |

你的项目 `.Build.cs` 文件应包含：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "MRMesh", "MeshReconstruction" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接以使用安全协议。 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 第三轮清理构建文件。 |
| 2022-01-12 | `a48a2f87` | PR #8711: Fix MRMesh vertices (Contributed by fieldsJacksonG) | 修复MRMesh顶点问题（由社区贡献）。 |
| 2021-10-13 | `a12d56ff` | Merge from Release-Engine-Staging @ 17791557 to Release-Engine-Test | 引擎版本合并。 |
| 2021-08-03 | `33008a18` | Fix for CIS error | 修复持续集成系统错误。 |

### 维护评价

-   **创建时间**：2017年，历史悠久。
-   **近期更新**：最近一次功能性更新（修复顶点）发生在2022年1月，之后的两次提交（2022年9月、10月）均为项目基础设施（链接、构建文件）的维护性清理，无新功能。
-   **活跃度**：作为 **示例/演示插件**，其核心功能早已完成，不需频繁更新。最近的维护集中在保持与当前引擎版本的兼容性（链接、构建）。
-   **已知限制**：明确标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它是一个实验性的示例，不应直接用于生产项目。
-   **推荐使用**：**推荐用于学习和参考**，特别是当你需要理解 MRMesh API 如何工作，或者作为开发自定义网格重建器的起点时。不建议在最终产品中直接使用它作为网格重建方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshReconstruction/DummyMeshReconstructor)
-   官方文档：无
-   测试用例：插件本身没有包含测试文件。引擎级别的 MRMesh 测试可能位于 `Engine/Tests` 目录下。