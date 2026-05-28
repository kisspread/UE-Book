# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraNaniteEditor` (Editor), `NiagaraNanite` (Runtime), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

此插件为 Niagara 粒子系统提供了一个新的 **Nanite 渲染器**，专门用于渲染 Nanite 网格体（Nanite Geometry）。传统 Niagara 网格渲染器使用实例化静态网格（Instanced Static Meshes, ISM）或层次化实例化静态网格（Hierarchical ISM, HISM），而此插件通过生成 Nanite 网格组件（`UNiagaraStaticMeshComponent`）和利用 Nanite 的实例化渲染管线，使 Niagara 能够以 Nanite 方式高效渲染海量高精度几何体。这解决了使用标准网格渲染器渲染大量复杂粒子（如碎石、植被碎片）时可能出现的性能瓶颈。

## 使用场景

-   你需要为 Niagara 粒子系统创建由数万甚至数十万个高多边形网格组成的特效（如大规模爆炸的碎屑、建筑坍塌的碎片）。
-   你希望利用 Nanite 的细节层次（LOD）和虚拟化几何体技术来自动优化粒子渲染的性能和内存占用，而无需手动管理 LOD。
-   你的项目已经广泛使用 Nanite 技术，希望粒子系统能无缝接入相同的渲染管线，保持渲染风格和质量的一致性。

## 蓝图用法

此插件的核心配置通过 Niagara 发射器编辑器面板中的 **“渲染器”** 部分完成，而非传统的蓝图节点调用。其核心类 `UNiagaraNaniteRendererProperties` 提供了大量可在编辑器中设置的属性。

### 核心属性（在 Niagara 发射器属性面板中配置）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Meshes` | 网格数组。定义粒子要渲染的 Nanite 静态网格及其基础变换（缩放、旋转）。支持通过参数绑定动态选择网格。 | `UNiagaraNaniteRendererProperties` |
| `SourceMode` | 源数据模式。选择渲染单个元素（`Emitter`）还是逐粒子实例化（`Particles`）。 | `UNiagaraNaniteRendererProperties` |
| `bOverrideMaterials` | 启用材质覆盖。勾选后可使用自定义的材质替换原始网格的材质。 | `UNiagaraNaniteRendererProperties` |
| `OverrideMaterials` | 覆盖材质数组。当 `bOverrideMaterials` 启用时生效，支持直接指定材质或绑定到用户参数。 | `UNiagaraNaniteRendererProperties` |
| `RendererVisibility` | 渲染器可见性标签。配合粒子属性 `RendererVisibilityTag`，实现选择性渲染。 | `UNiagaraNaniteRenderer属性` |
| `PositionBinding` | 位置绑定。指定用于确定实例位置的 Niagara 变量（通常为 `Particles.Position`）。 | `UNiagaraNaniteRendererProperties` |
| `RotationBinding` | 旋转绑定。指定用于确定实例旋转的 Niagara 变量。 | `UNiagaraNaniteRendererProperties` |
| `ScaleBinding` | 缩放绑定。指定用于确定实例缩放的 Niagara 变量。 | `UNiagaraNaniteRendererProperties` |
| `MeshIndexBinding` | 网格索引绑定。用于在 `Meshes` 数组中动态选择要渲染的网格。 | `UNiagaraNaniteRenderer属性` |
| `MaterialParameters` | 材质参数。用于将 Niagara 模拟数据动态传递给材质实例（MID）。 | `UNiagaraNaniteRenderer属性` |

### 使用示例（在 Niagara 编辑器中）

1.  创建或打开一个 Niagara 发射器。
2.  在发射器的 **“渲染器”** 部分，点击 **“+”** 添加一个新渲染器。
3.  在渲染器类型列表中，选择 **“Nanite Renderer”**。
4.  在右侧的细节面板中：
    -   在 `Meshes` 数组中添加一个条目，并为其指定一个支持 Nanite 的 `UStaticMesh` 资产。
    -   将 `SourceMode` 设置为 `Particles`。
    -   在 `Bindings` 分类下，确保 `PositionBinding` 绑定到了发射器中定义的位置变量（如 `Particles.Position`）。
    -   （可选）勾选 `bOverrideMaterials` 并指定覆盖材质，以自定义粒子的外观。
