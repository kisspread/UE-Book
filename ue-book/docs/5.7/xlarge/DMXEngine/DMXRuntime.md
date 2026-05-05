# DMX Engine

> Functionality and assets for communication with DigitalMultiplexer (DMX) enabled devices

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXBlueprintGraph` (UncookedOnly), `DMXEditor` (Runtime), `DMXRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-02-19 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine) | |

## 用途

DMX Engine 是 Unreal Engine 虚拟制片管线中的 **DMX 协议通信核心插件**，解决以下问题：

1. **DMX 设备通信**：通过 Art-Net、sACN 等 DMX 协议与舞台灯光、LED 面板、烟雾机等物理 DMX 设备进行双向数据通信
2. **Fixture 管理**：基于 GDTF（General Device Type Format）标准定义灯具类型（Fixture Type），通过 Fixture Patch 将灯具映射到 DMX 宇宙（Universe）和通道（Channel）
3. **MVR 场景交换**：支持 MVR（My Virtual Rig）标准，实现虚拟场景与灯光控制台之间的场景数据导入/导出，包括灯具位置、层级关系等
4. **Sequencer 集成**：在 Sequencer 时间轴上对 DMX 属性进行关键帧动画，实现精确的灯光编程回放
5. **蓝图集成**：通过 DMXComponent 和 DMXSubsystem 提供完整的蓝图 API，使游戏逻辑能够发送和接收 DMX 数据

简而言之，这个插件让 Unreal Engine 成为一个完整的 DMX 灯光控制工作站，同时支持虚拟制片中的实时灯光同步。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED Volume 拍摄中，将 Unreal 中的虚拟灯光与实际 LED 面板和舞台灯具实时同步
- **灯光预编程**：在演出前使用 Sequencer 对灯光 cue 进行编程和预览，然后导出到灯光控制台
- **实时灯光控制**：通过蓝图接收来自灯光控制台的 DMX 数据，驱动场景中的灯光效果或触发游戏事件
- **MVR 场景导入**：从灯光设计软件（如 grandMA3）导入 MVR 文件，在 Unreal 中自动创建对应的灯具 Actor
- **交互式灯光装置**：在互动艺术装置中，用游戏逻辑控制 DMX 灯具实现动态灯光效果
- **LED 像素映射（Pixel Mapping）**：将视频内容映射到 LED 面板阵列，通过 DMX 协议驱动每个像素

## 蓝图用法

### 核心节点 — DMXComponent

DMXComponent 是挂载到 Actor 上的组件，用于接收来自 Fixture Patch 的 DMX 数据。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Fixture Patch` | 获取组件关联的 Fixture Patch | `UDMXComponent` |
| `Set Fixture Patch` | 设置组件关联的 Fixture Patch | `UDMXComponent` |
| `Set Receive DMX From Patch` | 启用/禁用从 Patch 接收 DMX 数据 | `UDMXComponent` |
| `On Fixture Patch Received` | 委托：当 Fixture Patch 收到 DMX 时广播 | `UDMXComponent` |
| `On DMX Component Tick` | 委托：每 Tick 广播（当组件有 Patch 且接收 DMX 启用时） | `UDMXComponent` |

### 核心节点 — DMXSubsystem

DMXSubsystem 是引擎子系统，提供全局 DMX 操作函数。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Clear DMX Buffers` | 清除所有端口和 Fixture Patch 的缓冲数据 | `UDMXSubsystem` |
| `Send DMX To Output Port` | 通过输出端口发送原始 DMX 数据 | `UDMXSubsystem` |
| `Get DMX Data From Input Port` | 从输入端口获取指定宇宙的 DMX 数据 | `UDMXSubsystem` |
| `Get DMX Data From Output Port` | 从输出端口获取指定宇宙的 DMX 数据 | `UDMXSubsystem` |
| `Get All Fixtures Of Type` | 获取使用指定 Fixture Type 的所有 Patch | `UDMXSubsystem` |
| `Get All Fixtures Of Category` | 获取指定分类的所有 Patch | `UDMXSubsystem` |
| `Get All Fixtures In Universe` | 获取指定宇宙中的所有 Patch | `UDMXSubsystem` |
| `Get All Fixtures With Tag` | 获取带指定自定义标签的所有 Patch | `UDMXSubsystem` |
| `Get All Fixtures In Library` | 获取 DMX Library 中所有 Patch | `UDMXSubsystem` |
| `Get Fixture By Name` | 通过名称查找 Fixture Patch | `UDMXSubsystem` |

