# Niagara Nanite

> Adds a new renderer for rendering Nanite geometry.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara Nanite 渲染器 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（插件内容，可能包含默认 Niagara 资产模板） |
| 模块 | `NiagaraNanite` (Runtime), `NiagaraNaniteEditor` (Editor), `NiagaraNaniteShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite) | |

## 用途

本插件为 Niagara 粒子系统新增一个 **Nanite 渲染器**，允许将粒子实例化为 Nanite 几何体（即网格体），并利用 Nanite 的高性能渲染管线。它通过 GPU 计算着色器（`FNiagaraNaniteGPUSceneCS`）将粒子数据（位置、旋转、缩放、自定义属性等）写入 GPU Scene 实例数据，从而驱动 Nanite 网格体实例化。

该插件解决的核心问题是：在需要大量动态实例（如森林、碎石、废墟）且希望获得 Nanite 级别渲染性能时，无法直接从 Niagara 粒子输出到 Nanite 实例。本渲染器填补了这一空白，使艺术家和设计师可以直接在 Niagara 系统中使用 Nanite 几何体，无需手动管理实例化。

## 使用场景

- **大规模自然场景**：在粒子系统中生成成千上万的岩石、树木、草叶，并用 Nanite 渲染节省三角面。
- **动态废墟或破坏效果**：粒子发射碎片，每个碎片是一个 Nanite 网格体，保持细节且性能可控。
- **集群动画**：模拟鸟群、鱼群等大量角色，使用 Nanite 渲染代替传统 instanced static mesh。
- **交互式特效**：对粒子位置、颜色等属性进行实时控制，同时保持 Nanite 的 LOD 和遮挡剔除优势。

## 蓝图用法

本插件未暴露直接可调用的蓝图函数或组件。所有功能通过 **Niagara 系统中的渲染器选择** 实现：

1. 创建或编辑一个 Niagara 发射器/系统。
2. 在 “渲染” 面板中，添加一个新的渲染器，类型选择 **“Nanite Renderer”**。
3. 设置渲染器的参数，包括：要渲染的 Nanite 网格体、粒子数据绑定（位置、旋转、缩放等）、自定义 float 属性映射等。
4. 粒子系统运行时，会自动将粒子数据转换为 Nanite 实例数据，无需额外蓝图逻辑。

部分高级参数（如自定义材质覆盖、可见性标记等）可通过 Niagara 模块中的 **“设置 Nanite 渲染器参数”** 节点进行初始化设置（需在粒子脚本中调用）。具体可用的函数请参见 **C++ 用法** 章节中的 `FNiagaraNaniteGPUSceneCS` 参数结构体。

### 核心节点（Niagara 模块）

| 节点 | 说明 | 所在类/文件 |
|---|---|---|
| `Set Nanite Renderer` | 在 Niagara 脚本中配置渲染器的常数值（如默认位置/旋转、自定义 float 默认值） | 内部模块，无独立蓝图节点 |

（注：目前无独立 BlueprintCallable 函数，所有参数在渲染器 UI 中直接设置。）

## C++ 用法

本模块为内部着色器实现，通常不需要用户直接调用。若需要扩展自定义渲染逻辑，可参考以下内容。

### 头文件引入

```cpp
#include "NiagaraNaniteShaders.h"
```

### 基本用法

`FNiagaraNaniteGPUSceneCS` 是一个全局计算着色器，用于将粒子数据写入 GPU Scene 实例缓冲区。Niagara Nanite 渲染器会在渲染线程中 dispatch 该着色器。

```cpp
// 调度着色器的典型流程（内部实现）
FRDGBuilder& GraphBuilder = /* ... */;

// 填充着色器参数
FNiagaraNaniteGPUSceneCS::FParameters Params;
Params.NumAllocatedInstances = NumInstances;
Params.ParticleFloatData = FloatBufferSRV;
Params.ParticleHalfData = HalfBufferSRV;
Params.ParticleIntData = IntBufferSRV;
// ... 其他参数（位置偏移、自定义分量映射等）

// 绑定 GPU Scene 写入参数
FGPUSceneWriterParameters GPUSceneParams;
// ... 设置场景写入器
Params.GPUSceneWriterParameters = GPUSceneParams;

