# Niagara

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | Niagara 粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例资源） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

---

## 用途

Niagara 是 Unreal Engine 5 的**核心 GPU/CPU 粒子系统与视觉特效框架**，用于替代旧版 Cascade 粒子系统。它提供了一个完全可编程、基于节点图的视觉特效编辑器，支持：

- **GPU 与 CPU 双模态仿真**：粒子可以在 CPU 或 GPU 上运行，GPU 模式可处理数十万甚至百万级粒子
- **Data Interface 体系**：通过数据接口（Data Interface）机制将外部数据（骨骼网格、静态网格、样条线、场景捕获、音频、渲染目标等）注入粒子仿真管线
- **Data Channel 系统**：实现 Niagara 系统之间、Niagara 与游戏逻辑之间的数据通信，支持跨发射器/跨系统的数据读写
- **Simulation Stage**：多阶段仿真管线，支持迭代数据接口（如 2D/3D 网格），实现流体模拟、扩散等高级效果
- **Stateless 粒子系统**：无状态粒子模式，适用于大规模背景粒子（如草地、星场），无需逐帧模拟
- **性能基线系统**：内置性能基线对比与监控，帮助团队控制特效性能开销
- **SimCache**：仿真缓存机制，支持录制、回放和对比粒子仿真结果
- **Scalability 体系**：基于重要性（Significance）和距离的自动 LOD/剔除，控制全局特效预算

---

## 使用场景

- 你需要制作**火焰、烟雾、爆炸、魔法、子弹轨迹**等视觉特效 → 使用 Niagara 创建发射器和系统
- 你需要**GPU 大规模粒子**（百万级草地、星海、雨雪）→ 使用 Stateless 模式 + GPU 仿真
- 你需要粒子**采样骨骼网格表面**生成血液飞溅或皮肤效果 → 使用 Skeletal Mesh Data Interface
- 你需要粒子**沿样条线流动**（如能量光束、管道中的液体）→ 使用 Spline Data Interface
- 你需要**多个 Niagara 系统之间传递数据**（如一个系统写入数据，另一个系统读取并生成粒子）→ 使用 Data Channel
- 你需要在粒子中**播放音效**（枪声、碰撞声）→ 使用 Audio Player Data Interface
- 你需要粒子与**2D/3D 网格交互**（如流体模拟、烟雾扩散）→ 使用 Grid2D/Grid3D Collection
- 你需要将粒子仿真数据**渲染到 Render Target** 供材质使用 → 使用 Render Target 2D/Volume Data Interface
- 你需要通过蓝图**动态控制粒子数组数据** → 使用 `UNiagaraDataInterfaceArrayFunctionLibrary`
- 你需要从**场景捕获相机**采样数据驱动粒子 → 使用 Scene Capture 2D Data Interface

---

## 蓝图用法

### 核心节点 — 系统生成与控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn System At Location` | 在世界坐标位置生成 Niagara 系统 | `UNiagaraFunctionLibrary` |
| `Spawn System Attached` | 附加到组件上生成 Niagara 系统 | `UNiagaraFunctionLibrary` |
| `Get Niagara Parameter Collection` | 获取 Niagara 参数集合实例 | `UNiagaraFunctionLibrary` |
| `Create Niagara Parameter Collection Instance` | 创建新的参数集合实例 | `UNiagaraFunctionLibrary` |

