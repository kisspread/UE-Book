# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara Nanite 渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

Niagara Nanite 插件在 Niagara 粒子系统中添加了 **Nanite 渲染器**（`UNiagaraNaniteRendererProperties`），使粒子能够渲染 Nanite 几何体（即经过 Nanite 处理的静态网格体）。Nanite 是 UE5 的虚拟几何体系统，能高效渲染极高面数的模型，此插件将 Nanite 的优势引入粒子系统，实现大规模的精细静态网格体粒子效果（如碎片、建筑物、植被实例）。

该插件解决的核心问题：传统的 Niagara 粒子渲染器（如 Sprite、Mesh 渲染器）无法利用 Nanite 的 LOD 和剔除优势，当需要渲染大量高复杂度网格体时性能受限。Nanite 渲染器使用 Nanite 的实例化渲染管线，允许粒子直接引用 `UStaticMesh`（需启用 Nanite），并支持每粒子变换（位置、旋转、缩放），从而在极高的实例数量下仍保持性能。

## 使用场景

- **大规模建筑群粒子**：在 Niagara 中创建城市楼房倒塌、喷出大量砖块的效果，每个砖块使用 Nanite 网格体，渲染上万实例。
- **高密度植被粒子**：利用粒子系统模拟树叶飘落、花粉飞舞，每个粒子引用一个高精度 Nanite 叶片模型。
- **碎片效果**：爆炸产生的瓦砾、玻璃碎片，使用 Nanite 网格体获得丰富的几何细节，同时保持帧率。
- **机械部件喷出**：在过场动画或游戏中，大量机械零件飞出，使用 Nanite 渲染器保持每个零件的精度。

## 蓝图用法

Nanite 渲染器主要在 **Niagara 发射器编辑器** 中配置，而非通过蓝图节点直接控制。其属性通过 `UNiagaraNaniteRendererProperties` 暴露，可在渲染器堆栈中添加并设置。

### 核心可编辑属性（在编辑器细节面板中）

| 属性 | 说明 | 可访问性 |
|---|---|---|
| `Mesh` | 用于渲染的静态网格体（需启用 Nanite） | 蓝图（通过绑定） |
| `Scale` | 每个粒子的缩放因子（FVector3f） | 蓝图（通过绑定） |
| `Rotation` | 每个粒子的旋转（FRotator3f） | 蓝图（通过绑定） |
| `ExplicitMat` | 材质覆盖（如设置，则使用此材质） | 蓝图（通过绑定） |
| `UserParamBinding` | 允许通过用户变量动态指定材质 | 蓝图（通过绑定） |
| `MeshParameterBinding` | 允许通过粒子参数动态绑定网格体 | 蓝图（通过绑定） |

这些属性属于 `FNiagaraNaniteMeshRendererMeshProperties` 结构体，可在渲染器细节面板中为每个网格插槽（Slot）配置。虽然它们没有标记为 `BlueprintCallable`，但 **Niagara 参数绑定**（`FNiagaraParameterBinding`）允许通过蓝图变量（如用户参数）动态控制这些值，因此在实际使用中可以通过 `Set Niagara Variable` 节点间接修改。

### 使用提示

