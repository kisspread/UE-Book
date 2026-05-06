# Skeletal Mesh Simplifier (Early Access)

> A plugin to generate LOD for deforming meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼网格简化器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SkeletalMeshReduction` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-09-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SkeletalReduction) | |

## 用途

该插件为**变形网格**（如骨骼网格体动画）提供自动生成 LOD（细节层次）的功能。它基于四边误差度量（Quadric Error Metric, QEM）的边折叠算法，在保持网格外形和重要属性（法线、切线、UV、顶点颜色、蒙皮权重等）的前提下，减少三角形数量。

核心特性：
- 支持蒙皮骨骼网格体的简化，保留变形后的形状。
- 可控制生成 LOD 面数/顶点数，以及最大误差。
- 内部使用稀疏属性优化，高效处理关键属性。
- 作为引擎默认的骨骼网格简化工具（`IMeshReduction` 接口实现）。

## 使用场景

- **游戏 LOD 创建**：为高精度角色模型自动生成低面版本，提高渲染性能。
- **运行时简化**：可根据剧情或性能需求动态生成低模（需额外封装）。
- **资产清理**：对导入的多边形数过多的骨骼网格快速生成低面替代品。

## 蓝图用法

该插件为编辑器模块，提供后端简化算法，**不暴露蓝图可调用节点**。其功能通过引擎内置的网格简化流程触发（如右键资产 → 创建 LOD → 使用此简化器）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无公开蓝图节点 | — | — |

## C++ 用法

### 头文件引入

```cpp
#include "ISkeletalMeshReduction.h"
```

### 基本用法

1. **获取简化模块**  
   通过 `ISkeletalMeshReduction::Get()` 获得模块实例（`IMeshReductionModule` 接口）。

2. **触发简化**  
   使用 `IMeshReduction` 接口（从模块中获取）对 `FMeshDescription` 进行简化。

```cpp
// 来源：Engine/Plugins/Experimental/SkeletalReduction/Source/Private/...（示例推断）
#include "IMeshReductionInterfaces.h"
#include "ISkeletalMeshReduction.h"

void SimplifySkeletalMesh(USkeletalMesh* SkeletalMesh, int32 TargetTriCount)
{
    // 1. 获取网格简化模块
    ISkeletalMeshReduction& ReductionModule = ISkeletalMeshReduction::Get();
    IMeshReduction* MeshReducer = ReductionModule.GetMeshReduction();
    check(MeshReducer);

    // 2. 准备 MeshDescription（需从 SkeletalMesh 提取，略）
    FMeshDescription SourceMesh;
    // ... 填充 SourceMesh ...

    // 3. 设置简化参数
    FMeshReductionSettings Settings;
    Settings.bSimplify = true;
    Settings.TriangleCount = TargetTriCount;
    Settings.Metric = EMeshSimplifyMetrics::QEM;
    // ... 其他设置 ...

    // 4. 执行简化
    FMeshDescription ReducedMesh;
    MeshReducer->Reduce(ReducedMesh, SourceMesh, Settings);
}
```

### 进阶用法

使用 `SkeletalSimplifier` 命名空间中的底层工具进行自定义简化（通常不需要直接使用）：

```cpp
// 来源：SkeletalSimplifierMeshManager.h, SkeletalSimplifier.h
using namespace SkeletalSimplifier;

// 创建网格管理器
TArray<MeshVertType> Verts;
TArray<uint32> Indices;
// ... 填充顶点/索引 ...

FSimplifierMeshManager MeshManager(Verts.GetData(), Verts.Num(), Indices.GetData(), Indices.Num(), true);

// 配置终止条件（保留至少 100 个三角形，最大误差 0.01）
FSimplifierTerminator Terminator(100, 0, 0, 0, 0.01f, FLT_MAX);

// 运行简化（需配合 Quadric 缓存和优化器，此处简化）
TQuadricCache<WedgeQuadricType> Cache;
Cache.RegisterMesh(MeshManager);
// ... 初始化优化器并迭代边折叠 ...
```

**注意**：直接使用底层类如 `FSimplifierMeshManager` 需要谨慎处理顶点属性和边界情况，建议通过 `IMeshReduction` 接口进行简化。

## Demo 示例

以下是一个在编辑器模块中注册的控制台命令，用于简化当前选中的骨骼网格。

**头文件** `MyReductionDemo.h`

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyReductionDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**实现文件** `MyReductionDemo.cpp`

```cpp
#include "MyReductionDemo.h"
#include "IMeshReductionInterfaces.h"
#include "ISkeletalMeshReduction.h"
#include "Engine/SkeletalMesh.h"
#include "Misc/OutputDevice.h"