### 核心节点 — 用户参数覆盖

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Niagara Static Mesh Component` | 覆盖静态网格用户参数 | `UNiagaraFunctionLibrary` |
| `Set Niagara Skeletal Mesh Component` | 覆盖骨骼网格用户参数 | `UNiagaraFunctionLibrary` |
| `Set Texture Object` | 覆盖纹理用户参数 | `UNiagaraFunctionLibrary` |
| `Set Volume Texture Object` | 覆盖体积纹理用户参数 | `UNiagaraFunctionLibrary` |
| `Set Texture 2D Array Object` | 覆盖 2D 数组纹理用户参数 | `UNiagaraFunctionLibrary` |
| `Set Scene Capture 2D Data Interface Managed Mode` | 设置场景捕获 DI 的托管模式参数 | `UNiagaraFunctionLibrary` |
| `Get All User Parameters` | 获取系统所有用户参数信息 | `UNiagaraFunctionLibrary` |
| `Get All Emitters` | 获取系统所有发射器信息 | `UNiagaraFunctionLibrary` |

### 核心节点 — 数组数据接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Niagara Float Array` | 设置浮点数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Get Niagara Float Array` | 获取浮点数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Float Array Value` | 设置数组中单个浮点值 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Get Niagara Float Array Value` | 获取数组中单个浮点值 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Vector Array` | 设置向量数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Position Array` | 设置位置数组数据（支持 LWC） | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Color Array` | 设置颜色数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Int32 Array` | 设置整数数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Bool Array` | 设置布尔数组数据 | `UNiagaraDataInterfaceArrayFunctionLibrary` |
| `Set Niagara Matrix Array` | 设置矩阵数组数据（支持 LWC Rebase） | `UNiagaraDataInterfaceArrayFunctionLibrary` |

> 数组类型支持完整的一一对应 Set/Get，包括 Float、Vector2D、Vector、Position、Vector4、Color、Quat、Matrix、Int32、UInt8、Bool。

### 核心节点 — Data Channel

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Write To Niagara Data Channel (Batch)` | 批量写入数据通道 | `UNiagaraDataChannelLibrary` |
| `Read From Niagara Data Channel (Batch)` | 批量读取数据通道 | `UNiagaraDataChannelLibrary` |
| `Read From Niagara Data Channel` | 从数据通道读取单条数据 | `UNiagaraDataChannelLibrary` |
| `Write To Niagara Data Channel` | 写入单条数据到数据通道 | `UNiagaraDataChannelLibrary` |
| `Get Data Channel Element Count` | 获取数据通道中的元素数量 | `UNiagaraDataChannelLibrary` |
| `Subscribe To Niagara Data Channel` | 订阅数据通道更新事件 | `UNiagaraDataChannelLibrary` |
| `Unsubscribe From Niagara Data Channel` | 取消数据通道订阅 | `UNiagaraDataChannelLibrary` |

### 核心节点 — HWRT 碰撞

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Component Niagara GPU Ray Traced Collision Group` | 为组件设置 GPU 光追碰撞组 | `UNiagaraFunctionLibrary` |
| `Set Actor Niagara GPU Ray Traced Collision Group` | 为 Actor 设置 GPU 光追碰撞组 | `UNiagaraFunctionLibrary` |
| `Acquire Niagara GPU Ray Traced Collision Group` | 获取一个可用的光追碰撞组 | `UNiagaraFunctionLibrary` |
| `Release Niagara GPU Ray Traced Collision Group` | 释放光追碰撞组 | `UNiagaraFunctionLibrary` |

### 核心节点 — 刚体网格碰撞 DI

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Source Actors` | 设置刚体网格碰撞查询的数据源 Actor 列表 | `UNiagaraDIRigidMeshCollisionFunctionLibrary` |

### 核心节点 — 静态网格 DI

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Niagara Static Mesh DI Instance Index` | 设置静态网格 DI 的实例索引（用于 ISM） | `UNiagaraDataInterfaceStaticMesh` |

### 使用示例（蓝图描述）

**生成爆炸特效并传递网格数据：**

1. 从蓝图事件（如 OnHit）调用 `Spawn System At Location`，传入爆炸 NiagaraSystem、碰撞位置和旋转
2. 通过 `Set Niagara Skeletal Mesh Component` 将被击中的骨骼网格组件绑定到粒子的采样 DI 参数上
3. 可选：通过 `Set Niagara Static Mesh Component` 同时传递静态网格参数

