# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、示例系统、材质模板） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 UE5 的下一代粒子特效系统，用于替代传统的 Cascade 粒子系统。它提供了基于数据驱动的可视化效果编辑框架，支持 GPU 粒子模拟、蓝图可编程逻辑、模块化发射器架构以及与物理、动画、AI 等系统的深度集成。

**Niagara 解决的核心问题：**
- **可编程性**：通过 Niagara 脚本语言（类似蓝图的节点图）让美术和技术美术自定义粒子行为，无需编写 C++ 代码
- **GPU 粒子**：完整的 GPU 模拟管线，支持大规模粒子（数百万级）的高效渲染和物理交互
- **模块化架构**：发射器、系统、模块可复用和组合，支持继承和覆盖
- **数据通道**：粒子之间、粒子与世界之间可以通过数据接口进行通信
- **多渲染器支持**：Sprite、Mesh、Ribbon（带状）、Light、Component 等多种渲染器类型

**当前文档范围**：本文档聚焦于 `NiagaraVertexFactories` 模块，该模块提供 Niagara 渲染器所需的底层顶点工厂（Vertex Factory）实现，是粒子渲染管线的核心 GPU 渲染基础设施。

## 使用场景

- 你需要创建火焰、烟雾、爆炸等视觉特效 → 用 Niagara 系统（整体插件）
- 你需要自定义粒子发射、更新、渲染逻辑 → 用 Niagara 的 Module 和 Script 功能
- 你需要 GPU 模拟百万级粒子 → 用 Niagara GPU Compute 管线
- 你需要让粒子与世界碰撞或查询物理 → 用 Niagara 的 Data Interface（Grid2D、Skeletal Mesh 等）
- 你需要为自定义渲染器编写顶点工厂 → 参考 `NiagaraVertexFactories` 模块

## 蓝图用法

Niagara 的蓝图集成主要通过 `NiagaraBlueprintNodes` 模块提供。以下是核心的蓝图 API 分组：

### 系统生命周期

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnSystemAtLocation` | 在世界位置生成 Niagara 系统实例 | `UNiagaraFunctionLibrary` |
| `SpawnSystemAttached` | 附加到组件上生成 Niagara 系统 | `UNiagaraFunctionLibrary` |
| `OverrideSystemUserVariable*` | 覆盖系统中用户暴露的变量 | `UNiagaraFunctionLibrary` |

### 组件控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateSystem` | 激活 Niagara 组件 | `UNiagaraComponent` |
| `DeactivateSystem` | 停用 Niagara 组件 | `UNiagaraComponent` |
| `SetVariable*` | 设置发射器参数（Float/Vector/Bool 等） | `UNiagaraComponent` |
| `SetNiagaraVariable*` | 按名称设置任意 Niagara 变量 | `UNiagaraComponent` |

### 使用示例（蓝图描述）

**快速生成特效：**
1. 调用 `SpawnSystemAtLocation` 节点
2. `System Template` 引用一个 `UNiagaraSystem` 资产
3. `Spawn Location` 设置世界坐标
4. `Auto Destroy` 设为 true 表示播完自动销毁

**附加到角色骨骼：**
1. 调用 `SpawnSystemAttached` 节点
2. `Attach To Component` 连接到角色的 Mesh 组件
3. `Attach Point Name` 设置骨骼名（如 "hand_r"）
4. `Location Type` 选 `KeepRelativeOffset`

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"
#include "NiagaraFunctionLibrary.h"
```

对于 `NiagaraVertexFactories` 模块：

```cpp
#include "NiagaraVertexFactory.h"
#include "NiagaraSpriteVertexFactory.h"
#include "NiagaraMeshVertexFactory.h"
#include "NiagaraRibbonVertexFactory.h"
```

### 基本用法 — 运行时生成 Niagara 系统

```cpp
// 在 Actor 中生成 Niagara 特效
UNiagaraComponent* NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
    GetWorld(),
    MyNiagaraSystem,        // UNiagaraSystem* 资产引用
    GetActorLocation(),     // FWorldLocation
    GetActorRotation(),     // FRotator
    FVector::OneVector,     // Scale
    true,                   // bAutoDestroy
    true,                   // bAutoActivate
    ENCPoolMethod::None,    // Pooling method
    true                    // bPreCullCheck
);

// 设置运行时参数
if (NiagaraComp)
{
    NiagaraComp->SetVariableFloat(FName("User.SpawnRate"), 100.0f);
    NiagaraComp->SetVariableLinearColor(FName("User.Color"), FLinearColor::Red);
}
```

### 基本用法 — 自定义顶点工厂

Niagara 的 `FNiagaraVertexFactoryBase` 是所有粒子顶点工厂的基类，提供三种主要工厂类型：

```cpp
// 顶点工厂类型枚举
enum ENiagaraVertexFactoryType
{
    NVFT_Sprite,    // Sprite 粒子
    NVFT_Ribbon,    // Ribbon/Trail 带状粒子
    NVFT_Mesh,      // Mesh 粒子（使用 3D 模型）
    NVFT_MAX
};

