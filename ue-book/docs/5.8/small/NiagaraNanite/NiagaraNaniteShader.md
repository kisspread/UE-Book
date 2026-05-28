# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara纳米石渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

该插件为 Unreal Engine 的粒子系统插件 Niagara 提供了 Nanite 几何体渲染功能。Nanite 是 UE5 的虚拟化微多边形几何体系统，主要用于高效渲染高多边形静态网格体（如景观、建筑）。`NiagaraNanite` 允许 Niagara 粒子系统将 Nanite 网格体作为粒子资产进行渲染，从而可以将 Nanite 的高效渲染优势应用于动态粒子效果。例如，生成成千上万个由 Nanite 处理的复杂几何体（如碎石、瓦砾、植被实例）作为粒子，而不会造成性能瓶颈。

## 使用场景

- 你需要在大规模开放世界中生成海量、复杂的粒子效果（如漫天飞舞的瓦片、碎片、植被叶片）。
- 你需要将 Nanite 处理的高精度资产作为粒子进行实例化渲染，同时保持高性能。
- 你正在开发一个视觉效果要求极高的项目，希望利用 Nanite 的 LOD 和渲染优化来处理粒子系统。

## 蓝图用法

该插件为 Niagara 系统引入了新的渲染器类型。在 Niagara 发射器的“渲染”模块中，可以选择 `Niagara Nanite Renderer` 来启用此功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNiagaraNaniteMesh` | 为 Niagara 组件设置用于 Nanite 渲染的网格体。 | `UNiagaraFunctionLibrary` |
| `SetNiagaraNanitePosition` | 设置粒子在世界空间中的位置。 | `UNiagaraFunctionLibrary` |
| `SetNiagaraNaniteRotation` | 设置粒子的旋转。 | `UNiagaraFunctionLibrary` |
| `SetNiagaraNaniteScale` | 设置粒子的缩放。 | `UNiagaraFunctionLibrary` |

*注：上述节点是根据插件用途和常见的 Niagara 扩展模式推断，具体函数名可能随版本变化。*

### 使用示例（蓝图描述）

1.  在一个 Niagara 系统中，为你的发射器添加或选择 **渲染器（Renderer）**。
2.  在渲染器的类型下拉菜单中，选择 **Niagara Nanite Renderer**。
3.  在新渲染器的设置中，指定一个用于渲染的 **静态网格体（Static Mesh）** 资产（该网格体必须是 Nanite 启用的）。
4.  配置粒子的位置、旋转、缩放等数据模块，这些属性将直接用于控制 Nanite 网格体实例的变换。
5.  系统运行时，Niagara 会将每个粒子作为 Nanite 网格体的一个实例进行高效渲染。

## C++ 用法

该插件的核心是集成到 Niagara 渲染流水线中的自定义渲染器和 GPU 着色器。对于插件使用者，主要通过蓝图或编辑器界面进行配置。对于插件开发者或深度定制，主要涉及 C++ 模块和着色器。

### 头文件引入

```cpp
#include "Niagara/NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
```

### 基本用法

通常，你不需要直接调用 C++ 代码来驱动基础功能。所有设置都在 Niagara 编辑器中完成。但在 C++ 中，你可以动态创建和配置 Niagara 组件。

```cpp
// 动态创建一个使用 Nanite 渲染器的 Niagara 组件 (通常从蓝图资产加载)
UNiagaraComponent* NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
    GetWorld(),
    LoadObject<UNiagaraSystem>(nullptr, TEXT("/Game/Path/To/YourNaniteParticleSystem")),
    SpawnLocation,
    SpawnRotation
);

// 如果需要，可以通过 SetVariableObject 等函数动态传递参数
```

### 进阶用法

深度定制可能需要理解其内部模块。
- **NiagaraNaniteEditor** (Editor 模块)：负责在编辑器中注册该渲染器类型，并提供相关的属性编辑界面。
- **NiagaraNaniteShader** (Runtime 模块)：包含核心的全局着色器 `FNiagaraNaniteGPUSceneCS`。该计算着色器负责将 Niagara 粒子数据（位置、旋转、缩放、自定义属性）打包并转换为 Nanite GPU 场景（GPUScene）所需的格式，从而驱动 Nanite 渲染。

## Demo 示例

以下是一个使用 `NiagaraNanite` 渲染器的最小系统示例的 C++ 创建代码（假设你已有一个配置好的 Niagara 系统资产）。

**MyNaniteParticleSpawner.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNaniteParticleSpawner.generated.h"

class UNiagaraComponent;

UCLASS()
class AMyNaniteParticleSpawner : public AActor
{
    GENERATED_BODY()
    
public:
    AMyNaniteParticleSpawner();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "FX")
    UNiagaraComponent* NaniteNiagaraComp;
};
```

**MyNaniteParticleSpawner.cpp**
```cpp
#include "MyNaniteParticleSpawner.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"

AMyNaniteParticleSpawner::AMyNaniteParticleSpawner()
{
    PrimaryActorTick.bCanEverTick = false;
    
    // 创建根组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    
    // 创建 Niagara 组件
    NaniteNiagaraComp = CreateDefaultSubobject<UNiagaraComponent>(TEXT("NaniteFX"));
    NaniteNiagaraComp->SetupAttachment(RootComponent);
    
    // 在蓝图中，你需要在编辑器里将 NaniteNiagaraComp 的 Asset 属性设置为一个
    // 内置了 Niagar Nanite Renderer 的 Niagara 系统资产。
}
```

## 模块依赖

要使用此插件，你的项目或模块需要依赖以下插件（已在 `.uplugin` 中声明）：

| 插件 | 用途 |
|---|---|
| `Niagara` | 核心粒子系统框架，本插件为其提供 Nanite 渲染支持 |

你的模块 `Build.cs` 通常不需要直接添加对 `NiagaraNanite` 子模块的依赖，除非你正在开发需要与该插件内部功能（如自定义着色器）交互的插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-03 | `a811ae50` | Refactor UseGPUScene to only require EShaderPlatform argument, remove the FeatureLevel argument | 重构GPUScene的用法，简化接口参数 |
| 2026-02-02 | `eaa0098d` | Include all bound variables in parameter view model RW counts | 修复参数视图模型中的读写计数，包含所有绑定变量 |
| 2026-01-08 | `6297259f` | Fix shutdown crash. The UObject destruction order is not deterministic on shutdown. | 修复引擎关闭时的崩溃问题，确保UObject销毁顺序 |
| 2025-10-22 | `297b8f95` | Added renderer mesh info to niagara BP function library | 在Niagara蓝图函数库中添加了渲染器网格信息 |
| 2025-10-15 | `d7179c85` | Fix crash when adding additional meshes to Nanite renderer | 修复向Nanite渲染器添加额外网格时导致的崩溃 |

### 维护评价

- **创建时间**: 2025年6月创建，是一个相对较新的插件。
- **活跃度**: 最近的更新（截至2026年3月）显示该插件仍在积极维护中，内容包括功能重构、Bug修复和崩溃修复，表明其正在从实验性阶段走向稳定。
- **状态**: 标记为**实验性（IsExperimentalVersion=true）** 且**默认未启用（EnabledByDefault=false）**。这意味着该功能尚未达到生产就绪状态，API和行为在未来版本中可能会发生变化。
- **推荐**: 建议在**实验性或原型项目**中探索使用，以便提前体验和评估 Nanite 粒子渲染的能力。不建议在需要高度稳定性的正式生产项目中立即采用，除非你准备好跟随 Epic 的后续更新进行适配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite)
- [官方文档]() (暂无)