**通过 Data Channel 实现跨系统通信：**

1. 在系统 A 的蓝图中，使用 `Write To Niagara Data Channel` 将数据（如爆炸位置、强度）写入名为 "ExplosionChannel" 的 Data Channel
2. 在系统 B（如碎屑系统）的 Emitter 脚本中，添加 `Data Channel Reader` DI，绑定到 "ExplosionChannel"
3. 使用 `Spawn Conditional` 节点根据数据通道中的条目生成碎屑粒子

**动态控制粒子数组：**

1. 在 Niagara 组件中添加一个 `Array Float` 类型的用户参数，命名为 "Heights"
2. 在蓝图中，使用 `Set Niagara Float Array` 节点，传入 NiagaraComponent、参数名 "Heights" 和高度数组
3. 在粒子脚本中通过 `Get` 函数读取这些高度值

---

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"
#include "NiagaraDataInterfaceArrayFunctionLibrary.h"
#include "NiagaraDataChannelFunctionLibrary.h"
#include "NiagaraDataInterface.h"
#include "NiagaraWorldManager.h"
#include "NiagaraModule.h"
```

### 基本用法 — C++ 中生成 Niagara 系统

```cpp
// 来源: UNiagaraFunctionLibrary
// 生成一个 Niagara 系统到指定世界位置
UNiagaraComponent* SpawnNiagaraEffect(UWorld* World, UNiagaraSystem* SystemTemplate, FVector Location)
{
    return UNiagaraFunctionLibrary::SpawnSystemAtLocation(
        World,
        SystemTemplate,
        Location,
        FRotator::ZeroRotator,          // Rotation
        FVector(1.f),                    // Scale
        true,                            // bAutoDestroy
        true,                            // bAutoActivate
        ENCPoolMethod::None,             // PoolingMethod
        true                             // bPreCullCheck
    );
}

// 附加到组件上生成
UNiagaraComponent* SpawnAttachedNiagara(USceneComponent* AttachTo, UNiagaraSystem* System)
{
    return UNiagaraFunctionLibrary::SpawnSystemAttached(
        System,
        AttachTo,
        NAME_None,                       // AttachPointName
        FVector::ZeroVector,             // Location
        FRotator::ZeroRotator,           // Rotation
        EAttachLocation::KeepRelativeOffset,
        true,                            // bAutoDestroy
        true,                            // bAutoActivate
        ENCPoolMethod::None              // PoolingMethod
    );
}
```

### 基本用法 — 动态设置用户参数

```cpp
// 来源: UNiagaraFunctionLibrary

// 覆盖静态网格参数
UNiagaraFunctionLibrary::OverrideSystemUserVariableStaticMeshComponent(
    NiagaraComponent,
    TEXT("MyMeshParam"),                // 参数名
    StaticMeshComponent
);

// 覆盖骨骼网格参数
UNiagaraFunctionLibrary::OverrideSystemUserVariableSkeletalMeshComponent(
    NiagaraComponent,
    TEXT("MySkeletalMeshParam"),
    SkeletalMeshComponent
);

// 设置纹理对象
UNiagaraFunctionLibrary::SetTextureObject(
    NiagaraComponent,
    TEXT("MyTextureParam"),
    Texture
);
```

### 基本用法 — 数组数据接口操作

```cpp
// 来源: UNiagaraDataInterfaceArrayFunctionLibrary
// 设置浮点数组到 Niagara
TArray<float> Positions;
Positions.Add(100.f);
Positions.Add(200.f);
Positions.Add(300.f);

UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloat(
    NiagaraComponent,
    FName("MyFloatArray"),
    Positions
);

// 读取回来
TArray<float> ReadPositions = UNiagaraDataInterfaceArrayFunctionLibrary::GetNiagaraArrayFloat(
    NiagaraComponent,
    FName("MyFloatArray")
);