### 核心节点 — Fixture Patch

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Fixture Patch In Library` | 在 DMX Library 中创建新的 Fixture Patch | `UDMXEntityFixturePatch` |
| `Remove Fixture Patch From Library` | 从 DMX Library 中移除 Fixture Patch | `UDMXEntityFixturePatch` |

### 核心节点 — DMXModulator

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Modulate` | 调制单个 Fixture Patch 的归一化属性值 | `UDMXModulator` |
| `Modulate Matrix` | 调制 Fixture Matrix 的归一化属性值数组 | `UDMXModulator` |

### 使用示例（蓝图描述）

**接收 DMX 数据并驱动灯光：**

1. 在场景中的 Actor 上添加 `DMXComponent`
2. 在组件的 Details 面板中设置 `Fixture Patch Ref` 指向 DMX Library 中的某个 Fixture Patch
3. 将 `On Fixture Patch Received` 委托拖入 Event Graph
4. 从委托输出引脚 `Value Per Attribute`（FDMXNormalizedAttributeValueMap）中获取属性值
5. 使用 `Map Find` 节点查找具体属性（如 "Dimmer"、"ColorAdd_R" 等），获取 0.0~1.0 的归一化值
6. 将值连接到灯光组件的 Intensity 或 Color 参数

**通过蓝图发送 DMX：**

1. 获取 `DMXSubsystem` 引用
2. 创建 `FDMXOutputPortReference` 结构体，指定输出端口
3. 构建 `TMap<int32, uint8>` 映射（通道号 → DMX 值 0-255）
4. 调用 `Send DMX To Output Port` 节点

**查询 DMX Library 中的 Fixture：**

1. 获取 `DMXSubsystem` 引用
2. 拖入 `Get All Fixtures In Library` 节点，传入 DMX Library 资产引用
3. 遍历返回的 `TArray<UDMXEntityFixturePatch*>` 进行操作

## C++ 用法

### 头文件引入

```cpp
#include "DMXSubsystem.h"
#include "DMXComponent.h"
#include "Library/DMXEntityFixturePatch.h"
#include "Library/DMXEntityFixtureType.h"
#include "Library/DMXLibrary.h"
```

### 基本用法 — 通过 Fixture Patch 接收 DMX

```cpp
// 来源: DMXEntityFixturePatch.h, DMXComponent.h

// 方式一：使用 DMXComponent 组件
// 在 Actor 中添加 UDMXComponent，绑定委托
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    UDMXComponent* DMXComp = FindComponentByClass<UDMXComponent>();
    if (DMXComp)
    {
        DMXComp->OnFixturePatchReceived.AddDynamic(this, &AMyActor::OnDMXReceived);
    }
}

void AMyActor::OnDMXReceived(UDMXEntityFixturePatch* FixturePatch, const FDMXNormalizedAttributeValueMap& ValuePerAttribute)
{
    // 从 Map 中获取 Dimmer 值 (0.0 ~ 1.0)
    if (const float* DimmerValue = ValuePerAttribute.Map.Find(FDMXAttributeName("Dimmer")))
    {
        // 驱动灯光亮度
        PointLight->SetIntensity(*DimmerValue * 10000.f);
    }
}
```

### 基本用法 — 发送 DMX 数据

```cpp
// 来源: DMXSubsystem.h

// 通过输出端口发送原始 DMX 数据
UDMXSubsystem* DMXSubsystem = GEngine->GetEngineSubsystem<UDMXSubsystem>();

FDMXOutputPortReference OutputPortRef;
OutputPortRef.PortName = TEXT("MyArtNetPort"); // 需要在项目设置中配置

TMap<int32, uint8> ChannelToValueMap;
ChannelToValueMap.Add(1, 255);  // 通道 1 = 255
ChannelToValueMap.Add(2, 128);  // 通道 2 = 128
ChannelToValueMap.Add(3, 0);    // 通道 3 = 0

UDMXSubsystem::SendDMXToOutputPort(OutputPortRef, ChannelToValueMap, 1); // 宇宙 1
```