// 所有工厂继承自 FNiagaraVertexFactoryBase
// 编译环境会自动定义 NIAGARA_PARTICLE_FACTORY=1
```

### 进阶用法 — GPU 排序与剔除

```cpp
// GPU 排序使用 compute shader 生成排序键
// FNiagaraSortKeyGenCS 支持多种排列组合：
// - FEnableCulling: 启用 GPU 剔除
// - FSortUsingMaxPrecision: 高精度排序
// - FUseWaveOps: 使用 Wave Operations 加速

// Draw Indirect 生成
// FNiagaraDrawIndirectArgsGenCS 为 GPU 粒子生成间接绘制参数
// 支持纹理 RW 和非 RW 两种路径
// NIAGARA_DRAW_INDIRECT_ARGS_GEN_THREAD_COUNT = 64
```

## Demo 示例

### 自定义 Niagara 顶点工厂派生类

```cpp
// MyCustomNiagaraVertexFactory.h
#pragma once

#include "NiagaraVertexFactory.h"
#include "VertexFactory.h"

class FMyCustomVertexFactory : public FNiagaraVertexFactoryBase
{
    DECLARE_VERTEX_FACTORY_TYPE(FMyCustomVertexFactory);

public:
    explicit FMyCustomVertexFactory(ERHIFeatureLevel::Type InFeatureLevel)
        : FNiagaraVertexFactoryBase(NVFT_Sprite, InFeatureLevel)
    {}

    // 声明是否在当前平台和材质组合下编译此工厂
    static bool ShouldCompilePermutation(const FVertexFactoryShaderPermutationParameters& Parameters)
    {
        return IsFeatureLevelSupported(Parameters.Platform, ERHIFeatureLevel::SM5);
    }

    // 修改着色器编译环境
    static void ModifyCompilationEnvironment(
        const FVertexFactoryShaderPermutationParameters& Parameters,
        FShaderCompilerEnvironment& OutEnvironment)
    {
        FNiagaraVertexFactoryBase::ModifyCompilationEnvironment(Parameters, OutEnvironment);
        OutEnvironment.SetDefine(TEXT("MY_CUSTOM_FACTORY"), TEXT("1"));
    }

    // 初始化 RHI 资源
    virtual void InitRHI(FRHICommandListBase& RHICmdList) override
    {
        FVertexDeclarationElementList Elements;
        // 添加顶点元素声明
        Elements.Add(AccessStreamComponent(
            FVertexStreamComponent(&PositionBuffer, 0, sizeof(FVector3f), VET_Float3), 0));

        InitDeclaration(Elements);
    }

private:
    FVertexBuffer PositionBuffer;
};
```

```cpp
// MyCustomNiagaraVertexFactory.cpp
#include "MyCustomNiagaraVertexFactory.h"

IMPLEMENT_VERTEX_FACTORY_TYPE(FMyCustomVertexFactory, 
    "/Engine/Private/MyCustomVertexFactory.ush", 
    EVertexFactoryFlags::UsedWithMaterials,
    EVertexFactoryFlags::SupportsStaticLighting);
```

## 模块依赖

`NiagaraVertexFactories` 模块的依赖：

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 核心数据类型和工具函数 |
| `NiagaraShader` | Niagara 着色器编译基础设施 |
| `RenderCore` | 渲染核心，顶点工厂基类 `FVertexFactory` |
| `RHI` | 渲染硬件接口，缓冲区、SRV、UAV 管理 |
| `Renderer` | 场景渲染管线，材质渲染代理 |

整个 Niagara 插件还依赖：
- `PythonScriptPlugin`（脚本自动化）
- `ToolsetRegistry`（工具注册）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 防止数据层级监听器递归重入导致同步异常 |
| 2026-05-22 | `85c6d110` | Avoid creating an empty RHI buffer for SKM sampling data | 优化骨骼网格采样，避免创建空 RHI 缓冲区 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende | 修复 Mesh 渲染器光线追踪实例损坏 GPUScene 的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复 Ribbon 渲染器对同一光线追踪几何体多次更新导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复 AI 工具或 Python 写入空值导致 Baker 设置崩溃 |

### 维护评价

**⭐ 活跃维护中，强烈推荐使用。**

- **创建时间**：2017 年 8 月，已迭代约 9 年，是 Epic 官方力推的下一代粒子系统
- **更新频率**：2026 年 5 月仍在密集更新（一周内 5+ commits），持续修复光线追踪兼容性、性能优化、崩溃修复
- **维护状态**：作为 UE5 的官方粒子系统，由 Epic 团队持续维护，属于引擎核心模块
- **源码规模**：1622 个源文件，8 个子模块，大型框架级插件
- **推荐程度**：这是 UE5 中唯一推荐的粒子系统，Cascade 已被标记为过时

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/Niagara/)