# Cascade To Niagara Converter

> Add support for scriptable conversion of Cascade Systems to Niagara Systems.

| 属性 | 值 |
|---|---|
| 中文名 | Cascade转Niagara工具 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、脚本） |
| 模块 | `CascadeToNiagaraConverter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/CascadeToNiagaraConverter) | |

## 用途

该插件提供了一个**可脚本化的**工具，用于将旧版的 Cascade 粒子系统资产批量或逐个转换为 Niagara 粒子系统。它并非简单的“一键”转换，而是通过 Python 脚本和蓝图逻辑来驱动，允许开发者自定义转换规则，处理 Cascade 中复杂的参数映射，并生成符合 Niagara 逻辑的新系统。它主要解决的是从 Cascade 项目迁移到 Niagara 的遗留资产处理问题。

## 使用场景

- 你的项目正在从 UE4 迁移到 UE5，其中有大量使用 Cascade 创建的粒子特效，需要升级到更现代、性能更好的 Niagara。
- 你希望自动化整个转换流程，并能针对项目中特定的 Cascade 模块组合编写自定义的转换规则。
- 你在开发一个需要维护多个粒子系统版本的游戏，希望将旧版 Cascade 特效统一转换为 Niagara 以便于长期维护。

## 蓝图用法

此插件的核心功能通过 Python 脚本调用，但提供了丰富的蓝图库函数 (`UCascadeToNiagaraConverterUtilities`) 来读取和分析 Cascade 系统的内部数据结构，为转换脚本提供支持。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDistributionType` | 获取一个 Cascade `UDistribution` 的类型（常量、曲线、参数等）和值类型（浮点、向量） | `UCascadeToNiagaraConverterUtilities` |
| `GetFloatDistributionConstValues` | 从 `UDistributionFloatConstant` 中提取常量浮点值 | `UCascadeToNiagaraConverterUtilities` |
| `GetVectorDistributionUniformValues` | 从 `UDistributionVectorUniform` 中提取向量的最小值和最大值 | `UCascadeToNiagaraConverterUtilities` |
| `GetFloatDistributionConstCurveValues` | 从 `UDistributionFloatConstantCurve` 中提取浮点插值曲线数据 | `UCascadeToNiagaraConverterUtilities` |
| `KeysFromInterpCurveFloat` | 将 `FInterpCurveFloat` 转换为 Niagara 可用的 `FRichCurveKey` 数组 | `UCascadeToNiagaraConverterUtilities` |

### 使用示例（蓝图描述）

在蓝图中，你不会直接调用“转换”按钮。典型用法是编写一个 Python 脚本（或蓝图工具）来遍历场景中的 Cascade Actor 或资产库中的 `UParticleSystem` 资产。对于每个要转换的 Cascade 系统：
1.  使用 `UEditorAssetLibrary` 等模块加载 `UParticleSystem`。
2.  对于系统中的每个发射器模块（如 `UParticleModuleSize`），使用 `GetDistributionType` 等节点查询其参数的分布类型。
3.  根据类型，调用对应的 `GetFloat...` 或 `GetVector...` 节点获取具体的数值或曲线数据。
4.  将这些获取到的旧参数数据，按照自定义逻辑映射到新的 Niagara 模块或参数上，并构建 `UNiagaraSystem` 资产。

## C++ 用法

插件的 C++ 代码主要提供底层数据访问库，供 Python/蓝图脚本调用。直接使用 C++ 进行转换脚本编写较为复杂，通常由插件内部的 Python 脚本环境调用这些接口。

### 头文件引入

```cpp
#include "NiagaraStackGraphUtilitiesAdapterLibrary.h"
```

### 基本用法

以下是使用 `UCascadeToNiagaraConverterUtilities` 静态方法读取 Cascade 数据的示例（简化逻辑）。
**来源**: `Engine/Plugins/FX/CascadeToNiagaraConverter/Source/CascadeToNiagaraConverter/Public/NiagaraStackGraphUtilitiesAdapterLibrary.h`

```cpp
// 假设我们有一个 UParticleModuleSizeFloat 模块
UParticleModuleSizeFloat* SizeModule = ...;
if (SizeModule && SizeModule->StartSize.Distribution)
{
    // 1. 确定分布类型
    EDistributionType DistType;
    EDistributionValueType DistValueType;
    UCascadeToNiagaraConverterUtilities::GetDistributionType(
        SizeModule->StartSize.Distribution, DistType, DistValueType);

    // 2. 根据类型获取具体值
    if (DistType == EDistributionType::Const && DistValueType == EDistributionValueType::Float)
    {
        float ConstValue;
        UCascadeToNiagaraConverterUtilities::GetFloatDistributionConstValues(
            Cast<UDistributionFloatConstant>(SizeModule->StartSize.Distribution), ConstValue);
        // 使用 ConstValue 去设置 Niagara 的某个参数
    }
    else if (DistType == EDistributionType::ConstCurve)
    {
        FInterpCurveFloat Curve;
        UCascadeToNiagaraConverterUtilities::GetFloatDistributionConstCurveValues(
            Cast<UDistributionFloatConstantCurve>(SizeModule->StartSize.Distribution), Curve);
        // 将 Curve 转换为 Niagara 曲线
        TArray<FRichCurveKeyBP> Keys = UCascadeToNiagaraConverterUtilities::KeysFromInterpCurveFloat(Curve);
        // ... 处理 Keys ...
    }
}
```

