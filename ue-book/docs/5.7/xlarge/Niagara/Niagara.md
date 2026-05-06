# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例资源） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知（UE4.12 引入，约 2016 年） |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 Unreal Engine 的下一代视觉特效系统，用于创建高性能、GPU 驱动的粒子效果。相比传统的 Cascade 粒子系统，Niagara 提供了更灵活的数据驱动架构、基于计算着色器的模拟、以及强大的数据接口（Data Interface），允许粒子系统与场景、骨骼网格体、音频、纹理等实时交互。它解决了传统粒子系统在 GPU 性能、复杂模块化和跨系统数据共享方面的不足，是实现电影级视觉效果、大规模环境特效（如烟雾、火焰、爆炸）和动态天气效果的首选方案。

## 使用场景

- **大规模动态特效**：例如使用 GPU Compute 模拟数千个火焰粒子，每帧与骨骼网格体碰撞。
- **交互式环境**：玩家经过时触发飞散落叶或灰尘，利用碰撞查询数据接口获取场景几何体信息。
- **音频驱动效果**：通过音频振荡器数据接口将实时音频波形映射到粒子的颜色或运动。
- **纹理采样**：使用 2D/3D 纹理数据接口将体积纹理或渲染目标作为粒子属性场的输入。
- **网格渲染信息查询**：粒子系统运行时获取网格渲染器的局部边界盒或子 UV 细节。

## 蓝图用法

Niagara 的蓝图 API 主要通过 **数据接口函数库** 暴露，允许在运行时动态设置和读取粒子数组参数。此外，通过 **粒子回调处理接口** 可以每帧接收粒子数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNiagaraArrayFloat` | 设置 Niagara 系统的 Float 类型数组参数 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `SetNiagaraArrayVector` | 设置 FVector 数组参数 | 同上 |
| `SetNiagaraArrayColor` | 设置 FLinearColor 数组参数 | 同上 |
| `SetNiagaraArrayInt32` | 设置 int32 数组参数 | 同上 |
| `SetNiagaraArrayBool` | 设置 bool 数组参数 | 同上 |
| `SetNiagaraArrayFloatValue` | 设置数组中单个元素的值（可自动扩展数组） | 同上 |
| `GetNiagaraArrayFloat` | 获取 Niagara 系统的 Float 数组参数 | 同上 |
| `GetNiagaraArrayVector` | 获取 FVector 数组参数 | 同上 |
| `GetNiagaraArrayColor` | 获取 FLinearColor 数组参数 | 同上 |
| `GetNiagaraArrayInt32` | 获取 int32 数组参数 | 同上 |
| `ReceiveParticleData` | BlueprintNativeEvent，每帧接收从 Export 数据接口导出的粒子数据 | `INiagaraParticleCallbackHandler` |

### 使用示例（蓝图描述）

1. **运行时动态修改粒子数组**：
   - 在关卡蓝图中，获取需要控制的 Niagara 组件（`Niagara Component`）。
   - 调用 `SetNiagaraArrayFloat`，输入组件引用、参数名称（如 `User.SomeFloatArray`）以及一个 Float 数组。
   - 粒子系统内部使用该数组的数据接口读取这些值，实现实时参数驱动。

2. **导出粒子数据到蓝图**：
   - 在粒子发射器中添加 `Export` 数据接口，并将 `Callback Handler Parameter` 绑定到实现 `INiagaraParticleCallbackHandler` 接口的 Actor 或 Object。
   - 在该 Actor 的 `ReceiveParticleData` 事件中处理接收到的 `FBasicParticleData` 数组（包含位置、大小、速度）。

## C++ 用法

Niagara 运行时模块的核心是各种数据接口类和模拟上下文。以下示例展示如何通过 C++ 访问 Niagara 的数组数据接口。

### 头文件引入

```cpp
#include "NiagaraDataInterfaceArrayFunctionLibrary.h"
#include "NiagaraComponent.h"
```

### 基本用法（来自头文件 `NiagaraDataInterfaceArrayFunctionLibrary.h`）

```cpp
// 获取 Niagara 组件
UNiagaraComponent* NiagaraComp = ...;

// 设置 Float 数组
TArray<float> FloatData = { 1.0f, 2.0f, 3.0f };
UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloat(NiagaraComp, FName("User.ArrayFloat"), FloatData);

// 获取 Float 数组
TArray<float> OutData = UNiagaraDataInterfaceArrayFunctionLibrary::GetNiagaraArrayFloat(NiagaraComp, FName("User.ArrayFloat"));

