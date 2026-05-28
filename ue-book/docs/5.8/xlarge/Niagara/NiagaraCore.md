# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（粒子资产、材质模板、蓝图节点） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 UE5 的下一代粒子特效系统，用于替代旧版 Cascade 粒子系统。它提供了基于节点的可视化编辑器，支持 GPU 加速模拟、数据接口（Data Interface）扩展、事件驱动、模块化堆栈等现代特效开发所需的能力。

**核心解决的问题**：
- Cascade 粒子系统架构陈旧，难以扩展和自定义
- 需要 GPU 驱动的大规模粒子模拟（百万级粒子）
- 需要与游戏数据（物理、网格体、音频等）深度交互
- 需要支持复杂的发射器继承和模块化脚本组合

**模块职责**：
| 模块 | 职责 |
|---|---|
| `NiagaraCore` | 基础类型、数据接口基类、编译哈希、版本管理等核心基础设施 |
| `Niagara` | 运行时核心：发射器、系统、模拟器、渲染器、数据集管理 |
| `NiagaraShader` | GPU 着色器编译和参数管理 |
| `NiagaraVertexFactories` | 顶点工厂，支持自定义渲染管线 |
| `NiagaraBlueprintNodes` | 蓝图公开的函数节点 |
| `NiagaraAnimNotifies` | 动画通知集成，可在动画蒙太奇中触发粒子事件 |
| `NiagaraEditor` | 编辑器工具、节点图、属性面板等 |
| `NiagaraEditorWidgets` | 编辑器自定义 UI 控件 |

## 使用场景

- 你需要制作火焰、烟雾、雨水等环境特效 → 用 Niagara 发射器系统
- 你需要百万级粒子的 GPU 模拟（如人群、弹幕） → 用 Niagara GPU 计算
- 你需要粒子与游戏世界交互（碰撞、力场、骨骼绑定） → 用 Niagara Data Interface
- 你需要在动画播放时触发特效（如攻击刀光、脚步灰尘） → 用 NiagaraAnimNotifies
- 你需要通过蓝图在运行时控制粒子参数 → 用 NiagaraComponent + Blueprint API

## 蓝图用法

Niagara 的蓝图 API 主要集中在 `Niagara` 主模块和 `NiagaraBlueprintNodes` 模块中。以下基于 NiagaraCore 公开的基础类型和通用模式说明。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Niagara Variable (Float/Vector/...)` | 运行时设置 Niagara 系统的用户变量 | `UNiagaraComponent` |
| `Set Niagara Float/Vector Parameter` | 按名称设置 Niagara 参数 | `UNiagaraComponent` |
| `Reset System` | 重置 Niagara 系统到初始状态 | `UNiagaraComponent` |
| `Set Asset` | 运行时替换 Niagara 系统资产 | `UNiagaraComponent` |
| `Set Auto Destroy` | 设置系统完成后自动销毁 | `UNiagaraComponent` |

### 使用示例（蓝图描述）

1. **创建 Niagara 组件并播放**：在 Actor 上添加 `NiagaraComponent`，设置 `Asset` 属性为你的 NiagaraSystem 资产，勾选 `Auto Activate` 即可。
2. **运行时控制粒子参数**：在蓝图中使用 `Set Niagara Variable (Float)` 节点，指定参数名称和值，连接到你的 `NiagaraComponent` 引用，可在游戏运行时动态改变粒子行为（如颜色、大小、速度）。

## C++ 用法

NiagaraCore 模块提供了 Niagara 体系的底层基础类型。以下是基于源码的核心用法。

### 头文件引入

```cpp
#include "NiagaraCore.h"
#include "NiagaraDataInterfaceBase.h"
#include "NiagaraCompileHash.h"
#include "NiagaraCustomVersion.h"
```

### 基本用法 — 自定义 Data Interface

创建自定义 Data Interface 需要继承 `UNiagaraDataInterfaceBase` 并重写关键虚函数：

```cpp
// 来源: Public/NiagaraDataInterfaceBase.h
#include "NiagaraDataInterfaceBase.h"

