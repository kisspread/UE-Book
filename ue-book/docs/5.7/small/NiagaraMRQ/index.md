# Niagara MRQ Support

> Contains a data interface that can be used to read Movie Render Queue information in Niagara simulations.

| 属性 | 值 |
|---|---|
| 中文名 | MRQ Niagara 支持 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraMRQ` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraMRQ) | |

## 用途

该插件提供了一个 Niagara 数据接口（`UNiagaraDataInterfaceMRQ`），允许 Niagara 粒子系统在运行时读取当前 **Movie Render Queue（MRQ）** 的渲染状态信息。主要用于电影渲染管线中，让粒子特效能够感知渲染过程（如是否激活、当前累积采样索引、帧率等），从而实现与 MRQ 同步的粒子行为（例如运动模糊、时间累积采样相关特效）。

## 使用场景

- **电影级粒子渲染**：使用 Movie Render Queue 渲染过场动画时，粒子系统需要知道当前正在进行的渲染采样次数（TemporalSampleCount）和采样索引（TemporalSampleIndex），以便粒子运动模糊、透明度累积值与 MRQ 的采样方式匹配。
- **动态调整粒子行为**：在非渲染（编辑器或运行时预览）与 MRQ 渲染时切换不同粒子逻辑，例如仅在 MRQ 渲染时开启高精度运动模糊或粒子数量倍增。

## 蓝图用法

该插件不提供直接在蓝图蓝图中调用的 `UFUNCTION(BlueprintCallable)` 节点。所有的功能通过 Niagara 系统内部的数据接口暴露。在 **Niagara 编辑器** 中，你可以将数据接口作为模块输入添加：

1. 在 Niagara 发射器或系统中，添加一个 **User Exposed** 或 **Parameter** 类型为 `MovieRenderQueue`（即 `UNiagaraDataInterfaceMRQ`）。
2. 在粒子脚本（如 Spawn、Update）中，使用该数据接口提供的变量或函数来读取 MRQ 状态。

数据接口内部暴露了以下可在 Niagara 脚本中访问的变量（通过 HLSL 或 CPU 绑定）：

| 变量名               | 类型    | 说明                               |
|----------------------|---------|------------------------------------|
| `Active`             | int32   | 当前 MRQ 是否处于激活渲染状态         |
| `TemporalSampleCount`| int32   | 总的时间采样帧数（Sub‑Frame 数量）    |
| `TemporalSampleIndex`| int32   | 当前正在渲染的采样索引（从 0 开始）   |
| `SequenceFPS`        | float   | 序列帧率（FPS）                     |

### 使用示例（Niagara 蓝图描述）

1. 在 Niagara 系统变量面板中创建一个 `MovieRenderQueue` 类型参数（命名为 `MRQDI`）。
2. 在粒子 **Update** 脚本中，使用 **Get Value** 节点从 `MRQDI` 读取 `TemporalSampleIndex` 和 `TemporalSampleCount`。
3. 将 `TemporalSampleIndex / TemporalSampleCount` 作为粒子颜色的不透明度（Alpha）输入，实现每帧累积淡入效果。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraDataInterfaceMRQ.h"
```

### 基本用法

数据接口本身需要被添加到 Niagara System 实例中。以下示例展示如何在 C++ 中创建并配置一个使用该数据接口的 Niagara 组件：

```cpp
// 获取 Niagara 系统（例如从组件或蓝图）
UNiagaraComponent* NiagaraComp = ...;

// 确保数据接口已经通过参数暴露
// 通常数据接口会作为 User Parameter 配置在 Niagara 资产中
// 下面展示如何从代码中设置一个自定义数据接口实例
UNiagaraDataInterfaceMRQ* MRQDI = NewObject<UNiagaraDataInterfaceMRQ>(NiagaraComp);
FNiagaraVariableBase Var(FNiagaraTypeDefinition(MRQDI->GetClass()), TEXT("MRQDI"));
FNiagaraUserVariableBinding Binding;
Binding.Parameter = Var;
NiagaraComp->SetUserVariableBinding(Binding, MRQDI);
```