// 设置单个值（自动扩展数组）
UNiagaraDataInterfaceArrayFunctionLibrary::SetNiagaraArrayFloatValue(
    NiagaraComponent,
    FName("MyFloatArray"),
    5,                                  // Index
    999.f,                              // Value
    true                                // bSizeToFit
);
```

### 进阶用法 — Data Channel C++ 写入/读取

```cpp
// 来源: UNiagaraDataChannelLibrary
// 批量写入数据通道
void WriteExplosionData(UWorld* World, UNiagaraDataChannelAsset* Channel, FVector ExplosionPos)
{
    UNiagaraDataChannelWriter* Writer = UNiagaraDataChannelLibrary::WriteToNiagaraDataChannel(
        World,
        Channel,
        FNiagaraDataChannelSearchParameters(),
        1,                              // Count
        true,                           // bVisibleToGame
        true,                           // bVisibleToCPU
        false,                          // bVisibleToGPU
        TEXT("ExplosionSystem")
    );
    
    if (Writer && Writer->Num() > 0)
    {
        // 使用 Writer 写入具体数据...
        // Writer->WriteFloat(FName("ExplosionRadius"), 0, 500.f);
    }
}

// 读取数据通道
void ReadExplosionData(UWorld* World, UNiagaraDataChannelAsset* Channel)
{
    UNiagaraDataChannelReader* Reader = UNiagaraDataChannelLibrary::ReadFromNiagaraDataChannel(
        World,
        Channel,
        FNiagaraDataChannelSearchParameters(),
        true                            // bReadPreviousFrame
    );
    
    if (Reader)
    {
        int32 Count = Reader->Num();
        for (int32 i = 0; i < Count; ++i)
        {
            // 使用 Reader 读取第 i 条数据...
        }
    }
}
```

### 进阶用法 — 自定义 Data Interface

```cpp
// 来源: UNiagaraDataInterface (基类模式)
// 创建自定义数据接口需要继承 UNiagaraDataInterface
UCLASS(EditInlineNew, Category = "Custom", meta = (DisplayName = "My Custom DI"))
class UMyCustomDataInterface : public UNiagaraDataInterface
{
    GENERATED_UCLASS_BODY()

public:
    // 属性
    UPROPERTY(EditAnywhere, Category = "Custom")
    float MyValue = 1.0f;

    // 实现虚拟函数
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo,
        void* InstanceData, FVMExternalFunction& OutFunc) override;
    
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override
    {
        return Target == ENiagaraSimTarget::CPUSim; // 仅 CPU 仿真
    }

    virtual bool InitPerInstanceData(void* PerInstanceData,
        FNiagaraSystemInstance* SystemInstance) override;
    virtual void DestroyPerInstanceData(void* PerInstanceData,
        FNiagaraSystemInstance* SystemInstance) override;

    virtual bool Equals(const UNiagaraDataInterface* Other) const override;

protected:
    virtual bool CopyToInternal(UNiagaraDataInterface* Destination) const override;

#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif
};
```

### 进阶用法 — 访问 Niagara 模块与性能基线

```cpp
// 来源: INiagaraModule
// 获取 Niagara 模块实例
INiagaraModule& NiagaraModule = FModuleManager::GetModuleChecked<INiagaraModule>("Niagara");

// 生成性能基线
#if NIAGARA_PERF_BASELINES
TArray<UNiagaraEffectType*> Baselines;
// ... 填充 Baselines ...
NiagaraModule.GeneratePerfBaselines(Baselines);

// 切换性能基线显示
NiagaraModule.ToggleStatPerfBaselines(GetWorld(), nullptr);
#endif

// 控制全局缩放
float SpawnScale = INiagaraModule::GetGlobalSpawnCountScale();
float SystemScale = INiagaraModule::GetGlobalSystemCountScale();