### 进阶用法 — 创建 Fixture Patch 并查询属性

```cpp
// 来源: DMXEntityFixturePatch.h, DMXEntityFixtureType.h

// 创建 Fixture Patch
FDMXEntityFixturePatchConstructionParams Params;
Params.FixtureTypeRef.SetEntity(MyFixtureType);  // 设置 Fixture Type
Params.ActiveMode = 0;                            // 使用第一个模式
Params.UniverseID = 1;                            // 宇宙 1
Params.StartingAddress = 1;                       // 起始地址 1

UDMXEntityFixturePatch* NewPatch = UDMXEntityFixturePatch::CreateFixturePatchInLibrary(
    Params, TEXT("MySpotLight"), true);

// 获取 Patch 的属性值
if (NewPatch)
{
    FDMXNormalizedAttributeValueMap NormalizedValues;
    NewPatch->GetNormalizedAttributeValues(NormalizedValues);

    for (const auto& Pair : NormalizedValues.Map)
    {
        UE_LOG(LogTemp, Log, TEXT("Attribute: %s, Value: %f"), 
            *Pair.Key.ToString(), Pair.Value);
    }
}
```

### 进阶用法 — MVR 场景导入/导出

```cpp
// 来源: DMXMVRGeneralSceneDescription.h

// 从 DMX Library 创建 MVR 场景描述
UDMXMVRGeneralSceneDescription* SceneDesc = UDMXMVRGeneralSceneDescription::CreateFromDMXLibrary(
    *MyDMXLibrary, GetTransientPackage());

// 配置导出参数
UE::DMX::FDMXMVRGeneralSceneDescriptionWorldParams WorldParams;
WorldParams.World = GetWorld();
WorldParams.bExportPatchesNotPresentInWorld = false;
WorldParams.bUseTransformsFromLevel = true;

SceneDesc->WriteDMXLibrary(*MyDMXLibrary, WorldParams);

// 导出为 XML 文件
TSharedPtr<FXmlFile> XmlFile = SceneDesc->CreateXmlFile();
if (XmlFile.IsValid())
{
    XmlFile->Save(TEXT("MyScene.mvr"));
}
```

### 进阶用法 — 自定义 DMX Modulator

```cpp
// 来源: DMXModulator.h

// 创建自定义调制器（蓝图或 C++）
UCLASS()
class UMyCustomModulator : public UDMXModulator
{
    GENERATED_BODY()

public:
    virtual void Modulate_Implementation(
        UDMXEntityFixturePatch* FixturePatch,
        const TMap<FDMXAttributeName, float>& InNormalizedAttributeValues,
        TMap<FDMXAttributeName, float>& OutNormalizedAttributeValues) override
    {
        // 复制输入到输出
        OutNormalizedAttributeValues = InNormalizedAttributeValues;

        // 将 Dimmer 值限制在 50%
        if (float* Dimmer = OutNormalizedAttributeValues.Find(FDMXAttributeName("Dimmer")))
        {
            *Dimmer = FMath::Clamp(*Dimmer, 0.f, 0.5f);
        }
    }
};
```

## Demo 示例

### 最小 DMX 接收 Actor

```cpp
// MyDMXLightActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "DMXTypes.h"
#include "MyDMXLightActor.generated.h"

class UDMXComponent;
class UPointLightComponent;
class UDMXEntityFixturePatch;

UCLASS()
class AMyDMXLightActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDMXLightActor();

    UFUNCTION()
    void OnDMXReceived(UDMXEntityFixturePatch* FixturePatch, 
                       const FDMXNormalizedAttributeValueMap& ValuePerAttribute);

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDMXComponent> DMXComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPointLightComponent> PointLight;
};
```

