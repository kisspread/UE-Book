# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara Nanite 渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

NiagaraNanite 插件为 Unreal Engine 的粒子系统框架 **Niagara** 添加了一种全新的 **渲染器（Renderer）**。它的核心功能是允许 Niagara 粒子使用 **Nanite** 技术来渲染几何体。

**解决的问题**：默认的 Niagara 渲染器（如静态网格体渲染器）在渲染大量静态网格体实例时，CPU 开销较大。Nanite 是 UE 的虚拟化微多边形几何系统，专为高效渲染海量静态网格体而设计。该插件将两者结合，使得 Niagara 粒子可以直接利用 Nanite 的 GPU 驱动渲染管线，从而在粒子系统需要渲染成千上万个复杂静态网格体时，获得远超传统渲染方式的性能。

**为什么存在**：填补了 Niagara 高级粒子效果与 Nanite 次世代渲染技术之间的空白，使开发者能够创建兼具复杂几何表现和高性能的粒子特效，例如建筑可视化中的植被、大型场景中的重复物体、或游戏里需要大量渲染 Nanite 几何体的粒子效果。

## 使用场景

- 你需要创建一个粒子系统，其中每个粒子都是一个复杂的、拥有高多边形细节的静态网格体（如岩石、建筑构件），并且数量成千上万。
- 你在进行建筑可视化或电影渲染，需要通过粒子系统高效地散布大量 Nanite 资产，例如树木、灌木或装饰物。
- 你的游戏玩法需要生成大量具有复杂外形的物体（如魔法碎片、科幻飞船残骸），并希望最大化渲染性能。

## 蓝图用法

该插件为 Niagara 系统提供了新的渲染器选项，并可能通过蓝图函数库提供了一些查询信息的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Renderer Mesh Info` | 获取指定 Niagara 系统实例中 Nanite 渲染器的网格体信息（如网格体资产、实例数量等）。 | `UNiagaraFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **配置 Niagara 系统**：
    - 在 Niagara 系统编辑器中，添加或修改一个“网格体渲染器（Mesh Renderer）”。
    - 在渲染器的细节面板中，找到 **Renderer Name**，将其设置为 `NiagaraNanite` 或选择对应的 Nanite 渲染器类型（具体名称可能为 `NaniteStaticMesh`）。
    - 设置要渲染的 **Static Mesh** 资产（确保该资产已启用 Nanite）。
    - 配置其他常规属性，如材质、UV 通道等。

2.  **运行时查询**（可选）：
    - 在蓝图中，可以使用 `Get Renderer Mesh Info` 节点来获取运行中的粒子系统使用了哪些 Nanite 网格体以及其实例数量，用于调试或显示统计信息。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraNanite/NiagaraNaniteModule.h" // 通常用于模块的静态函数或类型
#include "Niagara/NiagaraFunctionLibrary.h" // 包含扩展后的函数库
```

### 基本用法

该插件的核心用法是在 Niagara 系统资产中配置渲染器。C++ 层面更多用于创建和配置系统，以及处理底层逻辑。以下代码片段展示了如何通过 C++ 启用 Nanite 渲染能力的思路。

```cpp
// 来源于对插件模块和渲染器注册的推断
// 首先，确保你的项目或模块的 .Build.cs 文件中添加了对 “NiagaraNanite” 模块的依赖。

// 在某个初始化或系统配置的地方（例如自定义的 Niagara 后处理器或场景构建函数中），
// 可以访问 Niagara 系统并检查或设置其渲染器。
// 注意：直接通过 C++ 动态修改运行中系统的渲染器是复杂且不常见的，
// 通常是在编辑器中或通过数据资产预设。

UNiagaraSystem* MyNaniteParticleSystem = LoadObject<UNiagaraSystem>(nullptr, TEXT("/Game/Path/To/Your/NaniteParticleSystem"));
if (MyNaniteParticleSystem)
{
    // 系统的具体渲染器类型由其内部发射器设置决定，
    // C++ 代码通常不直接操作渲染器组件，而是触发系统发射或管理其生命周期。
    UNiagaraFunctionLibrary::SpawnSystemAttached(MyNaniteParticleSystem, ...);
}
```

### 进阶用法

利用插件提供的蓝图函数库，在 C++ 中获取运行时信息。

```cpp
// 来源于对 NiagaraFunctionLibrary 扩展的推断（见 git commit 信息）
#include "Kismet/NiagaraFunctionLibrary.h"