static TAutoConsoleVariable<int32> CVarDemoSimplify(
    TEXT("Demo.SimplifySkeletalMesh"),
    0,
    TEXT("Simplify the currently selected skeletal mesh to 500 triangles.\n")
    TEXT("0: off, 1: run once"),
    ECVF_Cheat);

void FMyReductionDemoModule::StartupModule()
{
    // 监听控制台变量变化
    CVarDemoSimplify.AsVariable()->SetOnChangedCallback(FConsoleVariableDelegate::CreateLambda([](IConsoleVariable* Var)
    {
        if (Var->GetInt() != 0)
        {
            // 获取当前选中的骨骼网格（编辑器场景）
            // 这里简化演示，直接获取第一个骨骼网格
            USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Characters/MyCharacter.MyCharacter"));
            if (!Mesh)
            {
                UE_LOG(LogTemp, Warning, TEXT("DemoSimplify: Mesh not found"));
                return;
            }

            // 获取简化模块
            ISkeletalMeshReduction& ReductionMod = ISkeletalMeshReduction::Get();
            IMeshReduction* Reducer = ReductionMod.GetMeshReduction();
            if (!Reducer)
            {
                UE_LOG(LogTemp, Error, TEXT("DemoSimplify: No mesh reduction available"));
                return;
            }

            // 准备 MeshDescription（实际需要从 SkeletalMesh 构建）
            FMeshDescription SourceDesc;
            Mesh->GetMeshDescription(SourceDesc);

            // 设置简化参数
            FMeshReductionSettings Settings;
            Settings.bSimplify = true;
            Settings.TriangleCount = 500;
            Settings.bKeepMesh = false;
            Settings.bDiscardAttributes = false;  // 保留属性

            FMeshDescription ReducedDesc;
            Reducer->Reduce(ReducedDesc, SourceDesc, Settings);

            // 将简化结果写回（简化后还需更新渲染数据，此处省略）
            // Mesh->SetMeshDescription(ReducedDesc);
            // Mesh->PostEditChange();

            UE_LOG(LogTemp, Log, TEXT("DemoSimplify: Reduced from %d to %d tris"), 
                   SourceDesc.Triangles().Num(), ReducedDesc.Triangles().Num());

            // 重置变量
            Var->Set(0, EConsoleVariableFlags::ECVF_SetByConsole);
        }
    }));
}

void FMyReductionDemoModule::ShutdownModule() {}
```

**模块注册（.Build.cs 中）**  
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "SkeletalMeshReduction", "MeshDescription" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshReductionInterface` | 提供 `IMeshReduction` 接口，简化器作为其实现 |
| `SkeletalMeshDescription` | 骨骼网格体描述（实际依赖，但插件内部不直接暴露） |
| `MeshBuild` | 公用网格构建工具，用于属性比较 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, Projects, DeveloperSettings。

## 维护状态

### 近期更新

- 2025-03-13 `b059f7b4` 修复不可达代码警告
- 2024-12-06 `91fff71f` 修复备选蒙皮权重配置文件生成渲染网格时的多个问题
- 2024-11-10 `66e9bb39` 移除所有 `UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域
- 2024-11-06 `bc63a88d` 重定向旧的 cppcompilewarning 属性到新的 `*.CppCompileWarningSettings`
- 2024-09-26 `f00385dd` 禁用 clang 检查器 `core.uninitialized.ArraySubscript`

### 维护评价

该插件于 2024 年 9 月首次引入，作为骨骼网格简化器的早期访问版。最近的提交（2025 年 3 月）表明项目仍处于活跃修复和维护中，但主要是针对编译警告和兼容性，而非功能增强。整体稳定可靠，推荐用于 UE5.5+ 项目。未来可能随引擎更新合并到主要模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SkeletalReduction)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/skeletal-mesh-lod-in-unreal-engine/)（通用 LOD 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SkeletalReduction/Tests)（如存在）