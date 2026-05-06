# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara Nanite渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Niagara渲染器资产、材质） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

该插件为 Niagara 粒子系统添加了一种基于 Nanite 技术的渲染器。Nanite 是 UE5 的虚拟几何体系统，能够按像素级精度渲染大量多边形。通过此插件，Niagara 粒子可以直接使用 Nanite Mesh 进行渲染，实现超大规模粒子群体的高性能绘制，且自动支持 LOD 和遮挡裁剪。

**为什么存在**：传统 Niagara 渲染器（如 Sprite、Ribbon、Mesh）在处理成千上万的粒子时性能开销较大，且无法利用 Nanite 的几何体优化。此插件将 Nanite 的渲染能力与 Niagara 的粒子系统结合，使开发者能够创建包含数万甚至数十万高精度几何体粒子的特效。

## 使用场景

- 需要渲染海量高精度动态物体（如星空、蜂群、弹幕、碎片风暴）的特效
- 粒子需要保持 Nanite 级别的细节，且性能要求严格
- 利用 Nanite 的自动 LOD 处理远近距离的粒子，无需手动管理渲染距离

## 蓝图用法

当前插件版本（1.0）没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有与 Nanite 渲染器相关的配置通过 Niagara 系统编辑器中的渲染器属性面板进行，这些面板属性是原生 UPROPERTY，非蓝图节点。因此，在蓝图中无法直接调用或设置特定的 Nanite 渲染器参数。

如果需要动态控制渲染器行为，建议使用 C++ 扩展或通过 Niagara 的 Data Interface 机制。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraNaniteModule.h"       // 主运行时模块
#include "NiagaraNaniteRendererProperties.h" // 渲染器属性类（假设存在，实际需根据源码路径调整）
```

### 基本用法

以下示例展示了如何在 C++ 中为 Niagara 系统创建并配置 Nanite 渲染器。实际使用时，通常通过编辑器操作，但也可通过代码动态修改。

```cpp
// 假设已有 UNiagaraSystem* NiagaraSystem
UNiagaraSystem* System = ...;

// 获取粒子发射器（示例：添加一个新的发射器）
FNiagaraEmitterHandle Handle = System->AddEmitter("NaniteEmitter");
UNiagaraEmitter* Emitter = Handle.GetInstance();

// 设置 Nanite 渲染器
UNiagaraNaniteRendererProperties* RendererProps = NewObject<UNiagaraNaniteRendererProperties>(Emitter);
RendererProps->SetMeshOverride(MeshAsset); // 指定 Nanite 网格体
Emitter->SetRendererProperties(RendererProps);
```

**注意**：上述代码基于常见 API 模式，实际接口可能因官方实现而异。建议参考 `Engine/Plugins/FX/NiagaraNanite/Source/NiagaraNanite/Public/NiagaraNaniteRendererProperties.h` 了解完整 API。

### 进阶用法

通过 `FNiagaraNaniteRendererProperties` 可以调整粒子相对于网格的变换、材质覆盖、GPU 场景实例数据等。以下是从最近修复中提取的常见注意点：

- **实例数据冲突**：Nanite 渲染器可能覆写 GPUScene 实例数据（`a0f5c688`），避免在自定义 Shader 中手动修改 Nanite 实例数据。
- **上一帧变换**：CPU 端需正确处理上一帧的粒子变换（`c1117853`），否则可能出现抖动。
- **材质覆盖**：命名约定已调整（`c7595dab`），使用 `MaterialOverride` 结构时应检查最新 API。

## Demo 示例

```cpp
// NaniteNiagaraDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NaniteNiagaraDemo.generated.h"

UCLASS()
class ANaniteNiagaraDemo : public AActor
{
	GENERATED_BODY()
public:
	virtual void BeginPlay() override;
};

// NaniteNiagaraDemo.cpp
#include "NaniteNiagaraDemo.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "NiagaraNaniteRendererProperties.h"

void ANaniteNiagaraDemo::BeginPlay()
{
	Super::BeginPlay();
	// 加载 Nanite 网格
	UStaticMesh* NaniteMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Example/NaniteMesh.NaniteMesh"));
	if (!NaniteMesh) return;

	// 创建临时 Niagara 系统（实际项目中建议通过资产创建）
	UNiagaraSystem* System = NewObject<UNiagaraSystem>();
	UNiagaraEmitter* Emitter = System->AddEmitter("NaniteEmitter").GetInstance();
	UNiagaraNaniteRendererProperties* Renderer = NewObject<UNiagaraNaniteRendererProperties>(Emitter);
	Renderer->SetMeshOverride(NaniteMesh);
	Emitter->SetRendererProperties(Renderer);
	System->UpdateCompiledVariables();

	// 在世界中生成粒子
	UNiagaraComponent* Comp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), System, GetActorLocation());
	Comp->Activate();
}
```

**构建依赖**：需要在 `.Build.cs` 中添加 `PublicDependencyModuleNames.AddRange(new string[] { "Niagara", "NiagaraNanite" });`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 核心系统，提供粒子框架和发射器 |
| `NiagaraNanite` | 运行时渲染器实现，包含渲染器属性、数据接口 |
| `NiagaraNaniteShader` | 着色器模块，提供 Nanite 渲染所需的 HLSL |
| `NiagaraNaniteEditor` | 编辑器模块，提供属性定制、缩略图支持 |
| `Renderer` | UE 渲染基础模块（隐式依赖） |
| `Nanite` | Nanite 渲染系统（隐式依赖） |

**注意**：以上依赖基于插件结构推测，实际编译需检查各模块的 `Build.cs` 文件。

## 维护状态

### 近期更新

- 2025-10-15 `2673f681` - Fix crash when adding additional meshes to Nanite renderer
- 2025-08-25 `a0f5c688` - Fix bug where nanite niagara shader can stomp the instance data in GPUScene
- 2025-08-18 `c1117853` - Fix for previous transforms being incorrect on CPU
- 2025-08-13 `c7595dab` - Fix naming of material override struct
- 2025-08-11 `8c7d4887` - Fix for niagara nanite renderer thumbnail crash

### 维护评价

该插件于 2025 年 8 月首次提交，属于全新实验性功能。最近两个月内仍有积极修复（2025年10月），且修复内容涉及实际崩溃和逻辑错误，说明开发团队正在快速迭代。虽然版本号为 1.0，但 IsExperimentalVersion=true 表明 API 和行为可能频繁变化。适合尝试前沿特效开发的团队，但应预期后续版本可能不兼容。

**推荐度**：实验性，建议在非生产项目中评估；继续关注官方后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/setting-up-nanite-niagara/)（待官方发布）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite/Tests)（如有）