```cpp
// MyDMXLightActor.cpp
#include "MyDMXLightActor.h"
#include "DMXComponent.h"
#include "Components/PointLightComponent.h"
#include "Library/DMXEntityFixturePatch.h"

AMyDMXLightActor::AMyDMXLightActor()
{
    DMXComponent = CreateDefaultSubobject<UDMXComponent>(TEXT("DMXComponent"));
    RootComponent = DMXComponent;

    PointLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("PointLight"));
    PointLight->SetupAttachment(RootComponent);
    PointLight->SetIntensity(0.f);
}

void AMyDMXLightActor::BeginPlay()
{
    Super::BeginPlay();
    DMXComponent->OnFixturePatchReceived.AddDynamic(this, &AMyDMXLightActor::OnDMXReceived);
}

void AMyDMXLightActor::OnDMXReceived(
    UDMXEntityFixturePatch* FixturePatch,
    const FDMXNormalizedAttributeValueMap& ValuePerAttribute)
{
    const TMap<FDMXAttributeName, float>& AttrMap = ValuePerAttribute.Map;

    // Dimmer → 灯光强度
    if (const float* Dimmer = AttrMap.Find(FDMXAttributeName("Dimmer")))
    {
        PointLight->SetIntensity(*Dimmer * 10000.f);
    }

    // RGB 颜色
    const float* R = AttrMap.Find(FDMXAttributeName("ColorAdd_R"));
    const float* G = AttrMap.Find(FDMXAttributeName("ColorAdd_G"));
    const float* B = AttrMap.Find(FDMXAttributeName("ColorAdd_B"));
    if (R && G && B)
    {
        PointLight->SetLightColor(FLinearColor(*R, *G, *B));
    }
}
```

## 子模块文档

本插件包含 3 个模块，详见各子模块文档：

| 模块 | 类型 | 说明 |
|---|---|---|
| [DMXRuntime](DMXRuntime.md) | Runtime | 核心运行时：DMX 协议通信、Fixture 管理、MVR 场景、Sequencer 集成 |
| [DMXEditor](DMXEditor.md) | Runtime | 编辑器工具：DMX Library 编辑器、GDTF/MVR 导入器、Fixture Patch 编辑 UI |
| [DMXBlueprintGraph](DMXBlueprintGraph.md) | UncookedOnly | 蓝图图表：自定义 K2 节点用于蓝图中的 DMX 操作 |

## 模块依赖

从各模块 Build.cs 提取的独特依赖（省略 Core/Engine/Slate 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `DMXProtocol` | DMX 协议底层实现（Art-Net, sACN 等） |
| `DMXGDTF` | GDTF（General Device Type Format）标准解析 |
| `DMXFixtureActorInterface` | MVR Fixture Actor 接口定义 |

## 维护状态

### 近期更新

```
- 185622ca3bfb DMX: Fix DMX components cannot be patched
- ed12aec9a262 DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate
- c64541d21b57 DMX: Fix projects using DMX components cannot be packaged
```

### 维护评价

DMX Engine 是 Epic Games 官方维护的虚拟制片核心插件，**仍在活跃维护中**。

- **创建时间**：2020 年 2 月，约 5 年历史
- **代码规模**：476 个源文件，属于大型插件，架构成熟
- **近期更新**：最近的提交集中在 bug 修复（组件 patch 问题、打包问题）和代码质量改进（移除 FORCEINLINE），表明插件处于稳定维护阶段
- **API 演进**：源码中大量 `UE_DEPRECATED` 标记（如 Controller 系统在 4.27 废弃、旧 Import 系统在 5.5 废弃），说明 API 经历了多次重大重构，当前版本使用 Port 系统和 Fixture Type 工作流
- **已知限制**：部分旧 API 已废弃但仍保留兼容性，新项目应使用 Fixture Patch + Port 系统而非旧的 Controller 系统
- **推荐程度**：**强烈推荐**用于任何需要 DMX 通信的虚拟制片或灯光控制项目。作为 Epic 官方插件，与 Sequencer、蓝图系统深度集成，文档和社区支持较好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine)
- [DMXRuntime 子模块文档](DMXRuntime.md)
- [DMXEditor 子模块文档](DMXEditor.md)
- [DMXBlueprintGraph 子模块文档](DMXBlueprintGraph.md)