// 假设你有一个正在运行的 Niagara 组件
UNiagaraComponent* MyNiagaraComp = GetMyNiagaraComponent();
if (MyNiagaraComp)
{
    // 调用新增的函数来获取 Nanite 渲染器的网格体信息
    TArray<FNiagaraRendererMeshInfo> MeshInfos;
    UNiagaraFunctionLibrary::GetRendererMeshInfo(MyNiagaraComp, MeshInfos);

    for (const auto& Info : MeshInfos)
    {
        UE_LOG(LogTemp, Log, TEXT("Nanite Mesh: %s, Instances: %d"), 
            *Info.MeshAsset->GetName(), Info.InstanceCount);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个使用 Nanite 渲染器的 Niagara 系统实例并将其添加到场景中。**前提**：已在编辑器中创建并配置好一个启用了 `NaniteStaticMesh` 渲染器的 Niagara 系统资产。

```cpp
// MyNaniteParticleActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNaniteParticleActor.generated.h"

UCLASS()
class MYPROJECT_API AMyNaniteParticleActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyNaniteParticleActor();

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<class UNiagaraComponent> NiagaraComp;

	UPROPERTY(EditAnywhere, Category="Nanite FX")
	TObjectPtr<class UNiagaraSystem> NaniteParticleSystem;
};
```

```cpp
// MyNaniteParticleActor.cpp
#include "MyNaniteParticleActor.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"

AMyNaniteParticleActor::AMyNaniteParticleActor()
{
	PrimaryActorTick.bCanEverTick = false;
	NiagaraComp = CreateDefaultSubobject<UNiagaraComponent>(TEXT("NiagaraComponent"));
	RootComponent = NiagaraComp;
}

void AMyNaniteParticleActor::BeginPlay()
{
	Super::BeginPlay();

	if (NaniteParticleSystem && NiagaraComp)
	{
		NiagaraComp->SetAsset(NaniteParticleSystem);
		NiagaraComp->Activate(true);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统的核心模块，本插件为其提供扩展渲染器。 |
| `NiagaraShader` | Niagara 的着色器相关代码，Nanite 渲染器需要定制着色器。 |
| `NaniteCore`, `NaniteRuntime` | 引擎的 Nanite 核心和运行时模块，提供 Nanite 的底层渲染功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-03-03 | `a811ae50` | Refactor UseGPUScene to only require EShaderPlatform argument, remove the FeatureLevel argument | 重构了 UseGPUScene 函数签名，简化参数 |
| 2026-02-02 | `eaa0098d` | Include all bound variables in parameter view model RW counts | 修复参数视图模型中读写计数的问题 |
| 2026-01-08 | `6297259f` | Fix shutdown crash. The UObject destruction order is not deterministic on shutdown. | 修复了编辑器关闭时可能发生的崩溃 |
| 2025-10-22 | `297b8f95` | Added renderer mesh info to niagara BP function library | 为蓝图函数库添加了获取渲染器网格信息的功能 |
| 2025-10-15 | `d7179c85` | Fix crash when adding additional meshes to Nanite renderer | 修复了向 Nanite 渲染器添加额外网格时导致的崩溃 |

### 维护评价

- **状态**：**活跃维护中**。
- **分析**：该插件于 **2025 年 6 月** 首次提交，非常年轻。从提交历史看，开发者（Epic Games）在近一年内持续进行维护和更新，最近一次更新在 **2026 年 3 月**，频率稳定。更新内容主要包括 **Bug 修复**（崩溃修复）和 **功能增强**（添加蓝图API），表明其处于积极的开发和迭代阶段。
- **已知限制**：该插件目前标记为 **实验性 (Experimental)**，且 **默认未启用**。这意味着 API 可能尚未稳定，未来版本可能有 breaking changes。它目前仅支持 `Win64` 和 `Mac` 平台。
- **推荐**：适合在 **原型开发、技术预览或对最新渲染技术有强烈需求的项目** 中使用。对于追求绝对稳定性的生产项目，建议密切关注其状态，或在验证阶段使用。由于其解决了特定的性能瓶颈，在合适的场景下值得尝试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraNanite/Tests) (位于插件目录内的 `Tests` 文件夹)