- 在 Niagara 系统编辑器中，添加“Nanite Renderer”渲染器到发射器。
- 在细节面板的“Mesh”类别下，设置要渲染的静态网格体。
- 若需要每粒子不同网格体，可勾选“Mesh Parameter Binding”并绑定一个用户变量（如 `MeshDynamic`），然后在蓝图中每帧更新该变量。
- 材质覆盖同样支持用户变量绑定，实现运行时换材质。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraNaniteRendererProperties.h"
#include "NiagaraStaticMeshComponent.h" // 如果需操作组件
```

### 基本用法：创建和配置Nanite渲染器

以下示例展示如何在C++创建Niagara系统时添加Nanite渲染器并设置参数（假设已有 `UNiagaraSystem*` 和发射器句柄）：

```cpp
// 从发射器属性列表创建Nanite渲染器
UNiagaraNaniteRendererProperties* NaniteRenderer = NewObject<UNiagaraNaniteRendererProperties>(Emitter);
if (NaniteRenderer)
{
    // 设置基本属性
    NaniteRenderer->MeshProperties.Add(FNiagaraNaniteMeshRendererMeshProperties());
    auto& MeshProp = NaniteRenderer->MeshProperties.Last();
    MeshProp.Mesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/MyNaniteMesh.MyNaniteMesh"));
    MeshProp.Scale = FVector3f(1.5f, 1.5f, 1.5f);
    MeshProp.Rotation = FRotator3f(0.0f, 45.0f, 0.0f);

    // 添加材质覆盖（可选）
    FNiagaraNaniteMaterialOverride MatOverride;
    MatOverride.ExplicitMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MyMaterial.MyMaterial"));
    NaniteRenderer->MaterialOverrides.Add(MatOverride);

    // 将渲染器添加到发射器
    // ... 实际需要根据Niagara API添加到渲染器列表
}
```

### 进阶用法：使用动态材质覆盖

通过用户变量绑定材质，允许在游戏运行时切换材质（来自 `FNiagaraNaniteMaterialOverride`）：

```cpp
// 假设已有 UNiagaraSystem* System 和 FNiagaraUserParameterBinding 绑定到某个材质变量
FNiagaraNaniteMaterialOverride DynMatOverride;
DynMatOverride.UserParamBinding.Parameter.SetName("DynamicMaterial");
NaniteRenderer->MaterialOverrides.Add(DynMatOverride);
```

### 内部组件： `UNiagaraStaticMeshComponent`

当渲染器激活时，会创建 `UNiagaraStaticMeshComponent` 实例（每个网格插槽一个），该组件负责管理 Nanite 实例数据。通过该组件可以手动更新实例变换（如果需要低层级控制）：

```cpp
// 在渲染器初始化后获取内部组件（通常不推荐直接使用）
UNiagaraStaticMeshComponent* MeshComp = /* 从渲染器内部获取 */;
if (MeshComp)
{
    int32 NumInstances = 1000;
    MeshComp->UpdateInstanceCPU(NumInstances, [](FInstanceSceneDataBuffers::FWriteView& View)
    {
        // 设置每个实例的位置、旋转、缩放
        // View.InstanceLocalTransform/View.InstanceLocalScale 等
    });
}
```

来源：`Engine/Plugins/FX/NiagaraNanite/Source/NiagaraNanite/Private/Renderer/NiagaraStaticMeshComponent.h`

## Demo 示例

以下是一个完整的可编译插件级示例，展示如何在 C++ 中创建一个 Niagara 系统发射器并附加 Nanite 渲染器。假设项目已启用 `NiagaraNanite` 插件。

### NaniteRendererDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraNaniteRendererProperties.h"
#include "NaniteRendererDemo.generated.h"

UCLASS()
class ANaniteRendererDemo : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Demo")
    UNiagaraSystem* SourceSystem;

    UPROPERTY(EditAnywhere, Category = "Demo")
    UStaticMesh* NaniteMesh;

    UPROPERTY(EditAnywhere, Category = "Demo")
    UMaterialInterface* MaterialOverride;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Demo")
    void CreateNaniteNiagaraSystem();

    virtual void BeginPlay() override;
};
```

### NaniteRendererDemo.cpp

