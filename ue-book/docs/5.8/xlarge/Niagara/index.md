# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例特效） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 UE 的下一代粒子特效系统，旨在取代旧的 Cascade 系统。它提供了一个基于节点和模块化设计的完整框架，用于创建高度可定制、数据驱动且性能优异的视觉特效。Niagara 的核心优势在于其 **GPU 加速能力**、与蓝图/C++的**深度集成**以及**灵活的编辑工作流**，允许开发者和技术美术人员通过图形化界面组合模块来构建复杂的特效逻辑，而无需编写大量代码。

## 使用场景

- 你需要创建复杂的、与游戏逻辑交互的交互式特效（如根据角色状态改变行为的粒子）。
- 你需要渲染数十万甚至上百万粒子的大规模环境效果（如雪、雨、星群），并追求高性能。
- 你需要特效能够访问引擎中的动态数据（如骨骼位置、网格顶点、物理表面信息）。
- 你需要一个统一的系统来管理模拟、渲染和数据接口，而不是在多个独立的、功能单一的系统间切换。

## 蓝图用法

Niagara 的蓝图 API 主要围绕 `UNiagaraComponent` 和各种数据接口（Data Interface）展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn System At Location` | 在指定世界位置生成并播放一个 Niagara 特效系统实例。 | `UNiagaraFunctionLibrary` |
| `Spawn System Attached` | 将 Niagara 特效系统附加到另一个组件上，并生成播放。 | `UNiagaraFunctionLibrary` |
| `Set Niagara Variable (Bool/Float/Vector...)` | 在运行时设置 Niagara 系统实例中的一个参数（变量）值。 | `UNiagaraComponent` |
| `Activate System` / `Deactivate System` | 激活或停止一个已有的 Niagara 组件。 | `UNiagaraComponent` |
| `Set Niagara Static Mesh` | 为使用 Static Mesh 数据接口的发射器指定网格体资产。 | `UNiagaraDataInterfaceStaticMesh` |

### 使用示例（蓝图描述）

1.  **创建简单特效**：在蓝图中，从 `NiagaraComponent` 创建一个新组件，并将其 `Asset` 属性设置为你的 Niagara 系统资产。然后连接一个 `Event`（如 `BeginPlay`）到 `Activate System` 节点。
2.  **动态控制参数**：使用 `Set Niagara Variable (Float)` 节点。将你的 `NiagaraComponent` 引用连接到目标，设置变量名为你在 Niagara 编辑器中定义的暴露参数（如 `User.Density`），然后设置一个浮点值。这可以实现根据游戏状态（如玩家距离）动态调整特效。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
```

### 基本用法

从测试用例中提取的典型用法，用于动态生成和控制 Niagara 特效。

```cpp
// 来自 Engine/Plugins/FX/Niagara/Tests/Private/NiagaraComponentTests.cpp
// 在 Actor 的 BeginPlay 中生成一个 Niagara 特效
UNiagaraSystem* NiagaraSystem = LoadObject<UNiagaraSystem>(nullptr, TEXT("/Game/Path/To/YourNiagaraSystem"));
if (NiagaraSystem)
{
    UNiagaraComponent* NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
        GetWorld(), 
        NiagaraSystem, 
        GetActorLocation(), 
        FRotator::ZeroRotator, 
        FVector(1.f), 
        true, // bAutoDestroy
        true, // bAutoActivate
        ENCPoolMethod::None, 
        true  // bPreCullCheck
    );

    if (NiagaraComp)
    {
        // 在运行时修改系统参数
        NiagaraComp->SetNiagaraVariableFloat(FString("User.DynamicSpeed"), 100.0f);
    }
}
```

### 进阶用法

结合 C++ 和数据接口，实现更复杂的交互。

```cpp
// 在 C++ 中为 Niagara 组件设置自定义数据接口
UNiagaraComponent* MyNiagaraComp = ...; // 获取或创建组件

// 假设有一个自定义的数据接口类 UMyCustomDataInterface
UMyCustomDataInterface* CustomDI = NewObject<UMyCustomDataInterface>();
CustomDI->Initialize(/* 参数 */);

// 将数据接口实例绑定到 Niagara 系统中的特定数据接口参数
// 参数名（如 “MyDI”）需与 Niagara 编辑器中发射器模块的参数名一致
MyNiagaraComp->SetDataInterface(UMyCustomDataInterface::StaticClass(), TEXT("MyDI"), CustomDI);
```

## Demo 示例

一个最小的、可编译的 C++ Actor 示例，用于生成并播放 Niagara 特效。

**ANiagaraDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NiagaraDemoActor.generated.h"

class UNiagaraComponent;
class UNiagaraSystem;

UCLASS()
class ANiagaraDemoActor : public AActor
{
    GENERATED_BODY()
    
public:    
    ANiagaraDemoActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    UNiagaraComponent* NiagaraComponent;

    UPROPERTY(EditAnywhere, Category = "FX")
    UNiagaraSystem* NiagaraSystemAsset;
};
```

**ANiagaraDemoActor.cpp**
```cpp
#include "NiagaraDemoActor.h"
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"

ANiagaraDemoActor::ANiagaraDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    NiagaraComponent = CreateDefaultSubobject<UNiagaraComponent>(TEXT("NiagaraFX"));
    RootComponent = NiagaraComponent;
}

void ANiagaraDemoActor::BeginPlay()
{
    Super::BeginPlay();
    if (NiagaraSystemAsset && NiagaraComponent)
    {
        NiagaraComponent->SetAsset(NiagaraSystemAsset);
        NiagaraComponent->Activate(true);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 系统的核心基础类型、接口和共享实用程序。 |
| `NiagaraShader` | Niagara 特效着色器的定义、编译和管理。 |
| `NiagaraVertexFactories` | 处理 Niagara 粒子与 UE 渲染管线之间的顶点工厂。 |
| `NiagaraAnimNotifies` | 将 Niagara 特效与动画通知系统集成，实现动画驱动的特效播放。 |
| `NiagaraBlueprintNodes` | 提供可在蓝图中使用的 Niagara 相关节点。 |
| `NiagaraEditor` | Niagara 系统编辑器的核心逻辑和UI。 |
| `NiagaraEditorWidgets` | Niagara 编辑器中使用的自定义控件和小部件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级同步中由监听器重入导致的问题，增强稳定性。 |
| 2026-05-22 | `85c6d110` | - Avoid creating an empty RHI buffer for SKM sampling data | 优化骨骼网格体采样数据，避免创建空的RHI缓冲区，节省资源。 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rendering... | 修复硬件光线追踪相关渲染器破坏GPUScene的问题。 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe... | 修复带状渲染器在相同光线追踪几何体上请求多次更新导致的崩溃。 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复AI工具或Python脚本向烘焙设置的输出数组写入空值时导致的崩溃。 |

### 维护评价

**活跃维护**。Niagara 作为 UE 核心的下一代 FX 系统，持续接收来自 Epic 的更新和修复。最近的提交记录显示其专注于**性能优化**（如渲染器、数据层级）、**稳定性提升**（如修复崩溃和重入问题）以及**新特性支持**（如硬件光线追踪）。该插件已非常成熟（约9年历史），是创建现代高性能视觉特效的**推荐选择**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/creating-visual-effects-in-unreal-engine/) (无特定 DocsURL，链接至官方 FX 文档首页)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Tests)