// 设置单个元素，索引超出时自动扩展数组（bSizeToFit = true）
UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloatValue(NiagaraComp, FName("User.ArrayFloat"), 5, 42.0f, true);
```

来源：`Engine/Plugins/FX/Niagara/Source/Niagara/Classes/NiagaraDataInterfaceArrayFunctionLibrary.h`

### 进阶用法

**使用碰撞查询数据接口**：

```cpp
// 在自定义 Niagara Data Interface 的 C++ 实现中
#include "NiagaraDataInterfaceCollisionQuery.h"
#include "NiagaraCollision.h"

// 假设已有 UNiagaraDataInterfaceCollisionQuery* CollisionDI
// 通过 FVMExternalFunctionContext 调用 PerformQuerySyncCPU 进行同步碰撞检测
void UMyDataInterface::PerformQuery(FVectorVMExternalFunctionContext& Context)
{
    // 函数签名包含 StartPos, EndPos, TraceChannel, ResultPos, ResultNormal 等
    // 参考头文件声明：void PerformQuerySyncCPU(FVectorVMExternalFunctionContext& Context);
}
```

**自定义音频振荡器采样**（GPU 端 HLSL 生成）：

Niagara 的数据接口通过 `GetFunctionHLSL` 和 `GetParameterDefinitionHLSL` 生成 GPU 计算着色器代码。以 `UNiagaraDataInterfaceAudioOscilloscope` 为例，其代理类 `FNiagaraDataInterfaceProxyOscilloscope` 负责将 CPU 音频数据烘焙为 GPU 可读的 SRV 缓冲区。

## Demo 示例

以下是一个最小 C++ 示例，演示在 Actor 中运行时修改 Niagara 粒子系统的数组参数。假设已有一个 Niagra 系统资源。

**MyNiagaraActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNiagaraActor.generated.h"

class UNiagaraComponent;

UCLASS()
class MYGAME_API AMyNiagaraActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNiagaraActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Effects")
    UNiagaraComponent* NiagaraComponent;

    UFUNCTION(BlueprintCallable, Category = "Effects")
    void UpdateMyFloatArray(const TArray<float>& NewData);
};
```

**MyNiagaraActor.cpp**
```cpp
#include "MyNiagaraActor.h"
#include "NiagaraComponent.h"
#include "NiagaraDataInterfaceArrayFunctionLibrary.h"

AMyNiagaraActor::AMyNiagaraActor()
{
    PrimaryActorTick.bCanEverTick = false;
    NiagaraComponent = CreateDefaultSubobject<UNiagaraComponent>(TEXT("NiagaraComponent"));
    SetRootComponent(NiagaraComponent);
}

void AMyNiagaraActor::BeginPlay()
{
    Super::BeginPlay();
    // 设置初始数组
    TArray<float> InitData = { 0.1f, 0.2f, 0.3f };
    UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloat(NiagaraComponent, FName("User.MyArray"), InitData);
}

void AMyNiagaraActor::UpdateMyFloatArray(const TArray<float>& NewData)
{
    UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloat(NiagaraComponent, FName("User.MyArray"), NewData);
}
```

## 模块依赖

Niagara Runtime 模块（`Niagara`）的独特依赖模块：

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | 提供基础数据类型、编译哈希、数据缓冲区等核心框架 |
| `NiagaraShader` | 定义 Niagara 计算着色器参数、HLSL 生成上下文 |
| `NiagaraVertexFactories` | 提供 Niagara 渲染所需的顶点工厂和渲染资源 |
| `VectorVM` | 轻量级向量虚拟机，用于 CPU 端的粒子模拟 |

**省略常见依赖**：Core, CoreUObject, Engine, Slate, UMG, RenderCore, RHI, Projects, DeveloperSettings 等。

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` Fix for issue with access to freed Niagara Components during cleanup.
- 2025-10-22 `3f549682` Fixed issue with lingering NDC data when there are updates with no data from the CPU.
- 2025-10-21 `6ac05a79` Added off-by-default workaround for Niagara crash we hit in internal testing.
- 2025-10-17 `f6546371` Fix issue caused by mis-matched GT and RT ticks causing NDC data to be effectively lost from the POV
- 2025-10-16 `566219ca` [Backout] - CL47013072

### 维护评价

Niagara 是 Epic Games 核心维护的特效系统，持续获得功能和稳定性更新。近期 commit 集中在内存安全、多线程同步、以及 GPU 渲染管线修复，表明团队仍在积极优化。该插件自 UE4.12 引入以来经历了大规模重构和增强，目前是引擎默认粒子系统。**高度推荐使用**，但不建议用于需要极低内存占用的历史项目（可继续使用 Cascade）。已知限制：GPU 模拟对部分移动设备支持有限，以及部分高级数据接口（如音频）可能需要额外硬件支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/niagara-visual-effects-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests/Niagara)