UCLASS(EditInlineNew, MinimalAPI)
class UMyCustomDataInterface : public UNiagaraDataInterfaceBase
{
    GENERATED_UCLASS_BODY()

public:
    // 为 GPU 提供着色器参数（SRV/UAV/Constants）
    // 此函数仅在 CDO 上调用，不在实例上
    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override
    {
        // 例如添加自定义 Shader 参数结构
        // ShaderParametersBuilder.AddNestedStruct<FMyShaderParameters>();
    }

    // 可选：创建每 Shader 的存储对象（非 Legacy 绑定模式）
    virtual FNiagaraDataInterfaceParametersCS* CreateShaderStorage(
        const FNiagaraDataInterfaceGPUParamInfo& ParameterInfo,
        const FShaderParameterMap& ParameterMap) const override
    {
        return nullptr;
    }

    // 如果实现了 CreateShaderStorage，必须提供序列化类型
    virtual const FTypeLayoutDesc* GetShaderStorageType() const override
    {
        return nullptr;
    }

    // 声明是否从其他发射器读取属性
    virtual bool HasInternalAttributeReads(
        const UNiagaraEmitter* OwnerEmitter,
        const UNiagaraEmitter* Provider) const override
    {
        return false;
    }
};
```

### 基本用法 — 编译哈希与版本管理

```cpp
// 来源: Public/NiagaraCompileHash.h, Public/NiagaraCustomVersion.h
#include "NiagaraCompileHash.h"
#include "NiagaraCustomVersion.h"

// 检查编译哈希是否有效
void CheckCompileHash(const FNiagaraCompileHash& CompileHash)
{
    if (CompileHash.IsValid())
    {
        FString HashString = CompileHash.ToString();
        UE_LOG(LogTemp, Log, TEXT("Compile hash: %s"), *HashString);
    }

    // 与 FSHAHash 比较
    FSHAHash ShaHash;
    if (CompileHash.ToSHAHash(ShaHash))
    {
        // 成功转换
    }
}

// 获取当前 Niagara 自定义版本号
FNiagaraCustomVersion::Type CurrentVersion = FNiagaraCustomVersion::LatestVersion;

// 获取最新的脚本编译版本 GUID（用于 DDC 缓存判断）
FGuid ScriptCompileVersion = FNiagaraCustomVersion::GetLatestScriptCompileVersion();
```

### 进阶用法 — 事件监听与变量引用

```cpp
// 来源: Public/NiagaraNotifyOnChanged.h, Public/NiagaraCore.h
#include "NiagaraNotifyOnChanged.h"
#include "NiagaraCore.h"

// 监听 Niagara 对象属性变化（编辑器环境下）
void BindToNiagaraObject(UNiagaraDataInterfaceBase* DataInterface)
{
#if WITH_EDITOR
    DataInterface->OnChanged().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Niagara data interface property changed!"));
    });
#endif
}

// 使用 FNiagaraVariableCommonReference 进行跨模块变量引用
void UseVariableReference()
{
    FNiagaraVariableCommonReference VarRef;
    VarRef.Name = FName(TEXT("MyVariable"));
    // UnderlyingType 指向变量类型的 UObject

    // 序列化支持
    TArray<uint8> Buffer;
    FMemoryWriter Ar(Buffer);
    Ar << VarRef;
}
```

## Demo 示例

一个最小的自定义 Niagara Data Interface 实现：

```cpp
// MyCustomDataInterface.h
#pragma once

#include "NiagaraDataInterfaceBase.h"
#include "MyCustomDataInterface.generated.h"

UCLASS(EditInlineNew, MinimalAPI)
class UMyCustomDataInterface : public UNiagaraDataInterfaceBase
{
    GENERATED_UCLASS_BODY()

public:
    // Niagara 系统中显示的名称
    virtual void GetFunctions(TArray<FNiagaraFunctionSignature>& OutFunctions) const;