> **注意**：实际使用中，更推荐在 Niagara 资产编辑器中直接添加 `MovieRenderQueue` 数据接口作为参数，并通过蓝图或 C++ 绑定参数名称。上述代码仅为演示如何以最小方式注入数据接口。

### 进阶用法

在自定义 C++ 模块中，如果需要手动读取 MRQ 信息，可以访问数据接口的 `FShaderParameters` 结构：

```cpp
// 从 Niagara 系统实例中获取数据接口实例
UNiagaraDataInterfaceMRQ* DI = ...;
if (DI)
{
    // 数据接口内部维护了当前 MRQ 状态（通过 PerInstanceData）
    // 可以直接调用 PerInstanceTick 更新，但通常由 Niagara 系统自动处理
    // 若需直接获取参数，可构建 FShaderParameters 并填充
}
```

由于该数据接口的主要设计目标是供 Niagara 内部使用，不推荐用 C++ 直接操作其数据。正确的做法是让 Niagara 系统通过该数据接口自动同步 MRQ 信息。

## Demo 示例

以下是一个最小的 C++ 演示，展示如何在运行时创建一个 Niagara System，并为其设置一个 `MovieRenderQueue` 数据接口，然后激活粒子系统。

### DemoSystem.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NiagaraComponent.h"
#include "NiagaraDataInterfaceMRQ.h"
#include "DemoSystem.generated.h"

UCLASS()
class ADemoSystem : public AActor
{
    GENERATED_BODY()

public:
    ADemoSystem();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Niagara")
    UNiagaraComponent* NiagaraComponent;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "Niagara")
    void SetupMRQDataInterface();
};
```

### DemoSystem.cpp

```cpp
#include "DemoSystem.h"

ADemoSystem::ADemoSystem()
{
    PrimaryActorTick.bCanEverTick = false;

    NiagaraComponent = CreateDefaultSubobject<UNiagaraComponent>(TEXT("NiagaraComponent"));
    RootComponent = NiagaraComponent;
}

void ADemoSystem::SetupMRQDataInterface()
{
    if (!NiagaraComponent || !NiagaraComponent->GetAsset())
        return;

    // 创建 MRQ 数据接口实例
    UNiagaraDataInterfaceMRQ* MRQDI = NewObject<UNiagaraDataInterfaceMRQ>(this);

    // 参数名称需要与 Niagara 资产中定义的 User Parameter 名称一致
    const FName ParamName = TEXT("MRQDI");
    NiagaraComponent->SetUserVariableBinding(
        FNiagaraUserVariableBinding(FNiagaraVariableBase(FNiagaraTypeDefinition(MRQDI->GetClass()), ParamName)),
        MRQDI
    );

    // 重新初始化组件以应用新的数据接口
    NiagaraComponent->ReinitializeSystem();
}
```

> 注意：实际项目中建议在 Niagara 资产中预先配置好数据接口参数，然后通过蓝图或 C++ 直接绑定到该参数，而不是动态创建数据接口实例。

## 模块依赖

该插件在 `NiagaraMRQ.Build.cs` 中声明了唯一的独特依赖：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 用于编辑器中的 MRQ 数据同步（允许在编辑器中测试时也可获取到假数据） |

除此外无其他特殊依赖（标准 Core/Engine/Slate 等省略）。

## 维护状态

### 近期更新

- 2024-11-22 `36771d79` 更新 uplugin 描述文件标记（实验性和Beta标志清理）
- 2023-12-13 `608f1437` 优化 `UNiagaraDataInterface::GetFunctions()` 函数序列（涉及基础结构改动）
- 2023-07-27 `4f537bda` 初始创建 Niagara MovieRenderQueue 插件

### 维护评价

该插件自创建（2023‑07‑27）以来仅有一次实质性更新（2023‑12‑13 的基础接口优化），最近一次更新为 uplugin 元数据清理。项目处于**维护不活跃**状态，未添加新功能或修复已知问题。目前仍标记为 Beta 版本（`IsBetaVersion=true`），不建议在生产环境中无限制使用。对于大多数常规 MRQ 渲染需求，该数据接口基本可用，但如遇问题可能需要自行调试或等待未来更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraMRQ)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/NiagaraMRQ)（无独立测试文件，测试内容继承于 Niagara 核心）