### 进阶用法

转换的完整流程涉及创建 `UNiagaraSystemConversionContext` 和 `UNiagaraEmitterConversionContext`，并通过一系列“堆栈操作”来构建 Niagara 系统。这通常由内置的 Python 脚本框架管理。开发者可以继承和覆盖脚本中的逻辑，处理更复杂的 Cascade 模块（如轨道、粒子爆发、事件等），这些都通过 `NiagaraStackGraphUtilitiesAdapterLibrary.h` 中定义的丰富结构体（如 `FOrbitOptionsBP`, `FParticleBurstBlueprint`, `FNiagaraEventHandlerAddAction`）来传递数据。

## Demo 示例

以下是一个极简的 C++ 概念示例，展示了如何启动转换流程（实际流程由插件内部脚本驱动）。
**注意**: 此示例仅作结构说明，无法直接编译，缺少必要的上下文和对象生命周期管理。

```cpp
// MyConverterDemo.h
#pragma once
#include "CoreMinimal.h"

class FMyConverterDemo
{
public:
    static void ConvertSimpleSystem(UParticleSystem* CascadeSystemToConvert, const FString& SavePath);
};

// MyConverterDemo.cpp
#include "MyConverterDemo.h"
#include "CascadeToNiagaraConverterModule.h"
#include "NiagaraStackGraphUtilitiesAdapterLibrary.h"

void FMyConverterDemo::ConvertSimpleSystem(UParticleSystem* CascadeSystem, const FString& SavePath)
{
    // 1. 创建目标 Niagara 系统资产 (通常通过 UFactory)
    UNiagaraSystem* NewNiagaraSystem = NewObject<UNiagaraSystem>(GetTransientPackage(), NAME_None, RF_Transient);
    // ... 设置基本属性 ...

    // 2. 创建系统转换上下文 (这是插件提供的核心上下文对象)
    UNiagaraSystemConversionContext* SystemContext = NewObject<UNiagaraSystemConversionContext>();
    // 注意：这里简化了，实际需要传入 NiagaraSystemViewModel 等
    // SystemContext->Init(NewNiagaraSystem, SystemViewModel);

    // 3. 对于 Cascade 系统中的每个发射器...
    for (UParticleEmitter* CascadeEmitter : CascadeSystem->Emitters)
    {
        // 创建发射器转换上下文
        UNiagaraEmitterConversionContext* EmitterContext = NewObject<UNiagaraEmitterConversionContext>();
        // ... 初始化 EmitterContext，读取 CascadeEmitter 的属性 ...

        // 4. 根据 Cascade 模块，调用 Utility 函数分析并添加 Niagara 模块
        // 这个过程非常复杂，实际由脚本中定义的规则驱动
        // 例如：分析粒子大小模块
        // GetDistributionType(...);
        // GetFloatDistributionConstValues(...);
        // 然后 EmitterContext->AddModule(..., 参数); // 伪代码

        // 5. 将发射器添加到系统
        SystemContext->AddEmitter(EmitterContext, CascadeEmitter->EmitterName);
    }

    // 6. 完成转换并保存 (实际流程更复杂，需要 Finalize 和处理资产保存)
    // SystemContext->Finalize();
    // 保存 NewNiagaraSystem 到 SavePath...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，提供所有 Niagara API、资产类型和编辑器支持。 |
| `PythonScriptPlugin` | 提供 Python 运行时和脚本环境，是驱动整个可脚本化转换流程的基础。 |
| `EditorScriptingUtilities` | 提供蓝图和脚本中使用的编辑器工具函数（如资产操作）。 |
| `FXConverterUtilities` | 插件自身提供的工具库模块，包含本文档中提到的蓝图/脚本可用函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-03 | `a9c04697` | PR #13744: CascadeToNiagaraConverter: Allow adding template emitters. | 允许在转换时添加模板发射器，增强了转换灵活性。 |
| 2025-06-25 | `049e4868` | - Add bass class for emitter / versioned emitter | 添加了发射器和版本化发射器的基类，优化了代码结构。 |
| 2025-06-04 | `0244d9f8` | PR #13323: CascadeToNiagaraConverter: Add more script input types. | 增加了更多脚本输入类型支持，提升了转换覆盖面。 |

### 维护评价

- **实验性插件**: `.uplugin` 标记为 `IsBetaVersion = true` 且默认未启用，表明其功能可能不完整或接口有变。
- **活跃维护**: 尽管创建于 2020 年，但近一年内仍有实质性功能更新（如添加模板发射器支持），表明仍在积极开发中。
- **复杂度高**: 作为 Cascade 到 Niagara 的通用转换器，其覆盖所有可能性是极其复杂的。它更适合作为一个**可定制、可脚本化的框架**，而非开箱即用的完美工具。
- **推荐使用**: 适用于有批量迁移需求且愿意投入精力编写自定义转换脚本的项目。对于少量或简单的特效，直接手动重做可能更高效。使用前请充分测试，并做好脚本调试的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/CascadeToNiagaraConverter)
- 官方文档（暂无）