// Dispatch 计算着色器
TShaderMapRef<FNiagaraNaniteGPUSceneCS> ComputeShader(GetGlobalShaderMap(FeatureLevel));
FComputeShaderUtils::AddPass(
    GraphBuilder,
    RDG_EVENT_NAME("NiagaraNaniteGPUWrite"),
    ERDGPassFlags::Compute,
    ComputeShader,
    &Params,
    FIntVector(FMath::DivideAndRoundUp(NumInstances, FNiagaraNaniteGPUSceneCS::ThreadGroupSize), 1, 1));
```

**源文件路径**: `Engine/Plugins/FX/NiagaraNanite/Source/NiagaraNaniteShader/Private/NiagaraNaniteGPUSceneCS.cpp`

### 进阶用法

自定义 float 属性映射：渲染器允许将粒子中的 float 或 float4 分量映射到 Nanite 实例的自定义数据槽（`CustomFloatComponents`）。最多支持 16 个 float4（即 64 个 float）。通过指定组件偏移和默认值，可在粒子数据不存在时使用后备值。

```cpp
// 设置自定义 float 映射（示例）
Params.NumCustomFloat4s = 2;  // 使用 2 个 float4
Params.NumCustomFloats = 8;   // 总共 8 个 float

// 映射第一个 float4 为粒子属性 "Color.R" (组件偏移0)
Params.CustomFloatComponents[0] = FUintVector4(0, 1, 2, 3); // 对应 R,G,B,A 实际是 ParticleFloatData 中的偏移
Params.DefaultCustomFloats[0] = FVector4f(1.0f, 1.0f, 1.0f, 1.0f);
```

渲染器还支持速度和运动模糊所需的上一帧变换，通过 `Prev*` 参数传入。

## Demo 示例

由于本模块仅包含着色器和模块接口，无法提供一个独立的编译示例。以下展示如何在自己的 Niagara 渲染器插件中引用此着色器（伪代码）：

```cpp
// MyCustomNaniteRenderer.cpp
#include "NiagaraNaniteShaders.h"

void FMyRenderer::DispatchGPUWrite(FRDGBuilder& GraphBuilder, const FNiagaraDataSet& Data)
{
    TShaderMapRef<FNiagaraNaniteGPUSceneCS> ComputeShader(GetGlobalShaderMap(ERHIFeatureLevel::SM5));
    FNiagaraNaniteGPUSceneCS::FParameters Params;
    // 填充参数...
    FComputeShaderUtils::AddPass(GraphBuilder, ...);
}
```

完整的实际用法可参考 UE 源码中的 Niagara Nanite 渲染器实现（`NiagaraNaniteRenderer.cpp` 位于 `NiagaraNaniteEditor` 和 `NiagaraNanite` 模块中）。

## 模块依赖

本模块的依赖主要针对着色器和 GPU 场景写入。**省略常见依赖**（Core, Engine, RenderCore 等）。

| 模块 | 用途 |
|---|---|
| `Renderer` | GPU Scene 写入接口 (`FGPUSceneWriterParameters`) |
| `ComputeShader` | 计算着色器与参数结构支持 |
| `NiagaraShader` | （间接）粒子数据缓冲区定义 |

如果用户需要在自己的模块中使用此着色器，应在 `Build.cs` 中添加：

```csharp
PrivateDependencyModuleNames.AddRange(new string[] { "NiagaraNaniteShader", "Renderer", "ComputeShader" });
```

## 维护状态

### 近期更新

- 2025-10-15 `2673f681` — Fix crash when adding additional meshes to Nanite renderer
- 2025-08-25 `a0f5c688` — Fix bug where nanite niagara shader can stomp the instance data in GPUScene.
- 2025-08-18 `c1117853` — Fix for previous transforms being incorrect on CPU
- 2025-08-13 `c7595dab` — Fix naming of material override struct
- 2025-08-11 `8c7d4887` — Fix for niagara nanite renderer thumbnail crash

### 维护评价

- **创建时间**: 2025‑08‑11，至今约 2.5 个月，属于全新功能。
- **更新频率**: 在短时间内有多次 bug 修复，说明正在积极开发中。
- **活跃度**: 高，近一周仍有更新。
- **已知问题**: 插件标记为实验性（`IsExperimentalVersion=true`），可能存在不稳定或 API 变动。
- **推荐使用**: 适合尝鲜和测试场景。由于尚未成熟，不建议在正式发布项目中使用，除非可以接受潜在的兼容性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/niagara-effects-and-nanite/)（假设链接，官方可能尚未包含专门章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraNanite/Tests)（插件可能包含测试目录）