// 刷新数据通道
INiagaraModule::RefreshDataChannels();
```

### 进阶用法 — GPU 计算调度接口

```cpp
// 来源: FNiagaraGpuComputeDispatchInterface
// 在渲染线程中获取 GPU 计算调度接口
FNiagaraGpuComputeDispatchInterface* ComputeDispatch = 
    FNiagaraGpuComputeDispatchInterface::Get(World);

if (ComputeDispatch)
{
    // 获取全局距离场数据
    const FGlobalDistanceFieldParameterData* GDFData = 
        ComputeDispatch->GetGlobalDistanceFieldData();
    
    // 获取 GPU 实例计数管理器
    FNiagaraGPUInstanceCountManager& CountManager = 
        ComputeDispatch->GetGPUInstanceCounterManager();
    
    // 刷新所有待处理的 tick
    ComputeDispatch->FlushPendingTicks_GameThread();
    
    // 获取黑色纹理（用于空绑定）
    // FRDGTextureRef BlackTex = ComputeDispatch->GetBlackTexture(GraphBuilder, ETextureDimension::Texture2D);
}
```

---

## Demo 示例

一个完整的最小示例：创建自定义 Niagara 数据接口，暴露一个 Float 值给粒子脚本使用。

### MyCustomDataInterface.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NiagaraDataInterface.h"
#include "NiagaraShared.h"
#include "MyCustomDataInterface.generated.h"

UCLASS(EditInlineNew, Category = "Custom", meta = (DisplayName = "My Custom DI"))
class MYPROJECT_API UMyCustomDataInterface : public UNiagaraDataInterface
{
    GENERATED_UCLASS_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Custom")
    float MyValue = 1.0f;

    // UObject Interface
    virtual bool Equals(const UNiagaraDataInterface* Other) const override;
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override;

    // UNiagaraDataInterface Interface
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo,
        void* InstanceData, FVMExternalFunction& OutFunc) override;
    virtual int32 PerInstanceDataSize() const override { return 0; }

protected:
    virtual bool CopyToInternal(UNiagaraDataInterface* Destination) const override;

#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif

private:
    void VMGetMyValue(FVectorVMExternalFunctionContext& Context);
};
```

### MyCustomDataInterface.cpp

```cpp
#include "MyCustomDataInterface.h"
#include "NiagaraTypes.h"
#include "NiagaraCustomVersion.h"
#include "VectorVM.h"

UMyCustomDataInterface::UMyCustomDataInterface(FObjectInitializer const& ObjectInitializer)
    : Super(ObjectInitializer)
{
    Proxy.Reset();
}

bool UMyCustomDataInterface::Equals(const UNiagaraDataInterface* Other) const
{
    if (!Super::Equals(Other))
        return false;

    const UMyCustomDataInterface* OtherTyped = Cast<const UMyCustomDataInterface>(Other);
    if (!OtherTyped)
        return false;

    return MyValue == OtherTyped->MyValue;
}

bool UMyCustomDataInterface::CanExecuteOnTarget(ENiagaraSimTarget Target) const
{
    return Target == ENiagaraSimTarget::CPUSim;
}

bool UMyCustomDataInterface::CopyToInternal(UNiagaraDataInterface* Destination) const
{
    if (!Super::CopyToInternal(Destination))
        return false;

    UMyCustomDataInterface* TypedDest = CastChecked<UMyCustomDataInterface>(Destination);
    TypedDest->MyValue = MyValue;
    return true;
}

#if WITH_EDITORONLY_DATA
void UMyCustomDataInterface::GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
    {
        FNiagaraFunctionSignature Sig;
        Sig.Name = TEXT("GetMyValue");
        Sig.bMemberFunction = true;
        Sig.bRequiresContext = false;
        Sig.Outputs.Add(FNiagaraVariable(FNiagaraTypeDefinition::GetFloatDef(), TEXT("Value")));
        OutFunctions.Add(Sig);
    }
}
#endif

void UMyCustomDataInterface::GetVMExternalFunction(
    const FVMExternalFunctionBindingInfo& BindingInfo,
    void* InstanceData,
    FVMExternalFunction& OutFunc)
{
    if (BindingInfo.Name == TEXT("GetMyValue"))
    {
        OutFunc = FVMExternalFunction::CreateUObject(
            this, &UMyCustomDataInterface::VMGetMyValue);
    }
}

void UMyCustomDataInterface::VMGetMyValue(FVectorVMExternalFunctionContext& Context)
{
    VectorVM::FExternalFuncRegisterHandler<float> OutValue(Context);

    for (int32 i = 0; i < Context.GetNumInstances(); ++i)
    {
        OutValue.GetAndAdvance() = MyValue;
    }
}
```