```cpp
#include "NaniteRendererDemo.h"
#include "NiagaraEmitter.h"
#include "NiagaraRendererProperties.h"

void ANaniteRendererDemo::BeginPlay()
{
    Super::BeginPlay();
    // 在运行时自动创建（可选）
}

void ANaniteRendererDemo::CreateNaniteNiagaraSystem()
{
    if (!SourceSystem || !NaniteMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("Missing SourceSystem or NaniteMesh"));
        return;
    }

    // 复制系统以避免修改原始资产
    UNiagaraSystem* NewSystem = DuplicateObject(SourceSystem, this);
    if (!NewSystem) return;

    // 遍历发射器，为第一个发射器添加 Nanite 渲染器
    for (const FNiagaraEmitterHandle& Handle : NewSystem->GetEmitterHandles())
    {
        UNiagaraEmitter* Emitter = Handle.GetInstance();
        if (!Emitter) continue;

        // 创建 Nanite 渲染器
        UNiagaraNaniteRendererProperties* NaniteRenderer = NewObject<UNiagaraNaniteRendererProperties>(Emitter);
        if (!NaniteRenderer) continue;

        // 配置网格属性
        FNiagaraNaniteMeshRendererMeshProperties MeshProp;
        MeshProp.Mesh = NaniteMesh;
        MeshProp.Scale = FVector3f(1.0f, 1.0f, 1.0f);
        MeshProp.Rotation = FRotator3f::ZeroRotator;
        NaniteRenderer->MeshProperties.Add(MeshProp);

        // 材质覆盖（可选）
        if (MaterialOverride)
        {
            FNiagaraNaniteMaterialOverride MatOverride;
            MatOverride.ExplicitMat = MaterialOverride;
            NaniteRenderer->MaterialOverrides.Add(MatOverride);
        }

        // 将渲染器添加到发射器的 RendererProperties 列表
        TArray<UNiagaraRendererProperties*> Renderers = Emitter->GetRendererProperties();
        Renderers.Add(NaniteRenderer);
        Emitter->SetRendererProperties(Renderers);
        break; // 只为第一个发射器添加
    }

    // 在世界中生成粒子系统
    UNiagaraComponent* NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
        GetWorld(), NewSystem, GetActorLocation(), GetActorRotation());
    if (NiagaraComp)
    {
        NiagaraComp->Activate(true);
    }
}
```

### 使用说明

1. 在编辑器中创建蓝图继承自该 Actor。
2. 设置 `SourceSystem` 为一个已有的 Niagara 系统（至少包含一个粒子发射器）。
3. 设置 `NaniteMesh` 为一个启用了 Nanite 的静态网格体。
4. 可选 `MaterialOverride`。
5. 点击蓝图中的 `CreateNaniteNiagaraSystem` 函数（CallInEditor）即可测试。

## 模块依赖

使用 Niagara Nanite 插件的模块需要添加以下依赖（在 `Build.cs` 中）：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心 Niagara 框架，必须依赖 |
| `UnrealEd` | 编辑器功能（即使在 Runtime 运行时也依赖，用于某些组件创建） |

注意：`UnrealEd` 是一个编辑器模块，如果在纯运行时（无编辑器）打包，需要验证是否正常工作。当前 `NiagaraNanite` Runtime 模块的 `Build.cs` 中明确依赖了 `UnrealEd`，因此打包时需要确保包含编辑器依赖（通常通过 `Engine` 模块间接包含）。

其他模块 (`NiagaraNaniteEditor`, `NiagaraNaniteShader`) 自动包含，无需手动添加。

## 维护状态

### 近期更新

| 日期 | Hash | 内容 |
|---|---|---|
| 2025-10-15 | `2673f681` | 修复添加额外网格到 Nanite 渲染器时的崩溃 |
| 2025-08-25 | `a0f5c688` | 修复 Nanite Niagara 着色器可能覆盖 GPUScene 中实例数据的错误 |
| 2025-08-18 | `c1117853` | 修复 CPU 上前一帧变换不正确的问题 |
| 2025-08-13 | `c7595dab` | 修复材质覆盖结构体命名 |
| 2025-08-11 | `8c7d4887` | 修复 Niagara Nanite 渲染器缩略图崩溃 |

### 维护评价

该插件创建于 2025 年 8 月，属于 **非常新的实验性功能**。从 git 历史看，Epic 团队在持续进行修复和改进，更新频率高（每月至少 1-2 次），且修复内容涉及核心逻辑（崩溃、数据竞争、变换计算）。目前没有发现废弃或停止维护的迹象。

**评价**：开发活跃，适合用于前瞻性项目，但因其实验性，建议在未充分测试前不要用于生产环境。已知限制可能包括：仅支持 Nanite 网格体、编辑器依赖（Runtime 模块依赖 `UnrealEd`）、可能存在未发现的边缘情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/niagara-effects-for-unreal-engine/)（Niagara 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite/Tests)（如存在）