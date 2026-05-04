# Custom Mesh Component

> A new renderable Component class that allows you to specify custom geometry via C++ or Blueprint.

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | CustomMeshComponent (Runtime, PreDefault) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CustomMeshComponent) | |

## 用途

CustomMeshComponent 提供了一个可以在运行时通过代码或蓝图动态生成三角形网格的组件。与 StaticMesh 需要预烘焙资产不同，这个组件允许你在运行时用纯顶点数据（三角形列表）构建可见几何体。

它是 `UMeshComponent` 的子类，内部使用 `FDynamicMeshVertex` + `FLocalVertexFactory` 构建渲染代理（SceneProxy），支持材质、法线自动计算、线框调试模式等标准渲染特性。

**典型用途**：快速原型验证、程序化几何体、调试可视化形状。注意这个组件非常简单——没有 UV 坐标支持（顶点色固定为白色）、没有 LOD、没有碰撞生成，**不适合用于正式游戏项目的生产级几何体渲染**。

## 使用场景

- 你需要在蓝图中快速画几个三角形做调试可视化 → 用 CustomMeshComponent
- 你需要在运行时根据算法动态生成简单的几何形状（如平面、箭头、简单地形） → 用 CustomMeshComponent
- 你需要生产级的程序化网格（带 UV、法线贴图、碰撞等） → 考虑 `ProceduralMeshComponent` 或 `GeometryScript`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Custom Mesh Triangles` | 替换整个网格的三角形数据（推荐，减少内存分配） | `UCustomMeshComponent` |
| `Add Custom Mesh Triangles` | 追加三角形数据到现有网格（可能触发额外分配） | `UCustomMeshComponent` |
| `Clear Custom Mesh Triangles` | 清除所有三角形数据（不释放内存，便于复用） | `UCustomMeshComponent` |

### 数据结构

`FCustomMeshTriangle` 是一个蓝图可用的结构体（`BlueprintType`），包含三个顶点：

| 属性 | 类型 | 说明 |
|---|---|---|
| `Vertex0` | `FVector` | 第一个顶点（局部坐标） |
| `Vertex1` | `FVector` | 第二个顶点（局部坐标） |
| `Vertex2` | `FVector` | 第三个顶点（局部坐标） |

三个顶点按逆时针方向排列时为正面（法线自动从边向量叉积计算）。

### 使用示例（蓝图描述）

1. 在 Actor 上添加 `CustomMeshComponent`（在组件列表中搜索 "Custom Mesh"）
2. 创建一个 `FCustomMeshTriangle` 数组，例如构造一个简单的三角形：
   - Vertex0 = (0, 0, 0)
   - Vertex1 = (100, 0, 0)
   - Vertex2 = (50, 100, 0)
3. 调用 `Set Custom Mesh Triangles`，传入该数组
4. 可选：在组件的 Material 属性上指定材质，否则使用默认材质

## C++ 用法

### 头文件引入

```cpp
#include "CustomMeshComponent.h"  // FCustomMeshTriangle + UCustomMeshComponent
```

### 基本用法

在 Actor 中创建组件并设置三角形网格：

```cpp
// MyActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
public:
    AMyActor();

    UPROPERTY(VisibleAnywhere)
    UCustomMeshComponent* MeshComp;
};

// MyActor.cpp
#include "MyActor.h"
#include "CustomMeshComponent.h"

AMyActor::AMyActor()
{
    MeshComp = CreateDefaultSubobject<UCustomMeshComponent>(TEXT("CustomMesh"));
    RootComponent = MeshComp;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 构建两个三角形（一个四边形）
    TArray<FCustomMeshTriangle> Triangles;

    FCustomMeshTriangle Tri1;
    Tri1.Vertex0 = FVector(0, 0, 0);
    Tri1.Vertex1 = FVector(100, 0, 0);
    Tri1.Vertex2 = FVector(100, 100, 0);
    Triangles.Add(Tri1);

    FCustomMeshTriangle Tri2;
    Tri2.Vertex0 = FVector(0, 0, 0);
    Tri2.Vertex1 = FVector(100, 100, 0);
    Tri2.Vertex2 = FVector(0, 100, 0);
    Triangles.Add(Tri2);

    MeshComp->SetCustomMeshTriangles(Triangles);
}
```

> 来源：`Engine/Plugins/Runtime/CustomMeshComponent/Source/CustomMeshComponent/Classes/CustomMeshComponent.h`

### 进阶用法

运行时动态追加和清除几何体：

```cpp
// 追加更多三角形（不替换已有数据）
TArray<FCustomMeshTriangle> MoreTriangles;
// ... 填充数据 ...
MeshComp->AddCustomMeshTriangles(MoreTriangles);

// 清除所有三角形（保留内存分配）
MeshComp->ClearCustomMeshTriangles();

// 设置材质
MeshComp->SetMaterial(0, MyMaterial);
```

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "CustomMeshComponent"  // 插件模块名
});
```

在 `.uproject` 中确保插件已启用（默认已启用）：

```json
{
    "Plugins": [
        {
            "Name": "CustomMeshComponent",
            "Enabled": true
        }
    ]
}
```

## 模块依赖

插件自身的 `Build.cs` 声明的依赖（使用者无需额外添加这些）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 组件和场景系统 |
| `RenderCore` | 渲染资源管理（VertexBuffer, VertexFactory） |
| `RHI` | 渲染硬件接口 |

使用者只需要依赖 `CustomMeshComponent` 模块即可。

## 技术细节

- **渲染方式**：动态创建 `FCustomMeshSceneProxy`，使用 `FStaticMeshVertexBuffers` + `FLocalVertexFactory`，走 `GetDynamicMeshElements` 路径
- **法线计算**：自动从三角形边向量叉积计算 TangentX/TangentY/TangentZ，无需手动提供
- **顶点色**：固定白色 `(255, 255, 255)`，无法自定义
- **UV**：不支持，`FDynamicMeshVertex` 使用默认 UV（全零）
- **材质**：单材质插槽，未设置时回退到 `MD_Surface` 默认材质
- **碰撞**：不生成碰撞几何体，仅设置默认碰撞配置文件（`BlockAllDynamic`）
- **Tick**：禁用（`PrimaryComponentTick.bCanEverTick = false`）
- **包围盒**：从所有三角形顶点实时计算 AABB

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e7518` | 添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏 | 全引擎范围的代码现代化，非针对性功能更新 |
| 2025-06-18 | `08316db` | ShaderPlatform 缓存重构 | 渲染管线内部重构，影响所有渲染组件 |
| 2025-04-23 | `6ae5733` | DLL 导出标记批量转换 | 构建系统适配，无功能变化 |

### 维护评价

**维护状态：稳定但停滞**

- 创建于 2014 年（UE4 早期），已超过 11 年
- 最近 3 次提交全部是引擎级别的批量重构/代码现代化，**没有任何针对 CustomMeshComponent 本身的功能更新**
- 组件功能自创建以来几乎未变（仅 3 个公开函数、1 个结构体）
- 没有 UV 支持、没有顶点色自定义、没有碰撞生成——功能非常有限
- Epic 自身似乎将其视为演示/示例性质的组件，从未投入精力扩展
- **如果需要更强的程序化网格能力，建议使用 `ProceduralMeshComponent` 插件或 UE5 的 `GeometryScript` 框架**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/CustomMeshComponent)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未找到针对此插件的自动化测试