5.  编译并预览发射器。你将看到粒子以指定的 Nanite 网格进行渲染。

## C++ 用法

### 头文件引入

```cpp
#include “NiagaraNaniteRendererProperties.h”
// 通常不需要直接引入，因为你通过 Niagara 编辑器和已有的系统来使用它。
```

### 基本用法（获取渲染器信息）

虽然不常直接创建，但可以通过 Niagara 系统查询当前使用的渲染器信息。
（示例基于代码推断的典型用法）

```cpp
// 假设你有一个有效的 Niagara 系统实例
UNiagaraSystem* NiagaraSystem = ...;
UNiagaraEmitter* Emitter = NiagaraSystem->GetEmitter(0); // 获取第一个发射器

// 获取发射器的渲染器属性
TArray<UNiagaraRendererProperties*> RendererProperties = Emitter->GetRenderers();
for (UNiagaraRendererProperties* RendererProps : RendererProperties)
{
    if (UNiagaraNaniteRendererProperties* NaniteRendererProps = Cast<UNiagaraNaniteRendererProperties>(RendererProps))
    {
        // 成功获取到 Nanite 渲染器属性
        UE_LOG(LogTemp, Log, TEXT(“Found Nanite Renderer. Number of mesh slots: %d”), NaniteRendererProps->Meshes.Num());

        // 可以读取其绑定信息
        const FNiagaraVariableAttributeBinding& PosBinding = NaniteRendererProps->PositionBinding;
        UE_LOG(LogTemp, Log, TEXT(“Position bound to variable: %s”), *PosBinding.GetAttribute().GetName().ToString());
    }
}
```

### 进阶用法（通过用户参数控制材质）

此插件支持通过 `FNiagaraUserParameterBinding` 动态控制覆盖材质。在 C++ 端，你可以创建并传递一个材质接口指针。

```cpp
// 1. 定义一个用户参数（通常在蓝图或代码中完成）
// 假设在你的 Niagara 系统中定义了一个名为 “ParticleMaterial” 的用户参数

// 2. 在游戏代码中设置这个参数
UNiagaraComponent* NiagaraComp = ...; // 获取你的 Niagara 组件
UMaterialInterface* DynamicMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT(“/Game/Effects/M_MyParticleMaterial”));
if (DynamicMaterial && NiagaraComp)
{
    NiagaraComp->SetVariableObject(FName(TEXT(“ParticleMaterial”)), DynamicMaterial);
}

// 3. 在 Niagara 编辑器的 Nanite 渲染器属性中，将 `OverrideMaterials` 的某个条目的 `UserParamBinding` 绑定到 “ParticleMaterial” 变量。
//    运行时，渲染器将使用你通过 C++ 代码设置的材质。
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在运行时通过代码修改 Nanite 渲染器所使用的网格数据（通常用于调试或动态生成）。

```cpp
// NiagaraNaniteDemoActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “NiagaraComponent.h”
#include “NiagaraNaniteDemoActor.generated.h”

UCLASS()
class ANiagaraNaniteDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ANiagaraNaniteDemoActor();

protected:
    virtual void BeginPlay() override;

    void ChangeMesh();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UNiagaraComponent> NiagaraComp;

    UPROPERTY(EditAnywhere)
    TObjectPtr<UStaticMesh> AlternateMesh;
};
```

```cpp
// NiagaraNaniteDemoActor.cpp
#include “NiagaraNaniteDemoActor.h”
#include “NiagaraSystem.h”
#include “NiagaraEmitter.h”
#include “NiagaraNaniteRendererProperties.h”