---

## 模块依赖

Niagara 是一个庞大的插件，以下列出其**独特**的模块依赖关系（基于 Build.cs 中的 PublicDependencyModuleNames 和 PrivateDependencyModuleNames）。

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 核心基础类型与共享工具 |
| `NiagaraShader` | Niagara 着色器编译与 HLSL 生成 |
| `NiagaraVertexFactories` | Niagara 顶点工厂（精灵、网格、条带渲染） |
| `NiagaraBlueprintNodes` | Niagara 蓝图专用节点 |
| `NiagaraAnimNotifies` | 动画通知集成（在动画 Montage 中触发 Niagara 特效） |
| `NiagaraEditor` | Niagara 编辑器 UI、节点图、属性面板 |
| `NiagaraEditorWidgets` | Niagara 编辑器自定义控件 |
| `VectorVM` | 向量虚拟机（CPU 仿真的执行引擎） |
| `Renderer` | 渲染器模块（GPU 渲染管线集成） |
| `RHI` / `RenderCore` | 底层图形 API 与渲染核心 |
| `AnimGraphRuntime` | 动画图运行时（骨骼网格采样） |
| `MeshDescription` | 网格描述数据（静态网格采样） |
| `AudioMixer` | 音频混合器（Audio Player DI） |
| `SignalProcessing` | 信号处理（音频相关） |
| `PhysicsCore` | 物理核心（Physics Asset DI、刚体碰撞查询） |
| `DataflowCore` | 数据流核心（实验性 Dataflow DI） |
| `GeometryCollectionEngine` | 几何集合引擎（Chaos 破碎 DI） |
| `PythonScriptPlugin` | Python 脚本插件（自动化工具支持） |
| `ToolsetReg` | 工具集注册（编辑器集成） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级中视图同步被重复调用的问题 |
| 2026-05-22 | `85c6d110` | Avoid creating an empty RHI buffer for SKM sampling data | 优化骨骼网格采样时避免创建空 RHI 缓冲区 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene | 修复硬件光追实例获取时损坏 GPUScene 的问题 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复条带渲染器光追几何体多次更新导致的崩溃 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复 AI 工具或 Python 脚本写入空数据时烘焙设置崩溃 |

### 维护评价

**活跃维护 — 核心引擎级组件**

- **创建时间**：2017 年 8 月，已持续维护约 9 年
- **更新频率**：极为活跃，2026 年 5 月仍有持续功能性更新和 bug 修复
- **代码规模**：1622 个源文件，8 个模块，是 UE5 中规模最大的插件之一
- **维护状态**：Epic Games 持续投入开发，作为 Cascade 的正式替代方案，是 UE5 粒子特效的唯一官方系统
- **特性成熟度**：从基础粒子到 Data Channel、Stateless 模式、GPU 仿真、SimCache 等高级功能均已稳定
- **已知限制**：部分功能标记为 Experimental（如 Dynamic Mesh DI、Scene Capture 2D DI、Dataflow DI），但核心功能完全稳定
- **推荐程度**：**强烈推荐**。这是 UE5 的标准粒子系统，所有需要视觉特效的项目都应使用 Niagara 而非已废弃的 Cascade

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/creating-visual-effects-in-niagara-for-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Tests)