    // 定义 DI 如何在 GPU 侧提供数据
    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override;

    // 设置 GPU 侧参数数据（每个 Tick）
    virtual void SetShaderParameters(
        const FNiagaraDataInterfaceGPUParamInfo& ParameterInfo,
        class FNiagaraShaderParameters& Bindings,
        const FNiagaraDataInterfaceSetArgs& Context) const;

    // 是否有内部属性读取
    virtual bool HasInternalAttributeReads(
        const UNiagaraEmitter* OwnerEmitter,
        const UNiagaraEmitter* Provider) const override { return false; }
};
```

```cpp
// MyCustomDataInterface.cpp
#include "MyCustomDataInterface.h"

UMyCustomDataInterface::UMyCustomDataInterface(FObjectInitializer const& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

void UMyCustomDataInterface::GetFunctions(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
    // 注册可被 Niagara 脚本调用的自定义函数
    // FNiagaraFunctionSignature Sig;
    // Sig.Name = FName(TEXT("GetCustomValue"));
    // OutFunctions.Add(MoveTemp(Sig));
}

void UMyCustomDataInterface::BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const
{
    // 添加 GPU 着色器参数结构
    // ShaderParametersBuilder.AddNestedStruct<FMyGPUParams>();
}

void UMyCustomDataInterface::SetShaderParameters(
    const FNiagaraDataInterfaceGPUParamInfo& ParameterInfo,
    FNiagaraShaderParameters& Bindings,
    const FNiagaraDataInterfaceSetArgs& Context) const
{
    // 填充 GPU 参数数据
}
```

## 模块依赖

以下是 Niagara 插件独特的依赖项（省略 Core、CoreUObject、Engine、Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `RHI` | GPU 资源和渲染硬件接口，用于 GPU 粒子模拟 |
| `RenderCore` | 渲染管线核心，管理着色器编译 |
| `ShaderCore` | 着色器编译基础设施 |
| `VectorVM` | Niagara 自有的向量虚拟机，执行粒子模拟脚本 |
| `MeshDescription` | 网格体描述，用于网格粒子渲染 |
| `StaticMeshDescription` | 静态网格资产导入导出 |
| `PythonScriptPlugin` | Python 脚本支持，用于自动化和批量操作 |
| `ProceduralMeshComponent` | 程序化网格组件（可选依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级同步时的重入问题，防止 OnHierarchyChanged 监听器递归调用导致崩溃 |
| 2026-05-22 | `85c6d110` | Avoid creating an empty RHI buffer for SKM sampling data | 优化骨骼网格采样数据的 RHI 缓冲区创建，避免分配空缓冲区浪费资源 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende | 修复硬件光线追踪模式下网格渲染器获取动态光追实例时损坏 GPUScene 的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复带状渲染器在硬件光追模式下因重复请求同几何体更新而导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复 AI 工具或 Python 脚本向 BakingSettings 的 Outputs 数组写入空条目时的崩溃 |

### 维护评价

**🟢 活跃维护** — Niagara 作为 UE5 的官方主力粒子系统，处于持续高强度维护中。

- **创建时间**：2017 年（与 UE4 时代的 Paragon 项目同期），已有 9 年历史
- **更新频率**：最近的提交在 2026 年 5 月，每周都有多次功能修复和优化
- **维护内容**：涵盖 GPU 模拟修复、硬件光追支持、性能优化、编辑器稳定性、Python 自动化等全方位
- **已知限制**：作为 xlarge 级别插件（1622 源文件），学习曲线较陡，自定义扩展需深入理解 Data Interface 和脚本系统
- **推荐使用**：✅ 强烈推荐。这是 UE5 中创建粒子特效的**标准方式**，新项目不应再使用 Cascade

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/creating-visual-effects-in-niagara-for-unreal-engine/)（Epic 官方 Niagara 文档）