ANiagaraNaniteDemoActor::ANiagaraNaniteDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    NiagaraComp = CreateDefaultSubobject<UNiagaraComponent>(TEXT(“NiagaraComp”));
    RootComponent = NiagaraComp;
}

void ANiagaraNaniteDemoActor::BeginPlay()
{
    Super::BeginPlay();
    // 延迟一小会再更改，确保系统已初始化
    FTimerHandle TimerHandle;
    GetWorldTimerManager().SetTimer(TimerHandle, this, &ANiagaraNaniteDemoActor::ChangeMesh, 2.0f, false);
}

void ANiagaraNaniteDemoActor::ChangeMesh()
{
    UNiagaraSystem* System = NiagaraComp->GetAsset();
    if (!System) return;

    // 获取第一个发射器的第一个渲染器
    UNiagaraEmitter* Emitter = System->GetEmitter(0);
    if (!Emitter) return;

    const TArray<UNiagaraRendererProperties*>& Renderers = Emitter->GetRenderers();
    if (Renderers.Num() == 0) return;

    UNiagaraNaniteRendererProperties* NaniteRenderer = Cast<UNiagaraNaniteRendererProperties>(Renderers[0]);
    if (!NaniteRenderer) return;

    // 修改第一个网格槽位的网格
    if (NaniteRenderer->Meshes.Num() > 0 && AlternateMesh)
    {
        NaniteRenderer->Meshes[0].Mesh = AlternateMesh;
        UE_LOG(LogTemp, Warning, TEXT(“Changed Nanite renderer mesh slot 0 to: %s”), *AlternateMesh->GetName());

        // 注意：直接修改资产上的属性在运行时可能不被立即应用。
        // 通常，最佳实践是通过 Niagara 参数或重新初始化组件来触发动态更改。
        // 此示例主要用于说明如何访问和修改渲染器属性。
        NiagaraComp->ReinitializeSystem();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，提供 Niagara 粒子系统框架和渲染器基类。 |
| `Engine` | 用于 `UStaticMeshComponent`、`UStaticMesh` 等核心引擎类。 |

**注意**：`NiagaraNanite` (Runtime) 模块在其 Build.cs 中依赖 `UnrealEd`，这通常意味着该模块包含一些仅在编辑器下可用的功能或需要编辑器模块的某些实现。在纯运行时（打包后）环境中，这可能导致编译问题，表明该插件目前主要服务于编辑器环境或开发调试阶段，符合其“实验性”状态。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-03 | `a811ae50` | Refactor UseGPUScene to only require EShaderPlatform argument, remove the FeatureLevel argument | 重构 GPU 场景使用函数，简化接口参数 |
| 2026-02-02 | `eaa0098d` | Include all bound variables in parameter view model RW counts | 修复参数视图中读写计数不包含所有绑定变量的问题 |
| 2026-01-08 | `6297259f` | Fix shutdown crash. The UObject destruction order is not deterministic on shutdown. | 修复因 UObject 销毁顺序不确定导致的关闭崩溃 |
| 2025-10-22 | `297b8f95` | Added renderer mesh info to niagara BP function library | 向 Niagara 蓝图函数库添加渲染器网格信息 |
| 2025-10-15 | `d7179c85` | Fix crash when adding additional meshes to Nanite renderer | 修复向 Nanite 渲染器添加额外网格时发生的崩溃 |

### 维护评价

该插件创建于 2025 年 6 月，是一个相对较新的功能。从提交历史看，维护**活跃**，最近一次更新在 2026 年 3 月，且近一年的更新集中于功能增强（如添加蓝图接口）、性能优化（GPU场景重构）和稳定性修复（解决多个崩溃）。由于其标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，它仍处于实验阶段，API 和行为未来可能会有变化，且默认未开启，使用者需自行评估风险。目前推荐在需要利用 Nanite 渲染大规模粒子的实验性或开发项目中试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite)
- [官方文档]() (无)
- [测试用例]() (暂未提供)